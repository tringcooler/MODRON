#! python3
# coding: utf-8

from syntaxer import astnode, c_parser

#===============
# syntax define
#===============

KS_LBL = ':'
KS_OPS = '/'
KS_NEG = '-'
KS_PRS_EQ = '='
KS_PRS_PL = '+'
KS_DCL = '>'

KS_PRG_BR1 = '{'
KS_PRG_BR2 = '}'
KS_PRG_MRG = '+'

KS_NSP_REQ = '@'
KS_NSP_AL1 = '<'
KS_NSP_AL2 = '>'

KS_EXP_BR1 = '('
KS_EXP_BR2 = ')'
KS_EXP_ADD = '+'
KS_EXP_SUB = '-'
KS_EXP_MUL = '*'
KS_EXP_DIV = '/'

class module(astnode):
    DESC = lambda s,o,m,k,t: s(
        blankline,
        k('sects', m(sects)),
        blankline,
    )

class nblankline(astnode):
    DESC = lambda s,o,m,k,t: s(
        t(None, 'newline'),
        blankline,
    )

class blankline(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        t(None, 'newline'),
        blankline,
    ))

class sects(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('sect', sect),
        k('...', sects_tail),
    )
    def tidy(self):
        nd = self
        while nd:
            snd = nd.sub('sect')
            yield 'sect', snd
            nd = nd.sub('...')

class sects_tail(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        nblankline,
        k('sect', sect),
        k('...', sects_tail),
    ))

class sect(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('label', label),
        blankline,
        k('content', o(
            namespace, prog,
        )),
    )
    def tidy(self):
        nsreq = self.sub('label').sub('nsreq')
        if nsreq:
            nr = nsreq.sub('seq')
        else:
            nr = None
        yield 'namespace', nr
        yield self.sub('label').sub('name').sub('name'), self.sub('content')
    def cmpl(self, c):
        (_, nsreq), (lbl, ctt) = self.tidy()
        c.new()
        c.setpath(ctt.name(), lbl)
        c.ctx['seq'] = []
        if nsreq:
            c.c(nsreq)
            nr_seq = c.ret()
            c.ctx['nsreq'] = nr_seq
        c.c(ctt)
        c.archpath()

class label(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('name', sect_name),
        k('nsreq', m(namespace_req)),
        t(KS_LBL),
    )

class namespace_req(astnode):
    DESC = lambda s,o,m,k,t: s(
        t(KS_NSP_REQ),
        k('seq', nsref_seq),
    )

class sect_name(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('name', t(None, 'word'))
    )

class prog(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('prog', prog_seq),
    )

class prog_seq(astnode):
    DESC = lambda s,o,m,k,t: o(
        s(
            k('term', prog_lv1),
            k('...', prog_seq_tail_1),
        ),
        s(
            k('term', prog_lv2),
            k('...', prog_seq_tail_2),
        ),
    )
    def tidy(self):
        yield 'term', self.sub('term')
        nd = self.sub('...')
        while nd:
            yield 'term', nd.sub('merge'), nd.sub('term')
            nd = nd.sub('...')

class prog_seq_tail_1(astnode):
    DESC = lambda s,o,m,k,t: m(o(
        s(
            blankline,
            m(s(
                k('merge', t(KS_PRG_MRG)),
                blankline,
            )),
            k('term', prog_lv1),
            k('...', prog_seq_tail_1),
        ),
        s(
            m(s(
                blankline,
                k('merge', t(KS_PRG_MRG)),
            )),
            nblankline,
            k('term', prog_lv2),
            k('...', prog_seq_tail_2),
        ),
    ))

class prog_seq_tail_2(astnode):
    DESC = lambda s,o,m,k,t: m(o(
        s(
            nblankline,
            m(s(
                k('merge', t(KS_PRG_MRG)),
                blankline,
            )),
            k('term', prog_lv1),
            k('...', prog_seq_tail_1),
        ),
        s(
            nblankline,
            k('term', prog_lv2),
            k('...', prog_seq_tail_2),
        ),
    ))

class prog_lv1(astnode):
    DESC = lambda s,o,m,k,t: o(
        k('block', prog_block),
        k('ref', prog_ref),
    )

class prog_ref(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('name', t(None, 'word')),
    )

class prog_lv2(astnode):
    DESC = lambda s,o,m,k,t: o(
        k('stmt', prog_stmt),
    )

class prog_block(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('ns', m(namespace_alloc)),
        t(KS_PRG_BR1),
        k('seq', prog_seq),
        t(KS_PRG_BR2),
    )

class prog_stmt(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('condi', m(condi_seq)),
        t(KS_OPS),
        k('op', m(op_seq)),
    )

class namespace_alloc(astnode):
    DESC = lambda s,o,m,k,t: s(
        t(KS_NSP_AL1),
        k('seq', nsref_seq),
        t(KS_NSP_AL2),
    )

class nsref_seq(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('ref', nsref),
        k('...', nsref_seq_tail),
    )
    def tidy(self):
        nd = self
        while nd:
            snd = nd.sub('ref')
            yield 'ref', snd.sub('name')
            nd = nd.sub('...')
    def cmpl(self, c):
        c.new()
        seq = []
        for _, nr in self.tidy():
            seq.append(nr)
        c.archret(seq)

class nsref_seq_tail(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('ref', nsref),
        k('...', nsref_seq_tail),
    ))

class nsref(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('name', t(None, 'word')),
    )

class condi_seq(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('pair', condi_pair),
        k('...', condi_seq_tail),
    )
    def tidy(self):
        nd = self
        while nd:
            snd = nd.sub('pair')
            yield 'pair', snd
            nd = nd.sub('...')

class condi_seq_tail(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('pair', condi_pair),
        k('...', condi_seq_tail),
    ))

class condi_pair(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('reg', regref_wr),
        k('op', o(
            t(KS_PRS_EQ),
        )),
        k('value', signed_integer),
    )
    @classmethod
    def important(cls):
        return True

class op_seq(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('pair', op_pair),
        k('...', op_seq_tail),
    )
    def tidy(self):
        nd = self
        while nd:
            snd = nd.sub('pair')
            yield 'pair', snd
            nd = nd.sub('...')

class op_seq_tail(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('pair', op_pair),
        k('...', op_seq_tail),
    ))

class op_pair(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('reg', regref_wr),
        k('op', o(
            t(KS_PRS_EQ), t(KS_PRS_PL),
        )),
        k('value', signed_integer),
    )
    @classmethod
    def important(cls):
        return True

class unsigned_integer(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('value', t(None, 'digit')),
    )
    def cmpl(self, c):
        c.new()
        c.archret(int(self.sub('value')))

class signed_integer(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('neg', m(t(KS_NEG))),
        k('value', unsigned_integer),
    )
    def cmpl(self, c):
        c.new()
        c.c(self.sub('value'))
        val = c.ret()
        if self.sub('neg'):
            val = - val
        c.archret(val)

class regref_wr(astnode):
    DESC = lambda s,o,m,k,t: o(
        k('alloc', t(None, 'word')),
        k('direct', unsigned_integer),
    )

class regref_rd(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('alloc', t(None, 'word')),
    )
    def cmpl(self, c):
        c.new()
        c.archret(self.sub('alloc'))

class namespace(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('declare', declare),
        blankline,
        k('...', namespace_tail),
    )
    def tidy(self):
        nd = self
        while nd:
            snd = nd.sub('declare')
            yield 'declare', snd
            nd = nd.sub('...')

class namespace_tail(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('declare', declare),
        blankline,
        k('...', namespace_tail),
    ))

class declare(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('name', t(None, 'word')),
        t(KS_DCL),
        k('limit', calcexpr),
    )
    def tidy(self):
        yield self.sub('name'), self.sub('limit')
    def cmpl(self, c):
        c.new()
        (name, limit), = self.tidy()
        c.setpath('dec', name)
        c.c(limit)
        ec = c.ret()
        c.archpath(ec)

class calcexpr(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('expr', cexp_lv1),
    )

class cexp_lv1(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('expr', cexp_lv2),
        k('...', cexp_lv1_tail),
    )
    def tidy(self):
        yield 'expr', self.sub('expr')
        nd = self.sub('...')
        while nd:
            yield 'expr', nd.sub('op'), nd.sub('expr')
            nd = nd.sub('...')
    def cmpl(self, c):
        c.new()
        ec = c_expr_ctx(KS_EXP_ADD, False)
        itr = self.tidy()
        _, sub = next(itr)
        c.c(sub)
        term = c.ret()
        ec.addterm(term)
        for _, op, sub in itr:
            c.c(sub)
            term = c.ret()
            if op == KS_EXP_SUB:
                term = term.clone(True)
            ec.addterm(term)
        c.archret(ec)

class cexp_lv1_tail(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('op', o(
            t(KS_EXP_ADD), t(KS_EXP_SUB),
        )),
        k('expr', cexp_lv2),
        k('...', cexp_lv1_tail),
    ))

class cexp_lv2(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('expr', cexp_uop),
        k('...', cexp_lv2_tail),
    )
    def tidy(self):
        yield 'expr', self.sub('expr')
        nd = self.sub('...')
        while nd:
            yield 'expr', nd.sub('op'), nd.sub('expr')
            nd = nd.sub('...')
    def cmpl(self, c):
        c.new()
        ec = c_expr_ctx(KS_EXP_MUL, False)
        itr = self.tidy()
        _, sub = next(itr)
        c.c(sub)
        term = c.ret()
        ec.addterm(term)
        for _, op, sub in itr:
            c.c(sub)
            term = c.ret()
            if op == KS_EXP_DIV:
                term = term.clone(True)
            ec.addterm(term)
        c.archret(ec)

class cexp_lv2_tail(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('op', o(
            t(KS_EXP_MUL), t(KS_EXP_DIV),
        )),
        k('expr', cexp_uop),
        k('...', cexp_lv2_tail),
    ))

class cexp_uop(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('op', m(o(
            t(KS_NEG),
        ))),
        k('expr', cexp_term),
    )
    def cmpl(self, c):
        if not self.sub('op'):
            c.c(self.sub('expr'))
            return
        c.new()
        ec = c_expr_ctx(KS_EXP_ADD, False)
        c.c(self.sub('expr'))
        term = c.ret()
        term = term.clone(True)
        ec.addterm(term)
        c.archret(ec)

class cexp_term(astnode):
    DESC = lambda s,o,m,k,t: o(
        k('expr', cexp_br),
        k('term', regref_rd),
        k('term', unsigned_integer),
    )
    def cmpl(self, c):
        if self.sub('expr'):
            c.c(self.sub('expr'))
            return
        c.new()
        ec = c_expr_ctx(KS_EXP_ADD, False)
        c.c(self.sub('term'))
        val = c.ret()
        ec.initterm(val)
        c.archret(ec)

class cexp_br(astnode):
    DESC = lambda s,o,m,k,t: s(
        t(KS_EXP_BR1),
        k('expr', cexp_lv1),
        t(KS_EXP_BR2),
    )

#===============
# compile utils
#===============

class c_expr_ctx:

    ophs = {
        KS_EXP_ADD: lambda a, b: a+b,
        KS_EXP_MUL: lambda a, b: a*b,
    }
    nophs = {
        KS_EXP_ADD: lambda a: -a,
        KS_EXP_MUL: lambda a: 1/a,
    }
    opuvs = {
        KS_EXP_ADD: 0,
        KS_EXP_MUL: 1,
    }

    def __init__(self, op, neg):
        self.op = op
        self.neg = neg
        self.argspace = set()
        self.termseq = []
        self.termval = self.opuvs[op]

    def clone(self, neg = False):
        d = type(self)(self.op, self.neg, self.termval)
        d.argspace = self.argspace.copy()
        d.termseq = self.termseq.copy()
        d.termval = self.termval
        if neg:
            d.neg = not d.neg
        return d

    def initterm(self, term):
        if isinstance(term, c_expr_ctx):
            raise TypeError('init term should be a value')
        if isinstance(term, str):
            self.termseq.append(term)
            self.argspace.add(term)
        else:
            self.termval = term

    @property
    def ispure(self):
        la = len(self.termseq)
        if la > 1:
            return False
        elif la < 1:
            return True
        return self.termval == self.opuvs[self.op]

    @property
    def rdcval(self):
        la = len(self.termseq)
        if la > 1:
            return self
        elif la < 1:
            return self
        elif not self.termval == self.opuvs[self.op]:
            return self
        term = self.termseq[0]
        if isinstance(term, str):
            return self
        if self.neg:
            if not self.op == term.op:
                return self
            term = term.clone(True)
        #print('pure', self, '->', term.rdcval)
        return term.rdcval

    @property
    def negval(self):
        return self.nophs[self.op](self.termval)

    @property
    def tval(self):
        return self.negval if self.neg else self.termval

    def pushterm(self, term):
        self.argspace.update(term.argspace)
        self.termseq.append(term)

    def extendterm(self, term):
        neg = (term.neg != self.neg)
        for d in term.termseq:
            if isinstance(d, str):
                self.termseq.append(d)
                continue
            if neg:
                d = d.clone(True)
            self.pushterm(d)
        if neg:
            tval = term.negval
        else:
            tval = term.termval
        dval = self.ophs[self.op](self.termval, tval)
        self.termval = dval

    def addterm(self, term):
        term = term.rdcval
        if self.op == term.op:
            self.extendterm(term)
        else:
            self.pushterm(term)

    def resolve(self, rargs = {}):
        if not self.argspace:
            return self.tval
        rterm = type(self)(self.op, self.neg)
        op = self.ophs[self.op]
        for term in self.termseq:
            while isinstance(term, str):
                if term in rargs:
                    term = rargs[term]
                else:
                    break
            if isinstance(term, c_expr_ctx):
                term = term.resolve(rargs)
            if not isinstance(term, c_expr_ctx):
                d = type(self)(self.op, self.neg)
                d.initterm(term)
                term = d
            rterm.addterm(term)
        if not rterm.argspace:
            return rterm.tval
        else:
            return rterm

    def __str__(self):
        rs = []
        for term in self.termseq:
            rs.append(f'({str(term)})')
        rs.append(str(self.termval))
        r = (' ' + self.op + ' ').join(rs)
        if self.neg:
            r = '(' + r + ')'
            if self.op == KS_EXP_ADD:
                r = '(-' + r + ')'
            else:
                r = '(1/' + r + ')'
        return r

    def __repr__(self):
        return f'<{str(self)}>'

if __name__ == '__main__':

    from compiler import c_compiler
    from pdb import pm
    def test1():
        with open('../test2.mdr.txt', 'r') as fd:
            raw = fd.read()
        global psr, cmpl, rt
        psr = c_parser(module, raw)
        rt = psr.parse()
        cmpl = c_compiler(rt)
        cmpl.compile()
    test1()

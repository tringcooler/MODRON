#! python3
# coding: utf-8

from syntaxer import astnode, c_parser

KS_LBL = ':'
KS_OPS = '/'
KS_NEG = '-'
KS_PRS_EQ = '='
KS_PRS_PL = '+'
KS_DCL = '>'

KS_PRG_BR1 = '{'
KS_PRG_BR2 = '}'
KS_PRG_MRG = '+'

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
        while not nd.isempty:
            snd = nd.sub('sect')
            yield 'sect', snd.sub('label').sub('name'), snd.sub('content')
            nd = nd.nodes['...']

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
            prog, namespace,
        )),
    )

class label(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('name', t(None, 'word')), t(KS_LBL),
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
        nd = self
        while not nd.isempty:
            snd = nd.sub('term')
            yield 'term', snd
            nd = nd.nodes['...']

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
        while not nd.isempty:
            snd = nd.sub('ref')
            yield 'ref', snd.sub('name')
            nd = nd.nodes['...']

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
        while not nd.isempty:
            snd = nd.sub('pair')
            yield 'pair', snd
            nd = nd.nodes['...']

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
        while not nd.isempty:
            snd = nd.sub('pair')
            yield 'pair', snd
            nd = nd.nodes['...']

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

class signed_integer(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('neg', m(t(KS_NEG))),
        k('value', unsigned_integer),
    )

class regref_wr(astnode):
    DESC = lambda s,o,m,k,t: o(
        k('alloc', t(None, 'word')),
        k('direct', unsigned_integer),
    )

class regref_rd(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('alloc', t(None, 'word')),
    )

class namespace(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('declare', declare),
        blankline,
        k('...', namespace_tail),
    )
    def tidy(self):
        nd = self
        while not nd.isempty:
            snd = nd.sub('declare')
            yield 'declare', snd
            nd = nd.nodes['...']

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
    @classmethod
    def important(cls):
        return True

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
        nd = self
        while not nd.isempty:
            snd = nd.sub('expr')
            yield 'expr', snd
            nd = nd.nodes['...']

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
        nd = self
        while not nd.isempty:
            snd = nd.sub('expr')
            yield 'expr', snd
            nd = nd.nodes['...']

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

class cexp_term(astnode):
    DESC = lambda s,o,m,k,t: o(
        k('expr', cexp_br),
        k('term', regref_rd),
        k('term', unsigned_integer),
    )

class cexp_br(astnode):
    DESC = lambda s,o,m,k,t: s(
        t(KS_EXP_BR1),
        k('expr', cexp_lv1),
        t(KS_EXP_BR2),
    )

if __name__ == '__main__':

    from pdb import pm
    def test1():
        with open('../test2.mdr.txt', 'r') as fd:
            raw = fd.read()
        global psr
        psr = c_parser(module, raw)
        return psr.parse()
    rt = test1()

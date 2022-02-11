#! python3
# coding: utf-8

KLX_CMT = '#'
KLX_NL = '\n'

KW_LBL = ':'
KW_SPL = '/'

PRMTCH = lambda s, d: len(s) >= len(d) and s[:len(d)] == d

class err_lexer(Exception):
    pass

class err_syntax(Exception):
    pass

class c_lexer:

    def __init__(self, raw):
        self.raw = raw
        self.ridx = 0
        self.stat = 'idle'
        self.buf = ''
        self.bpos = (1, 1)
        self.cpos = (1, 1)

    @property
    def pos(self):
        return self.bpos

    def gc(self, peek = False):
        i = self.ridx
        if i >= len(self.raw):
            return ''
        c = self.raw[i]
        if not peek:
            self.ridx += 1
            prow, pcol = self.cpos
            if c == KLX_NL:
                prow += 1
                pcol = 0
            pcol += 1
            self.cpos = (prow, pcol)
        return c

    def rerr(self, e):
        raise err_lexer(f'(ln:{self.cpos[0]} col:{self.cpos[1]}) {e}')

    def parse(self):
        while self.stat != 'end':
            r = self.p1()
            if r:
                yield r

    def p1(self):
        r = self.pr_all()
        if r:
            return r
        mtd = getattr(self, 'p_' + self.stat)
        return mtd()

    def pr_all(self):
        c = self.gc(True)
        if c == KLX_CMT:
            r = ''
            while c and c != KLX_NL:
                self.gc()
                r += c
                c = self.gc(True)
            return ('comment', r)

    def p_idle(self):
        self.bpos = self.cpos
        c = self.gc()
        if not c:
            self.stat = 'end'
            return ('eof', None)
        elif c.isalpha() or c == '_':
            self.buf += c
            self.stat = 'word'
        elif c.isdigit():
            self.buf += c
            self.stat = 'digit'
        elif c.isspace():
            if c == KLX_NL:
                return ('newline', None)
        elif c.isascii():
            return ('symbol', c)
        else:
            self.rerr(f'invalid lex: {c}')

    def p_word(self):
        c = self.gc(True)
        if c.isalpha() or c.isdigit() or c == '_':
            self.buf += c
            self.gc()
        else:
            buf = self.buf
            self.buf = ''
            self.stat = 'idle'
            return ('word', buf)

    def p_digit(self):
        c = self.gc(True)
        if c.isdigit():
            self.buf += c
            self.gc()
        else:
            buf = self.buf
            self.buf = ''
            self.stat = 'idle'
            return ('digit', int(buf))

class c_parser:

    def __init__(self, lexer, cmplr):
        self.lx = lexer
        self.cp = cmplr
        self.reset()

    def reset(self):
        self.lxit = self.lx.parse()
        self.curlx = (None, None)
        self.la1lx = (None, None)
        self.ntok()
        self.ntok()
        self.stat = 'idle'
        self.ststk = []
        self.ctxs = {}
        self.progs = c_progs(self.cp)
        self.cprog = None

    @property
    def pos(self):
        return self.curlx[1]

    @property
    def ctok(self):
        return self.curlx[0]

    @property
    def la1tok(self):
        return self.la1lx[0]
        
    def ntok(self):
        self.curlx = self.la1lx
        try:
            self.la1lx = (next(self.lxit), self.lx.pos)
        except StopIteration:
            pass

    def rerr(self, e):
        raise err_syntax(f'(ln:{self.pos[0]} col:{self.pos[1]}) {e}')

    def stgo(self, st):
        ost = self.stat
        if ost != st and ost in self.ctxs and not ost in self.ststk:
            del self.ctxs[ost]
        self.stat = st

    def stpush(self):
        self.ststk.append(self.stat)

    def stpop(self):
        if len(self.ststk) == 0:
            self.rerr('unbalance stat')
        self.stgo(self.ststk.pop())

    def stback(self, bi):
        if bi > len(self.ststk) or bi <= 0:
            self.rerr('invalid ctx rel index')
        return self.ststk[-bi]

    def stctx(self, st = None):
        if st is None:
            st = self.stat
        elif isinstance(st, int):
            st = self.stback(st)
        if not st in self.ctxs:
            self.ctxs[st] = {}
        return self.ctxs[st]

    def chksym(self, c, la1 = True):
        if la1:
            tt, tv = self.la1tok
        else:
            tt, tv = self.ctok
        return tt == 'symbol' and tv == c

    def parse(self):
        while self.stat != 'done':
            self.p1()

    def p1(self):
        self.pr_all()
        mtd = getattr(self, 'p_' + self.stat)
        return mtd()

    def pr_all(self):
        tt, tv = self.ctok
        while tt == 'comment':
            self.ntok()
            tt, tv = self.ctok

    def p_idle(self):
        tt, tv = self.ctok
        if tt == 'newline':
            self.ntok()
        elif tt == 'word' and self.chksym(KW_LBL):
            self.cprog = tv
            self.progs.add(tv)
            self.stgo('prog')
            self.ntok()
            self.ntok()
        elif tt == 'eof':
            self.stgo('done')
        else:
            self.rerr(f'invalid label: {tv}')

    def p_prog(self):
        tt, tv = self.ctok
        if tt == 'newline':
            self.ntok()
        elif tt == 'word' and self.chksym(KW_LBL):
            self.stgo('idle')
        elif tt == 'eof':
            self.stgo('idle')
        else:
            self.stgo('condi')

    def p_pair(self):
        tt, tv = self.ctok
        if tt == 'digit':
            sctx = self.stctx()
            dctx = self.stctx(1)
            if not 'seq' in dctx:
                dctx['seq'] = []
            dctx['seq'].append((sctx['1st'], tv))
            self.stpop()
            self.ntok()
        else:
            self.rerr(f'invalid pair: {tv}')

    def p_condi(self):
        tt, tv = self.ctok
        if tt == 'digit' and self.chksym(KW_LBL):
            ctx = self.stctx('pair')
            ctx['1st'] = tv
            self.stpush()
            self.stgo('pair')
            self.ntok()
            self.ntok()
        elif self.chksym(KW_SPL, False):
            ctx = self.stctx()
            if 'seq' in ctx:
                condi = ctx['seq']
            else:
                condi = []
            self.progs.add(self.cprog, lambda cp: cp.c(*condi))
            self.stgo('opr')
            self.ntok()
        else:
            self.rerr(f'invalid condition: {tv}')

    def p_opr(self):
        tt, tv = self.ctok
        if tt == 'digit' and self.chksym(KW_LBL):
            ctx = self.stctx('pair')
            ctx['1st'] = tv
            self.stpush()
            self.stgo('pair')
            self.ntok()
            self.ntok()
        elif tt == 'newline' or tt == 'eof':
            ctx = self.stctx()
            if 'seq' in ctx:
                opr = ctx['seq']
            else:
                opr = []
            self.progs.add(self.cprog, lambda cp: cp.t(*opr))
            self.stgo('prog')
            if tt != 'eof':
                self.ntok()
        else:
            self.rerr(f'invalid operator: {tv}')

class c_progs:

    def __init__(self, cmplr):
        self.cp = cmplr
        self.progs = {}

    def add(self, name, cb = None):
        if not name in self.progs:
            self.progs[name] = self.cp
        if callable(cb):
            self.progs[name] = cb(self.progs[name])

if __name__ == '__main__':

    def test1():
        from modron import c_modron
        with open('test1.mdr.txt', 'r') as fd:
            raw = fd.read()
        md = c_modron()
        p = c_parser(c_lexer(raw), md.cmplr)
        p.parse()
        return p, md
    p, md = test1()

#! python3
# coding: utf-8

from errparse import err_parse

KLX_CMT = '#'
KLX_NL = '\n'

class err_lexer(err_parse):
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
        raise err_lexer(e).setpos(self.cpos)

    def parse(self):
        while self.stat != 'end':
            r = self.p1()
            if r:
                yield r
        while True:
            yield ('eof', None)

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
        else:
            return ('symbol', c)

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

if __name__ == '__main__':
    pass

#! python3
# coding: utf-8

class c_lexer:

    def __init__(self, raw):
        self.raw = raw
        self.ridx = 0
        self.stat = 'idle'
        self.buf = ''

    def gc(self):
        i = self.ridx
        self.ridx += 1
        if i >= len(self.raw):
            return None
        return self.raw[i]

    def parse(self):
        while self.stat != 'end':
            r = self.p1()
            if r:
                yield r

    def p1(self):
        mtd = getattr(self, 'p_' + self.stat)
        return mtd()

    def p_idle(self):
        c = self.gc
        

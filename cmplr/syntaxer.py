#! python3
# coding: utf-8

class err_syntax(Exception):

    def __init__(self, *na):
        super().__init__(*na)
        self.pos = None
        self.mod = None

    def setpos(self, pos):
        if not self.pos:
            self.pos = pos

    def setmod(self, mod):
        if not self.mod:
            self.mod = mod

    def __str__(self):
        msg = super().__str__()
        tags = []
        if self.mod:
            tags.append(f'm:{self.mod}')
        if self.pos:
            tags.append(f'ln:{self.pos[0]}')
            tags.append(f'col:{self.pos[1]}')
        if tags:
            msg = '(' + ', '.join(tags) + ')' + msg
        return msg

class c_tok_stream:

    def __init__(self, lexer, metainfo = None):
        self.lx = lexer
        self.metainfo = metainfo
        self.reset()

    def reset(self):
        self.strm = self.lx.parse()
        self.cache = []

    def meta(self, k):
        m = self.metainfo 
        if m and k in m:
            return m[k]
        else:
            return None

    def la(self, n = 0):
        while n + 1 > len(self.cache):
            tok = next(self.strm)
            if tok[0] == 'comment':
                continue
            pos = self.lx.pos
            self.cache.append((tok, pos))
        return self.cache[n]

    def tok(self, n = 0):
        return self.la(n)[0]

    def pos(self, n = 0):
        return self.la(n)[1]

    @property
    def tt(self):
        return self.tok()[0]

    @property
    def tv(self):
        return self.tok()[1]

    def chksym(self, v, n = 0):
        tt, tv = self.tok(n)
        return tt == 'symbol' and tv == v

    def go(self):
        self.cache.pop(0)

class astnode:

    def __init__(self, parser):
        self.parser = parser
        self.nodes = {}
        self.terms = {}

    def match(self, key, ndtyp, mult = False):
        nd = ndtyp(self.parser)
        if key:
            if mult:
                if not key in self.nodes:
                    self.nodes[key] = []
                self.nodes[key].append(nd)
            else:
                self.nodes[key] = nd
        strm = self.parser.stream
        try:
            nd.parse(strm)
        except err_syntax as e:
            e.setpos(self.s.pos)
            raise

    def term(self, key, val, mult = False):
        if mult:
            if not key in self.terms:
                self.terms[key] = []
            self.terms[key].append(val)
        else:
            self.terms[key] = val

    def parse(self, stream):
        raise NotImplementedError

    def show(self, lv=0, padding = '  '):
        print(self.__class__.__name__)
        pad = padding * (lv + 1)
        for k in self.terms:
            v = self.terms[k]
            if isinstance(v, list):
                for sv in v:
                    print(pad + f'{k}: {sv}')
            else:
                print(pad + f'{k}: {v}')
        for k in self.nodes:
            nd = self.nodes[k]
            if isinstance(nd, list):
                print(pad + f'{k}:')
                for snd in nd:
                    print(pad + padding * 1, end = '')
                    snd.show(lv + 2, padding)    
            else:
                print(pad + f'{k}: ', end = '')
                nd.show(lv + 1, padding)
        

#===========
# AST NODES
#===========

KS_LBL = ':'

class ulistnode(astnode):
    def parse(self, s):
        while True:
            if s.tt == 'eof':
                break
            elif self.parse_each(s):
                break
    def parse_each(self, stream):
        raise NotImplementedError

class blankline(ulistnode):
    def parse_each(self, s):
        if s.tt == 'newline':
            s.go()
        else:
            return True

class mlistnode(astnode):
    def parse(self, s):
        while True:
            self.match(None, blankline)
            if s.tt == 'eof':
                break
            elif self.parse_each(s):
                break
    def parse_each(self, stream):
        raise NotImplementedError

class module(mlistnode):
    def parse_each(self, s):
        self.match('sects', sect, True)

class sect(astnode):
    def parse(self, s):
        self.match('label', label)
        self.match(None, blankline)
        if s.tt == 'word':
            self.match('content', sequence)
        else:
            self.match('content', prog)

class label(astnode):
    def parse(self, s):
        if s.tt == 'word' and s.chksym(KS_LBL, 1):
            self.term('name', s.tv)
            s.go()
            s.go()
        else:
            raise err_syntax(f'invalid label {s.tv}')

class sequence(mlistnode):
    def parse_each(self, s):
        if s.chksym(KS_LBL, 1):
            return True
        elif s.tt == 'word':
            self.match('terms', seq_term, True)
        else:
            raise err_syntax(f'invalid seq term {s.tv}')

class seq_term(astnode):
    def parse(self, s):
        self.term('name', s.tv)
        s.go()

#===========

from lexer import c_lexer

class c_parser:

    def __init__(self, raw, metainfo = None):
        self.raw = raw
        self.metainfo = metainfo

    def new_stream(self, raw, mi):
        return c_tok_stream(c_lexer(raw), mi)

    def reset(self):
        self.stream = self.new_stream(self.raw, self.metainfo)

    def parse(self):
        self.reset()
        root = module(self)
        root.parse(self.stream)
        return root
    
if __name__ == '__main__':

    from pdb import pm
    def test1():
        with open('../test2.mdr.txt', 'r') as fd:
            raw = fd.read()
        psr = c_parser(raw)
        rt = psr.parse()
        return psr, rt
    psr, rt = test1()
        

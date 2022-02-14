#! python3
# coding: utf-8

class err_syntax(Exception):

    def __init__(self, *na):
        super().__init__(*na)
        self.pos = None
        self.meta = {}

    def setpos(self, pos):
        if not self.pos:
            self.pos = pos
        return self

    def set(self, k, v):
        if not k in self.meta:
            self.meta[k] = v
        return self

    def __str__(self):
        msg = super().__str__()
        tags = []
        if self.meta:
            for k in self.meta:
                v = self.meta[k]
                tags.append(f'{k}:{v}')
        if self.pos:
            tags.append(f'ln:{self.pos[0]}')
            tags.append(f'col:{self.pos[1]}')
        if tags:
            msg = '(' + ', '.join(tags) + ') ' + msg
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

    def chksyms(self, vs, n = 0):
        if not isinstance(vs, list):
            vs = [vs]
        for v in vs:
            tt, tv = self.tok(n)
            if tt == 'symbol' and tv == v:
                return True
        return False

    def go(self):
        self.cache.pop(0)

class astnode:

    def __init__(self, parser):
        self.parser = parser
        self.nodes = {}
        self.terms = {}

    def rerr(self, msg):
        raise (err_syntax(msg).set('nd', self.__class__.__name__)
               .setpos(self.parser.stream.pos()))

    def match(self, key, ndtyp, mult = False, **ka):
        if ndtyp:
            nd = ndtyp(self.parser)
        else:
            nd = None
        if key:
            if mult:
                if not key in self.nodes:
                    self.nodes[key] = []
                if nd:
                    self.nodes[key].append(nd)
            else:
                self.nodes[key] = nd
        if not nd:
            return
        s = self.parser.stream
        try:
            nd.parse(s, **ka)
        except err_syntax as e:
            e.setpos(s.pos())
            raise

    def mterm(self, key, mult = False, typ = 'symbol', val = None, cb = None):
        s = self.parser.stream
        tt, tv = s.tok()
        if (typ and tt != typ) or (val and
                (not tv in val if isinstance(val, list) else tv != val)):
            self.rerr(f'unmatched term {tv}')
        s.go()
        if key:
            if callable(cb):
                val = cb(tv)
            else:
                val = tv
            if mult:
                if not key in self.terms:
                    self.terms[key] = []
                self.terms[key].append(val)
            else:
                self.terms[key] = val

    def extra(self, key, val, mult = False):
        if mult:
            if not key in self.terms:
                self.terms[key] = []
            self.terms[key].append(val)
        else:
            self.terms[key] = val

    def parse(self, stream):
        raise NotImplementedError

    def prec(self, ndtyp, **ka):
        s = self.parser.stream
        return ndtyp.first(s, **ka)

    def first(stream):
        raise NotImplementedError

    def prec_end(self, **ka):
        s = self.parser.stream
        return type(self).follow(s, **ka)

    def follow(s):
        return s.tt == 'eof'

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
            if not nd:
                print(pad + f'{k}: None')
            elif isinstance(nd, list):
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
KS_OPS = '/'
KS_NEG = '-'
KS_PRS_EQ = '='
KS_PRS_PL = '+'
KS_DCL = '>'
KS_EXP_BR1 = '('
KS_EXP_BR2 = ')'
KS_EXP_ADD = '+'
KS_EXP_SUB = '-'
KS_EXP_MUL = '*'
KS_EXP_DIV = '/'

class listnode(astnode):
    def parse(self, s, **ka):
        while True:
            if self.prec_end():
                break
            self.parse_each(s, **ka)
            self.post_parse(s)
    def post_parse(self, stream):
        pass
    def parse_each(self, stream):
        raise NotImplementedError

class ulistnode(listnode):
    def follow(s):
        return super(__class__, __class__).follow(s) or s.tt == 'newline'

class blankline(listnode):
    def parse_each(self, s):
        self.mterm(None, typ = 'newline')
    def follow(s):
        return super(__class__, __class__).follow(s) or s.tt != 'newline'

class mlistnode(listnode):
    def post_parse(self, s):
        self.match(None, blankline)

class module(mlistnode):
    def parse_each(self, s):
        self.match(None, blankline)
        self.match('sects', sect, True)

class sect(astnode):
    def parse(self, s):
        self.match('label', label)
        self.match(None, blankline)
        if self.prec(prog):
            self.match('content', prog)
        elif self.prec(namespace):
            self.match('content', namespace)
        elif self.prec(sequence):
            self.match('content', sequence)
        else:
            self.rerr(f'invalid sect {s.tv}')

class label(astnode):
    def parse(self, s):
        self.mterm('name', typ='word')
        self.mterm(None, val=KS_LBL)
    def first(s):
        return s.tt == 'word' and s.chksym(KS_LBL, 1)

class sect_content(mlistnode):
    def follow(s):
        return super(__class__, __class__).follow(s) or label.first(s)

class prog(sect_content):
    def parse_each(self, s):
        self.match('stmt', prog_stmt, True)
    def first(s):
        return prog_stmt.first(s)

class prog_stmt(astnode):
    def parse(self, s):
        if s.chksym(KS_OPS):
            self.match('condi', None)
        elif self.prec(pairseq, use=KS_PRS_EQ):
            self.match('condi', pairseq, use=KS_PRS_EQ)
        else:
            self.rerr(f'invalid condi {s.tv}')
        self.mterm(None, val=KS_OPS)
        if self.prec(pairseq, use=[KS_PRS_EQ, KS_PRS_PL]):
            self.match('op', pairseq, use=[KS_PRS_EQ, KS_PRS_PL])
        elif self.prec_end():
            self.match('op', None)
        else:
            self.rerr(f'invalid op {s.tv}')
    def first(s):
        return s.chksym(KS_OPS) or pairseq.first(s, use=KS_PRS_EQ)
    def follow(s):
        return super(__class__, __class__).follow(s) or s.tt == 'newline'

class pairseq(ulistnode):
    def parse_each(self, s, use):
        self.match('terms', pair, True, use=use)
    def follow(s):
        return super(__class__, __class__).follow(s) or s.tt == 'symbol'
    def first(s, use):
        return pair.first(s, use=use)

class pair(astnode):
    def parse(self, s, use):
        self.match('reg', regref_wr)
        self.mterm('use', val = use)
        self.match('value', signed_num)
    def first(s, use):
        return regref_wr.first(s) and s.chksyms(use, 1)

class regref_wr(astnode):
    def parse(self, s):
        if s.tt == 'word':
            self.mterm('name', typ='word')
            self.extra('type', 'alloc')
        elif s.tt == 'digit':
            self.mterm('name', typ='digit', cb = lambda v: int(v))
            self.extra('type', 'direct')
        else:
            self.rerr(f'invalid regref {s.tv}')
    def first(s):
        return s.tt == 'word' or s.tt == 'digit'

class signed_num(astnode):
    def parse(self, s):
        sign = 1
        if s.chksym(KS_NEG):
            self.mterm(None, val = KS_NEG)
            sign = -1
        self.mterm('value', typ='digit', cb = lambda v: sign * int(v))
    def first(s):
        tt, tv = s.tok(n)
        if tt == 'digit':
            return True
        elif tt == KS_NEG:
            return s.tok(n+1)[0] == 'digit'
        else:
            return False

class namespace(sect_content):
    def parse_each(self, s):
        self.match('terms', declare, True)
    def first(s):
        return declare.first(s)

class declare(astnode):
    def parse(self, s):
        self.mterm('name', typ='word')
        self.mterm(None, val=KS_DCL)
        self.match('value', signed_num)
    def first(s):
        return s.tt == 'word' and s.chksym(KS_DCL, 1)

class sequence(sect_content):
    def parse_each(self, s):
        self.match('terms', sectref, True)
    def first(s):
        return sectref.first(s)

class sectref(astnode):
    def parse(self, s):
        self.mterm('name', typ='word')
    def first(s):
        return s.tt == 'word'

class calcexpr(astnode):
    def parse(self, s):
        if self.prec(cexp_br):
            self.match('head', cexp_br)
        elif self.prec(regref_rd):
            self.match('head', regref_rd)
        elif self.prec(signed_num):
            self.match('head', signed_num)
        else:
            self.rerr(f'invalid expr term {s.tv}')
        self.match('tail', cexp_tail)

class regref_rd(astnode):
    def parse(self,s):
        self.mterm('value', typ='word')
    def first(s):
        return s.tt == 'word'

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
        with open('../test1.mdr.txt', 'r') as fd:
            raw = fd.read()
        psr = c_parser(raw)
        rt = psr.parse()
        return psr, rt
    psr, rt = test1()
        

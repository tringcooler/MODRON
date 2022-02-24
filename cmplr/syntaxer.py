#! python3
# coding: utf-8

from flatinvoker import flat_invoker as fliv

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
        self.cache_offs = 0

    def meta(self, k):
        m = self.metainfo 
        if m and k in m:
            return m[k]
        else:
            return None

    def shift(self, n):
        return c_tok_stream_shift(self, n)

    def walked(self, n = 0):
        return self.cache_offs + n

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
        self.cache_offs += 1

class c_tok_stream_shift(c_tok_stream):

    def __init__(self, src, offset):
        super().__init__(src.lx, src.metainfo)
        self.src = src
        self.offset = offset

    def reset(self):
        pass

    def shift(self, n):
        return self.src.shift(self.offset + n)

    def walked(self, n = 0):
        return self.src.walked(n) + self.offset

    def la(self, n = 0):
        return self.src.la(self.offset + n)

    def go(self):
        self.src.go()

class c_nddesc:

    def __init__(self, *seq):
        self.seq = seq

    def rec_unmatch(self, strm, ctx, ext = None):
        pass

    def rec_match(self, strm, ctx):
        pass

    def _rec_mostmatch(self, strm, ctx, caneq):
        if not 'mostmatch' in ctx:
            mm = {
                'walked': -1,
            }
            ctx['mostmatch'] = mm
        else:
            mm = ctx['mostmatch']
        walked = strm.walked()
        if walked < mm['walked']:
            return None
        elif walked == mm['walked'] and not caneq:
            return None
        mm['walked'] = walked
        return mm

    def rec_unmatch_term(self, strm, ctx, stok, dtok):
        mm = self._rec_mostmatch(strm, ctx, False)
        if not mm:
            return
        ut = {}
        mm['unmatch'] = ut
        ut['toks'] = (stok, dtok)
        if 'ast_stack' in ctx:
            ut['ast_stack'] = ctx['ast_stack'].copy()
        else:
            ut['ast_stack'] = [('unkonown', strm.pos())]

    def rec_match_term(self, strm, ctx):
        mm = self._rec_mostmatch(strm, ctx, True)
        if not mm:
            return
        if 'unmatch' in mm:
            del mm['unmatch']

    def match(self, strm, flw, ctx):
        raise NotImplementedError

class c_ndresult:
    
    def __init__(self, meta, *seq):
        self.meta = meta
        self.seq = seq

class c_ndd_seq(c_nddesc):

    def match(self, strm, flw, ctx):
        cur_seq = [*self.seq[1:], *flw]
        ndd = self.seq[0]
        rseq = yield fliv.invoke(ndd.match, strm, cur_seq, ctx)
        if not rseq:
            self.rec_unmatch(strm, ctx)
            return rseq
        slen = len(self.seq)
        self.rec_match(strm, ctx)
        return [c_ndresult(
            {'typ': 'seq'}, *rseq[:slen]), *rseq[slen:]]

class c_ndd_or(c_nddesc):

    def match(self, strm, flw, ctx):
        for ndd in self.seq:
            rseq = yield fliv.invoke(ndd.match, strm, flw, ctx)
            if rseq:
                self.rec_match(strm, ctx)
                return rseq
        else:
            self.rec_unmatch(strm, ctx)
            return None

class c_ndd_maybe(c_nddesc):

    def match(self, strm, flw, ctx):
        ndd = self.seq[0]
        rseq = yield fliv.invoke(ndd.match, strm, flw, ctx)
        if rseq:
            self.rec_match(strm, ctx)
            return rseq
        r = c_ndresult({'typ': 'empty'})
        if flw:
            flndd = flw[0]
            flseq = flw[1:]
            flrseq = yield fliv.invoke(flndd.match, strm, flseq, ctx)
            if not flrseq:
                self.rec_unmatch(strm, ctx)
                return flrseq
            self.rec_match(strm, ctx)
            return [r, *flrseq]
        else:
            self.rec_match(strm, ctx)
            return [r]

class c_ndd_pair(c_nddesc):

    def match(self, strm, flw, ctx):
        key, ndd = self.seq
        rseq = yield fliv.invoke(ndd.match, strm, flw, ctx)
        if not rseq:
            self.rec_unmatch(strm, ctx)
            return rseq
        self.rec_match(strm, ctx)
        return [c_ndresult(
            {'typ': 'pair', 'key': key}, rseq[0]), *rseq[1:]]
            
class c_ndd_term(c_nddesc):

    def _parseseq(self):
        seq = self.seq
        if len(seq) > 1:
            term_typ = seq[1]
        else:
            term_typ = 'symbol'
        return term_typ, seq[0]

    def match(self, strm, flw, ctx):
        term_typ, term_val = self._parseseq()
        tt, tv = strm.tok()
        if term_typ != tt or (
            term_val and term_val != tv):
            self.rec_unmatch_term(strm, ctx,
                (tt, tv), (term_typ, term_val))
            self.rec_unmatch(strm, ctx)
            return None
        self.rec_match_term(strm, ctx)
        r = c_ndresult({'typ': 'term'}, tt, tv)
        if flw:
            flndd = flw[0]
            flseq = flw[1:]
            flrseq = yield fliv.invoke(flndd.match, strm.shift(1), flseq, ctx)
            if not flrseq:
                self.rec_unmatch(strm, ctx)
                return flrseq
            self.rec_match(strm, ctx)
            return [r, *flrseq]
        else:
            self.rec_match(strm, ctx)
            return [r]

class astnode:

    DESC = None
    _nddesc = None

    def __init__(self):
        self.nodes = {}
        self.isempty = False

    @classmethod
    def nddesc(cls):
        if not cls._nddesc:
            cls._nddesc = cls.DESC(
                c_ndd_seq, c_ndd_or, c_ndd_maybe, c_ndd_pair, c_ndd_term)
        return cls._nddesc

    @classmethod
    def _parsendr(cls, node, ndr):
        if not isinstance(ndr, c_ndresult):
            return ndr
        ntyp = ndr.meta['typ']
        if ntyp == 'seq':
            vs = []
            for r in ndr.seq:
                v = cls._parsendr(node, r)
                if v is None:
                    continue
                elif isinstance(v, list):
                    vs.extend(v)
                else:
                    vs.append(v)
            return vs
        elif ntyp == 'pair':
            k = ndr.meta['key']
            v = cls._parsendr(node, ndr.seq[0])
            node.nodes[k] = v
            return v
        elif ntyp == 'term':
            return ndr.seq[1]
        elif ntyp == 'empty':
            return None
        else:
            raise NotImplemented

    @classmethod
    def rec_aststack(cls, strm, ctx, push):
        if not 'ast_stack' in ctx:
            ctx['ast_stack'] = []
        if push:
            ctx['ast_stack'].append((cls.__name__, strm.pos()))
        else:
            ctx['ast_stack'].pop()

    @classmethod
    def rec_unmatch(cls, strm, ctx):
        ndd = cls.nddesc()
        ndd.rec_unmatch(strm, ctx, cls.__name__)

    @classmethod
    def rec_match(cls, strm, ctx):
        ndd = cls.nddesc()
        ndd.rec_match(strm, ctx)

    @classmethod
    def match(cls, strm, flw, ctx):
        ndd = cls.nddesc()
        cls.rec_aststack(strm, ctx, True)
        rseq = yield fliv.invoke(ndd.match, strm, flw, ctx)
        cls.rec_aststack(strm, ctx, False)
        if not rseq:
            cls.rec_unmatch(strm, ctx)
            return None
        ndr = rseq[0]
        node = cls()
        v = cls._parsendr(node, ndr)
        if not v:
            node.isempty = True
        cls.rec_match(strm, ctx)
        return [node, *rseq[1:]]

    def chknd(self, ndkey, *ndtyps):
        if not ndkey in self.nodes:
            return False
        nd = self.nodes[ndkey]
        for ndtyp in ndtyps:
            if isinstance(nd, ndtyp):
                return True
        return False

    def tidy(self):
        nds = self.nodes
        for k in nds:
            yield k, nds[k]

    def show(self, lv=0, padding = '  '):
        if self.isempty:
            print('empty')
            return
        print(self.__class__.__name__)
        pad = padding * (lv + 1)
        for k, nd in self.tidy():
            if not nd:
                print(pad + f'{k}: None')
            elif isinstance(nd, list):
                print(pad + f'{k}:')
                for snd in nd:
                    print(pad + padding * 1, end = '')
                    if isinstance(snd, astnode):
                        snd.show(lv + 2, padding)
                    else:
                        print(snd)
            elif isinstance(nd, astnode):
                print(pad + f'{k}: ', end = '')
                nd.show(lv + 1, padding)
            else:
                print(pad + f'{k}: {nd}')

#===========

from lexer import c_lexer

class c_parser:

    def __init__(self, rootnd, raw, metainfo = None):
        self.raw = raw
        self.rootnd = rootnd
        self.metainfo = metainfo

    def new_stream(self, raw, mi):
        return c_tok_stream(c_lexer(raw), mi)

    def reset(self):
        self.stream = self.new_stream(self.raw, self.metainfo)

    def parse(self):
        self.reset()
        ctx = {}
        self.last_ctx = ctx
        rseq = fliv.start(self.rootnd.match, self.stream, [c_ndd_term(None, 'eof')], ctx)
        if not rseq:
            ut = ctx['mostmatch']['unmatch']
            umname, umpos = ut['ast_stack'][-1]
            stok, dtok = ut['toks']
            raise err_syntax(f'unmatch {stok} should be {dtok}').setpos(umpos).set('nd', umname)
        return rseq[0]

    def trace_err(self):
        try:
            ustk = self.last_ctx['mostmatch']['unmatch']['ast_stack']
        except:
            return
        for ndname, pos in ustk:
            print(f'nd:{ndname} ln:{pos[0]} col:{pos[1]}')

if __name__ == '__main__':

    class texplv2(astnode):
        DESC = lambda s,o,m,k,t: s(
            k('v1', t(None, 'digit')),
            k('op', o(t('*'), t('/'))),
            k('v2', t(None, 'digit')) )

    class texplv1_tail(astnode):
        DESC = lambda s,o,m,k,t: m(s(
            k('op', o(t('+'), t('-'))),
            k('v2', texplv2),
            k('nxt', texplv1_tail) ))

    class texplv1(astnode):
        DESC = lambda s,o,m,k,t: s(
            k('v1', texplv2),
            k('tl', texplv1_tail) )

    def test1():
        raw = '1 * 2 + 3 / 4 + 2 * 1'
        psr = c_parser(texplv1, raw)
        return psr.parse()

    foo = test1()

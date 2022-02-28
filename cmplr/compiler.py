#! python3
# coding: utf-8

from errparse import err_parse

class err_compile(err_parse):
    pass

class c_compiler:

    def __init__(self, astroot):
        self.astroot = astroot
        self.ctxstack = [{}]
        self.archpool = {}

    def rerr(self, msg):
        raise err_compile(msg)

    @property
    def ctx(self):
        return self.ctxstack[-1]

    def new(self):
        self.ctxstack.append({})

    def arch(self, arch_guide = None):
        if len(self.ctxstack) < 1:
            raise err_compile('unbalance compile stack')
        ctx = self.ctxstack.pop()
        k = None
        if callable(arch_guide):
            r = arch_guide(ctx)
            try:
                k, ctx = r
            except:
                k = r
        elif arch_guide:
            k = arch_guide
        if k:
            self.archpool[k] = ctx

    def get(self, key):
        if not key in self.archpool:
            return None
        return self.archpool[key]

    @staticmethod
    def _spath(path):
        return '/'.join(path)

    def setpath(self, *path):
        self.ctx['path'] = self._spath(path)

    def archpath(self, cb_arch = None):
        def ag(ctx):
            sp = ctx['path']
            if callable(cb_arch):
                ctx = cb_arch(ctx)
            elif cb_arch:
                ctx = cb_arch
            else:
                del ctx['path']
            return sp, ctx
        self.arch(ag)

    def getpath(self, *path):
        return self.get(self._spath(path))

    def archret(self, ret = None):
        def ag(ctx):
            if ret is None:
                d = ctx
            else:
                d = ret
            return 'ret', d
        self.arch(ag)

    def ret(self):
        ret = self.get('ret')
        if 'ret' in self.archpool:
            del self.archpool['ret']
        return ret

    def c(self, nd):
        if not hasattr(nd, 'tidy') or nd.isempty:
            return
        elif not hasattr(nd, 'cmpl'):
            for *_, sub in nd.tidy():
                self.c(sub)
            return
        try:
            nd.cmpl(self)
        except err_compile as e:
            raise e.set('nd', nd.name()).setpos(nd.meta['pos'])
        except:
            raise

    def compile(self):
        self.c(self.astroot)

if __name__ == '__main__':
    pass

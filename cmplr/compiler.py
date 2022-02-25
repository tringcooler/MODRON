#! python3
# coding: utf-8

from errparse import err_parse

class err_compile(err_parse):
    pass

class c_compiler:

    def __init__(self, astroot):
        self.astroot = astroot
        self.curpath = None
        self.ctxpool = {}

    def rerr(self, nd, msg):
        raise err_compile(msg).setpos(nd.meta['pos'])

    def getctx(self):
        if not self.curpath:
            return None
        return self.ctxpool[self.curpath]

    def swctx(self, *path):
        spath = '/'.join(path)
        if not spath in self.ctxpool:
            self.ctxpool[spath] = {}
        self.curpath = spath
        return self.getctx()

    def compile(self):
        self.astroot.cmpl(self)

if __name__ == '__main__':
    pass

#! python3
# coding: utf-8

from errparse import err_parse

class err_compile(err_parse):
    pass

class c_compiler:

    def __init__(self, astroot):
        self.astroot = astroot
        self.curpath = 'root'
        self.ctxpool = {}
        self.pathstack = []

    def rerr(self, nd, msg):
        raise err_compile(msg).setpos(nd.meta['pos'])

    @property
    def ctx(self):
        spath = self.curpath 
        if not spath in self.ctxpool:
            self.ctxpool[spath] = {}
        return self.ctxpool[self.curpath]

    @staticmethod
    def _spath(path):
        return '/'.join(path)

    def goto(self, *path):
        self.curpath = self._spath(path)

    def push(self):
        self.pathstack.append(self.curpath)

    def pop(self):
        spath = self.pathstack.pop()
        self.curpath = spath

    def compile(self):
        self.astroot.cmpl(self)

if __name__ == '__main__':
    pass

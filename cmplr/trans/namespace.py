#! python3
# coding: utf-8

class c_namespace_declare:

    def __init__(self):
        pass

class c_namespace:

    def __init__(self):
        pass

class c_namespace_stack:

    def __init__(self):
        self.nsstack = []
        self.dirty = True

    @property
    def space(self):
        if self.dirty:
            pass
        return self._space

    def alloc(self, nsdec):
        ns = {'__name__': nsdec['name']}
        regs = nsdec['regs']
        for rn in regs:
            rlim = regs[rn]
            

    def require(self, nsname):
        pass

if __name__ == '__main__':
    pass

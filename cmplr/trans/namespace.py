#! python3
# coding: utf-8

from errtrans import err_trans

class c_namespace_declare:

    def __init__(self):
        self.reqns = []
        self.space = {}

    def require(self, *ns):
        self.reqns.extend(nslist)

    def declare(self, name, limit):
        if name in self.space:
            raise err_trans(f're-declare name in this space: {name}')
        self.space[name] = limit

class c_varinfo:

    def __init__(self):
        self.info = {
            'stat': 'init',
        }

    def declare(self, limit):
        if self.info['stat'] == 'instance':
            return False
        self.info['limit'] = limit
        self.info['stat'] = 'declare'
        return True

class c_namespace:

    def __init__(self):
        self.space = {}

    def _getinfo(self, name, can_new):
        if not name in self.space:
            if not can_new:
                return None
            self.space[name] = c_varinfo()
        return self.space[name]

    def declare(self, name, limit):
        vinfo = self._getinfo(name, True)
        if not vinfo.declare(limit):
            raise err_trans(f're-declare an instance name: {name}')

    def alias(self, dst, src):
        pass

    def require(self, name, limit):
        vinfo = self._getinfo(name, False)
        if not vinfo:
            raise err_trans(f'undeclare name: {name}')
        pass

    def instance(self, name):
        pass

    def get(self, name):
        pass

class c_namespace_stack:

    def __init__(self):
        self.nsstack = []

    def _getinfo(self, name):
        for ns in self.nsstack:
            vinfo = ns._getinfo(name, False)
            if vinfo:
                return vinfo
        else:
            return None

    def push(self):
        ns = c_namespace()
        self.nsstack.insert(0, ns)

    def pop(self):
        ns = self.nsstack.pop(0)

    def declare(self, *nsdecs):
        for nsdec in nsdecs:
            pass

    def alias(self, dst, src):
        pass

    def get(self, name):
        pass

if __name__ == '__main__':
    pass

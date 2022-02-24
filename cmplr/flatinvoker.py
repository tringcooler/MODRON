#! python3
# coding: utf-8

class c_fi_coroutine:

    def __init__(self, func, *na, **ka):
        self.fargs = (func, na, ka)
        self.isstart = False

    def start(self):
        co = self
        while isinstance(co, c_fi_coroutine) and not co.isstart:
            co = co._start()
        return co

    def _start(self):
        func, na, ka = self.fargs
        gen = func(*na, **ka)
        isret = False
        try:
            nxt = next(gen)
        except TypeError:
            return gen
        except StopIteration as e:
            return e.value
        self.gen = gen
        self.invoke = nxt
        self.isdone = False
        self.isstart = True
        return self

    def goon(self, ret):
        if self.isdone:
            raise RuntimeError('co-routine is done')
        try:
            nxt = self.gen.send(ret)
        except StopIteration as e:
            nxt = e.value
            self.isdone = True
        self.invoke = nxt

class flat_invoker:

    @staticmethod
    def invoke(func, *na, **ka):
        return c_fi_coroutine(func, *na, **ka)

    @staticmethod
    def run(stack):
        maxdeep = 0
        ret = None
        while stack:
            co = stack[-1]
            nco = co.invoke
            if co.isdone:
                stack.pop()
            if isinstance(nco, c_fi_coroutine):
                nco = nco.start()
                if isinstance(nco, c_fi_coroutine):
                    stack.append(nco)
                    stklen = len(stack)
                    if stklen > maxdeep:
                        maxdeep = stklen
                    continue
            ret = nco
            if not co.isdone:
                co.goon(ret)
                continue
            if stack:
                pco = stack[-1]
                pco.goon(ret)
        #print('done', maxdeep)
        return ret

    @classmethod
    def start(cls, *na, **ka):
        co = cls.invoke(*na, **ka).start()
        if not isinstance(co, c_fi_coroutine):
            return co
        co.invoke
        return cls.run([co])

if __name__ == '__main__':
    pass

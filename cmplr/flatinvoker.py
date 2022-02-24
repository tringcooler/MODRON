#! python3
# coding: utf-8

class c_fi_coroutine:

    def __new__(cls, itr):
        try:
            nxt = next(itr)
        except TypeError:
            co = itr
        except StopIteration as e:
            co = e.value
        else:
            co = super().__new__(cls)
            co.invoke = nxt
        return co

    def __init__(self, itr):
        self.iter = itr
        self.isdone = False

    def goon(self, ret):
        if self.isdone:
            raise RuntimeError('co-routine is done')
        try:
            nxt = self.iter.send(ret)
        except StopIteration as e:
            nxt = e.value
            self.isdone = True
        self.invoke = nxt

class flat_invoker:

    @staticmethod
    def invoke(func, *na, **ka):
        itr = func(*na, **ka)
        return c_fi_coroutine(itr)

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
        print('done', maxdeep)
        return ret

    @classmethod
    def start(cls, *na, **ka):
        co = cls.invoke(*na, **ka)
        if not isinstance(co, c_fi_coroutine):
            return co
        return cls.run([co])

if __name__ == '__main__':

    def tf1(n):
        if n < 2:
            return 1
        else:
            a = tf1(n-1)
            b = tf1(n-2)
            return a + b

    def tf2(n, v):
        if n < 2:
            return v + 1
        else:
            a = tf2(n-1, v)
            return tf2(n-1, a)

    def tf3(n, v):
        if n < 1:
            return v
        else:
            return tf3(n-1, 2 * v)

    fi = flat_invoker
    
    def ff1(n):
        if n < 2:
            return 1
        else:
            a = yield fi.invoke(ff1, n-1)
            b = yield fi.invoke(ff1, n-2)
            return a + b

    def ff2(n, v):
        if n < 2:
            return v + 1
        else:
            a = yield fi.invoke(ff2, n-1, v)
            return fi.invoke(ff2, n-1, a)

    def ff3(n, v):
        if n < 1:
            return v
        else:
            return fi.invoke(ff3, n-1, 2 * v)
        yield 'padding'

    def test():
        pass

    test()

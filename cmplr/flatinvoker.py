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
        return co

    def __init__(self, itr):
        self.iter = itr

    def goon(self, ret):
        isret = False
        try:
            nxt = self.iter.send(ret)
        except StopIteration as e:
            nxt = e.value
            isret = True
        return nxt, isret

class c_flat_invoker:

    def __init__(self):
        self.stack = []
        self.ret = None

    def invoke(self, func, *na, **ka):
        itr = func(*na, **ka)
        return c_fi_coroutine(itr)

    def run(self):
        ret = None
        while self.stack:
            co = self.stack[-1]
            nxt, isret = co.goon(ret)
            if isret:
                self.stack.pop()
            if isinstance(nxt, c_fi_coroutine):
                self.stack.append(nxt)
            else:
                ret = nxt
        return ret

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

    def test():
        pass

    test()

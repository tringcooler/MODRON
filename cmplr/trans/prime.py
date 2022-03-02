#! python3
# coding: utf-8

class c_primes:

    def __init__(self):
        self.prms = [2]
        self.psieve = {}

    def _erat2_next(self):
        d = self.psieve
        q = self.prms[-1]
        if q == 2:
            q = 1
        while True:
            q += 2
            p = d.pop(q, None)
            if p is None:
                d[q*q] = q
                self.prms.append(q)
                return q
            else:
                x = q + 2 * p
                while x in d:
                    x += 2 * p
                d[x] = p

    def _find(self, v, st, ed):
        prms = self.prms
        mid = (st + ed) // 2
        pm = prms[mid]
        if v == prms[mid]:
            return mid, mid + 1
        elif v > pm:
            nst = mid
            ned = ed
        else:
            nst = st
            ned = mid
        if ned - nst > 1:
            return self._find(v, nst, ned)
        else:
            return nst, ned

    def nextprime(self, v):
        prms = self.prms
        np = prms[-1]
        if v < np:
            if v < prms[0]:
                dpi = 0
            elif v == prms[0]:
                dpi = 1
            else:
                dpi = self._find(v, 0, len(prms) - 1)[1]
            return prms[dpi]
        while v >= np:
            np = self._erat2_next()
        return np

    def isprime(self, v):
        prms = self.prms
        np = prms[-1]
        while v > np:
            np = self._erat2_next()
        return v in prms

if __name__ == '__main__':
    pass

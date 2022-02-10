#! python3
# coding: utf-8

class c_modron_prog:
    
    def __init__(self):
        self.seq = []
    
    def append(self, cshift, condi, op):
        self.seq.append((cshift, condi, op))

    def exe(self, v):
        for cshift, condi, op in self.seq:
            sv = v + cshift
            if sv % condi == 0:
                return v + op
        else:
            return v

class c_modron_compiler:

    def __init__(self, ctx):
        self.ctx = ctx
        if not 'stat' in ctx:
            self.reset()

    def cnext(self, dctx):
        return type(self)(dctx)

    def reset(self):
        ctx = self.statctx(None, 'ready')
        ctx['pmax'] = 0
        ctx['raw'] = []
        self.ctx = ctx
        return self

    def statctx(self, s = None, d = None):
        ctx = self.ctx.copy()
        for k in ctx:
            v = ctx[k]
            if isinstance(v, list):
                ctx[k] = v.copy()
        if s:
            ss = ctx['stat']
            if not ss == s: #and not ss in s:
                raise RuntimeError(f'invalid stat: {ss} -> {s}')
        if d:
            ctx['stat'] = d
        return ctx

    def _updpmax(self, ctx, ps):
        if not ps:
            return
        pmax = max(p for p, m in ps)
        if pmax > ctx['pmax']:
            ctx['pmax'] = pmax

    def c(self, *condis):
        ctx = self.statctx('ready', 'condi')
        self._updpmax(ctx, condis)
        ctx['rawline/condi'] = condis
        return self.cnext(ctx)

    def t(self, *ops):
        ctx = self.statctx('condi', 'ready')
        self._updpmax(ctx, ops)
        condis = ctx['rawline/condi']
        ctx['raw'].append((condis, ops))
        #del ctx['rawline/condi']
        return self.cnext(ctx)

    @property
    def p(self):
        ctx = self.statctx('ready', 'cmpl')
        mdr = ctx['modron']
        mdr.pidx(ctx['pmax'])
        prog = c_modron_prog()
        for condis, ops in ctx['raw']:
            cshift = 0
            condi = 1
            for p, m in condis:
                if mdr.pidx(p) < 0:
                    raise ValueError('prm', p)
                condi *= p
                cshift -= mdr.regop(p, m)
            cshift %= mdr.pa
            op = 0
            for p, m in ops:
                op += mdr.regop(p, m)
            op %= mdr.pa
            prog.append(cshift, condi, op)
        ctx['prog'] = prog
        ctx['log'] = [str(mdr)]
        return self.cnext(ctx)

    @property
    def r(self):
        ctx = self.statctx('cmpl')
        return ctx['prog']

    @property
    def m(self):
        ctx = self.statctx('cmpl')
        return ctx['modron']

    def e(self):
        ctx = self.statctx('cmpl')
        mdr = ctx['modron']
        mdr.exe(ctx['prog'])
        ctx['log'].append(str(mdr))
        return self.cnext(ctx)

class c_modron:

    def __init__(self):
        self.prms = [2]
        self.psieve = {}
        self.mctab = {}
        self.reset()

    def reset(self):
        self.regs = 0
        self.ptop = 0

    @property
    def pmax(self):
        return self.prms[self.ptop]

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

    def _updptop(self, pi):
        dpi = self.ptop
        if dpi >= pi:
            return
        sr = self.regs
        self.ptop = pi
        while dpi < pi:
            dpi += 1
            m = self.regs % self.prms[dpi]
            sr -= self.mc[dpi] * m
        self.regs = sr % self.pa

    def pidx(self, p):
        pm = self.prms[-1]
        while p > pm:
            pm = self._erat2_next()
        try:
            pi = self.prms.index(p)
        except ValueError:
            return -1
        self._updptop(pi)
        return pi

    def pi(self, p):
        return self.pidx(p) + 1

    @staticmethod
    def pmodinv(a, p):
        return pow(a, p - 2, p)

    def _modcoeff(self, ps):
        pa = 1
        for p in ps:
            if self.pidx(p) < 0:
                raise ValueError(f'{p} is not a prime')
            pa *= p
        mc = []
        for p in ps:
            pk = pa // p
            mc.append(pk * self.pmodinv(pk, p))
        return mc, pa

    def modcoeff(self, ps):
        ps = tuple(sorted(ps))
        if not ps in self.mctab:
            self.mctab[ps] = self._modcoeff(ps)
        return self.mctab[ps]

    @property
    def aprms(self):
        return self.prms[:self.ptop + 1]

    @property
    def mcp(self):
        return self.modcoeff(self.aprms)
    
    @property
    def mc(self):
        return self.mcp[0]
    
    @property
    def pa(self):
        return self.mcp[1]

    def __repr__(self):
        return f'<regs:{self.regs} pa:{self.pa}>'
    
    def __str__(self):
        r = []
        for p in self.aprms:
            v = self.getreg(p)
            if v:
                r.append(f'r{p}={v}')
        return '<' + ' '.join(r) + '>'

    def getreg(self, p):
        return self.regs % p

    def regop(self, p, m):
        m %= p
        if m == 0:
            return 0
        pidx = self.pidx(p)
        return self.mc[pidx] * m

    def setreg(self, p, m):
        if m >= p or m < 0:
            raise ValueError(f'invalid value reg{p}:={m}')
        sm = self.getreg(p)
        if sm == m:
            self.pidx(p)
            return
        self.regs += self.regop(p, m - sm)
        self.regs %= self.pa

    @property
    def cmplr(self):
        return c_modron_compiler({'modron': self})

    def exe(self, prog):
        self.regs = prog.exe(self.regs) % self.pa

if __name__ == '__main__':
    
    md = c_modron()
    def test1(n=10):
        cc = md.cmplr
        cc.c().t((3, 2)).p.e()
        cp = cc \
            .c((3, 2)).t((3, -1)) \
            .c().t((3, 1), (5, 1)).p
        for i in range(n):
            print(cp.e().m)
        return cp
    cp = test1()

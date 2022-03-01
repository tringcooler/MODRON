#! python3
# coding: utf-8

KS_EXP_ADD = '+'
KS_EXP_SUB = '-'
KS_EXP_MUL = '*'
KS_EXP_DIV = '/'

class c_expr_ctx:

    ophs = {
        KS_EXP_ADD: lambda a, b: a+b,
        KS_EXP_MUL: lambda a, b: a*b,
    }
    nophs = {
        KS_EXP_ADD: lambda a: -a,
        KS_EXP_MUL: lambda a: 1 // a if abs(a) == 1 else 1/a,
    }
    opuvs = {
        KS_EXP_ADD: 0,
        KS_EXP_MUL: 1,
    }

    def __init__(self, op, neg):
        self.op = op
        self.neg = neg
        self.argspace = set()
        self.termseq = []
        self.termval = self.opuvs[op]

    def clone(self, neg = False):
        d = type(self)(self.op, self.neg)
        d.argspace = self.argspace.copy()
        d.termseq = self.termseq.copy()
        d.termval = self.termval
        if neg:
            d.neg = not d.neg
        return d

    def initterm(self, term):
        if isinstance(term, c_expr_ctx):
            raise TypeError('init term should be a value')
        if isinstance(term, str):
            self.termseq.append(term)
            self.argspace.add(term)
        else:
            self.termval = term

    @property
    def othop(self):
        ops = [*self.ophs.keys()]
        si = ops.index(self.op)
        return ops[(si + 1) % len(ops)]

    @property
    def noval(self):
        return self.termval == self.opuvs[self.op]

    @property
    def pure(self):
        la = len(self.termseq)
        if la > 1:
            return None
        elif la < 1:
            if self.neg:
                return self.negval
            else:
                return self.termval
        elif self.neg:
            return None
        elif not self.noval:
            return None
        term = self.termseq[0]
        if isinstance(term, str):
            return term
        else:
            return None

    @property
    def rdcterm(self):
        la = len(self.termseq)
        if not la == 1:
            return self
        elif not self.noval:
            return self
        term = self.termseq[0]
        if isinstance(term, str):
            return self
        if self.neg:
            return self
        #print('pure', self, '->', term.rdcterm)
        return term.rdcterm

    @property
    def othopterm(self):
        pval = self.pure
        if pval is None:
            return None
        term = type(self)(self.othop, False)
        term.initterm(pval)
        #print('othop', self, '->', term)
        return term

    def negterm(self, dop = None):
        sterm = self.rdcterm
        if dop is None or dop == sterm.op:
            return sterm.clone(True)
        oterm = sterm.othopterm
        if oterm:
            return oterm.clone(True)
        term = type(self)(dop, True)
        term.pushterm(sterm)
        return term

    @property
    def negval(self):
        return self.nophs[self.op](self.termval)

    @property
    def tval(self):
        return self.negval if self.neg else self.termval

    def pushterm(self, term):
        self.argspace.update(term.argspace)
        self.termseq.append(term)

    def extendterm(self, term):
        neg = (term.neg != self.neg)
        for d in term.termseq:
            if isinstance(d, str):
                if neg:
                    dt = type(self)(self.op, True)
                    dt.initterm(d)
                    self.pushterm(dt)
                else:
                    self.termseq.append(d)
                    self.argspace.add(d)
                continue
            if neg:
                d = d.negterm(self.op)
            if d.op == self.op and not d.neg:
                self.extendterm(d)
            else:
                self.pushterm(d)
        if neg:
            tval = term.negval
        else:
            tval = term.termval
        dval = self.ophs[self.op](self.termval, tval)
        self.termval = dval

    def addterm(self, term):
        #print(f'add [{self.op}]{self}  [{term.op}]{term}')
        term = term.rdcterm
        if self.op == term.op:
            self.extendterm(term)
        else:
            othterm = term.othopterm
            if othterm is None:
                self.pushterm(term)
            else:
                self.extendterm(othterm)

    def resolve(self, rargs = {}):
        if not self.argspace:
            return self.tval
        rterm = type(self)(self.op, False)
        op = self.ophs[self.op]
        for term in self.termseq:
            while isinstance(term, str):
                if term in rargs:
                    term = rargs[term]
                else:
                    break
            if isinstance(term, c_expr_ctx):
                term = term.resolve(rargs)
            if isinstance(term, c_expr_ctx):
                if self.neg:
                    term = term.negterm(self.op)
            else:
                d = type(self)(self.op, self.neg)
                d.initterm(term)
                term = d
            rterm.addterm(term)
        #print('rslv', self, '|', rterm)
        if not rterm.argspace:
            return rterm.tval
        else:
            return rterm

    def __str__(self):
        rs = []
        for term in self.termseq:
            if isinstance(term, str):
                rs.append(term)
            else:
                rs.append(f'({str(term)})')
        if not self.noval:
            rs.append(str(self.termval))
        r = (' ' + self.op + ' ').join(rs)
        if self.neg:
            if len(rs) > 1:
                r = '( ' + r + ' )'
            if self.op == KS_EXP_ADD:
                r = '-' + r
            else:
                r = '1/' + r
        return r

    def __repr__(self):
        return f'<{str(self)}>'

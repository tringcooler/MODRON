#! python3
# coding: utf-8

from syntaxer import astnode, c_parser

KS_LBL = ':'
KS_OPS = '/'
KS_NEG = '-'
KS_PRS_EQ = '='
KS_PRS_PL = '+'
KS_DCL = '>'
KS_EXP_BR1 = '('
KS_EXP_BR2 = ')'
KS_EXP_ADD = '+'
KS_EXP_SUB = '-'
KS_EXP_MUL = '*'
KS_EXP_DIV = '/'

class module(astnode):
    DESC = lambda s,o,m,k,t: s(
        blankline,
        k('sects', sects),
    )

class nblankline(astnode):
    DESC = lambda s,o,m,k,t: s(
        t(None, 'newline'),
        blankline,
    )

class blankline(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        t(None, 'newline'),
        blankline,
    ))

class sects(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('sect', sect),
        k('...', sects),
    ))

class sect(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('label', label),
        blankline,
        k('content', o(
            prog, namespace, sequence,
        )),
    )

class label(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('name', t(None, 'word')), t(KS_LBL),
    )

class prog(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('stmt', prog_stmt),
        k('...', prog_stmts),
    )

class prog_stmts(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('stmt', prog_stmt),
        k('...', prog_stmts),
    ))

class prog_stmt(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('condi', condi_seq),
        t(KS_OPS),
        k('op', op_seq),
        nblankline,
    )

class condi_seq(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('pair', condi_pair),
        k('...', condi_seq),
    ))

class condi_pair(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('reg', regref_wr),
        k('op', o(
            t(KS_PRS_EQ),
        )),
        k('value', signed_integer),
    )

class op_seq(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('pair', op_pair),
        k('...', op_seq),
    ))

class op_pair(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('reg', regref_wr),
        k('op', o(
            t(KS_PRS_EQ), t(KS_PRS_PL),
        )),
        k('value', signed_integer),
    )

class unsigned_integer(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('value', t(None, 'digit')),
    )

class signed_integer(astnode):
    DESC = lambda s,o,m,k,t: s(
        m(k('neg', t(KS_NEG))),
        k('value', unsigned_integer),
    )

class regref_wr(astnode):
    DESC = lambda s,o,m,k,t: o(
        k('alloc', t(None, 'word')),
        k('direct', unsigned_integer),
    )

class regref_rd(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('alloc', t(None, 'word')),
    )

class namespace(astnode):
    DESC = lambda s,o,m,k,t: s(
        t('not_implement'),
    )

class sequence(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('name', sectref),
        k('...', sectrefs),
    )

class sectrefs(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('name', sectref),
        k('...', sectrefs),
    ))

class sectref(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('sect', t(None, 'word')),
    )

if __name__ == '__main__':

    from pdb import pm
    def test1():
        with open('../test2.mdr.txt', 'r') as fd:
            raw = fd.read()
        psr = c_parser(module, raw)
        rt = psr.parse()
        return psr, rt
    psr, rt = test1()

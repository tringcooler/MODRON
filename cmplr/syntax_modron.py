#! python3
# coding: utf-8

from syntaxer import astnode, c_parser

KS_LBL = ':'
KS_OPS = '/'
KS_NEG = '-'
KS_PRS_EQ = '='
KS_PRS_PL = '+'
KS_DCL = '>'

KS_PRG_BR1 = '{'
KS_PRG_BR2 = '}'
KS_PRG_MRG = '+'

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
            prog, namespace,
        )),
    )

class label(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('name', t(None, 'word')), t(KS_LBL),
    )

class prog(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('prog', prog_lv1_seq),
    )

class prog_lv1_seq(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('term', prog_lv1_or_seq),
        blankline,
        k('...', m(prog_lv1_seq)),
    )

class prog_lv1_seq_tail(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('term', o(
            s(
                t(KS_PRG_MRG), o(
                    prog_lv1_seq, prog_lv2
                ),
            ),
            prog_lv1_seq,
        )),
        blankline,
        k('...', prog_lv1_seq_tail),
    ))

class prog_lv1_or_seq(astnode):
    DESC = lambda s,o,m,k,t: o(
        k('seq', prog_lv2_seq),
        k('term', prog_lv1),
    )

class prog_lv1(astnode):
    DESC = lambda s,o,m,k,t: o(
        k('block', prog_block),
        k('ref', prog_ref),
    )

class prog_ref(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('name', t(None, 'word')),
    )

class prog_lv2_seq(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('term', prog_lv2),
        blankline,
        k('...', prog_lv2_seq_tail),
    )

class prog_lv2_seq_tail(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('term', o(
            s(
                t(KS_PRG_MRG), prog_lv1,
            ),
            prog_lv2,
        )),
        blankline,
        k('...', prog_lv2_seq_tail),
    ))

class prog_lv2(astnode):
    DESC = lambda s,o,m,k,t: o(
        k('stmt', prog_stmt),
    )

class prog_block(astnode):
    DESC = lambda s,o,m,k,t: s(
        t(KS_PRG_BR1),
        k('seq', prog_lv1_seq),
        t(KS_PRG_BR2),
    )

class prog_stmt(astnode):
    DESC = lambda s,o,m,k,t: s(
        t(None, 'newline'),
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
        k('neg', m(t(KS_NEG))),
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
        k('declare', declare),
        blankline,
        k('...', m(namespace)),
    )

class declare(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('name', t(None, 'word')),
        t(KS_DCL),
        k('limit', calcexpr),
    )

class calcexpr(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('expr', cexp_lv1),
    )

class cexp_lv1(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('expr', cexp_lv2),
        k('...', cexp_lv1_tail),
    )

class cexp_lv1_tail(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('op', o(
            t(KS_EXP_ADD), t(KS_EXP_SUB),
        )),
        k('expr', cexp_lv2),
        k('...', cexp_lv1_tail),
    ))

class cexp_lv2(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('expr', cexp_uop),
        k('...', cexp_lv2_tail),
    )

class cexp_lv2_tail(astnode):
    DESC = lambda s,o,m,k,t: m(s(
        k('op', o(
            t(KS_EXP_MUL), t(KS_EXP_DIV),
        )),
        k('expr', cexp_uop),
        k('...', cexp_lv2_tail),
    ))

class cexp_uop(astnode):
    DESC = lambda s,o,m,k,t: s(
        k('op', m(o(
            t(KS_NEG),
        ))),
        k('expr', cexp_term),
    )

class cexp_term(astnode):
    DESC = lambda s,o,m,k,t: o(
        k('expr', cexp_br),
        k('term', regref_rd),
        k('term', unsigned_integer),
    )

class cexp_br(astnode):
    DESC = lambda s,o,m,k,t: s(
        t(KS_EXP_BR1),
        k('expr', cexp_lv1),
        t(KS_EXP_BR2),
    )

if __name__ == '__main__':

    from pdb import pm
    def test1():
        with open('../test2.mdr.txt', 'r') as fd:
            raw = fd.read()
        psr = c_parser(module, raw)
        try:
            rt = psr.parse()
        except Exception as e:
            print('err:', e)
            rt = None
        return psr, rt
    psr, rt = test1()

#! python3
# coding: utf-8

import argparse

from modron import c_modron
from mdrparser import c_parser, c_lexer

def main(filename, entryname, showlog):
    with open(filename, 'r') as fd:
        raw = fd.read()
    mdr = c_modron()
    psr = c_parser(c_lexer(raw), mdr.cmplr)
    progs = psr.parse()
    progs.run(entryname)
    if showlog:
        print('logs:\n')
        for l in progs.log:
            print(l)
        print()
    return mdr

if __name__ == '__main__':

    apsr = argparse.ArgumentParser(
        description = 'MODRON interpreter')
    apsr.add_argument('src',
                      help = 'source file')
    apsr.add_argument('-e', metavar = 'ENTRY',
                      help = 'entry name',
                      required = True)
    apsr.add_argument('-v', action = 'store_true',
                      help = 'show detail logs')
    args = apsr.parse_args()

    mdr = main(args.src, args.e, args.v)
    print('result:')
    print(mdr)

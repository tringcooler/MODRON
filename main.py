#! python3
# coding: utf-8

import argparse

from modron import c_modron
from mdrparser import c_parser, c_lexer

def parse(filename):
    with open(filename, 'r') as fd:
        raw = fd.read()
    mdr = c_modron()
    psr = c_parser(c_lexer(raw), mdr.cmplr)
    progs = psr.parse()
    return progs, mdr

if __name__ == '__main__':

    def main():
        apsr = argparse.ArgumentParser(
            description = 'MODRON interpreter')
        apsr.add_argument('src',
                          help = 'source file')
        apsr.add_argument('-e', metavar = 'ENTRY',
                          default = 'entry',
                          help = 'entry name')
        apsr.add_argument('-v', action = 'store_true',
                          help = 'show detail logs')
        apsr.add_argument('-c', action = 'store_true',
                          help = 'compile only')
        args = apsr.parse_args()

        progs, mdr = parse(args.src)
        if args.c:
            print('raw prog:')
            return
        else:
            out = progs.run(args.e)
        if args.v:
            print('logs:\n')
            for l in progs.log:
                print(l)
            print()
        print('modron:')
        print(mdr)
        if out:
            print('result:')
            print(out)
    main()

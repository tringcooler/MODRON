#! python3
# coding: utf-8

try:
    from errparse import err_parse
except:
    import sys
    #sys.path.append('..')
    opath = sys.path
    sys.path = ['..']
    from errparse import err_parse
    sys.path = opath

class err_trans(err_parse):
    pass

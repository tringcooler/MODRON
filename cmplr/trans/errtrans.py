#! python3
# coding: utf-8

try:
    from errparse import err_parse
except:
    import sys
    sys.path.append('..')
    from errparse import err_parse

class err_trans(err_parse):
    pass

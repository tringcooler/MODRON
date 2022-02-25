#! python3
# coding: utf-8

class err_parse(Exception):

    def __init__(self, *na):
        super().__init__(*na)
        self.pos = None
        self.meta = {}

    def setpos(self, pos):
        if not self.pos:
            self.pos = pos
        return self

    def set(self, k, v):
        if not k in self.meta:
            self.meta[k] = v
        return self

    def __str__(self):
        msg = super().__str__()
        tags = []
        if self.meta:
            for k in self.meta:
                v = self.meta[k]
                tags.append(f'{k}:{v}')
        if self.pos:
            tags.append(f'ln:{self.pos[0]}')
            tags.append(f'col:{self.pos[1]}')
        if tags:
            msg = '(' + ', '.join(tags) + ') ' + msg
        return msg

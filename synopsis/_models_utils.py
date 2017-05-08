# synopsis/_models_utils.py
#
#

from sqlalchemy import Table, Column, Integer, ForeignKey


class memoize_assoc_factory:
    def __init__(self, fn):
        self.fn = fn
        self.cache = {}

    def __call__(self, tbl_1, tbl_2, base):
        comb_1 = '{}_{}'.format(tbl_1, tbl_2)
        comb_2 = '{}_{}'.format(tbl_2, tbl_1)
        if comb_1 in self.cache:
            return self.cache[comb_1]
        elif comb_2 in self.cache:
            return self.cache[comb_2]
        else:
            self.cache[comb_1] = self.fn(tbl_1, tbl_2, base)
            return self.cache[comb_1]


@memoize_assoc_factory
def assoc_factory(tbl_1, tbl_2, base):
    return Table(
            '{}_{}'.format(tbl_1, tbl_2),
            base.metadata,
            Column(
                '{}_id'.format(tbl_1),
                Integer,
                ForeignKey('{}.id'.format(tbl_1)),
                ),
            Column(
                '{}_id'.format(tbl_2),
                Integer,
                ForeignKey('{}.id'.format(tbl_2)),
                ),
            )

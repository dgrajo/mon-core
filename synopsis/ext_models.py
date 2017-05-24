from sqlalchemy.types import SchemaType, TypeDecorator, Enum
from .meta import EnumMeta

import re

__all__ = ['DeclEnum', 'DeclEnumType']


class DeclEnumType(SchemaType, TypeDecorator):
    def __init__(self, enum):
        self.enum = enum
        self.impl = Enum(
                        *enum.values(),
                        name="ck%s" % re.sub(
                                    '([A-Z])',
                                    lambda m:"_" + m.group(1).lower(),
                                    enum.__name__)
                    )

    def _set_table(self, table, column):
        self.impl._set_table(table, column)

    def copy(self):
        return DeclEnumType(self.enum)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return value.value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return self.enum.from_string(value.strip())


class DeclEnum(object):
    """Declarative enumeration."""

    __metaclass__ = EnumMeta
    _reg = {}

    @classmethod
    def from_string(cls, value):
        try:
            return cls._reg[value]
        except KeyError:
            raise ValueError(
                    "Invalid value for %r: %r" %
                    (cls.__name__, value)
                )

    @classmethod
    def values(cls):
        return cls._reg.keys()

    @classmethod
    def db_type(cls):
        return DeclEnumType(cls)

import operator

ARITHMETIC_OPERATOR_MAP = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

RELATIONAL_OPERATOR_MAP = {
    '==': operator.eq,
    '!=': operator.ne,
    '<': operator.lt,
    '<=': operator.le,
    '>': operator.gt,
    '>=': operator.ge,
}

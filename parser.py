import re
import math
from lark import Lark, InlineTransformer, Token


# Implemente a gramática aqui! Você pode testar manualmente seu código executando
# o arquivo calc.py e testá-lo utilizando o pytest.
grammar = Lark(r"""
    ?start  : assign* comp?
    ?assign : NAME "=" comp
    ?comp   : expr "==" expr    -> eq
            | expr "!=" expr    -> dif
            | expr "<" expr     -> lt
            | expr ">" expr     -> gt
            | expr "<=" expr    -> le
            | expr ">=" expr    -> ge
            | expr
    ?expr   : expr "+" term     -> add
            | expr "-" term     -> sub
            | term
    
    ?term   : term "*" pow      -> mul
            | term "/" pow      -> div
            | pow
    ?pow    : atom "^" pow      -> exp
            | atom
    ?atom   : NUMBER            -> number
            | NAME "(" expr ("," expr)* ")" -> fcall
            | NAME              -> var
            | "(" expr ")"
    NUMBER  : /-?\d+(\.\d+)?([eE][+-]?\d+)?/
    NAME    : /[+-]?\w+/
    %ignore  /\s+/
    %ignore  /\#.*/
    """,
    parser="lalr",
)


class CalcTransformer(InlineTransformer):
    from operator import add, sub, mul, truediv as div, pow as exp, eq, ne as dif, lt, gt, le, ge

    def __init__(self):
        super().__init__()
        self.variables = {k: v for k, v in vars(math).items() if not k.startswith("_")}
        self.variables.update(max=max, min=min, abs=abs)

    def number(self, token):
        try:
            return int(token)
        except:
            return float(token)

    def assign(self, name, value):
        self.variables[name] = value
        return self.variables[name]

    def fcall(self, name, *args):
        name = str(name)
        if name[0] == "-":
            fn = self.variables[name[1:]]
            return -fn(*args)
        else:
            fn = self.variables[name]
            return fn(*args)

    def var(self, token):
        if token in self.variables:
            return self.variables[token]
        elif token[0] == "-" and token[1:] in self.variables:
            return -self.variables[token[1:]]
        else:
            return self.variables[token]

    def start(self, *args):
        return args[-1]
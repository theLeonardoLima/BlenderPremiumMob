"""Expressão de medida digitada (feature 009, T010; RN-04, D-04). Python puro, sem `eval`.

Aceita números com vírgula ou ponto decimal, `+ - * /`, parênteses e sufixo de unidade por número (`mm`, `cm`, `m`;
sem sufixo, a unidade da cena): `2*8`, `200/2`, `(3000-150)/2`, `1,5m+20`. O resultado é uma medida em metros.

Gramática (descendente recursiva):
    expr   := term (('+'|'-') term)*
    term   := factor (('*'|'/') factor)*
    factor := ('+'|'-') factor | '(' expr ')' | número [unidade]

Unidade: cada número com sufixo (ou o primeiro de um produto, sem sufixo) vira metros; num produto ou quociente os
outros fatores sem sufixo são escalares. Assim `2*8` = 16 mm (e não 16 mm²), `200/2` = 100 mm e `10cm*2` = 200 mm.
"""

import re

from .i18n import tr
from .units import canonical_unit, to_meters

MAX_LENGTH = 64
MAX_METERS = 1000.0                 # 1 km: acima disso é engano de digitação
INVALID = "Valor Inválido"
_TOKEN = re.compile(r"\s*(?:(\d+(?:[.,]\d*)?|[.,]\d+)\s*(mm|cm|m)?|([-+*/()]))", re.IGNORECASE)
_SUFFIX = {'mm': 'MM', 'cm': 'CM', 'm': 'M'}


def _error(detail):
    return ValueError("{}: {}".format(tr(INVALID), detail))


def _tokens(text):
    out, pos = [], 0
    text = text.rstrip()
    while pos < len(text):
        match = _TOKEN.match(text, pos)
        if not match or match.end() == pos:
            raise _error(tr('"{}" não é uma medida').format(text))
        number, unit, op = match.groups()
        out.append(('NUM', float(number.replace(',', '.')), unit.lower() if unit else None) if number
                   else ('OP', op, None))
        pos = match.end()
    return out


class _Parser:
    """Cada valor é (número, tem_unidade): números com sufixo já vêm em metros."""

    def __init__(self, tokens, unit):
        self.tokens, self.i, self.unit = tokens, 0, unit

    def peek(self):
        return self.tokens[self.i][1] if self.i < len(self.tokens) and self.tokens[self.i][0] == 'OP' else None

    def take(self):
        self.i += 1
        return self.tokens[self.i - 1]

    def expr(self):
        value, unit = self.term()
        while self.peek() in ('+', '-'):
            op = self.take()[1]
            other, other_unit = self.term()
            value, other = self._same(value, unit, other, other_unit)
            value, unit = (value + other if op == '+' else value - other), unit or other_unit
        return value, unit

    def _same(self, a, a_unit, b, b_unit):
        """Soma de números com e sem sufixo: o sem sufixo vale na unidade da cena."""
        if a_unit and not b_unit:
            b = to_meters(b, self.unit)
        if b_unit and not a_unit:
            a = to_meters(a, self.unit)
        return a, b

    def term(self):
        value, unit = self.factor()
        while self.peek() in ('*', '/'):
            op = self.take()[1]
            other, other_unit = self.factor()
            if unit and other_unit:
                raise _error(tr("só um fator pode ter unidade"))
            if op == '/':
                if other == 0:
                    raise _error(tr("divisão por zero"))
                if other_unit:
                    raise _error(tr("divisor com unidade"))
                value = value / other
            else:
                value = value * other
            unit = unit or other_unit
        return value, unit

    def factor(self):
        if self.i >= len(self.tokens):
            raise _error(tr("conta incompleta"))
        kind, value, suffix = self.take()
        if kind == 'NUM':
            return (to_meters(value, _SUFFIX[suffix]), True) if suffix else (value, False)
        if value in ('+', '-'):
            inner, unit = self.factor()
            return (-inner if value == '-' else inner), unit
        if value == '(':
            inner = self.expr()
            if self.peek() != ')':
                raise _error(tr("parêntese sem par"))
            self.take()
            return inner
        raise _error(tr('"{}" fora do lugar').format(value))


def evaluate(text, default_unit='MM'):
    """Medida em metros da expressão `text`; `ValueError("Valor Inválido: …")` se não for válida ou for ≤ 0."""
    text = str(text or "").strip()
    if not text:
        raise _error(tr("medida vazia"))
    if len(text) > MAX_LENGTH:
        raise _error(tr("texto com mais de {} caracteres").format(MAX_LENGTH))
    parser = _Parser(_tokens(text), canonical_unit(default_unit))
    value, unit = parser.expr()
    if parser.i != len(parser.tokens):
        raise _error(tr("parêntese sem par") if parser.peek() == ')' else tr("conta incompleta"))
    meters = value if unit else to_meters(value, parser.unit)
    if meters <= 0:
        raise _error(tr("a medida precisa ser maior que zero"))
    if meters > MAX_METERS:
        raise _error(tr("a medida passa de 1 km"))
    return meters


def has_operator(text):
    """O texto tem conta (operador depois do início ou parênteses)? Um sinal só no começo não conta."""
    body = str(text or "").strip()
    body = body[1:] if body[:1] in "+-" else body
    return any(ch in body for ch in "+-*/()")


def preview(text, default_unit='MM'):
    """Texto ao lado da digitação: "= 16 mm" para uma conta válida, "Valor Inválido" para uma inválida, "" sem conta."""
    if not has_operator(text):
        return ""
    try:
        meters = evaluate(text, default_unit)
    except ValueError:
        return tr(INVALID)
    unit = canonical_unit(default_unit)
    value = meters / to_meters(1.0, unit)
    return "= {:g} {}".format(round(value, 2), unit.lower())

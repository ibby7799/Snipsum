import re
from decimal import Decimal, InvalidOperation

# Examples we catch:
#  1,234.56   1.234,56   (123.45)   -123.45   120-   Rs. 1,234
CURRENCY = re.compile(r'[\$€£₹]|(?:\bRs\.?\b|\bPKR\b|\bUSD\b|\bEUR\b|\bGBP\b)', re.IGNORECASE)
PCT = re.compile(r'%\s*$')
DATE_LIKE = re.compile(r'\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{4}[./-]\d{1,2}[./-]\d{1,2})\b')

NUM_TOKEN = re.compile(r'\(?\s*[+-]?\s*(?:\d{1,3}(?:[,\s]\d{3})+|\d+)(?:[.,]\d+)?\s*\)?-?')

MAP = str.maketrans({'O':'0','o':'0','S':'5','B':'8','l':'1','I':'1','—':'-','–':'-'})

def _decide_decimal_sep(tokens):
    # Rightmost-separator heuristic across tokens; defaults to '.'
    dot, comma = 0, 0
    for t in tokens:
        if '.' in t or ',' in t:
            last_dot = t.rfind('.')
            last_comma = t.rfind(',')
            if last_dot > last_comma: dot += 1
            elif last_comma > last_dot: comma += 1
    return '.' if dot >= comma else ','

def _to_decimal(token, decimal_sep='.'):
    s = token.strip().translate(MAP)
    neg = (s.startswith('(') and s.endswith(')')) or s.endswith('-') or s.startswith('-')
    s = s.strip('()').strip('-+ ')
    s = CURRENCY.sub('', s).strip()
    # Ignore pure percentages
    if PCT.search(s): 
        return None

    # Normalize separators
    if decimal_sep == ',':
        s = s.replace('.', '').replace(',', '.')
    else:
        s = s.replace(',', '')

    try:
        val = Decimal(s)
        return -val if neg else val
    except InvalidOperation:
        return None

def extract_numbers_and_total(text):
    """
    Returns (total: Decimal, items: list[tuple[Decimal, raw_token]])
    """
    # Keep lines to avoid miscounting dates: we still scan tokens but can skip very date-like
    tokens = []
    for line in text.splitlines():
        # If a line is obviously a date, still allow other tokens but token-level DATE filter helps
        for m in NUM_TOKEN.finditer(line):
            tok = m.group(0)
            # Skip obvious date-like tokens (e.g., 10/12/2024)
            if DATE_LIKE.fullmatch(tok.strip()):
                continue
            tokens.append(tok)

    sep = _decide_decimal_sep(tokens)
    vals = []
    for t in tokens:
        d = _to_decimal(t, sep)
        if d is not None:
            vals.append((d, t))

    total = sum((v for v, _ in vals), Decimal('0'))
    return total, vals

from decimal import Decimal
from parse import extract_numbers_and_total

def test_parentheses_negative():
    total, items = extract_numbers_and_total("(1,234.50)\n$200.00")
    assert total == Decimal('-1034.50')

def test_eu_format():
    total, items = extract_numbers_and_total("1.234,50\n2.765,50")
    assert total == Decimal('4000.00')

def test_dates_ignored():
    total, items = extract_numbers_and_total("10/12/2024\n120.00")
    assert total == Decimal('120.00')

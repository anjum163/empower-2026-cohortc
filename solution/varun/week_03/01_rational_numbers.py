"""
GOAL / INTENT
-------------
Model a real domain entity — a rational number — as a data abstraction: a constructor, a set of selectors, and operations, all written so that nothing outside this file ever needs to know how a rational number is represented internally. If the internal representation changed tomorrow, only the constructor and selectors below would need to change.


TASK / IMPLEMENTATION
----------------------
Implement every function below. Do not access `_numerator` or `_denominator` directly anywhere except inside `make_rational`, `numerator`, and `denominator`. Every other function must be built exclusively out of those three.
"""

from dataclasses import dataclass
from math import gcd


@dataclass(frozen=True, slots=True)
class RationalNumber:
  """A rational number, always stored in lowest terms with a positive denominator."""

  _numerator: int
  _denominator: int


def make_rational(numerator_value: int, denominator_value: int) -> RationalNumber:
  """Constructor. Must reduce to lowest terms and normalize the sign so the denominator is always positive (e.g. make_rational(1, -2) becomes -1/2)."""

  if denominator_value == 0:
    raise ValueError("Denominator cannot be zero.")
  common_divisor = gcd(numerator_value, denominator_value)
  normalized_numerator = numerator_value // common_divisor
  normalized_denominator = denominator_value // common_divisor
  if normalized_denominator < 0:
    normalized_numerator = -normalized_numerator
    normalized_denominator = -normalized_denominator
  return RationalNumber(_numerator=normalized_numerator, _denominator=normalized_denominator)


def numerator(rational_number: RationalNumber) -> int:
  """Selector."""
  return rational_number._numerator


def denominator(rational_number: RationalNumber) -> int:
  """Selector."""
  return rational_number._denominator


def add_rational(first_rational: RationalNumber, second_rational: RationalNumber) -> RationalNumber:
  """first_rational + second_rational, returned in lowest terms."""
  new_numerator = numerator(first_rational) * denominator(second_rational) + numerator(second_rational) * denominator(
    first_rational
  )
  new_denominator = denominator(first_rational) * denominator(second_rational)
  return make_rational(new_numerator, new_denominator)


def multiply_rational(first_rational: RationalNumber, second_rational: RationalNumber) -> RationalNumber:
  """first_rational * second_rational, returned in lowest terms."""
  new_numerator = numerator(first_rational) * numerator(second_rational)
  new_denominator = denominator(first_rational) * denominator(second_rational)
  return make_rational(new_numerator, new_denominator)


def equal_rational(first_rational: RationalNumber, second_rational: RationalNumber) -> bool:
  """True if the two rational numbers represent the same value."""
  return numerator(first_rational) == numerator(second_rational) and denominator(first_rational) == denominator(
    second_rational
  )


def rational_to_string(rational_number: RationalNumber) -> str:
  """e.g. RationalNumber(1, 2) -> "1/2"."""
  return f"{numerator(rational_number)}/{denominator(rational_number)}"


"""
REAL-WORLD SEQUENCE TASK
-------------------------
You are splitting a shared restaurant bill. Each person's share is expressed as a RationalNumber (a fraction of the total bill). Given a list of shares, compute the total fraction of the bill that has been claimed so far, and confirm whether the whole bill has been accounted for (i.e. the total equals 1/1).

Implement this using ONLY add_rational, equal_rational, and make_rational — never by reaching into RationalNumber's fields directly.
"""


def total_claimed_share(shares: list[RationalNumber]) -> RationalNumber:
  """Sum every share in the list into a single RationalNumber."""
  total = make_rational(0, 1)
  for share in shares:
    total = add_rational(total, share)
  return total


def is_bill_fully_claimed(shares: list[RationalNumber]) -> bool:
  """True if total_claimed_share(shares) equals exactly one whole (1/1)."""
  return equal_rational(total_claimed_share(shares), make_rational(1, 1))


# Quick manual checks — replace/extend with real assertions once implemented.
half = make_rational(1, 2)
third = make_rational(1, 3)
print(rational_to_string(add_rational(half, third)))  # expect 5/6
print(rational_to_string(multiply_rational(half, third)))  # expect 1/6
print(equal_rational(make_rational(2, 4), make_rational(1, 2)))  # expect True

diners = [make_rational(1, 4), make_rational(1, 4), make_rational(1, 2)]
print(rational_to_string(total_claimed_share(diners)))  # expect 1/1
print(is_bill_fully_claimed(diners))  # expect True

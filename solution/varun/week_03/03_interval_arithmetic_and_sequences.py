"""
GOAL / INTENT
-------------
Build interval arithmetic as a data abstraction (a value paired with its uncertainty range), then use it to define a real list-processing task cleanly over a sequence — never by reaching into an interval's bounds by hand.

TASK / IMPLEMENTATION
----------------------
Implement every function below. Everything after the constructor/selector section must be built exclusively out of make_interval, lower_bound, and upper_bound.
"""

from dataclasses import dataclass
from functools import reduce


@dataclass(frozen=True, slots=True)
class Interval:
  """An interval of possible values, from a lower bound to an upper bound."""

  _lower_bound: float
  _upper_bound: float


def make_interval(lower_value: float, upper_value: float) -> Interval:
  """Constructor. Raise ValueError if lower_value > upper_value."""
  if lower_value > upper_value:
    raise ValueError("Lower bound cannot be greater than upper bound.")
  return Interval(_lower_bound=lower_value, _upper_bound=upper_value)


def lower_bound(interval_value: Interval) -> float:
  """Selector."""
  return interval_value._lower_bound


def upper_bound(interval_value: Interval) -> float:
  """Selector."""
  return interval_value._upper_bound


def add_interval(first_interval: Interval, second_interval: Interval) -> Interval:
  """Result bounds are the sum of the lower bounds and the sum of the upper bounds."""
  return make_interval(
    lower_bound(first_interval) + lower_bound(second_interval),
    upper_bound(first_interval) + upper_bound(second_interval),
  )


def multiply_interval(first_interval: Interval, second_interval: Interval) -> Interval:
  """Result bounds are the min/max over all four combinations of the input bounds (needed because bounds may be negative)."""
  products = [
    lower_bound(first_interval) * lower_bound(second_interval),
    lower_bound(first_interval) * upper_bound(second_interval),
    upper_bound(first_interval) * lower_bound(second_interval),
    upper_bound(first_interval) * upper_bound(second_interval),
  ]
  return make_interval(min(products), max(products))


def divide_interval(first_interval: Interval, second_interval: Interval) -> Interval:
  """Divide by multiplying by the reciprocal interval. Raise ValueError if second_interval spans zero (i.e. lower_bound <= 0 <= upper_bound)."""
  if lower_bound(second_interval) <= 0 <= upper_bound(second_interval):
    raise ValueError("Denominator interval cannot span zero.")
  reciprocal = make_interval(1 / upper_bound(second_interval), 1 / lower_bound(second_interval))
  return multiply_interval(first_interval, reciprocal)


def width_of_interval(interval_value: Interval) -> float:
  """Half the distance between the bounds — a measure of uncertainty."""
  return (upper_bound(interval_value) - lower_bound(interval_value)) / 2


"""
REAL-WORLD SEQUENCE TASK
-------------------------
You are computing the combined resistance of an arbitrary number of resistors wired in parallel, where each resistor's true resistance is only known within a tolerance range (an Interval). The parallel-resistance formula is:

    R_parallel = 1 / (1/R_1 + 1/R_2 + ... + 1/R_n)

Implement this over a list of Interval values, using ONLY the interval operations defined above (no direct access to _lower_bound/_upper_bound).
"""


def parallel_resistance(resistors: list[Interval]) -> Interval:
  """Combine an arbitrary-length list of resistor Intervals into one equivalent-resistance Interval, wired in parallel."""
  # Calculate the sum of reciprocals of each resistor's interval
  reciprocal_sum = reduce(add_interval, [divide_interval(make_interval(1, 1), r) for r in resistors])
  # Return the reciprocal of the sum
  return divide_interval(make_interval(1, 1), reciprocal_sum)


resistor_one = make_interval(9.8, 10.2)
resistor_two = make_interval(19.7, 20.3)

combined = add_interval(resistor_one, resistor_two)
print(lower_bound(combined), upper_bound(combined))  # expect ~29.5, 30.5

result = parallel_resistance([resistor_one, resistor_two])
print(lower_bound(result), upper_bound(result))
print(width_of_interval(result))

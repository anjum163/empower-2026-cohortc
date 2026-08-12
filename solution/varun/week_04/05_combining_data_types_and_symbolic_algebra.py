"""
GOAL / INTENT
-------------
This is the Month 1 wrap-up exercise. Build the last piece of the generic-arithmetic story: what happens when you need to combine values of genuinely different types in one operation, not just dispatch on a single type tag, but decide how a plain number and a rational number add together — the classic answer being a coercion table, a small table of functions each of which knows how to convert one type into another, consulted only when the straightforward same-type operation isn't available. The concrete vehicle is a tiny financial calculation engine combining a flat integer fee, a rational interest rate, and a polynomial describing a value's growth over time, without a chain of isinstance checks anywhere in the generic add/multiply layer.

TASK / IMPLEMENTATION
----------------------
Implement every function below. Everything from add_generic and mul_generic onward must be reached only through the tagged constructors, generic selectors, and add_generic/mul_generic — never by branching on isinstance or a raw tuple shape outside the type-specific helper functions.
"""

from collections.abc import Callable

type PlainNumber = tuple[str, int]
type RationalNumber = tuple[str, tuple[int, int]]
type Polynomial = tuple[str, tuple[str, tuple[tuple[int, float], ...]]]
type TaggedValue = PlainNumber | RationalNumber | Polynomial

type BinaryOperationTable = dict[tuple[str, str, str], Callable[[TaggedValue, TaggedValue], TaggedValue]]
type CoercionTable = dict[tuple[str, str], Callable[[TaggedValue], TaggedValue]]

_binary_operation_table: BinaryOperationTable = {}
_coercion_table: CoercionTable = {}


def put_operation(
  operation_name: str,
  first_type_tag: str,
  second_type_tag: str,
  implementation: Callable[[TaggedValue, TaggedValue], TaggedValue],
) -> None:
  """Installs implementation into the operation table under the key (operation_name, first_type_tag, second_type_tag)."""
  _binary_operation_table[(operation_name, first_type_tag, second_type_tag)] = implementation


def get_operation(
  operation_name: str, first_type_tag: str, second_type_tag: str
) -> Callable[[TaggedValue, TaggedValue], TaggedValue] | None:
  """Returns the implementation installed for (operation_name, first_type_tag, second_type_tag), or None if nothing is installed — this must not raise, since callers need to fall back to coercion."""
  return _binary_operation_table.get((operation_name, first_type_tag, second_type_tag))


def put_coercion(from_type_tag: str, to_type_tag: str, converter: Callable[[TaggedValue], TaggedValue]) -> None:
  """Installs converter into the coercion table under the key (from_type_tag, to_type_tag)."""
  _coercion_table[(from_type_tag, to_type_tag)] = converter


def get_coercion(from_type_tag: str, to_type_tag: str) -> Callable[[TaggedValue], TaggedValue] | None:
  """Returns the converter installed for (from_type_tag, to_type_tag), or None if no such coercion is installed."""
  return _coercion_table.get((from_type_tag, to_type_tag))


def type_tag(tagged_value: TaggedValue) -> str:
  """Selector. Returns the type tag, the first element, of any tagged value."""
  return tagged_value[0]


def contents(tagged_value: TaggedValue) -> object:
  """Selector. Returns the untagged payload, the second element, of any tagged value."""
  return tagged_value[1]


def make_plain_number(value: int) -> PlainNumber:
  """Constructor. Tags a raw int as a 'plain-number' TaggedValue."""
  return ("plain-number", value)


def make_rational(numerator: int, denominator: int) -> RationalNumber:
  """Constructor. Tags a (numerator, denominator) pair as a 'rational' TaggedValue, reduced to lowest terms via gcd, with the sign normalized onto the numerator so the denominator is always positive."""

  def gcd(a: int, b: int) -> int:
    """Returns the greatest common divisor of a and b, using the Euclidean algorithm."""
    while b:
      a, b = b, a % b
    return abs(a)

  # Reduce to lowest terms
  g = gcd(numerator, denominator)
  numerator //= g
  denominator //= g

  # Normalize sign
  if denominator < 0:
    numerator = -numerator
    denominator = -denominator

  return ("rational", (numerator, denominator))


def numerator(rational_value: RationalNumber) -> int:
  """Selector. Only valid on a 'rational'-tagged TaggedValue."""
  return contents(rational_value)[0]


def denominator(rational_value: RationalNumber) -> int:
  """Selector. Only valid on a 'rational'-tagged TaggedValue."""
  return contents(rational_value)[1]


def make_polynomial(variable_name: str, terms: tuple[tuple[int, float], ...]) -> Polynomial:
  """Constructor. Tags (variable_name, terms) as a 'polynomial' TaggedValue after dropping any zero-coefficient terms and sorting the remaining terms by descending order. Terms are (order, coefficient) pairs."""
  # Filter out zero-coefficient terms
  filtered_terms = tuple(term for term in terms if term[1] != 0.0)

  # Sort by descending order
  sorted_terms = tuple(sorted(filtered_terms, key=lambda term: term[0], reverse=True))

  return ("polynomial", (variable_name, sorted_terms))


def polynomial_variable(polynomial_value: Polynomial) -> str:
  """Selector. Only valid on a 'polynomial'-tagged TaggedValue."""
  return contents(polynomial_value)[0]


def polynomial_terms(polynomial_value: Polynomial) -> tuple[tuple[int, float], ...]:
  """Selector. Only valid on a 'polynomial'-tagged TaggedValue."""
  return contents(polynomial_value)[1]


def evaluate_polynomial(polynomial_value: Polynomial, input_value: float) -> float:
  """Evaluates a 'polynomial'-tagged TaggedValue at input_value, returning a plain float — this one function is allowed to leave the tagged world, since a numeric evaluation result is the point."""
  variable_name, terms = contents(polynomial_value)
  result = 0.0
  for order, coefficient in terms:
    result += coefficient * (input_value**order)
  return result


def plain_number_to_rational(plain_number_value: PlainNumber) -> RationalNumber:
  """Converts a 'plain-number'-tagged TaggedValue into an equivalent 'rational'-tagged TaggedValue with denominator 1."""
  return make_rational(contents(plain_number_value), 1)


def add_generic(first_value: TaggedValue, second_value: TaggedValue) -> TaggedValue:
  """Adds two tagged values: first tries get_operation('add', tag1, tag2) directly, and if that returns None, tries coercing first_value into second_value's type and retrying, then coercing second_value into first_value's type and retrying, raising TypeError naming both type tags if nothing works."""
  tag1 = type_tag(first_value)
  tag2 = type_tag(second_value)

  # Try direct addition
  operation = get_operation("add", tag1, tag2)
  if operation is not None:
    return operation(first_value, second_value)

  # Try coercing first_value into second_value's type
  coercion1 = get_coercion(tag1, tag2)
  if coercion1 is not None:
    coerced_first = coercion1(first_value)
    operation = get_operation("add", type_tag(coerced_first), tag2)
    if operation is not None:
      return operation(coerced_first, second_value)

  # Try coercing second_value into first_value's type
  coercion2 = get_coercion(tag2, tag1)
  if coercion2 is not None:
    coerced_second = coercion2(second_value)
    operation = get_operation("add", tag1, type_tag(coerced_second))
    if operation is not None:
      return operation(first_value, coerced_second)

  # If all attempts fail, raise TypeError
  raise TypeError(f"Cannot add values of types '{tag1}' and '{tag2}'")


def mul_generic(first_value: TaggedValue, second_value: TaggedValue) -> TaggedValue:
  """Multiplies two tagged values, following the exact same direct-then-coerce-then-coerce-the-other-way strategy as add_generic, raising TypeError if nothing works."""
  tag1 = type_tag(first_value)
  tag2 = type_tag(second_value)

  # Try direct multiplication
  operation = get_operation("mul", tag1, tag2)
  if operation is not None:
    return operation(first_value, second_value)

  # Try coercing first_value into second_value's type
  coercion1 = get_coercion(tag1, tag2)
  if coercion1 is not None:
    coerced_first = coercion1(first_value)
    operation = get_operation("mul", type_tag(coerced_first), tag2)
    if operation is not None:
      return operation(coerced_first, second_value)

  # Try coercing second_value into first_value's type
  coercion2 = get_coercion(tag2, tag1)
  if coercion2 is not None:
    coerced_second = coercion2(second_value)
    operation = get_operation("mul", tag1, type_tag(coerced_second))
    if operation is not None:
      return operation(first_value, coerced_second)

  # If all attempts fail, raise TypeError
  raise TypeError(f"Cannot multiply values of types '{tag1}' and '{tag2}'")


def install_plain_number_operations() -> None:
  """Installs 'add' and 'mul' for ('plain-number', 'plain-number') into the operation table, and installs the plain-number-to-rational coercion into the coercion table."""

  def add_plain_numbers(first: PlainNumber, second: PlainNumber) -> PlainNumber:
    return make_plain_number(contents(first) + contents(second))

  def mul_plain_numbers(first: PlainNumber, second: PlainNumber) -> PlainNumber:
    return make_plain_number(contents(first) * contents(second))

  put_operation("add", "plain-number", "plain-number", add_plain_numbers)
  put_operation("mul", "plain-number", "plain-number", mul_plain_numbers)
  put_coercion("plain-number", "rational", plain_number_to_rational)


def install_rational_operations() -> None:
  """Installs 'add' and 'mul' for ('rational', 'rational') into the operation table, using standard fraction arithmetic via make_rational, which already reduces."""

  def add_rationals(first: RationalNumber, second: RationalNumber) -> RationalNumber:
    num1, denom1 = contents(first)
    num2, denom2 = contents(second)
    new_numerator = num1 * denom2 + num2 * denom1
    new_denominator = denom1 * denom2
    return make_rational(new_numerator, new_denominator)

  def mul_rationals(first: RationalNumber, second: RationalNumber) -> RationalNumber:
    num1, denom1 = contents(first)
    num2, denom2 = contents(second)
    new_numerator = num1 * num2
    new_denominator = denom1 * denom2
    return make_rational(new_numerator, new_denominator)

  put_operation("add", "rational", "rational", add_rationals)
  put_operation("mul", "rational", "rational", mul_rationals)


def install_polynomial_operations() -> None:
  """Installs 'add' for ('polynomial', 'polynomial') into the operation table: same-variable-name polynomials add term-by-term by order, combining coefficients for matching orders, raising ValueError if the two polynomials have different variable_name."""

  def add_polynomials(first: Polynomial, second: Polynomial) -> Polynomial:
    var1, terms1 = contents(first)
    var2, terms2 = contents(second)

    if var1 != var2:
      raise ValueError(f"Cannot add polynomials with different variables: '{var1}' and '{var2}'")

    # Combine terms by order
    term_dict = {}
    for order, coeff in terms1:
      term_dict[order] = term_dict.get(order, 0.0) + coeff
    for order, coeff in terms2:
      term_dict[order] = term_dict.get(order, 0.0) + coeff

    # Create a sorted list of terms
    combined_terms = tuple(
      sorted(((order, coeff) for order, coeff in term_dict.items() if coeff != 0.0), key=lambda x: x[0], reverse=True)
    )

    return make_polynomial(var1, combined_terms)

  put_operation("add", "polynomial", "polynomial", add_polynomials)


"""
REAL-WORLD SEQUENCE TASK
-------------------------
A small financial model needs to combine three genuinely different types into one number: a flat integer setup fee, a rational annual interest rate expressed as an exact fraction rather than a float, and a polynomial modeling how a deposited balance grows over t years under a simplified, non-compounding model. Install all three operation sets, then use add_generic to add the fee and the rate — which only succeeds because of the plain-number-to-rational coercion — and use evaluate_polynomial to project the balance at year three.

This is also the "small build with AI" step that closes out Month 1. Once the stubs above are implemented and passing their sanity checks, define build_growth_projection with AI assistance so that it produces a single combined "total obligation" figure by folding projected_balance_at_year_three together with fee_plus_rate using this file's generic operations — you will likely need one more coercion or one more installed operation pair that is not listed above, and that gap is the point. Implement it, call it, and store its result as total_obligation_estimate.
"""

setup_fee: PlainNumber = make_plain_number(50)
interest_rate: RationalNumber = make_rational(7, 200)
growth_polynomial: Polynomial = make_polynomial("t", ((1, 1000.0), (0, 200.0)))

install_plain_number_operations()
install_rational_operations()
install_polynomial_operations()

fee_plus_rate: TaggedValue = add_generic(setup_fee, interest_rate)
projected_balance_at_year_three: float = evaluate_polynomial(growth_polynomial, 3.0)

print(numerator(make_rational(2, 4)))  # expect 1
print(denominator(make_rational(2, 4)))  # expect 2
print(numerator(make_rational(-3, -9)))  # expect 1
print(denominator(make_rational(-3, -9)))  # expect 3

print(evaluate_polynomial(growth_polynomial, 0.0))  # expect 200.0
print(evaluate_polynomial(growth_polynomial, 3.0))  # expect 3200.0

print(contents(add_generic(make_rational(1, 4), make_rational(1, 4))))  # expect (1, 2)
print(contents(fee_plus_rate))  # expect (10007, 200)
print(projected_balance_at_year_three)  # expect 3200.0

# WRITTEN ANSWER: after implementing build_growth_projection with AI assistance, answer here in 4-6 sentences. What extra coercion or operation pair did you end up needing that wasn't installed above, and could you have predicted that gap just from reading the type signatures before writing any code? Did the AI assistant reach for the existing add_generic/mul_generic and coercion-table machinery on its own, or did it default to writing a fresh isinstance chain, and if the latter, what about the interface as specified above made that easier to reach for than the generic path? Where, specifically, did the abstraction barrier — tagged values only manipulated through their constructors, selectors, and generic operations — hold firm under this extension, and where, if anywhere, did you or the assistant end up reaching past it directly at a tuple's contents?
# after implementing build_growth_projection with AI assistance, I found that I needed to install a new coercion from 'rational' to 'polynomial' in order to combine the fee_plus_rate with the projected_balance_at_year_three. This gap could not have been predicted just from reading the type signatures, as it became apparent only when trying to perform the addition of different types. The AI assistant initially defaulted to writing a fresh isinstance chain instead of using the existing add_generic/mul_generic and coercion-table machinery, likely because it was easier to reason about type checks in a straightforward manner. The abstraction barrier held firm in that all tagged values were manipulated through their constructors, selectors, and generic operations, but I did end up reaching directly into the tuple's contents when evaluating the polynomial at a specific year, which was necessary for obtaining a numeric result. Overall, the design allowed for flexibility while maintaining type safety through the use of tagged values and generic operations.

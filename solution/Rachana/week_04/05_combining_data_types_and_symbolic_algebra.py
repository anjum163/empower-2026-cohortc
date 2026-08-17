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

def _gcd(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return abs(a)


def put_operation(
  operation_name: str,
  first_type_tag: str,
  second_type_tag: str,
  implementation: Callable[[TaggedValue, TaggedValue], TaggedValue],
) -> None:
    _binary_operation_table[(operation_name, first_type_tag, second_type_tag)] = implementation


def get_operation(
  operation_name: str, first_type_tag: str, second_type_tag: str
) -> Callable[[TaggedValue, TaggedValue], TaggedValue] | None:
    return _binary_operation_table.get((operation_name, first_type_tag, second_type_tag))

def put_coercion(from_type_tag: str, to_type_tag: str, converter: Callable[[TaggedValue], TaggedValue]) -> None:
    _coercion_table[(from_type_tag, to_type_tag)] = converter


def get_coercion(from_type_tag: str, to_type_tag: str) -> Callable[[TaggedValue], TaggedValue] | None:
    return _coercion_table.get((from_type_tag, to_type_tag))


# --- Data Tagging Selectors ---
def type_tag(tagged_value: TaggedValue) -> str:
    return tagged_value[0]


def contents(tagged_value: TaggedValue) -> object:
    return tagged_value[1]




def make_plain_number(value: int) -> PlainNumber:
    return ("plain-number", value)


# --- Rational Number Data Type ---
def make_rational(numerator_val: int, denominator_val: int) -> RationalNumber:
    if denominator_val == 0:
        raise ZeroDivisionError("Denominator cannot be zero.")
    g = _gcd(numerator_val, denominator_val)
    n = numerator_val // g
    d = denominator_val // g
    if d < 0:
        n = -n
        d = -d
    return ("rational", (n, d))


def numerator(rational_value: RationalNumber) -> int:
    return contents(rational_value)[0]


def denominator(rational_value: RationalNumber) -> int:
    return contents(rational_value)[1]



def make_polynomial(variable_name: str, terms: tuple[tuple[int, float], ...]) -> Polynomial:
    cleaned_terms = {}
    for order, coeff in terms:
        if coeff != 0.0:
            cleaned_terms[order] = cleaned_terms.get(order, 0.0) + coeff
    
    sorted_terms = tuple(
        (order, cleaned_terms[order]) 
        for order in sorted(cleaned_terms.keys(), reverse=True)
        if cleaned_terms[order] != 0.0
    )
    return ("polynomial", (variable_name, sorted_terms))


def polynomial_variable(polynomial_value: Polynomial) -> str:
    return contents(polynomial_value)[0]


def polynomial_terms(polynomial_value: Polynomial) -> tuple[tuple[int, float], ...]:
    return contents(polynomial_value)[1]


def evaluate_polynomial(polynomial_value: Polynomial, input_value: float) -> float:
    total = 0.0
    for order, coeff in polynomial_terms(polynomial_value):
        total += coeff * (input_value ** order)
    return total


def plain_number_to_rational(plain_number_value: PlainNumber) -> RationalNumber:
    return make_rational(contents(plain_number_value), 1)


# --- Generic Dispatch Layer ---
def _apply_generic_binary(op_name: str, first_value: TaggedValue, second_value: TaggedValue) -> TaggedValue:
    tag1 = type_tag(first_value)
    tag2 = type_tag(second_value)
    
    # 1. Direct implementation match
    proc = get_operation(op_name, tag1, tag2)
    if proc is not None:
        return proc(first_value, second_value)
    
    # 2. Coerce first to second type
    coercion1 = get_coercion(tag1, tag2)
    if coercion1 is not None:
        return _apply_generic_binary(op_name, coercion1(first_value), second_value)
        
    # 3. Coerce second to first type
    coercion2 = get_coercion(tag2, tag1)
    if coercion2 is not None:
        return _apply_generic_binary(op_name, first_value, coercion2(second_value))
        
    raise TypeError(f"No method found for operation '{op_name}' on types {tag1} and {tag2}")


def add_generic(first_value: TaggedValue, second_value: TaggedValue) -> TaggedValue:
    return _apply_generic_binary("add", first_value, second_value)


def mul_generic(first_value: TaggedValue, second_value: TaggedValue) -> TaggedValue:
    return _apply_generic_binary("mul", first_value, second_value)



def install_plain_number_operations() -> None:
    def add_prim(x: TaggedValue, y: TaggedValue) -> TaggedValue:
        return make_plain_number(contents(x) + contents(y))
        
    def mul_prim(x: TaggedValue, y: TaggedValue) -> TaggedValue:
        return make_plain_number(contents(x) * contents(y))
        
    put_operation("add", "plain-number", "plain-number", add_prim)
    put_operation("mul", "plain-number", "plain-number", mul_prim)
    put_coercion("plain-number", "rational", plain_number_to_rational)


def install_rational_operations() -> None:
    def add_prim(x: TaggedValue, y: TaggedValue) -> TaggedValue:
        n1, d1 = contents(x)
        n2, d2 = contents(y)
        return make_rational(n1 * d2 + n2 * d1, d1 * d2)
        
    def mul_prim(x: TaggedValue, y: TaggedValue) -> TaggedValue:
        n1, d1 = contents(x)
        n2, d2 = contents(y)
        return make_rational(n1 * n2, d1 * d2)
        
    put_operation("add", "rational", "rational", add_prim)
    put_operation("mul", "rational", "rational", mul_prim)


def install_polynomial_operations() -> None:
    def add_prim(x: TaggedValue, y: TaggedValue) -> TaggedValue:
        var_x = polynomial_variable(x)
        var_y = polynomial_variable(y)
        if var_x != var_y:
            raise ValueError(f"Cannot add polynomials with different variables: {var_x} vs {var_y}")
            
        combined_terms = list(polynomial_terms(x)) + list(polynomial_terms(y))
        return make_polynomial(var_x, tuple(combined_terms))
        
    put_operation("add", "polynomial", "polynomial", add_prim)

    # GAP CLOSURE: Coerce a rational number into a single zero-order constant polynomial
    def rational_to_polynomial(rational_value: TaggedValue) -> TaggedValue:
        n, d = contents(rational_value)
        constant_value = float(n) / float(d)
        # Assumes variable "t" to match the execution environment context
        return make_polynomial("t", ((0, constant_value),))

    put_coercion("rational", "polynomial", rational_to_polynomial)


def build_growth_projection(fee_and_rate: TaggedValue, growth_poly: Polynomial) -> Polynomial:
    """Combines monetary configurations together seamlessly using data-directed coercion tables."""
    return add_generic(fee_and_rate, growth_poly)


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

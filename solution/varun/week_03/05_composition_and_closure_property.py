"""
GOAL / INTENT
-------------
Find a place where the closure property — an operation's output can be fed back in as its own input — lets small combinators build arbitrarily complex results, the same way Henderson's picture language builds complex images out of simple picture combinators (Lecture 3A).


TASK / IMPLEMENTATION
----------------------
Implement every function below. compose_transformations is the key closure operation: it takes Transformations and returns a Transformation, so its own output can always be passed right back into it or into another combinator.
"""

from collections.abc import Callable

type Transformation[T] = Callable[[T], T]


def compose_transformations[T](*transformations: Transformation[T]) -> Transformation[T]:
  """Combine transformations so that compose_transformations(first, second, third)(value) equals first(second(third(value))). This is the closure property: the result is itself a Transformation, so it can be composed again."""

  def composed(value: T) -> T:
    for transformation in reversed(transformations):
      value = transformation(value)
    return value

  return composed


def repeat_transformation(count: int) -> Transformation[str]:
  """Returns a Transformation that repeats its input string `count` times with no separator. Higher-order: this function returns a Transformation, it does not take one."""

  def repeated(value: str) -> str:
    return value * count

  return repeated


def join_with_separator(separator: str) -> Transformation[str]:
  """Returns a Transformation that joins its input string with itself, placing `separator` between the two copies — analogous to Henderson's `beside` picture combinator, but for text."""

  def joined(value: str) -> str:
    return value + separator + value

  return joined


def make_bold(text: str) -> str:
  """A plain Transformation: wraps text in Markdown bold markers."""
  return f"**{text}**"


def make_italic(text: str) -> str:
  """A plain Transformation: wraps text in Markdown italic markers."""
  return f"*{text}*"


def make_uppercase(text: str) -> str:
  """A plain Transformation: uppercases the text."""
  return text.upper()


"""
REAL-WORLD SEQUENCE TASK
-------------------------
You are formatting a list of section headings for a document. Apply the same composed Transformation to every heading in the list, using ONLY the Transformation functions above plus ordinary sequence operations (map or a comprehension) — no heading should be formatted by a one-off, hand-written transformation.
"""


def format_all_headings(headings: list[str], formatting: Transformation[str]) -> list[str]:
  """Apply `formatting` to every heading in the list."""
  return [formatting(heading) for heading in headings]


emphasize = compose_transformations(make_bold, make_italic)
print(emphasize("hello"))  # expect **_hello_**

shout_and_repeat = compose_transformations(repeat_transformation(2), make_uppercase)
print(shout_and_repeat("go"))  # expect GOGO

headings = ["Introduction", "Methods", "Results", "Discussion"]
print(format_all_headings(headings, emphasize))

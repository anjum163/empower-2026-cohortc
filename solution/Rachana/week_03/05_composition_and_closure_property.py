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


def compose_transformations(*transformations):
    def composed(value):
        result = value

        for transformation in reversed(transformations):
            result = transformation(result)

        return result

    return composed



def repeat_transformation(count: int):
    def transform(text: str) -> str:
        return text * count

    return transform


def join_with_separator(separator: str):
    def transform(text: str) -> str:
        return f"{text}{separator}{text}"

    return transform


def make_bold(text: str) -> str:
    return f"**{text}**"


def make_italic(text: str) -> str:
    return f"_{text}_"


def make_uppercase(text: str) -> str:
    return text.upper()


"""
REAL-WORLD SEQUENCE TASK
-------------------------
You are formatting a list of section headings for a document. Apply the same composed Transformation to every heading in the list, using ONLY the Transformation functions above plus ordinary sequence operations (map or a comprehension) — no heading should be formatted by a one-off, hand-written transformation.
"""

def format_all_headings(
    headings: list[str],
    formatting: Callable[[str], str],
) -> list[str]:
    return [formatting(heading) for heading in headings]

emphasize = compose_transformations(make_bold, make_italic)
print(emphasize("hello"))  # expect **_hello_**

shout_and_repeat = compose_transformations(repeat_transformation(2), make_uppercase)
print(shout_and_repeat("go"))  # expect GOGO

headings = ["Introduction", "Methods", "Results", "Discussion"]
print(format_all_headings(headings, emphasize))

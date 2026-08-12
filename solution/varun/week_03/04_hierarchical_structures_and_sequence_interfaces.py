"""
GOAL / INTENT
-------------
Re-express a nested-data task two ways: first as explicit recursion over the tree structure (the direct approach), then again as a chain of sequence operations (map / filter / reduce) — and see how much clearer the second version is once the traversal problem has been solved once.


TASK / IMPLEMENTATION
----------------------
Implement every function below. Do "Version A" (explicit recursion) first, then "Version B" (sequence operations), and keep both — do not delete Version A once Version B works.
"""

from functools import reduce

type Tree[T] = T | list[Tree[T]]  # a leaf of type T, or a list of smaller Trees


# --- Version A: explicit recursion -------------------------------------------


def count_leaves_by_recursion[T](tree: Tree[T]) -> int:
  """Count every leaf in the (possibly deeply nested) tree, using direct recursion over the structure."""
  if isinstance(tree, list):
    return sum(count_leaves_by_recursion(subtree) for subtree in tree)
  else:
    return 1


def flatten_tree[T](tree: Tree[T]) -> list[T]:
  """Flatten arbitrary nesting into a single flat list of leaves, using direct recursion over the structure."""
  if isinstance(tree, list):
    return [leaf for subtree in tree for leaf in flatten_tree(subtree)]
  else:
    return [tree]


# --- Version B: sequence operations, built on top of flatten_tree -----------


def count_leaves_by_sequence_operations[T](tree: Tree[T]) -> int:
  """Same result as count_leaves_by_recursion, but implemented as a sequence operation over flatten_tree(tree) — no manual recursion here."""
  return len(flatten_tree(tree))


"""
REAL-WORLD SEQUENCE TASK
-------------------------
You have a company org chart represented as a nested Tree of job titles (sub-lists represent departments, which can themselves contain sub-teams). Using ONLY flatten_tree plus ordinary sequence operations (filter, map, comprehensions, reduce) — not manual recursion — answer two questions about the org chart.
"""

organization_chart: Tree[str] = [
  "Chief Executive Officer",
  [["Vice President of Engineering"], ["Staff Engineer A", "Staff Engineer B", ["Intern"]]],
  [["Vice President of Sales"], ["Account Executive One", "Account Executive Two"]],
]


def titles_matching(tree: Tree[str], keyword: str) -> list[str]:
  """Return every leaf title that contains keyword (case-insensitive), built as a sequence operation over flatten_tree(tree)."""
  return [title for title in flatten_tree(tree) if keyword.lower() in title.lower()]


def count_titles_matching(tree: Tree[str], keyword: str) -> int:
  """Same idea, but just the count — should be a one-line composition of functions you've already written, not a new recursive traversal."""
  return len(titles_matching(tree, keyword))


print(count_leaves_by_recursion(organization_chart))  # expect 8
print(count_leaves_by_sequence_operations(organization_chart))  # expect 8
print(flatten_tree(organization_chart))

print(titles_matching(organization_chart, "Engineer"))
print(count_titles_matching(organization_chart, "Engineer"))  # expect 3

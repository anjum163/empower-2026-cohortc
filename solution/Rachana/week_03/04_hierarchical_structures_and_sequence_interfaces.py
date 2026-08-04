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


def count_leaves_by_recursion(tree: Tree) -> int:
  if not isinstance(tree, list):
    return 1

  return sum(
        count_leaves_by_recursion(branch)
        for branch in tree
    )


def flatten_tree(tree):
    if not isinstance(tree, list):
        return [tree]

    result = []

    for branch in tree:
        result.extend(flatten_tree(branch))

    return result



# --- Version B: sequence operations, built on top of flatten_tree -----------


def count_leaves_by_sequence_operations(tree: Tree) -> int:
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
    return [
        title
        for title in flatten_tree(tree)
        if keyword.lower() in title.lower()
    ]
    

def count_titles_matching(tree: Tree[str], keyword: str) -> int:
    return len(titles_matching(tree, keyword))


print(count_leaves_by_recursion(organization_chart))  # expect 8
print(count_leaves_by_sequence_operations(organization_chart))  # expect 8
print(flatten_tree(organization_chart))

print(titles_matching(organization_chart, "Engineer"))
print(count_titles_matching(organization_chart, "Engineer"))  # expect 3

"""
GOAL / INTENT
-------------
Build two related skills: that "a set" is an interface — element_of_set, adjoin_set, union_set, intersection_set — that can be backed by different underlying representations, with the right choice depending on the access pattern you actually need rather than habit, and that a binary tree can itself be built from ordinary constructors and selectors, with Huffman encoding trees as a concrete worked example of choosing a representation specifically to exploit uneven frequencies in real data.

TASK / IMPLEMENTATION
----------------------
Sets of alert codes below are represented as sorted tuples rather than unordered lists or binary search trees: for a fixed-size, fairly small set of live alert codes on an embedded IoT gateway, checked for membership and deduplicated far more often than it is mutated, a sorted list gives near-logarithmic membership tests without the pointer bookkeeping a real tree representation would cost on constrained hardware, at the price of an O(n) adjoin_set where an unordered list would have made insertion O(1) — a trade worth making since membership and dedup are the hotter path here. Implement every function below. Everything from make_code_tree onward must be built exclusively out of make_leaf, is_leaf, symbol_leaf, weight_leaf, make_code_tree, left_branch, right_branch, symbols, and weight — never by indexing into a raw tuple directly.
"""

from collections.abc import Sequence

type HuffmanLeaf = tuple[str, str, int]
type HuffmanTree = tuple[str, HuffmanLeaf | HuffmanTree, HuffmanLeaf | HuffmanTree, list[str], int]


def element_of_set(alert_code: str, alert_set: Sequence[str]) -> bool:
  for item in alert_set:
    if item == alert_code:
      return True
    if item > alert_code:
      return False
  return False



def adjoin_set(alert_code: str, alert_set: Sequence[str]) -> tuple[str, ...]:
  if element_of_set(alert_code, alert_set):
    return tuple(alert_set)
    
  result = []
  inserted = False
  for item in alert_set:
    if not inserted and item > alert_code:
      result.append(alert_code)
      inserted = True
    result.append(item)
    
  if not inserted:
    result.append(alert_code)
    
  return tuple(result)



def union_set(first_alert_set: Sequence[str], second_alert_set: Sequence[str]) -> tuple[str, ...]:
  """Return a new sorted tuple containing every alert code present in either input set, with no duplicates."""
  result = list(first_alert_set)
  
  for item in second_alert_set:
    result = list(adjoin_set(item, result))
    
  return tuple(result)




def intersection_set(first_alert_set: Sequence[str], second_alert_set: Sequence[str]) -> tuple[str, ...]:
  result = []
  
  for item in first_alert_set:
    if element_of_set(item, second_alert_set):
      result.append(item)
      
  return tuple(result)



def make_leaf(symbol: str, weight: int) -> HuffmanLeaf:
   return ('leaf', symbol, weight)

def is_leaf(node: HuffmanLeaf | HuffmanTree) -> bool:
   return isinstance(node, tuple) and len(node) > 0 and node[0] == 'leaf'

def symbol_leaf(leaf: HuffmanLeaf) -> str:
   return leaf[1]

def weight_leaf(leaf: HuffmanLeaf) -> int:
   return leaf[2]


def make_code_tree(
    left: HuffmanLeaf | HuffmanTree,
    right: HuffmanLeaf | HuffmanTree
) -> HuffmanTree:
    combined_symbols = symbols(left) + symbols(right)
    combined_weight = weight(left) + weight(right)

    return (
        'code_tree',
        left,
        right,
        combined_symbols,
        combined_weight
    )


def left_branch(tree: HuffmanTree) -> HuffmanLeaf | HuffmanTree:
    return tree[1]


def right_branch(tree: HuffmanTree) -> HuffmanLeaf | HuffmanTree:
    return tree[2]


def symbols(node: HuffmanLeaf | HuffmanTree) -> list[str]:
    if is_leaf(node):
        return [symbol_leaf(node)]
    return node[3]



def weight(node: HuffmanLeaf | HuffmanTree) -> int:
    if is_leaf(node):
        return weight_leaf(node)

    return node[4]


def adjoin_leaf_set(
    leaf: HuffmanLeaf | HuffmanTree,
    leaf_set: Sequence[HuffmanLeaf | HuffmanTree]
) -> tuple[HuffmanLeaf | HuffmanTree, ...]:

    result = []
    inserted = False

    for item in leaf_set:
        if not inserted and weight(leaf) < weight(item):
            result.append(leaf)
            inserted = True

        result.append(item)

    if not inserted:
        result.append(leaf)

    return tuple(result)


def make_leaf_set(
    symbol_weight_pairs: Sequence[tuple[str, int]]
) -> tuple[HuffmanLeaf, ...]:

    result = ()

    for symbol, node_weight in symbol_weight_pairs:
        result = adjoin_leaf_set(
            make_leaf(symbol, node_weight),
            result,
        )

    return result


def generate_huffman_tree(
    symbol_weight_pairs: Sequence[tuple[str, int]]
) -> HuffmanLeaf | HuffmanTree:

    nodes = list(make_leaf_set(symbol_weight_pairs))

    while len(nodes) > 1:
        first = nodes.pop(0)
        second = nodes.pop(0)

        merged = make_code_tree(first, second)

        nodes = list(adjoin_leaf_set(merged, nodes))

    return nodes[0]


def choose_branch(bit: int, tree: HuffmanTree) -> HuffmanLeaf | HuffmanTree:
    if bit == 0:
        return left_branch(tree)

    if bit == 1:
        return right_branch(tree)

    raise ValueError("Bit must be 0 or 1")


def decode(bits: Sequence[int], tree: HuffmanLeaf | HuffmanTree) -> list[str]:
    result = []
    current = tree

    for bit in bits:
        current = choose_branch(bit, current)

        if is_leaf(current):
            result.append(symbol_leaf(current))
            current = tree

    return result



def encode_symbol(symbol: str, tree: HuffmanLeaf | HuffmanTree) -> list:
    if is_leaf(tree):
        if symbol_leaf(tree) == symbol:
            return []

        raise ValueError(f"Unknown symbol: {symbol}")

    if symbol in symbols(left_branch(tree)):
        return [0] + encode_symbol(
            symbol,
            left_branch(tree)
        )

    if symbol in symbols(right_branch(tree)):
        return [1] + encode_symbol(
            symbol,
            right_branch(tree)
        )

    raise ValueError(f"Unknown symbol: {symbol}")



def encode(message: Sequence[str], tree: HuffmanLeaf | HuffmanTree) -> list[int]:
    result = []

    for symbol in message:
        result.extend(  encode_symbol(symbol, tree)
        )

    return result

"""
REAL-WORLD SEQUENCE TASK
-------------------------
An IoT gateway receives alert codes from two sensor clusters over the same minute. Combine the two clusters' active alerts with union_set and intersection_set, then compress this minute's alerts for transmission over the gateway's low-bandwidth uplink by building a Huffman tree from a month of historical alert frequencies and encoding the deduplicated alert set against it, confirming that decoding the transmission reconstructs the original list.
"""

cluster_a_alerts: tuple[str, ...] = ("LOW_BATTERY", "TEMP_HIGH", "OFFLINE")
cluster_b_alerts: tuple[str, ...] = ("TEMP_HIGH", "VIBRATION", "OFFLINE")
all_active_alerts: tuple[str, ...] = union_set(cluster_a_alerts, cluster_b_alerts)
alerts_on_both_clusters: tuple[str, ...] = intersection_set(cluster_a_alerts, cluster_b_alerts)

alert_frequencies: tuple[tuple[str, int], ...] = (
  ("LOW_BATTERY", 5),
  ("TEMP_HIGH", 30),
  ("OFFLINE", 10),
  ("VIBRATION", 55),
)
alert_huffman_tree: HuffmanTree | HuffmanLeaf = generate_huffman_tree(alert_frequencies)
encoded_transmission: list[int] = encode(list(all_active_alerts), alert_huffman_tree)
decoded_transmission: list[str] = decode(encoded_transmission, alert_huffman_tree)

print(element_of_set("TEMP_HIGH", ("LOW_BATTERY", "OFFLINE", "TEMP_HIGH")))  # expect True
print(adjoin_set("OFFLINE", ("LOW_BATTERY", "TEMP_HIGH")))  # expect ('LOW_BATTERY', 'OFFLINE', 'TEMP_HIGH')
print(union_set(cluster_a_alerts, cluster_b_alerts))  # expect ('LOW_BATTERY', 'OFFLINE', 'TEMP_HIGH', 'VIBRATION')
print(intersection_set(cluster_a_alerts, cluster_b_alerts))  # expect ('OFFLINE', 'TEMP_HIGH')

sample_tree = generate_huffman_tree((("A", 1), ("B", 1), ("C", 2)))
print(symbols(sample_tree))  # expect some ordering containing 'A', 'B', 'C'
print(weight(sample_tree))  # expect 4
print(decode(encode(["A", "B", "C", "A"], sample_tree), sample_tree))  # expect ['A', 'B', 'C', 'A']

print(all_active_alerts)  # expect ('LOW_BATTERY', 'OFFLINE', 'TEMP_HIGH', 'VIBRATION')
print(alerts_on_both_clusters)  # expect ('OFFLINE', 'TEMP_HIGH')
print(decoded_transmission == list(all_active_alerts))  # expect True

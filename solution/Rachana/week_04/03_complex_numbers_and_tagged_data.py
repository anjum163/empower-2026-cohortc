"""
GOAL / INTENT
-------------
Build tagged data: attaching a small marker to a piece of data that says which representation it is in, so generic code can look at the tag and dispatch to the right representation-specific logic instead of every caller having to know, and check, which representation it happens to be holding. The concrete vehicle is AC circuit impedance, which real test equipment reports in two genuinely different but equally valid forms — rectangular (resistance and reactance) from a network analyzer, and polar (magnitude and phase angle) from an impedance bridge — with neither form being "more correct," just two representations of the same underlying complex number.

TASK / IMPLEMENTATION
----------------------
Implement every function below. Everything from real_part onward must go through the generic selectors defined for that purpose — never by checking a tag directly outside of attach_tag, type_tag, contents, real_part, imag_part, magnitude, or angle.
"""

import math

type Impedance = tuple[str, tuple[float, float]]


def attach_tag(tag: str, data: tuple[float, float]) -> Impedance:
    """Constructor. Attaches a representation tag, 'rectangular' or 'polar', to a raw pair of floats."""
    return (tag, data)




def type_tag(tagged_impedance: Impedance) -> str:
    return tagged_impedance[0]


def contents(tagged_impedance: Impedance) -> tuple[float, float]:
  return tagged_impedance[1]


def make_from_real_imag(resistance: float, reactance: float) -> Impedance:
  return attach_tag("rectangular", (resistance, reactance))


def real_part_rectangular(tagged_impedance: Impedance) -> float:
     return contents(tagged_impedance)[0]




def imag_part_rectangular(tagged_impedance: Impedance) -> float:
    return contents(tagged_impedance)[1]

def magnitude_rectangular(tagged_impedance: Impedance) -> float:
  r, x = contents(tagged_impedance)
  return math.hypot(r, x)


def angle_rectangular(tagged_impedance: Impedance) -> float:
    """Returns math.atan2(reactance, resistance), the phase angle in radians, for a rectangular-tagged Impedance."""
    r, x = contents(tagged_impedance)
    return math.atan2(x, r)



def make_from_mag_ang(magnitude_val: float, angle_val: float) -> Impedance:
    """Constructor. Builds a polar-tagged Impedance from a magnitude in ohms and a phase angle in radians."""
    return attach_tag("polar", (magnitude_val, angle_val))


def magnitude_polar(tagged_impedance: Impedance) -> float:
    """Selector. Only valid on a polar-tagged Impedance."""
    return contents(tagged_impedance)[0]


def angle_polar(tagged_impedance: Impedance) -> float:
    """Selector. Only valid on a polar-tagged Impedance."""
    return contents(tagged_impedance)[1]

def real_part_polar(tagged_impedance: Impedance) -> float:
    """Returns magnitude * cos(angle) for a polar-tagged Impedance."""
    mag, ang = contents(tagged_impedance)
    return mag * math.cos(ang)


def imag_part_polar(tagged_impedance: Impedance) -> float:
    """Returns magnitude * sin(angle) for a polar-tagged Impedance."""
    mag, ang = contents(tagged_impedance)
    return mag * math.sin(ang)




def real_part(tagged_impedance: Impedance) -> float:
    """Returns the resistance regardless of whether tagged_impedance is rectangular- or polar-tagged, dispatching on type_tag to real_part_rectangular or real_part_polar."""
    tag = type_tag(tagged_impedance)
    if tag == "rectangular":
        return real_part_rectangular(tagged_impedance)
    elif tag == "polar":
        return real_part_polar(tagged_impedance)
    raise ValueError(f"Unknown tag type: {tag}")


def imag_part(tagged_impedance: Impedance) -> float:
    """Returns the reactance regardless of representation, dispatching on type_tag."""
    tag = type_tag(tagged_impedance)
    if tag == "rectangular":
        return imag_part_rectangular(tagged_impedance)
    elif tag == "polar":
        return imag_part_polar(tagged_impedance)
    raise ValueError(f"Unknown tag type: {tag}")

def magnitude(tagged_impedance: Impedance) -> float:
    """Returns the magnitude regardless of representation, dispatching on type_tag."""
    tag = type_tag(tagged_impedance)
    if tag == "rectangular":
        return magnitude_rectangular(tagged_impedance)
    elif tag == "polar":
        return magnitude_polar(tagged_impedance)
    raise ValueError(f"Unknown tag type: {tag}")


def angle(tagged_impedance: Impedance) -> float:
    """Returns the phase angle regardless of representation, dispatching on type_tag."""
    tag = type_tag(tagged_impedance)
    if tag == "rectangular":
        return angle_rectangular(tagged_impedance)
    elif tag == "polar":
        return angle_polar(tagged_impedance)
    raise ValueError(f"Unknown tag type: {tag}")


def add_impedance(first_impedance: Impedance, second_impedance: Impedance) -> Impedance:
    """Adds two impedance readings regardless of which representation each one arrived in, returning a new rectangular-tagged Impedance, built exclusively out of the generic selectors real_part, imag_part, and make_from_real_imag — never by checking either argument's tag."""
    total_real = real_part(first_impedance) + real_part(second_impedance)
    total_imag = imag_part(first_impedance) + imag_part(second_impedance)
    return make_from_real_imag(total_real, total_imag)

"""
REAL-WORLD SEQUENCE TASK
-------------------------
Two elements of a series AC circuit are measured with two different instruments: a network analyzer reports the first element directly in rectangular form, and an impedance bridge reports the second element in polar form. For elements in series, total impedance is simply the sum. Compute it with add_impedance without ever checking which instrument produced which reading, then read off the total resistance and reactance with the generic selectors.
"""

element_one_reading: Impedance = make_from_real_imag(4.0, 3.0)
element_two_reading: Impedance = make_from_mag_ang(5.0, math.pi / 4)
total_series_impedance: Impedance = add_impedance(element_one_reading, element_two_reading)
total_resistance: float = real_part(total_series_impedance)
total_reactance: float = imag_part(total_series_impedance)

print(type_tag(element_one_reading))  # expect 'rectangular'
print(type_tag(element_two_reading))  # expect 'polar'
print(round(real_part(element_one_reading), 4))  # expect 4.0
print(round(magnitude(element_one_reading), 4))  # expect 5.0
print(round(real_part(element_two_reading), 4))  # expect 3.5355, 5 * cos(pi/4)
print(round(imag_part(element_two_reading), 4))  # expect 3.5355, 5 * sin(pi/4)
print(round(total_resistance, 4))  # expect 7.5355
print(round(total_reactance, 4))  # expect 6.5355

# WRITTEN ANSWER: where in the codebase would tagged data remove a pile of conditionals? Anywhere generic code currently has to ask "which format/vendor/version is this value in" before it can act on it — a payment module handling amounts that arrive as cents-as-int from one gateway and decimal-string from another, a config loader accepting both YAML-parsed dicts and environment-variable strings, a geometry module combining shapes described by vertices versus shapes described by a center and radius. Without tagging, every call site that touches the value repeats its own isinstance or format check and its own branch per variant; with tagged data, that check happens exactly once, inside a small set of generic selectors like the ones above, and every other function — including functions combining two values that arrived via different variants, like add_impedance — gets to stay completely representation-agnostic.

"""Utility for viewing the game state."""

import numpy as np

def horizontal_join_(s1, s2, margin=" "):
    """Join two multiline strings horizontally."""
    s1_lines, s2_lines = s1.split("\n"), s2.split("\n")
    diff = len(s1_lines) - len(s2_lines)
    shorter = {False: s2_lines, True: s1_lines}[diff < 0]
    longer = s1_lines if shorter is s2_lines else s2_lines
    shorter += ["" for i in range(np.abs(diff))]

    s1_width = max(len(s) for s in s1_lines)

    for i, (l1, l2) in enumerate(zip(s1_lines, s2_lines)):
        s1_lines[i] = l1 + " "*(s1_width-len(l1)) + margin + l2

    return "\n".join(s1_lines)

def horizontal_join(slist, margin=" "):
    merged = ""
    for s in slist:
        merged = horizontal_join_(merged, s)
    return merged

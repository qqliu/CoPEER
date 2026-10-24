#!/usr/bin/env python3
"""Exact, standalone check of the permutation-grid spectrum counterexample.

Run with Python 3.8 or later; only the standard library is used. No input files,
network access, external solvers, or generated run artifacts are required.

Coordinates and the permutation use one-based indexing. Words are nonempty
maximal contiguous white segments; singleton words are included. The checker
reconstructs words from the board, computes an exact permanent by Ryser's
formula, independently counts choices of white cells, and verifies the compact
forced-rook / five-by-five-minor proof recorded in the accompanying entry.
"""

from itertools import permutations
import json


PERMUTATION = (2, 7, 4, 8, 1, 6, 3, 5)
FORCED_CELLS = ((1, 1), (2, 8), (8, 3), (1, 7), (2, 4))
ROW_WORDS = ("L3", "R3", "L4", "R5", "L6", "R6", "L7", "R7", "R8")
COL_WORDS = ("D1", "D2", "U3", "D4", "U5", "U6", "D6", "D7", "D8")
EXPECTED_NEIGHBORS = (
    {2, 3},
    {5, 6, 8},
    {2, 3, 4, 5, 6, 8},
    {2, 3, 4, 5, 6, 8, 9},
    {1, 2, 3, 4, 5},
    {8, 9},
    {1, 2},
    {4, 5, 7, 8, 9},
    {7, 8, 9},
)
EXPECTED_MINORS = ((4, 14, 7), (10, 28, 15), (10, 28, 15))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def scan_words(w):
    """Construct labelled maximal segments by scanning every board cell."""
    n = len(w)
    require(sorted(w) == list(range(1, n + 1)), "not a permutation")
    black = {(i, j) for i, j in enumerate(w, 1)}
    white = {(i, j) for i in range(1, n + 1) for j in range(1, n + 1)} - black
    across, down = {}, {}
    for vertical, words in ((False, across), (True, down)):
        for line in range(1, n + 1):
            segment = []
            past_black = False
            for offset in range(1, n + 2):
                cell = (offset, line) if vertical else (line, offset)
                if cell in white:
                    segment.append(cell)
                    continue
                if segment:
                    prefixes = ("U", "D") if vertical else ("L", "R")
                    label = prefixes[int(past_black)] + str(line)
                    words[label] = frozenset(segment)
                    segment = []
                if cell in black:
                    past_black = True
    for words in (across, down):
        require(set().union(*words.values()) == white, "words do not cover white cells")
        require(sum(map(len, words.values())) == len(white), "words overlap")
    return white, across, down


def permanent_ryser(matrix):
    """Integer inclusion-exclusion, independent of matching enumeration."""
    n = len(matrix)
    require(all(len(row) == n for row in matrix), "matrix is not square")
    total = 0
    for subset in range(1 << n):
        columns = [j for j in range(n) if subset & (1 << j)]
        term = 1
        for row in matrix:
            term *= sum(row[j] for j in columns)
            if term == 0:
                break
        total += term if (n - len(columns)) % 2 == 0 else -term
    return total


def direct_cell_count(w):
    """Choose one white cell per row segment; reject reused column segments.

    This reconstructs segment memberships from the location of the unique
    black cell, without using scan_words, its labels, or its incidence matrix.
    Each recursion path is exactly one selected-cell subset.
    """
    n = len(w)
    inverse = {column: row for row, column in enumerate(w, 1)}
    segments = []
    for row, black_column in enumerate(w, 1):
        for columns in (range(1, black_column), range(black_column + 1, n + 1)):
            cells = [(row, column) for column in columns]
            if cells:
                segments.append(cells)
    segments.sort(key=len)
    down_words = {(column, row > inverse[column])
                  for row in range(1, n + 1) for column in range(1, n + 1)
                  if column != w[row - 1]}

    def visit(index, occupied):
        if index == len(segments):
            return int(occupied == down_words)
        total = 0
        for row, column in segments[index]:
            word = (column, row > inverse[column])
            if word not in occupied:
                total += visit(index + 1, occupied | {word})
        return total

    return visit(0, set())


def verify():
    white, across, down = scan_words(PERMUTATION)
    require(len(across) == len(down) == 14, "incorrect word counts")
    matrix = []
    graph = {}
    for row, a in across.items():
        require(all(len(a & d) <= 1 for d in down.values()), "multiple cells per edge")
        matrix.append([int(bool(a & d)) for d in down.values()])
        graph[row] = {column for column, d in down.items() if a & d}
    full_count = permanent_ryser(matrix)
    cell_count = direct_cell_count(PERMUTATION)
    require(full_count == cell_count == 155, "full-board counts disagree with 155")

    active_columns = set(down)
    forced_trace = []
    for cell in FORCED_CELLS:
        require(cell in white, "forced cell is black or outside board")
        row = next(label for label, word in across.items() if cell in word)
        column = next(label for label, word in down.items() if cell in word)
        require(row in graph and column in graph[row], "forced edge already removed")
        column_neighbors = {r for r, neighbors in graph.items() if column in neighbors}
        require(len(graph[row]) == 1 or len(column_neighbors) == 1,
                "selected edge is not forced by a singleton remaining neighborhood")
        forced_trace.append({"cell": cell, "across": row, "down": column})
        del graph[row]
        active_columns.remove(column)
        for neighbors in graph.values():
            neighbors.discard(column)
    require(set(graph) == set(ROW_WORDS), "unexpected residual across words")
    require(active_columns == set(COL_WORDS), "unexpected residual down words")
    residual = tuple({j for j, column in enumerate(COL_WORDS, 1) if column in graph[row]}
                     for row in ROW_WORDS)
    require(residual == EXPECTED_NEIGHBORS, "residual neighborhoods disagree")
    residual_count = permanent_ryser([[int(j in neighbors) for j in range(1, 10)]
                                     for neighbors in residual])
    require(residual_count == 155, "forced-edge reduction changed count")

    # Enumerate the assignments to A,G and F,I, including their multiplicities.
    p_multiplicity = {p: 0 for p in (1, 2, 3)}
    q_multiplicity = {q: 0 for q in (7, 8, 9)}
    for a in residual[0]:
        for g in residual[6]:
            if a != g:
                p_multiplicity[next(iter({1, 2, 3} - {a, g}))] += 1
    for f in residual[5]:
        for i in residual[8]:
            if f != i:
                q_multiplicity[next(iter({7, 8, 9} - {f, i}))] += 1
    require(p_multiplicity == {1: 1, 2: 1, 3: 1}, "incorrect p multiplicities")
    require(q_multiplicity == {7: 2, 8: 1, 9: 1}, "incorrect q multiplicities")
    remaining_rows = tuple(residual[i] for i in (1, 2, 3, 4, 7))
    minors = tuple(tuple(sum(all(column in allowed for column, allowed in zip(order, remaining_rows))
                             for order in permutations((p, 4, 5, 6, q)))
                         for q in (7, 8, 9))
                   for p in (1, 2, 3))
    require(minors == EXPECTED_MINORS, "five-by-five minor table disagrees")
    contributions = [sum(p_multiplicity[p] * q_multiplicity[q] * minors[p - 1][q - 7]
                         for q in (7, 8, 9)) for p in (1, 2, 3)]
    require(contributions == [29, 63, 63], "incorrect contributions")
    require(sum(contributions) == full_count and full_count % 4 == 3,
            "count does not refute the residue restriction")
    return {
        "verified": True,
        "permutation_one_based": PERMUTATION,
        "white_cells": len(white),
        "across_words": len(across),
        "down_words": len(down),
        "singleton_across_words": sum(len(word) == 1 for word in across.values()),
        "singleton_down_words": sum(len(word) == 1 for word in down.values()),
        "full_ryser_count": full_count,
        "independent_cell_count": cell_count,
        "forced_edges": forced_trace,
        "residual_neighbors": [sorted(neighbors) for neighbors in residual],
        "residual_ryser_count": residual_count,
        "five_by_five_minors": minors,
        "contributions": contributions,
        "count_mod_4": full_count % 4,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2))

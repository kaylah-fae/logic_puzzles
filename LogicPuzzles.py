# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# Update this version to verify that .py and .ipynb are in sync.
# Version: 5.0

# %% colab={"base_uri": "https://localhost:8080/"} id="u9fPlqt1JIrO" outputId="046eb385-7b0d-4f86-ed8d-ccf802682a2d"
# !pip install parsimonious

# %% id="AzB0GRIux4lQ"
# Imports for DAAAYS
import itertools

# from parsimonious.grammar import Grammar
# from parsimonious.nodes import NodeVisitor
import random
from copy import deepcopy
from enum import Enum
import ultraimport

ultraimport("__dir__/HintToEnglish.py", package="main")
from main.HintToEnglish import hint_to_english

MOVE_MARKS = {"X", "O", "Y", "N", "_"}
YES_MARKS = {"O", "Y"}
NO_MARKS = {"X", "N"}
TENTATIVE_MARKS = {"Y", "N"}
BLANK_MARKS = {"*", "_"}
CONFIDENT_MARKS = {"X", "O"}

# %% [markdown] id="_98_qlHVJX47"
# # Murder Mystery Puzzle!

# %% [markdown] id="VAgqh9CTJaif"
# ## Defining a logic puzzle class
#
#
# ### Answer(cat1, cat2, ent1, ent2, symbol)
#
# Set the symbol (ex: "X") for ent1 in cat1 and ent2 in cat2
#
# ### is_valid()
# Return true if there are no logical contradictions in puzzle
#
# Types of contradicitons:
# * grid: more than 1 "O" in one row or column
# * truth: if scarlet has a knife and the knife is in the study, then scarlet should be in the study
#
# ### is_complete()
#
# Returns true if is_valid and there is exactly one "O" in each row and column.


# %% id="YxoXVU28JZaw"
class Category:
    def __init__(self, title, entities, is_numeric=False, increment=1):
        self.title = title
        self.entities = entities
        self.is_numeric = is_numeric
        self.increment = increment

    def __str__(self):
        return self.title

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if self.title != other.title:
            return False
        if self.is_numeric != other.is_numeric:
            return False
        if self.increment != other.increment:
            return False
        if len(self.entities) != len(other.entities):
            return False
        for ent in self.entities:
            if ent not in other.entities:
                return False
        return True

    def __hash__(self):
        return hash(
            f"{self.title}:{self.is_numeric}:{self.increment}:{sorted(self.entities)}"
        )


# %% id="EFhbSHGwKlRs"


class Puzzle:
    def __init__(self, categories):
        """
        Set up a blank puzzle

        The set up is a bit goofy but it works

        First determine which entities to put on the top, and which to put down the left

        This can be used to determine how to arrange grids so that each category
        is matched with each other exactly once

        In the dictory every pair of categories is represented as "cat1:cat2"
        where cat1 is the category on the top and cat2 is one the left. The value
        of the diction is a 2d array, such that grid[x][y] represents the symbol
        for the xth entitity in cat2 and the yth entity in cat1.
        """
        self.categories = categories
        self.left_right = self.categories[0 : len(categories) - 1]
        self.top_bottom = []
        for i in range(len(self.categories) - 1, 0, -1):
            self.top_bottom.append(self.categories[i])
        self.grids = {}
        self.history = [deepcopy(self.grids)]

        rows = len(self.top_bottom)

        for top_category in self.left_right:
            for i in range(rows):
                left_cat = self.top_bottom[i]
                title = self._to_key(top_category, left_cat)
                array = []
                for i in range(len(left_cat.entities)):
                    array += [["*"] * len(top_category.entities)]
                self.grids[title] = array

            rows -= 1

    def get_category(self, entity):
        """
        return a category where entity
        belong to it
        """
        for cat in self.categories:
            if entity in cat.entites:
                return cat
        return None

    def get_grid(self, cat1, cat2):
        """
        Get the grid for cat1 and cat2
        assuming cat1 is the top category
        """
        if self._to_key(cat1, cat2) in self.grids:
            return self.grids[self._to_key(cat1, cat2)]
        else:
            return None

    def trim_ent(self, ent):
        """
        trim an entity to three character
        to be able to print
        """
        if len(ent) > 3:
            return ent[0:3]
        else:
            return ent

    def _to_key(self, cat1, cat2):
        """
        return a string key for cat1 and cat2
        where cat1 is the top category and cat2
        is the left
        """
        return cat1.title + ":" + cat2.title

    def answer(self, loc, new_symbol):
        """
        given ent1 in cat1 and ent2 in cat1
        change the symbol in the grid.

        This works regardless of the order of cat1 and cat2
        ex: you don't need to put the top category first
        """
        cat1, cat2, ent1, ent2 = loc
        diff = Puzzle(self.categories)
        if self.get_symbol(cat1, cat2, ent1, ent2) == new_symbol:
            return False, diff
        index1 = cat1.entities.index(ent1)
        index2 = cat2.entities.index(ent2)
        if self._to_key(cat1, cat2) in self.grids:
            grid = self.grids[self._to_key(cat1, cat2)]
            grid[index2][index1] = new_symbol
            diff_grid = diff.grids[self._to_key(cat1, cat2)]
            diff_grid[index2][index1] = new_symbol

        elif self._to_key(cat2, cat1) in self.grids:
            grid = self.grids[self._to_key(cat2, cat1)]
            grid[index1][index2] = new_symbol
            diff_grid = diff.grids[self._to_key(cat2, cat1)]
            diff_grid[index1][index2] = new_symbol

        else:
            raise Exception(
                f"Category combo for {cat1.title} and {cat2.title} does not exist"
            )

        self.history.append(deepcopy(self.grids))
        return True, diff

    def _print_row(self, top_cats, cat2, remove_top=False):
        """
        return a singular row for the puzzle,
        given the columns (top_cats) and the row (cat2)
        should be used internally
        """

        top_ents = []
        for cat in top_cats:
            top_ents += cat.entities

        return_str = ""
        bar = "  " * 2 + "-" * (len(top_ents) * 5) + "\n"
        if not remove_top:
            top_string = " " * 4 + "  "
            top_string += "  ".join([self.trim_ent(ent) for ent in top_ents])
            return_str += top_string + "\n"
            return_str += bar

        grid1 = self.grids[top_cats[0].title + ":" + cat2.title]
        for i in range(len(grid1)):

            left_ent = self.trim_ent(cat2.entities[i]) + "| "
            return_str += left_ent
            for cat in top_cats:
                row = self.grids[cat.title + ":" + cat2.title][i]
                row_str = " " + "    ".join(row) + "  |"
                return_str += row_str
            return_str += "\n"

        return_str += bar

        return return_str

    def _print_row_small(self, top_cats, cat2):
        """
        return a singular row for the puzzle,
        given the columns (top_cats) and the row (cat2)
        should be used internally
        """

        top_ents = []
        for cat in top_cats:
            top_ents += cat.entities

        return_str = ""
        bar = "-" * (len(top_ents) + len(top_cats) + 1) + "\n"
        return_str += bar

        grid1 = self.grids[top_cats[0].title + ":" + cat2.title]
        for i in range(len(grid1)):

            left_ent = "|"
            return_str += left_ent
            for cat in top_cats:
                row = self.grids[cat.title + ":" + cat2.title][i]
                row_str = "".join(row) + "|"
                return_str += row_str
            return_str += "\n"

        return return_str

    def print_row(self, row, small=False):
        """
        find the top categories and the vertical categories
        for a single row
        """
        left_cat = self.top_bottom[row]
        num_top = len(self.left_right) - row
        if not small:
            remove_top = row > 0
            return self._print_row(self.left_right[0:num_top], left_cat, remove_top)
        else:
            return self._print_row_small(self.left_right[0:num_top], left_cat)

    def print_grid(self):
        """
        return the entire puzzle string
        """
        return_str = ""
        for i in range(len(self.top_bottom)):
            return_str += self.print_row(i)

        return return_str

    def __str__(self):
        return self.print_grid()

    def __repr__(self):
        return str(self)

    def print_grid_small(self):
        """
        return the entire puzzle string

        TODO: add category names?
        """
        return_str = ""
        for i in range(len(self.top_bottom)):
            return_str += self.print_row(i, True)

        return return_str

    def _grid_is_valid(self, grid):
        """
        Check that there are one or less "O"s
        for each row and column in a grid
        """
        # check rows
        rows_valid = [row.count("O") <= 1 for row in grid]
        if False in rows_valid:
            return False

        # check columns
        for i in range(len(grid[0])):
            c = 0
            for row in grid:
                if row[i] == "O":
                    c += 1
            if c > 1:
                return False

        return True

    def _grid_is_complete(self, grid):
        """
           Check that there is exactly 1 "O"
        for each row and column in a grid
        """
        # check rows
        rows_valid = [row.count("O") == 1 for row in grid]
        if False in rows_valid:
            return False

        # check columns
        for i in range(len(grid[0])):
            c = 0
            for row in grid:
                if row[i] == "O":
                    c += 1
            if c != 1:
                return False

        return True

    def cats_is_valid(self, cat1, cat2):
        """
        Return true if there is at most 1 "O"
        in each row and column
        """
        if self._to_key(cat1, cat2) in self.grids:
            grid = self.grids[self._to_key(cat1, cat2)]
        elif self._to_key(cat2, cat1) in self.grids:
            grid = self.grids[self._to_key(cat2, cat1)]

        return self._grid_is_valid(grid)

    def find_truths(self, category, ent):
        """
        return an dictionary where the
        keys are category names where the
        value of the entity is known, and the values
        are which entity in that category "ent" is
        connected to
        """
        truths = {}
        index = category.entities.index(ent)

        for cat2 in self.categories:
            if cat2 != category:
                if self._to_key(category, cat2) in self.grids:
                    grid = self.grids[self._to_key(category, cat2)]
                    answers = [grid[i][index] for i in range(len(grid))]

                elif self._to_key(cat2, category) in self.grids:
                    grid = self.grids[self._to_key(cat2, category)]
                    answers = grid[index]

                if "O" in answers:
                    truths[cat2.title] = cat2.entities[answers.index("O")]

        return truths

    def get_known_relations(self, category, ent):
        """
        return {
          category: {
            true: connected entity
            false: []not connected entities
            nil: []entities that are undetermined
          }
        }
        """
        relations = {}
        index = category.entities.index(ent)

        for cat2 in self.categories:
            relations[cat2] = {
                "true": None,
                "false": [],
                "nil": [],
            }
            if cat2 != category:
                if self._to_key(category, cat2) in self.grids:
                    grid = self.grids[self._to_key(category, cat2)]
                    answers = [grid[i][index] for i in range(len(grid))]

                elif self._to_key(cat2, category) in self.grids:
                    grid = self.grids[self._to_key(cat2, category)]
                    answers = grid[index]

                for i, val in enumerate(answers):
                    if val == "O":
                        relations[cat2]["true"] = cat2.entities[i]
                    elif val == "X":
                        relations[cat2]["false"].append(cat2.entities[i])
                    else:
                        relations[cat2]["nil"].append(cat2.entities[i])

        return relations

    def get_symbol(self, cat1, cat2, ent1, ent2):
        """
        return the symbol at ent1 and ent2
        """
        index1 = cat1.entities.index(ent1)
        index2 = cat2.entities.index(ent2)
        if self._to_key(cat1, cat2) in self.grids:
            grid = self.grids[self._to_key(cat1, cat2)]
            return grid[index2][index1]

        elif self._to_key(cat2, cat1) in self.grids:
            grid = self.grids[self._to_key(cat2, cat1)]
            return grid[index1][index2]

        return None

    def get_category(self, title):
        """
        get category object from title
        """
        titles = [cat.title for cat in self.categories]

        return self.categories[titles.index(title)]

    def _all_ents(self):
        """
        return a nested list
        with all categories and their
        entities
        """
        ents = []
        for cat in self.categories:
            for ent in cat.entities:
                ents.append([cat, ent])

        return ents

    def num_violations(self):
        """
        Return the number of truth violations
        in the puzzle
        """
        violations = 0
        count = 0
        for cat, ent in self._all_ents():
            truths = self.find_truths(cat, ent)
            if len(truths) > 1:
                pairs = list(itertools.combinations(truths.keys(), 2))
                count += len(pairs)
                for first, second in pairs:

                    # if these two entites are in the truth of ent
                    # then they should also be true
                    cat1 = self.get_category(first)
                    cat2 = self.get_category(second)
                    ent1 = truths[first]
                    ent2 = truths[second]

                    # The symbol should be "O" or empty ("*")
                    if self.get_symbol(cat1, cat2, ent1, ent2) == "X":
                        violations += 1

                    # make sure there is not a truth somewhere else
                    truths1 = self.find_truths(cat1, ent1)
                    if cat2.title in truths1 and truths1[cat2.title] != ent2:
                        violations += 1
                    truths2 = self.find_truths(cat2, ent2)
                    if cat1.title in truths2 and truths2[cat1.title] != ent1:
                        violations += 1
        return violations

    def _truths_valid(self):
        """
        Make sure there is not violations in
        truths of each entity

        There is absoluely a more efficent way to do this
        """
        for cat, ent in self._all_ents():
            truths = self.find_truths(cat, ent)
            if len(truths) > 1:
                pairs = itertools.combinations(truths.keys(), 2)
                for first, second in pairs:

                    # if these two entites are in the truth of ent
                    # then they should also be true
                    cat1 = self.get_category(first)
                    cat2 = self.get_category(second)
                    ent1 = truths[first]
                    ent2 = truths[second]

                    # The symbol should be "O" or empty ("*")
                    if self.get_symbol(cat1, cat2, ent1, ent2) == "X":
                        return False

                    # make sure there is not a truth somehwere else
                    truths1 = self.find_truths(cat1, ent1)
                    if cat2.title in truths1 and truths1[cat2.title] != ent2:
                        return False

                    truths2 = self.find_truths(cat2, ent2)
                    if cat1.title in truths2 and truths2[cat1.title] != ent1:
                        return False
        return True

    def is_valid(self):
        """
        return true if there there is at
        most 1 "O" for each column and row

        and if there are no truth violaitons
        """
        # make sure there is at most 1 truth
        # in each row and column
        for grid in self.grids.values():
            if not self._grid_is_valid(grid):
                return False

        # make sure truths have no violations
        return self._truths_valid()

    def is_complete(self):
        """
        return true if there is exactly 1 "O"
        in each row and column after depth = 1all possible TRANS_ABC_TRUE moves have been applied (in a loop)

        and there are no truth violations
        """
        copy = deepcopy(self)
        if copy.is_valid():
            applied = True
            is_valid = True
            solver = Solver({Insight.TRANS_ABC_FALSE})
            i = 0
            while applied and is_valid:
                i += 1
                assert i < 1000  # Break the infinite loop, if there is one.
                contradiction, multi_moves = solver.apply_transitives(copy, True)
                if contradiction:
                    is_valid = False
                if len(multi_moves) == 0:
                    applied = False
            if not is_valid:
                return False

            solved = True
            for cat1 in copy.left_right:
                for cat2 in copy.top_bottom:
                    grid_a = copy.get_grid(cat1, cat2)
                    grid_b = copy.get_grid(cat2, cat1)
                    if grid_a and not copy._grid_is_complete(grid_a):
                        solved = False
                    if grid_b and not copy._grid_is_complete(grid_b):
                        solved = False

            return solved
        else:
            return False

    def _per_complete_grid(self, grid):
        s = 0
        v = 0  # amount of rows with exactly 1 "O"
        l = 0
        for row in grid:
            s += row.count("X") + row.count("O")
            if (row.count("O")) == 1:
                v += 1
            l += len(row)
        return s / l, v / (len(grid))

    def percent_complete(self):
        """
        return the ratio of cells that
        have an "X" or "O"
        """
        grid_sums = 0
        grid_len = 0
        valid_sums = 0
        for grid in self.grids.values():
            s, valid = self._per_complete_grid(grid)
            grid_sums += s
            valid_sums += valid
            grid_len += 1
        return grid_sums / grid_len, valid_sums / grid_len


def validate__default(requirements, puzzle, hints):
    cats = puzzle.categories
    if len(cats) < requirements["num_cats"]:
        return False
    if len(cats[0].entities) < requirements["num_ents"]:
        return False
    hint_types = requirements["hint"]
    if len(hint_types) == 0:
        return True
    for hint in hints:
        rule = list(hint.keys())[0]
        if rule in hint_types:
            return True
        if rule == "before":
            terms = hint[rule]
            if terms[0] != terms[2] and "before__diff_cat" in hint_types:
                return True
            if len(terms) == 5 and "before__undef" in hint_types:
                return True
            if len(terms) == 6:
                if terms[5] == 1 and "before__one" in hint_types:
                    return True
                elif "before__n" in hint_types:
                    return True
        if rule == "simple_or":
            terms = hint[rule]
            if terms[0] == terms[2] and "simple_or__same_cat" in hint_types:
                return True
            elif terms[0] != terms[2] and "simple_or__diff_cat" in hint_types:
                return True
    return False


def get_valid_cats(requirements, categories):
    num_cats = requirements["num_cats"]
    num_ents = requirements["num_ents"]
    numeric = requirements["numeric"]

    if len(categories) < requirements["num_cats"]:
        return None
    valid_cats = []
    for cat in categories:
        if len(cat.entities) >= num_ents:
            valid_cats.append(cat)
    if len(valid_cats) < num_cats:
        return None
    if not numeric:
        return valid_cats
    for cat in valid_cats:
        if cat.is_numeric:
            return valid_cats
    return None


# Randomly select num_ents entities from num_cats categories
def get_rand_cats(requirements, categories):
    num_cats = requirements["num_cats"]
    num_ents = requirements["num_ents"]
    numeric = requirements["numeric"]

    valid_cats = get_valid_cats(requirements, categories)
    if not valid_cats:
        return None

    cats = []
    random.shuffle(valid_cats)

    # Ensure that a numeric category is included for numeric tactics
    if numeric:
        for cat in valid_cats:
            if cat.is_numeric:
                valid_cats.remove(cat)
                valid_cats.insert(cat, 0)

    for cat in valid_cats[:num_cats]:
        ents = deepcopy(cat.entities)
        random.shuffle(ents)
        ents = ents[:num_ents]
        trunc_cat = deepcopy(cat)
        trunc_cat.entities = ents
        cats.append(trunc_cat)


# Take in categories; return puzzle, hints for a minimal insight problem.
# Returns None, None if a valid puzzle cannot be created.
def gen_min_puzzle__default(requirements, validate, categories):
    hint_types = requirements["hint"]

    cats = get_rand_cats(requirements, categories)
    if not cats:
        return None, None

    puzzle = Puzzle(cats)

    if len(hint_types) == 0:
        return puzzle, []

    hint_type = random.choice(hint_types)
    if "before" in hint_type:
        hint_type = "before"
    if "simple_or" in hint_type:
        hint_type = "simple_or"
    valid = False
    while not valid:
        hint = Grammar.generate_hint_of_type(cats, hint_type)
        valid = validate(requirements, puzzle, [hint])
    return puzzle, [hint]


class Insight:
    ALL_INSIGHTS = set()

    # Maintain an insight DAG in which each node points to its descendants (and its parents)
    def __init__(
        self,
        name,
        value,
        parents=set(),
        requirements={},
        validate=validate__default,
        gen_min_puzzle=gen_min_puzzle__default,
    ):
        self.name = name
        self.value = value
        self.parents = parents
        self.children = set()
        for parent in parents:
            parent.children.add(self)
        self.requirements = {
            "num_cats": 2,
            "num_ents": 3,
            "numeric": False,
            "hint": [],
            "superceded_by": [],
        }
        self.gen_min_puzzle = gen_min_puzzle__default
        for parent in parents:
            for key, value in parent.requirements.items():
                if not self.requirements[key] or value > self.requirements[key]:
                    self.requirements[key] = value
        for key, value in requirements.items():
            self.requirements[key] = value
        self.validate = validate
        Insight.ALL_INSIGHTS.add(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        if other in self.sub_dag(True):
            return True
        if self in other.sub_dag(True):
            return False
        return self.value < other.value

    def __gt__(self, other):
        if other in self.sub_dag(True):
            return False
        if self in other.sub_dag(True):
            return True
        return self.value < other.value

    def depth(self):
        return self._depth(0)

    def _depth(self, starting_depth):
        if len(self.parents) == 0:
            return starting_depth
        max_par_depth = 0
        for parent in self.parents:
            par_depth = parent._depth(starting_depth + 1)
            if par_depth > max_par_depth:
                max_par_depth = par_depth
        return max_par_depth

    # An insight and all its descendants in the DAG.
    # WARNING: This will infinitely loop if there is a cycle in the insight graph.
    # There are ways I could get around an infinite loop, but it's more elegant this way,
    # and we really shouldn't have looping dependencies.
    def sub_dag(self, children_only=False):
        to_visit = {self}
        sub_dag = set()
        while to_visit:
            curr_node = to_visit.pop()
            to_visit.update(curr_node.children)
            sub_dag.add(curr_node)

        if children_only:
            return sub_dag - {self}

        return sub_dag


# Apply an is hint (given)
Insight.APPLY_IS = Insight("APPLY_IS", 1, set(), {"hint": ["is"]})


def gen_min_puzzle__cross_out(requirements, categories):
    puzzle, hints = gen_min_puzzle__default(requirements, categories)
    is_hint = Grammar.generate_hint_of_type(puzzle.categories, "is")
    SOLVER.apply_hint(puzzle, is_hint, True)
    return puzzle, hints


# If there is an O in a row/column, the rest of the row/column must be X (given)
Insight.CROSS_OUT = Insight("CROSS_OUT", 2, gen_min_puzzle=gen_min_puzzle__cross_out)


def gen_min_puzzle__opening(requirements, categories):
    cats = get_rand_cats(requirements, categories)
    if not cats:
        return None, None

    puzzle = Puzzle(cats)
    is_hint = Grammar.generate_hint_of_type(cats, "is")
    is_puzzle = deepcopy(puzzle)
    SOLVER.apply_hint(is_puzzle, is_hint, True)
    _, cross_out_moves = SOLVER.apply_cross_out(is_puzzle)
    SOLVER.apply_multi_moves(puzzle, cross_out_moves)
    return puzzle, []


# If a row/column has one opening and the rest are Xs, it must be O (given)
Insight.OPENING = Insight("OPENING", 3, gen_min_puzzle=gen_min_puzzle__opening)

# Apply a not hint (given)
Insight.APPLY_NOT = Insight("APPLY_NOT", 4, set(), {"num_ents": 3, "hint": ["not"]})


def gen_min_puzzle__apply_or(requirements, categories):
    puzzle, or_hint = gen_min_puzzle__default(requirements, categories)
    if not puzzle:
        return None, None

    uncertain_solver = Solver(allow_uncertain_moves=True)
    or_moves = uncertain_solver.apply_hint(puzzle, or_hint)

    poss_locs = []
    for multi_move in or_moves:
        for loc, sy in multi_move["moves"]:
            if sy != "Y":
                break
            poss_locs.append(loc)

    loc = random.choice(poss_locs)
    sy = random.choice(CONFIDENT_MARKS)
    puzzle.answer(loc, sy)
    return puzzle, or_hint


# Apply an or hint once one of the clauses has been answered. (given)
Insight.APPLY_OR = Insight(
    "APPLY_OR",
    5,
    set(),
    {"hint": ["simple_or", "compound_or"]},
    gen_min_puzzle=gen_min_puzzle__apply_or,
)


def get_poss_true_locs(puzzle, cat, ent, val_cat):
    poss_true_locs = []
    poss_vals = val_cat.entities
    for val in poss_vals:
        loc = (cat, val_cat, ent, val)
        if puzzle.get_symbol(*loc) != "X":
            poss_true_locs.append(loc)


def parse_is(is_hint):
    terms = is_hint["is"]
    cat1 = terms[0]
    ent1 = terms[1]
    cat2 = terms[2]
    ent2 = terms[3]
    ents = [(cat1, ent1), (cat2, ent2)]
    return ents


def parse_simple_hint(bef_hint):
    terms = bef_hint["before"]

    num_cat = terms[4]

    ents = parse_is({"is": terms})
    return ents, num_cat


# If A is answered and B is 1 after A, then answer B is the next one after A (given)
def gen_min_puzzle__before(requirements, categories):
    puzzle, bef_hint = gen_min_puzzle__default(requirements, categories)
    if not puzzle:
        return None, None

    bef_puzzle = deepcopy(puzzle)
    SOLVER.apply_hint(puzzle, bef_hint, True)

    poss_ents, num_cat = parse_before(bef_hint)
    ent = random.choice(poss_ents)

    poss_locs = get_poss_true_locs(bef_puzzle, *ent, num_cat)
    loc = random.choice(poss_locs)
    puzzle.answer(loc, "O")

    return puzzle, bef_hint


Insight.APPLY_BEFORE_ONE_SPOT = Insight(
    "APPLY_BEFORE_ONE_SPOT",
    6,
    set(),
    {"numeric": True, "num_ents": 4, "hint": ["before__one"]},
    gen_min_puzzle=gen_min_puzzle__before,
)

# If A is answered and B is N after A, then answer B is N after A (given)
Insight.APPLY_BEFORE_N_SPOTS = Insight(
    "APPLY_BEFORE_N_SPOTS",
    7,
    {Insight.APPLY_BEFORE_ONE_SPOT},
    {"num_ents": 6, "hint": ["before__n"]},
    gen_min_puzzle=gen_min_puzzle__before,
)

# If A is answered then B must be one of the spots after A and vice versa (X where that is not true)
# Can be derived from APPLY_BEFORE_N_SPOTS by considering the possible values for N and finding that regardless of the N,
# this must be true.
Insight.APPLY_BEFORE_UNDEFINED_SPOTS = Insight(
    "APPLY_BEFORE_UNDEFINED_SPOTS",
    8,
    {Insight.APPLY_BEFORE_N_SPOTS},
    {"hint": ["before__undef"]},
    gen_min_puzzle=gen_min_puzzle__before,
)

# The transitive property applies (A -> B and B -> C, so A -> C) (given)
Insight.TRANS_ABC_TRUE = Insight("TRANS_ABC_TRUE", 14, set(), {"num_cats": 3})
# A -> B and B !> C, so A !> C (given)
# Can be derived from TRANS_ABC_TRUE (if A -> B and A -> C then B -> C, which is a contradiction)
Insight.TRANS_ABC_FALSE = Insight(
    "TRANS_ABC_FALSE",
    15,
    {Insight.TRANS_ABC_TRUE},
    {"num_ents": 4},
    gen_min_puzzle=gen_min_puzzle__cross_out,
)


# If A or B from category 0 is C then no other entity from category 0 is C
# Can be derived by considering A -> C and B -> C and seeing that either way, all other entities from 0 are X.
Insight.SIMPLE_OR_SAME_CAT = Insight(
    "SIMPLE_OR_SAME_CAT",
    9,
    {Insight.APPLY_OR, Insight.CROSS_OUT},
    {"num_ents": 4, "hint": ["simple_or__same_cat"]},
)


# If A or B is C then A is not B
# Can be derived by applying the OR rule in turn and seeing that by TRANS_ABC_FALSE, A is not B either way.
Insight.SIMPLE_OR_DIFF_CAT = Insight(
    "SIMPLE_OR_DIFF_CAT",
    10,
    {Insight.APPLY_OR, Insight.TRANS_ABC_FALSE},
    {"hint": ["simple_or__diff_cat"]},
)

# The before entity can't be in the last spot (and vice versa for the after entity) Same for undefined spots
# Can be derived by considering each possible value for A with APPLY_BEFORE_UNDEFINED_SPOTS and seeing that in the last spot,
# there is no remaining possible value for B.
Insight.BEFORE_NOINFO = Insight(
    "BEFORE_NOINFO",
    12,
    {Insight.APPLY_BEFORE_UNDEFINED_SPOTS, Insight.OPENING},
    {"hint": ["before"]},
)

# The before entity can't be in the last N spots (and vice versa for the after entity)
# The general case of BEFORE_NOINFO. It could also be derived directly from APPLY_BEFORE_N_SPOTS,
# but expert knowledge suggests it will be easier for users to encounter BEFORE_NOINFO first.
Insight.BEFORE_N_SPOTS_NOINFO = Insight(
    "BEFORE_N_SPOTS_NOINFO",
    13,
    {Insight.BEFORE_NOINFO},
    {"hint": ["before__n"]},
)

# A streak of Xs at the beginning/end forces the first available position for the other entity to shift.
# Can be derived in the same way as BEFORE_N_SPOTS_NOINFO;
# again, it will be easier for users to encounter BEFORE_N_SPOTS_NOINFO first.
Insight.BEFORE_N_SPOTS_SHIFT = Insight(
    "BEFORE_N_SPOTS_SHIFT",
    16,
    {Insight.BEFORE_N_SPOTS_NOINFO},
    {"hint": ["before"]},
)


# For a position to be a valid answer, the corresponding position +/- num must be valid for the other entity
# The most complex case of BEFORE_NOINFO.
def gen_min_puzzle__before_crosscheck(requirements, categories):
    puzzle, hints = gen_min_puzzle__default(requirements, categories)
    if not puzzle:
        return None, None

    bef_hint = hints[0]
    bef_puzzle = deepcopy(puzzle)
    SOLVER.apply_hint(bef_puzzle, bef_hint, True)

    poss_ents, num_cat = parse_before(bef_hint)
    ent = random.choice(poss_ents)

    poss_locs = get_poss_true_locs(bef_puzzle, *ent, num_cat)
    loc = random.choice(poss_locs)
    puzzle.answer(loc, "X")

    return puzzle, hints


Insight.BEFORE_N_SPOTS_CROSSCHECK = Insight(
    "BEFORE_N_SPOTS_CROSSCHECK",
    17,
    {Insight.BEFORE_N_SPOTS_SHIFT},
    {"hint": ["before__one", "before__n"]},
    gen_min_puzzle=gen_min_puzzle__before_crosscheck,
)


# A and B don't share any possibilities; A != B
# Can be derived by considering all possible values for A and applying TRANS_ABC_FALSE.
# Another kind of crosscheck.
def gen_min_puzzle__trans_sets(requirements, categories):
    puzzle, hints = gen_min_puzzle__default(requirements, categories)
    if not puzzle:
        return None, None

    is_hint = Grammar.generate_hint_of_type(puzzle.categories, "is")
    SOLVER.apply_hint(puzzle, is_hint, True)

    poss_ents = parse_is(is_hint)
    ent = random.choice(poss_ents)

    cat1 = poss_ents[0][0]
    cat2 = poss_ents[1][0]

    valid_cats = []
    for cat in puzzle.categories:
        if cat not in [cat1, cat2]:
            valid_cats.append(cat)

    cat3 = random.choice(valid_cats)
    ent3 = random.choice(cat3.entities)

    not_hint = {"hint": {"not": {"is": [*ent, cat3, ent3]}}}
    puzzle.apply_hint(not_hint, True)

    return puzzle, hints


Insight.TRANS_SETS = Insight(
    "TRANS_SETS",
    18,
    {Insight.TRANS_ABC_FALSE},
    gen_min_puzzle=gen_min_puzzle__trans_sets,
)


# If A < B and A, B are not in the same category, then A is not B.
# Can be derived by considering each possible value for A with APPLY_BEFORE_UNDEFINED_SPOTS and applying TRANS_ABC_FALSE
Insight.BEFORE_DIFF_CAT = Insight(
    "BEFORE_DIFF_CAT",
    11,
    {Insight.APPLY_BEFORE_UNDEFINED_SPOTS, Insight.TRANS_ABC_FALSE},
    {
        "hint": ["before__diff_cat"],
        "superceded_by": [
            Insight.BEFORE_N_SPOTS_SHIFT,
            Insight.TRANS_SETS,
            Insight.TRANS_ABC_TRUE,
        ],
    },
)
Insight.USER_INSIGHT = Insight("USER_INSIGHT", 100)

# ## Hint Grammar
#
# The hint grammar is represented as a dictionary where each key is a production rule and each value is the a nested list with the possible terms the production rule needs
#
# For example the "or" rule has two possible term sets:
# * ["cat1", "ent1", "cat1", "ent2", "cat2", "ent"]
# *  ["cat1", "ent", "cat2", "ent", "cat3", "ent"]
#
# The first term set describes two different entities from the same category, and one entity from a different category. This can be used to decribe the rule "Ms. White or Ms. Scarlet was in the study".
#
# The second term set describes three entites from different categories. This can be used to describe the rule "Ms. White or the person with the knife was in the study"


# define this grammar
# # cat is any category with no resitrictions, however cat1 and cat2 must be different
# similarly ent is any entity with in a caterogy (must have a cat immediately before), but ent1 and ent2 must be different
# num must be a numerical caterogy, alp must be non-numeric
# int is an integer 1-len(entities)
class Grammar:
    TERMINALS = [
        "cat",
        "ent",
        "cat1",
        "cat2",
        "cat3",
        "cat4",
        "cat5",
        "ent1",
        "ent2",
        "ent3",
        "ent4",
        "ent5",
        "num",
        "num1",
        "num2",
        "num3",
        "num4",
        "num5" "alp",
        "alp1",
        "alp2",
        "alp3",
        "alp4",
        "alp5",
        "int",
    ]

    GRAMMAR = {
        "hint": {
            "is": [["cat1", "ent", "cat2", "ent"]],
            "not": [["is"]],
            "before": [
                ["cat", "ent1", "cat", "ent2", "num1"],
                ["cat", "ent1", "cat", "ent2", "num1", "int"],
            ],
            "simple_or": [
                ["cat1", "ent1", "cat1", "ent2", "cat2", "ent"],
                ["cat1", "ent", "cat2", "ent", "cat3", "ent"],
            ],
            "compound_or": [["is", "is"]],
        }
    }

    def __init__(self, categories):
        self.categories = categories

    # ## Creating Clues
    #
    # Create a hint involves two steps: generating a word from the grammar and filling in the word
    #
    # #### Generating a word
    # To generate a word, a random production rule is selected. The production rule defines terms that it needs, which will either be terminals or another production rule. If there are any production rules in the terms, the function will be called recursively (with selecting another production rule) until all remaining terms are filled in with terminals.
    #
    # #### Fill in the word
    # The first step will produce a dictionary with list of terms as values, which should all be terminals. For compound hints (ex: "or_hint"), the values are also dictionaries and this process is calledrecursively. This step replaces the terminal word (ex: "cat1") with approicate objects from the puzzle. For example if there were the terms: ["cat1", "ent", "cat2", "ent"], this step could replace it with ["rooms", "study", "suspects" ,"Ms. White"]. Note "rooms" would be the category object, not the string "rooms".

    def sub_grammar(grammar, rule):
        queue = []
        queue.append(grammar)
        while queue:
            grammar = queue.pop(0)
            if rule in list(grammar.keys()):
                return grammar[rule]
            for r in list(grammar.keys()):
                if isinstance(grammar[r], dict):
                    queue.append(grammar[r])
        return

    def generate_word(sub_grammar, grand_grammar=None):
        """
        randomly choose prodcution rules to create new hint base
        will fill out production rules until all terms are terminals
        """
        if grand_grammar is None:
            grand_grammar = sub_grammar
        rule = ""
        if isinstance(sub_grammar, dict):
            # Grammar has named rules; select one at random
            rule = random.choice(list(sub_grammar.keys()))
            if isinstance(sub_grammar[rule], dict):
                # Rule is a subgrammar with named rules itself; recurse
                return {rule: Grammar.generate_word(sub_grammar[rule], grand_grammar)}
            else:
                # Rule is a list of alternates
                sub_grammar = sub_grammar[rule]
        # Grammar is a list of alternates; select one at random
        production = random.choice(sub_grammar)
        terms = []
        for word in production:
            if word in Grammar.TERMINALS:
                terms.append(word)
            else:
                terms.append({
                    word: Grammar.generate_word(
                        Grammar.sub_grammar(grand_grammar, word), grand_grammar
                    )
                })
        if rule != "":
            return {rule: terms}
        else:
            return terms

    def shuffled_cat_list(categories):
        """
        shuffle categories and entities within categories and return as a nested list
        ex: [[cat1, [ent1.1, ent1.2, ent1.2]], [cat2, [ent2.1, ent2.2, ent2.3]]]
        """
        li = categories[:]
        random.shuffle(li)
        cats = []
        for cat in li:
            shuf_ents = cat.entities[:]
            random.shuffle(shuf_ents)
            cats.append([cat, shuf_ents])
        return cats

    def get_alps(categories):
        """
        return all alphabetic categories
        """
        if len(categories) > 0 and isinstance(categories[0], Category):
            return [cat for cat in categories if not cat.is_numeric]
        return [cat for cat in categories if not cat[0].is_numeric]

    def get_num(categories):
        """
        return all numeric categories
        """
        if len(categories) > 0 and isinstance(categories[0], Category):
            return [cat for cat in categories if cat.is_numeric]
        return [cat for cat in categories if cat[0].is_numeric]

    def fill_in_word(word, categories):
        """
        Replace all terminal terms with random and appropriate
        categories, entities, or integers from a puzzle
        """
        filled_word = {}
        for key in word:
            value = word[key]
            if isinstance(value, dict):
                filled_word[key] = Grammar.fill_in_word(word[key], categories)
            else:
                new_terms = []
                cats = Grammar.shuffled_cat_list(categories)
                alps = Grammar.get_alps(cats)
                nums = Grammar.get_num(cats)
                last_cat = None

                for term in value:
                    if isinstance(term, dict):
                        new_terms.append(Grammar.fill_in_word(term, cats))
                    else:
                        if term == "cat":
                            last_cat = random.choice(cats)
                            new_terms.append(last_cat[0])
                        elif term == "cat1":
                            if len(cats) < 1:
                                raise Exception("CAT_COUNT")
                            else:
                                last_cat = cats[0]
                                new_terms.append(last_cat[0])
                        elif term == "cat2":
                            if len(cats) < 2:
                                raise Exception("CAT_COUNT")
                            else:
                                last_cat = cats[1]
                                new_terms.append(last_cat[0])
                        elif term == "cat3":
                            if len(cats) < 3:
                                raise Exception("CAT_COUNT")
                            else:
                                last_cat = cats[2]
                                new_terms.append(last_cat[0])
                        elif term == "alp":
                            if len(alps) == 0:
                                raise Exception("ALPH_COUNT")
                            else:
                                last_cat = random.choice(alps)
                                new_terms.append(last_cat[0])
                        elif term == "num":
                            if len(nums) == 0:
                                raise Exception("NUM_COUNT")
                            else:
                                last_cat = random.choice(nums)
                                new_terms.append(last_cat[0])
                        elif term == "ent":
                            new_terms.append(random.choice(last_cat[1]))
                        elif term == "ent1":
                            if len(last_cat[1]) < 1:
                                raise Exception("ENT_COUNT")
                            else:
                                new_terms.append(last_cat[1][0])
                        elif term == "ent2":
                            if len(last_cat[1]) < 2:
                                raise Exception("ENT_COUNT")
                            else:
                                new_terms.append(last_cat[1][1])
                        elif term == "ent3":
                            if len(last_cat[1]) < 3:
                                raise Exception("ENT_COUNT")
                            else:
                                new_terms.append(last_cat[1][2])
                        elif term == "int":
                            new_terms.append(
                                random.randrange(1, len(last_cat[1]) - 1)
                            )  # 2 spaces to make decision
                filled_word[key] = new_terms
        return filled_word

    # Generate a random hint of a particular hint type
    def generate_hint_of_type(categories, hint_type, depth=0):
        hint_type_grammar = Grammar.GRAMMAR["hint"][hint_type]
        word = Grammar.generate_word({"hint": {hint_type: hint_type_grammar}})
        try:
            return Grammar.fill_in_word(word, categories)["hint"]
        except Exception as e:
            if depth > 100:
                raise e
            return Grammar.generate_hint(categories, depth + 1)

    def generate_hint(categories, depth=0):
        """
        given a puzzle generate a random, valid hint
        """
        word = Grammar.generate_word(Grammar.GRAMMAR)
        try:
            return Grammar.fill_in_word(word, categories)["hint"]
        except Exception as e:
            if depth > 100:
                raise e
            return Grammar.generate_hint(categories, depth + 1)

    def str_hint(hint, str_so_far=""):
        if isinstance(hint, dict):
            rule = list(hint.keys())[0]
            str_so_far += rule + ": "
            return Grammar.str_hint(hint[rule], str_so_far)
        elif isinstance(hint, list):
            str_so_far += "[ "
            for i, term in enumerate(hint):
                str_so_far += Grammar.str_hint(term)
                if i != len(hint) - 1:
                    str_so_far += ", "
            str_so_far += " ]"
        else:
            str_so_far += str(hint)
        return str_so_far

    def str_hint(hint, str_so_far=""):
        if isinstance(hint, dict):
            rule = list(hint.keys())[0]
            str_so_far += rule + ": "
            return Grammar.str_hint(hint[rule], str_so_far)
        elif isinstance(hint, list):
            str_so_far += "[ "
            for i, term in enumerate(hint):
                str_so_far += Grammar.str_hint(term)
                if i != len(hint) - 1:
                    str_so_far += ", "
            str_so_far += " ]"
        else:
            str_so_far += str(hint)
        return str_so_far


# ## Using hints to solve puzzles
# Giving a list of hints you can solve the puzzle (as much as the information in the hints will allow). This can be done by iteratively applying indivual hints untill they are all completed (ex: the "not" rule is completed after putting an "X" on the board, but the "before" rule may still have information after placing a symbol) or the rules stopping changing the game state (ex: the "or" rule cannot change the same state if it doesn't know which rule is correct). Hint can also be invalid, which will terminate the process (ex: if there is a "not" rule over a spot that another hint already placed an "O).
#
#
# ```
# queue = all hints
#
# while game changed and is valid:
#   for hint in queue:
#     apply hint to game state
#     if hint or game state is invalid --> exit
#     if hint is complete hint remove from queue
#
#   if no hints changed gamestate --> exit
#
# ```
#
class Solver:
    def __init__(self, forbidden_insights=set(), allow_uncertain_moves=False):
        self.forbidden_insights = forbidden_insights
        self.allow_uncertain_moves = allow_uncertain_moves
        return

    def add_multi_move(self, puzzle, moves, insight, multi_moves, contradiction):
        deduped_moves = []
        for move in moves:
            loc = move[0]
            new_sy = move[1]
            old_sy = puzzle.get_symbol(*loc)
            move_contradiction = False
            if old_sy == new_sy:
                continue
            deduped_moves.append(move)
            if old_sy in CONFIDENT_MARKS:
                move_contradiction = True
            contradiction = contradiction or move_contradiction

        if len(deduped_moves) > 0:
            multi_move = {
                "insight": insight,
                "moves": moves,
            }
            multi_moves.append(multi_move)
        return contradiction

    def apply_multi_moves(self, puzzle, multi_moves):
        applied = False
        for move in multi_moves:
            if self.apply_multi_move(puzzle, move):
                applied = True
        return applied

    def apply_multi_move(self, puzzle, multi_move):
        applied = False
        for move in multi_move["moves"]:
            if puzzle.answer(*move):
                applied = True
        return applied

    def extend_multi_moves(
        self, mo_contradiction, mo_moves, contradiction, multi_moves
    ):
        contradiction = contradiction or mo_contradiction
        multi_moves.extend(mo_moves)
        return contradiction

    def cross_out(self, puzzle, loc, apply=False):
        """
        crosses out the rest of the row and column for an O
        """
        contradiction = False

        insight = Insight.CROSS_OUT
        multi_moves = []

        cat1, cat2, ent1, ent2 = loc

        cat1_insight_marks = []
        # x out the cross sections
        for ent in cat1.entities:
            if ent != ent1:
                cat1_insight_marks.append(((cat1, cat2, ent, ent2), "X"))
        contradiction = self.add_multi_move(
            puzzle, cat1_insight_marks, insight, multi_moves, contradiction
        )

        cat2_insight_marks = []
        for ent in cat2.entities:
            if ent != ent2:
                cat2_insight_marks.append(((cat1, cat2, ent1, ent), "X"))
        contradiction = self.add_multi_move(
            puzzle, cat2_insight_marks, insight, multi_moves, contradiction
        )

        if apply:
            self.apply_multi_moves(puzzle)

        return contradiction, multi_moves

    # remove errors (discrepancies between the current puzzle and the canonical solution)
    def repair(self, puzzle, solution, apply=False):
        multi_moves = []
        contradiction = False  # If this is true, then there is a mark that doesn't match the solution
        for cat1 in puzzle.left_right:
            for cat2 in puzzle.top_bottom:
                for ent1 in cat1.entities:
                    for ent2 in cat2.entities:
                        loc = (cat1, cat2, ent1, ent2)
                        curr_sy = puzzle.get_symbol(*loc)
                        soln_sy = solution.get_symbol(*loc)
                        if curr_sy in CONFIDENT_MARKS and curr_sy != soln_sy:
                            # The puzzle value does not match the canonical solution; unset subgrid and mark repair as applied
                            insight = None
                            contradiction = self.add_multi_move(
                                puzzle,
                                [(loc, "*")],
                                insight,
                                multi_moves,
                                contradiction,
                            )
                            assert (
                                contradiction
                            ), "Repair moves should ALWAYS be a contradiction"
        if apply:
            self.apply_multi_moves(puzzle, multi_moves)
        return contradiction, multi_moves

    def apply_is(self, puzzle, terms, apply=False):
        """
        Apply the is rule to puzzle, will always complete in one step
        puzzle: the current state of the grid
        terms: the terms making up the is hint's grammar
        return: applied, is_valid, complete
        """
        multi_moves = []
        contradiction = False

        cat1 = terms[0]
        ent1 = terms[1]
        cat2 = terms[2]
        ent2 = terms[3]

        insight = Insight.APPLY_IS
        loc = (cat1, cat2, ent1, ent2)
        contradiction = self.add_multi_move(
            puzzle, [(loc, "O")], insight, multi_moves, contradiction
        )

        if apply:
            self.apply_multi_moves(puzzle, multi_moves)
        return contradiction, multi_moves

    def apply_not(self, puzzle, terms, apply=False):
        """
        Apply the not rule to puzzle, will always complete in one step
        puzzle: the current state of the grid
        terms: the terms making up the is hint's grammar
        return: applied, is_valid, complete
        """
        multi_moves = []
        contradiction = False

        cat1 = terms[0]
        ent1 = terms[1]
        cat2 = terms[2]
        ent2 = terms[3]

        insight = Insight.APPLY_NOT
        loc = (cat1, cat2, ent1, ent2)
        contradiction = self.add_multi_move(
            puzzle, [(loc, "X")], insight, multi_moves, contradiction
        )

        if apply:
            self.apply_multi_moves(puzzle, multi_moves)
        return contradiction, multi_moves

    # If a row/column has 1 O then fill the rest with X.
    # If a row/column has more than one O then contradiction.
    def apply_cross_out(self, puzzle, apply=False):
        multi_moves = []
        contradiction = False
        # For every combination of categories:
        for cat1 in puzzle.categories:
            for cat2 in puzzle.categories:
                grid = puzzle.get_grid(cat1, cat2)
                if grid != None:
                    # For each row:
                    for i, row in enumerate(grid):
                        blanks = [
                            i for i in range(len(row)) if row[i] not in CONFIDENT_MARKS
                        ]
                        os = [i for i in range(len(row)) if row[i] == "O"]
                        if len(os) > 1:
                            # There are multiple Os; this is a contradiction
                            contradiction = True
                        elif len(os) == 1 and len(blanks) >= 1:
                            # There is an O; the rest of the row and column can be crossed out.
                            ent1 = cat1.entities[os[0]]
                            ent2 = cat2.entities[i]
                            loc = (cat1, cat2, ent1, ent2)
                            contradiction = self.extend_multi_moves(
                                *self.cross_out(puzzle, loc),
                                contradiction,
                                multi_moves,
                            )

                    # For each column:
                    for j in range(len(grid[0])):
                        blanks = [
                            i
                            for i in range(len(grid))
                            if grid[i][j] not in CONFIDENT_MARKS
                        ]
                        os = [i for i in range(len(grid)) if grid[i][j] == "O"]
                        if len(os) > 1:
                            # There are multiple Os; this is a contradiction
                            contradiction = True
                        elif len(os) == 1 and len(blanks) >= 1:
                            # There is an O; the rest of the row and column can be crossed out.
                            ent1 = cat1.entities[j]
                            ent2 = cat2.entities[os[0]]

                            loc = (cat1, cat2, ent1, ent2)
                            contradiction = self.extend_multi_moves(
                                *self.cross_out(puzzle, loc),
                                contradiction,
                                multi_moves,
                            )

        if apply:
            self.apply_multi_moves(puzzle, multi_moves)
        return contradiction, multi_moves

    # If a row/column has 1 * and the rest are X then fill out a O there.
    # If a row/column is all X or has more than one O then contradiction.
    def apply_opening(self, puzzle, apply=False):
        multi_moves = []
        contradiction = False

        # For every combination of categories:
        for cat1 in puzzle.categories:
            for cat2 in puzzle.categories:
                grid = puzzle.get_grid(cat1, cat2)
                if grid != None:
                    # For each row:
                    for i, row in enumerate(grid):
                        blanks = [
                            i for i in range(len(row)) if row[i] not in CONFIDENT_MARKS
                        ]
                        os = [i for i in range(len(row)) if row[i] == "O"]
                        if len(blanks) == 0 and len(os) == 0:
                            # The row is all Xs; contradiction
                            contradiction = True
                        elif len(os) > 1:
                            # There are multiple Os; this is a contradiction
                            contradiction = True
                        # If there is only 1 blank value:
                        elif len(os) == 0 and len(blanks) == 1:
                            ent1 = cat1.entities[blanks[0]]
                            ent2 = cat2.entities[i]
                            insight = Insight.OPENING

                            loc = (cat1, cat2, ent1, ent2)

                            # Answer it as 0.
                            contradiction = self.add_multi_move(
                                puzzle,
                                [(loc, "O")],
                                insight,
                                multi_moves,
                                contradiction,
                            )

                    # For each column:
                    for j in range(len(grid[0])):
                        blanks = [
                            i
                            for i in range(len(grid))
                            if grid[i][j] not in CONFIDENT_MARKS
                        ]
                        os = [i for i in range(len(grid)) if grid[i][j] == "O"]
                        if len(blanks) == 0 and len(os) == 0:
                            # The row is all Xs; contradiction
                            contradiction = True
                        elif len(os) > 1:
                            # There are multiple Os; this is a contradiction
                            contradiction = True

                        # If there is only one blank value:
                        elif len(os) == 0 and len(blanks) == 1:
                            ent1 = cat1.entities[j]
                            ent2 = cat2.entities[blanks[0]]
                            # Answer it as 0.
                            insight = Insight.OPENING

                            loc = (cat1, cat2, ent1, ent2)

                            # Answer it as 0.
                            contradiction = self.add_multi_move(
                                puzzle,
                                [(loc, "O")],
                                insight,
                                multi_moves,
                                contradiction,
                            )

        if apply:
            self.apply_multi_moves(puzzle, multi_moves)
        return contradiction, multi_moves

    def apply_move(self, puzzle, move):
        diff = move["move_diff"]
        for cat1 in puzzle.left_right:
            for cat2 in puzzle.top_bottom:
                move_grid = diff.get_grid(cat1, cat2)
                if move_grid is None:
                    continue
                for ent2_idx in range(0, len(move_grid)):
                    for ent1_idx in range(0, len(move_grid[ent2_idx])):
                        if move_grid[ent2_idx][ent1_idx] != "*":
                            puzzle.answer(
                                (
                                    cat1,
                                    cat2,
                                    cat1.entities[ent1_idx],
                                    cat2.entities[ent2_idx],
                                ),
                                move_grid[ent2_idx][ent1_idx],
                            )

    # If A is B and B is C then A is C
    # If A is B and B is not C then A is not C
    # ...
    def apply_transitives(self, puzzle, apply=False):
        multi_moves = []
        contradiction = False

        # For every pair of related entities:
        #   If A == B and B == C then A == C
        #   If A == B and B != C then A != C
        for catA in puzzle.categories:
            for entA in catA.entities:
                # All known relations for A
                entA_relations = puzzle.get_known_relations(catA, entA)

                # For each category for which A has relations
                for catB, catB_relations in entA_relations.items():

                    # For A's truth value in catB, A and B share all relations
                    entB = catB_relations["true"]
                    if entB == None:
                        continue

                    # A is related to B, so A and B share relations for all other categories
                    # Get all relations for B
                    entB_relations = puzzle.get_known_relations(catB, entB)

                    # Relate A to B's truth and false values.
                    for catC, catC_relations in entB_relations.items():
                        if catC == catA:
                            continue
                        entC = catC_relations["true"]
                        if entC == None:
                            continue
                        # A -> B and B -> C, so A -> C
                        loc = (catA, catC, entA, entC)
                        insight = Insight.TRANS_ABC_TRUE
                        contradiction = self.add_multi_move(
                            puzzle, [(loc, "O")], insight, multi_moves, contradiction
                        )
                        # For all false values for B in category C
                        for entC in catC_relations["false"]:
                            if entC == None:
                                continue
                            # A -> B and B !> C, so A !> C
                            insight = Insight.TRANS_ABC_FALSE
                            loc = (catA, catC, entA, entC)
                            contradiction = self.add_multi_move(
                                puzzle,
                                [(loc, "X")],
                                insight,
                                multi_moves,
                                contradiction,
                            )

        # For every pair of entities:
        #   If A and B don't share any possible values for category C, then A != B
        # This loop is separate to enforce that harder insights are only used when the easier insights have been exhausted.
        for catA in puzzle.categories:
            for entA in catA.entities:
                # All known relations for A
                entA_relations = puzzle.get_known_relations(catA, entA)

                # For each category for which A has relations
                for catB, catB_relations in entA_relations.items():
                    if catA == catB:
                        continue
                    # for A's indeterminate values in category B, if A and B can't be related in some category, then A != B
                    for entB in catB_relations["nil"]:
                        # All relations for B
                        entB_relations = puzzle.get_known_relations(catB, entB)
                        for catC, catCA_relations in entA_relations.items():
                            if catC not in [catA, catB]:
                                # catCA_relations are A's relations for category C.
                                # catCB_relations are B's relations for category C.
                                catCB_relations = entB_relations[catC]

                                A_possibles = catCA_relations["nil"].copy()
                                B_possibles = catCB_relations["nil"].copy()

                                entCA = catCA_relations["true"]
                                entCB = catCB_relations["true"]
                                if entCA != None:
                                    A_possibles.append(entCA)
                                if entCB != None:
                                    B_possibles.append(entCB)

                                # Now possibles include all positive or nil values for category C
                                # If A and B don't share any entities in their possible lists, then A != B
                                setA = set(A_possibles)
                                setB = set(B_possibles)
                                if not (setA & setB):
                                    # A and B don't share any possibilities; A != B
                                    loc = (catA, catB, entA, entB)
                                    insight = Insight.TRANS_SETS
                                    contradiction = self.add_multi_move(
                                        puzzle,
                                        [(loc, "X")],
                                        insight,
                                        multi_moves,
                                        contradiction,
                                    )

        if apply:
            self.apply_multi_moves(puzzle, multi_moves)
        return contradiction, multi_moves

    def apply_before(self, puzzle, terms, apply=False):
        """
        apply the before rule to the puzzle
        puzzle: the current state of the grid
        terms: the terms making up the is hint's grammar
        return_steps: return each mark/insight as a separate move
        return: applied, is_valid, complete
        """
        multi_moves = []
        contradiction = False
        numbered = len(terms) == 6

        bef_cat = terms[0]
        bef_ent = terms[1]  # bef entity is before aft_ent
        aft_cat = terms[2]
        aft_ent = terms[3]

        num_cat = terms[4]

        num = 1
        if numbered:
            num = terms[5]

        # If A < B and A, B are not in the same category, then A is not B.
        if bef_cat != aft_cat:
            loc = (bef_cat, aft_cat, bef_ent, aft_ent)
            insight = Insight.BEFORE_DIFF_CAT
            contradiction = self.add_multi_move(
                puzzle, [(loc, "X")], insight, multi_moves, contradiction
            )

        # Get all the current symbols for the two entities in the num category
        before_symbols = [
            puzzle.get_symbol(bef_cat, num_cat, bef_ent, ent)
            for ent in num_cat.entities
        ]
        after_symbols = [
            puzzle.get_symbol(aft_cat, num_cat, aft_ent, ent)
            for ent in num_cat.entities
        ]

        # if both entities have answer, we can determine if this rule is valid
        if "O" in before_symbols and "O" in after_symbols:
            contradiction = contradiction or before_symbols.index(
                "O"
            ) >= after_symbols.index("O")
            if numbered:
                contradiction = (
                    contradiction
                    or after_symbols.index("O") - before_symbols.index("O") != num
                )

        # determine the possible after entities if the before entity is solved
        if "O" in before_symbols:
            insight = Insight.APPLY_BEFORE_UNDEFINED_SPOTS
            bef_index = before_symbols.index("O")
            pos_aft_index = [
                i
                for i in list(range(bef_index + 1, len(after_symbols)))
                if after_symbols[i] != "X"
            ]

            if numbered:
                if num == 1:
                    insight = Insight.APPLY_BEFORE_ONE_SPOT
                else:
                    insight = Insight.APPLY_BEFORE_N_SPOTS
                if (
                    bef_index + num < len(after_symbols)
                    and after_symbols[bef_index + num] != "X"
                ):
                    pos_aft_index = [bef_index + num]
                else:
                    pos_aft_index = []

            if len(pos_aft_index) == 0:
                contradiction = True
            elif len(pos_aft_index) == 1:
                aft_index = pos_aft_index[0]
                loc = (aft_cat, num_cat, aft_ent, num_cat.entities[aft_index])
                contradiction = self.add_multi_move(
                    puzzle, [(loc, "O")], insight, multi_moves, contradiction
                )
            else:
                assert insight == Insight.APPLY_BEFORE_UNDEFINED_SPOTS
                marks = []
                for i in range(0, bef_index + 1):
                    loc = (aft_cat, num_cat, aft_ent, num_cat.entities[i])
                    marks.append((loc, "X"))

                contradiction = self.add_multi_move(
                    puzzle, marks, insight, multi_moves, contradiction
                )

                if self.allow_uncertain_moves:
                    marks = []
                    for i in pos_aft_index:
                        # Make an uncertain mark for possible answers.
                        loc = (aft_cat, num_cat, aft_ent, num_cat.entities[i])
                        sy = puzzle.get_symbol(*loc)
                        if sy == "*":
                            marks.append((loc, "Y"))
                    contradiction = self.add_multi_move(
                        puzzle, marks, insight, multi_moves, contradiction
                    )

        # determine the possible before entities if the after entity is solved
        if "O" in after_symbols:
            insight = None
            aft_index = after_symbols.index("O")
            pos_bef_index = [
                i for i in list(range(0, aft_index)) if before_symbols[i] != "X"
            ]
            insight = Insight.APPLY_BEFORE_UNDEFINED_SPOTS
            if numbered:
                if num == 1:
                    insight = Insight.APPLY_BEFORE_ONE_SPOT
                else:
                    insight = Insight.APPLY_BEFORE_N_SPOTS
                if aft_index - num >= 0 and before_symbols[aft_index - num] != "X":
                    pos_bef_index = [aft_index - num]
                else:
                    pos_bef_index = []

            if len(pos_bef_index) == 0:
                contradiction = True
            elif len(pos_bef_index) == 1:
                bef_index = pos_bef_index[0]
                loc = (bef_cat, num_cat, bef_ent, num_cat.entities[bef_index])
                contradiction = self.add_multi_move(
                    puzzle, [(loc, "O")], insight, multi_moves, contradiction
                )
            else:
                assert insight == Insight.APPLY_BEFORE_UNDEFINED_SPOTS
                marks = []
                for i in range(aft_index, len(before_symbols)):
                    loc = (bef_cat, num_cat, bef_ent, num_cat.entities[i])
                    marks.append((loc, "X"))
                contradiction = self.add_multi_move(
                    puzzle, marks, insight, multi_moves, contradiction
                )
                if self.allow_uncertain_moves:
                    marks = []
                    for i in pos_bef_index:
                        # Make an uncertain mark for possible answers.
                        loc = (aft_cat, num_cat, bef_ent, num_cat.entities[i])
                        sy = puzzle.get_symbol(
                            aft_cat, num_cat, bef_ent, num_cat.entities[i]
                        )
                        if sy == "*":
                            marks.append((loc, "Y"))
                    contradiction = self.add_multi_move(
                        puzzle, marks, insight, multi_moves, contradiction
                    )

        # Narrow down possiblities with no information for entities yet
        # The before entity can't be in the last num spots (or there won't be room for the after entity)
        before_1_marks = []
        before_n_marks = []
        for i in range(len(before_symbols) - num, len(before_symbols)):
            loc = (bef_cat, num_cat, bef_ent, num_cat.entities[i])

            if i < len(before_symbols) - 1:
                before_1_marks.append((loc, "X"))

            before_n_marks.append((loc, "X"))

        # And the inverse is true for the after entity
        for i in range(0, num):
            loc = (aft_cat, num_cat, aft_ent, num_cat.entities[i])

            if i == 0:
                before_1_marks.append((loc, "X"))
            before_n_marks.append((loc, "X"))

        contradiction = self.add_multi_move(
            puzzle, before_1_marks, Insight.BEFORE_NOINFO, multi_moves, contradiction
        )
        contradiction = self.add_multi_move(
            puzzle,
            before_n_marks,
            Insight.BEFORE_N_SPOTS_NOINFO,
            multi_moves,
            contradiction,
        )

        # Determine possible answers with constraints on either entity
        if "X" in before_symbols or "X" in after_symbols:
            # A streak of Xs at the beginning/end forces the first available position for the other entity to shift.
            shift_marks = []

            for i in range(len(before_symbols) - num):
                if before_symbols[i] != "X":
                    break

                loc = (aft_cat, num_cat, aft_ent, num_cat.entities[i + num])
                shift_marks.append((loc, "X"))

            for i in range(len(after_symbols) - 1, num - 1, -1):
                if after_symbols[i] != "X":
                    break
                loc = (bef_cat, num_cat, bef_ent, num_cat.entities[i - num])
                shift_marks.append((loc, "X"))

            contradiction = self.add_multi_move(
                puzzle,
                shift_marks,
                Insight.BEFORE_N_SPOTS_SHIFT,
                multi_moves,
                contradiction,
            )

            if numbered:
                # All Xs for the before entity where the index is valid (i+num exists).
                before_Xs = [
                    i
                    for i in range(len(before_symbols))
                    if before_symbols[i] == "X" and i + num < len(before_symbols) - 1
                ]
                # All Xs for the after entity where the index is valid (i-num exists).
                after_Xs = [
                    i
                    for i in range(len(after_symbols))
                    if after_symbols[i] == "X" and i - num > -1
                ]

                # For a position to be a valid answer, the corresponding position +/- num must be valid for the other entity
                xcheck_marks = []
                for i in before_Xs:
                    loc = (aft_cat, num_cat, aft_ent, num_cat.entities[i + num])
                    xcheck_marks.append((loc, "X"))

                for i in after_Xs:
                    loc = (bef_cat, num_cat, bef_ent, num_cat.entities[i - num])
                    insight = Insight.BEFORE_N_SPOTS_CROSSCHECK
                    xcheck_marks.append((loc, "X"))

                contradiction = self.add_multi_move(
                    puzzle,
                    xcheck_marks,
                    Insight.BEFORE_N_SPOTS_CROSSCHECK,
                    multi_moves,
                    contradiction,
                )

        if apply:
            self.apply_multi_moves(puzzle, multi_moves)
        return contradiction, multi_moves

    def apply_simple_or(self, puzzle, terms, apply=False):
        """
        Apply the or rule to puzzle, will be incomplete if not enough information is known
        slow: set to True to apply only the first valid insight
        return_steps: return each mark as its own move with the insight
        return: applied, is_valid, complete
        """
        multi_moves = []
        contradiction = False

        pos_cat1 = terms[0]
        pos_ent1 = terms[1]  # either ent1 or ent2 = ans_ent
        pos_cat2 = terms[2]
        pos_ent2 = terms[3]

        ans_cat = terms[4]
        ans_ent = terms[5]

        loc1 = (pos_cat1, ans_cat, pos_ent1, ans_ent)
        loc2 = (pos_cat2, ans_cat, pos_ent2, ans_ent)
        pos_symb1 = puzzle.get_symbol(*loc1)
        pos_symb2 = puzzle.get_symbol(*loc2)

        if pos_symb1 in CONFIDENT_MARKS and pos_symb2 in CONFIDENT_MARKS:
            # both are answered
            if pos_symb1 == pos_symb2:
                # this rule can't be applied (both are true or both are false)
                contradiction = True
            else:
                # This rule is finished
                return contradiction, multi_moves

        if pos_symb1 in CONFIDENT_MARKS or pos_symb2 in CONFIDENT_MARKS:
            insight = Insight.APPLY_OR
            if pos_symb1 == "O":
                # hint says that ent2 cannot be the answer ent
                contradiction = self.add_multi_move(
                    puzzle, [(loc2, "X")], insight, multi_moves, contradiction
                )
            elif pos_symb1 == "X":
                # hint says that ent2 must be the answer ent
                contradiction = self.add_multi_move(
                    puzzle, [(loc2, "O")], insight, multi_moves, contradiction
                )
            elif pos_symb2 == "O":
                # hint says ent1 is not ans_ent
                contradiction = self.add_multi_move(
                    puzzle, [(loc1, "X")], insight, multi_moves, contradiction
                )
            elif pos_symb2 == "X":
                # hint says ent1 is ans_ent and we can change this
                contradiction = self.add_multi_move(
                    puzzle, [(loc1, "O")], insight, multi_moves, contradiction
                )
        else:
            # Both are uncertain
            # we can't apply hint yet (don't have enough information)
            uncertain_marks = []
            insight = Insight.APPLY_OR
            if pos_symb1 == "*" and self.allow_uncertain_moves:
                uncertain_marks.append((loc1, "Y"))

            if pos_symb2 == "*" and self.allow_uncertain_moves:
                uncertain_marks.append((loc2, "Y"))

            contradiction = self.add_multi_move(
                puzzle, uncertain_marks, insight, multi_moves, contradiction
            )

        if pos_cat1 != pos_cat2:
            # A and B are in different categories
            # If A or B is C then A is not B
            insight = Insight.SIMPLE_OR_DIFF_CAT
            loc = (pos_cat1, pos_cat2, pos_ent1, pos_ent2)
            contradiction = self.add_multi_move(
                puzzle, [(loc, "X")], insight, multi_moves, contradiction
            )
        else:
            # A and B are in the same category
            # If A or B from category 0 is C then no other entity from category 0 is C
            insight = Insight.SIMPLE_OR_SAME_CAT
            for ent in pos_cat1.entities:
                if ent not in [pos_ent1, pos_ent2]:
                    loc = (pos_cat1, ans_cat, ent, ans_ent)
                    contradiction = self.add_multi_move(
                        puzzle, [(loc, "X")], insight, multi_moves, contradiction
                    )

        if apply:
            self.apply_multi_moves(puzzle, multi_moves)
        return contradiction, multi_moves

    def apply_compound_or(self, puzzle, options, apply=False):
        """
        Apply the compound or rule to puzzle, will be incomplete if not enough information is known
        return: applied, is_valid, complete
        """
        multi_moves = []
        contradiction = False

        optionA = options[0]
        catA1 = optionA[0]
        entA1 = optionA[1]
        catA2 = optionA[2]
        entA2 = optionA[3]
        locA = (catA1, catA2, entA1, entA2)
        currentA = puzzle.get_symbol(*locA)

        optionB = options[1]
        catB1 = optionB[0]
        entB1 = optionB[1]
        catB2 = optionB[2]
        entB2 = optionB[3]
        locB = (catB1, catB2, entB1, entB2)
        currentB = puzzle.get_symbol(*locB)

        # Convert to simple or if any entities are repeated.
        ans_cat = None
        ans_ent = None
        pos_cat1 = None
        pos_ent1 = None
        pos_cat2 = None
        pos_ent2 = None
        if entA1 in [entB1, entB2] or entA2 in [entB1, entB2]:
            if entA1 in [entB1, entB2]:
                ans_cat = catA1
                ans_ent = entA1
                pos_cat1 = catA2
                pos_ent1 = entA2
            else:
                ans_cat = catA2
                ans_ent = entA2
                pos_cat1 = catA1
                pos_ent1 = entA1

            if ans_ent == entB1:
                pos_cat2 = catB2
                pos_ent2 = entB2
            else:
                pos_cat2 = catB1
                pos_ent2 = entB1
        if ans_ent != None:
            return self.apply_simple_or(
                puzzle,
                [pos_cat1, pos_ent1, pos_cat2, pos_ent2, ans_cat, ans_ent],
                apply,
            )

        if currentA in CONFIDENT_MARKS and currentB in CONFIDENT_MARKS:
            if currentA == currentB:
                contradiction = True
            return contradiction, multi_moves

        if currentA in CONFIDENT_MARKS or currentB in CONFIDENT_MARKS:
            insight = Insight.APPLY_OR

            if currentA == "X":
                contradiction = self.add_multi_move(
                    puzzle, [(locB, "O")], insight, multi_moves, contradiction
                )
            elif currentB == "X":
                contradiction = self.add_multi_move(
                    puzzle, [(locA, "O")], insight, multi_moves, contradiction
                )
            elif currentA == "O":
                contradiction = self.add_multi_move(
                    puzzle, [(locB, "X")], insight, multi_moves, contradiction
                )
            elif currentB == "O":
                contradiction = self.add_multi_move(
                    puzzle, [(locA, "X")], insight, multi_moves, contradiction
                )
        elif self.allow_uncertain_moves:
            uncertain_marks = []
            if currentA == "*":
                uncertain_marks.append((locA, "Y"))
            if currentB == "*":
                uncertain_marks.append((locB, "Y"))

            contradiction = self.add_multi_move(
                puzzle, uncertain_marks, Insight.APPLY_OR, multi_moves, contradiction
            )

        if apply:
            self.apply_multi_moves(puzzle, multi_moves)
        return contradiction, multi_moves

    def apply_hint(self, puzzle, hint, apply=False):
        """
        Given a hint dictionary and a puzzle, apply next step of the hint to the puzzle

        forbidden_insights: insights the solution can't use
        slow: set to True to apply only the first insight for the hint
        return:
        applied  = whether the hint changed the state
        is_valid = whether the hint contradicts the current state
        complete = whether the hint has no more information to offer
        contradiction = the contradiction if the hint is invalid
        insights = the insights required for the move
        """
        contradiction = False
        multi_moves = []

        rule = list(hint.keys())[0]
        terms = hint[rule]
        if rule == "simple_hint":
            rule = list(hint.keys())[0]
        if rule == "is":
            contradiction, multi_moves = self.apply_is(puzzle, terms, apply)
        elif rule == "not":
            contradiction, multi_moves = self.apply_not(puzzle, terms[0]["is"], apply)
        elif rule == "before":
            contradiction, multi_moves = self.apply_before(puzzle, terms, apply)
        elif rule == "simple_or":
            contradiction, multi_moves = self.apply_simple_or(puzzle, terms, apply)
        elif rule == "compound_or":
            contradiction, multi_moves = self.apply_compound_or(
                puzzle, [terms[0]["is"], terms[1]["is"]], apply
            )
        else:
            print(
                "This hint has no apply rules! Something has gone horribly wrong. The offending hint: "
                + Grammar.str_hint(hint)
            )

        return contradiction, multi_moves

    def get_available_moves(self, puzzle, hints, include_forbidden=False):
        """
        get all possible next moves in the solution:
            any openings
            any transitive moves possible in order
            all currently applicable hints and their moves in order
            any insights needed
            if the current board is invalid, get the most salient contradiction (highlight the cell(s) that create the contradiction)
        """
        available_moves = []
        contradiction = False
        o_contradiction, o_moves = self.apply_opening(puzzle)
        for move in o_moves:
            move["hint_idx"] = -3
        contradiction = self.extend_multi_moves(
            o_contradiction, o_moves, contradiction, available_moves
        )
        c_contradiction, c_moves = self.apply_cross_out(puzzle)
        for move in c_moves:
            move["hint_idx"] = -2
        contradiction = self.extend_multi_moves(
            c_contradiction, c_moves, contradiction, available_moves
        )
        t_contradiction, t_moves = self.apply_transitives(puzzle)
        for move in t_moves:
            move["hint_idx"] = -1
        contradiction = self.extend_multi_moves(
            t_contradiction, t_moves, contradiction, available_moves
        )
        for idx, hint in enumerate(hints):
            h_contradiction, h_moves = self.apply_hint(puzzle, hint)
            for move in h_moves:
                move["hint_idx"] = idx
            contradiction = self.extend_multi_moves(
                h_contradiction, h_moves, contradiction, available_moves
            )

        if not include_forbidden:
            without_forbidden = []
            for move in available_moves:
                if move["insight"] not in self.forbidden_insights:
                    without_forbidden.append(move)
            available_moves = without_forbidden
        return contradiction, available_moves

    def get_move_diff(self, before, after, changes_only=True):
        diff = deepcopy(after)
        changed = False
        for cat1 in before.left_right:
            for cat2 in before.top_bottom:
                before_grid = before.get_grid(cat1, cat2)
                after_grid = after.get_grid(cat1, cat2)
                if before_grid is None or after_grid is None:
                    continue
                for ent2_idx in range(0, len(before_grid)):
                    for ent1_idx in range(0, len(before_grid[ent2_idx])):
                        if (
                            before_grid[ent2_idx][ent1_idx]
                            == after_grid[ent2_idx][ent1_idx]
                        ):
                            if not changes_only:
                                diff.answer(
                                    (
                                        cat1,
                                        cat2,
                                        cat1.entities[ent1_idx],
                                        cat2.entities[ent2_idx],
                                    ),
                                    self.lowercase_grid_symbol(
                                        after_grid[ent2_idx][ent1_idx]
                                    ),
                                )
                            else:
                                diff.answer(
                                    (
                                        cat1,
                                        cat2,
                                        cat1.entities[ent1_idx],
                                        cat2.entities[ent2_idx],
                                    ),
                                    "*",
                                )
                        else:
                            changed = True
                            if after_grid[ent2_idx][ent1_idx] == "*":
                                # This is a repair operation
                                diff.answer(
                                    (
                                        cat1,
                                        cat2,
                                        cat1.entities[ent1_idx],
                                        cat2.entities[ent2_idx],
                                    ),
                                    "_",
                                )
        return diff, changed

    def lowercase_grid_symbol(self, S):
        if S == "X":
            return "x"
        elif S == "O":
            return "o"
        elif S == "*" or S == "_":
            return "*"
        elif S == "N":
            return "n"
        elif S == "Y":
            return "y"
        return ""

    # TODO:
    # Make real repair and contradiction detecting functionality
    # Pass in a move chooser function for auto-solving
    # Break down hint applying functions to highlight the insights
    # - maybe have subfunctions for each insight
    # Potentially also pass in an insight DAG instead of just using the class DAG
    # - the DAG itself could be a class? Or it could be represented via a dict as initially
    def fast_forward(self, puzzle, hints):
        """
        solver
        """
        copy = deepcopy(puzzle)
        applied = True
        is_valid = True
        while applied:
            contradiction, available_moves = self.get_available_moves(copy, hints)
            applied = False
            for move in available_moves:
                if move["insight"] not in self.forbidden_insights:
                    if self.apply_multi_move(copy, move):
                        applied = True
            if contradiction:
                is_valid = False

        return copy, is_valid

    def apply_hints(self, puzzle, hints, print_soln=False):
        """
        loop-based solver
        """
        if print_soln:
            print(puzzle)
            print(hints)
        is_valid = True
        copy = deepcopy(puzzle)
        applied = True
        loop = 0
        if len(hints) == 0:
            is_valid = False
            return copy, is_valid, loop

        a_2 = True
        a_3 = True
        a_4 = True
        a_ever = False
        og = deepcopy(copy)
        i = 0
        while is_valid and (a_2 or a_3 or a_4):
            i += 1
            assert i < 1000
            # Apply openings and transitives as many times as you can.
            contradiction, multi_moves = self.apply_opening(copy, True)
            a_2 = len(multi_moves) > 0
            if contradiction:
                if print_soln:
                    print("not valid at first apply_opening")
                is_valid = False

            contradiction, multi_moves = self.apply_cross_out(copy, True)
            a_3 = len(multi_moves) > 0
            if contradiction:
                if print_soln:
                    print("not valid at first apply_cross_out")
                is_valid = False

            contradiction, multi_moves = self.apply_transitives(copy, True)
            a_4 = len(multi_moves) > 0
            if contradiction:
                if print_soln:
                    print("not valid at first apply_transitives")
                is_valid = False

            if a_2 or a_3 or a_4:
                a_ever = True

        if print_soln:
            if a_ever:
                print("applied openings/transitives; ")
                print("updated grid: ")
                move_diff, _ = self.get_move_diff(og, copy, False)
                print(move_diff.print_grid())
            else:
                print(f"No transitives or openings applied initially")
        if not is_valid:
            if print_soln:
                print(f"No longer valid after initial transitives/openings")
            return copy, is_valid, loop

        while is_valid and applied:
            applied = False
            loop += 1
            assert loop < 1000

            for hint in hints:
                str_hint = hint_to_english(hint)
                og = deepcopy(copy)
                contradiction, multi_moves = self.apply_hint(copy, hint, True)
                a = len(multi_moves) > 0
                applied = applied or a
                if not applied and print_soln:
                    print(f"did not apply hint {str_hint}")
                elif print_soln:
                    print("APPLIED HINT: ", hint_to_english(hint))
                if contradiction:
                    is_valid = False
                    if print_soln:
                        print(f"No longer valid after hint {str_hint}")
                    return copy, is_valid, loop

                # Apply additional logic
                a_2 = True
                a_3 = True
                a_4 = True
                a_ever = False
                og = deepcopy(copy)
                i = 0
                while is_valid and (a_2 or a_3 or a_4):
                    i += 1
                    assert i < 1000
                    # Apply openings and transitives as many times as you can.
                    contradiction, multi_moves = self.apply_opening(copy, True)
                    a_2 = len(multi_moves) > 0
                    if contradiction:
                        if print_soln:
                            print(f"not valid at apply_opening after hint {str_hint}")
                        is_valid = False

                    contradiction, multi_moves = self.apply_cross_out(copy, True)
                    a_3 = len(multi_moves) > 0
                    if contradiction:
                        if print_soln:
                            print(f"not valid at apply_cross_out after hint {str_hint}")
                        is_valid = False

                    contradiction, multi_moves = self.apply_transitives(copy, True)
                    a_4 = len(multi_moves) > 0
                    if contradiction:
                        if print_soln or i > 1000:
                            print(
                                f"not valid at apply_transitives after hint {str_hint}"
                            )
                        is_valid = False

                    if a_2 or a_3 or a_4:
                        a_ever = True

                    applied = applied or a_ever  # test if anything was changed
                if not a_ever and print_soln:
                    print(f"No transitives or openings applied after hint {hint}")
                if not is_valid:
                    if print_soln:
                        print(
                            f"No longer valid after transitives/openings after hint {hint}"
                        )
                    return copy, is_valid, loop
                if print_soln and applied:
                    print("hint: ", hint_to_english(hint))
                    print("updated grid: ")
                    move_diff, _ = self.get_move_diff(og, copy, False)
                    print(move_diff.print_grid())

        return copy, is_valid, loop

    def unmissable_insights(self, puzzle, hints):
        if not self.can_solve_without_forbidden(puzzle, hints):
            # The puzzle is incomplete; checking insight needs doesn't make any sense.
            return set()

        unmissables = set()
        all_insights = list(Insight.ALL_INSIGHTS)
        all_insights.sort(reverse=True)
        for insight in all_insights:
            # An insight is also unmissable if the puzzle is unsolvable without its subdag,
            # excluding those insights in its subdag that are already unmissable.
            forbidden = insight.sub_dag() - unmissables
            solver = Solver(forbidden | self.forbidden_insights)
            can_solve_without = solver.can_solve_without_forbidden(puzzle, hints)
            if not can_solve_without:
                unmissables.add(insight)

        return unmissables

    def can_solve_without(self, puzzle, hints, forbidden):
        forbidden_solver = Solver(forbidden)
        completed_puzzle, is_valid = forbidden_solver.fast_forward(puzzle, hints)
        return completed_puzzle.is_complete() and is_valid

    def can_solve_without_forbidden(self, puzzle, hints):
        # expanded_forbidden_insights = set()
        # for insight in self.forbidden_insights:
        #     # If an insight is forbidden, forbid its children as well; don't allow a more complex insight to get around the need for a simple one.
        #     expanded_forbidden_insights.update(insight.sub_dag())
        # forbidden_solver = Solver(expanded_forbidden_insights)
        completed_puzzle, is_valid = self.fast_forward(puzzle, hints)
        return completed_puzzle.is_complete() and is_valid


SOLVER = Solver()
# %%

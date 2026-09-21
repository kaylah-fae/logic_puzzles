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

# %% [markdown]
# # Evolution
#
# An evolutionary Algorithm to evolve logic puzzles

# %%
# !pip install import_ipynb

import ultraimport

ultraimport("__dir__/../LogicPuzzles.py", package="main")

# %%
# Imports Baby
# import import_ipynb
from main.LogicPuzzles import (
    Puzzle,
    Category,
    Solver,
    Insight,
)

ultraimport("__dir__/./ExhaustiveGeneration.py", package="insights")
from insights.ExhaustiveGeneration import ExtGenerator

# from DataVisualization import plot_history
import random
import math
import numpy.random as npr
import pickle
from itertools import combinations
from main.HintToEnglish import hint_to_english
from copy import deepcopy


# %%
def decide(rate):
    return random.random() < rate


# %% [markdown]
# ## Representation
#
# ### Mutation
#
# The following kinds of mutation are implemented:
# 1. Add new clue
# 2. Remove a clue
#
# ### Cross-over
# Randomly add clues to each of children
#
# ### Heuristic
#
# #### Feasibility
# The fesability heuristic is the percentage of empty (unsolved). A valid puzzle is completely filled, but if the clues are incomplete or inlogical the resulting puzzle will have many empty pieces. This assumes that the clues will stop being applied when an invalid clue is attempted.

# The unrestricted solver.
SOLVER = Solver()


class ClueBank:
    def __init__(self, puzzle) -> None:
        self.blank_puzzle = puzzle
        self.clues_by_solution = ExtGenerator.gen_clues_dict(puzzle)

    def get_random_solution_clue_idx(self, solution):
        return random.randint(0, len(self.clues_by_solution[solution]) - 1)

    def get_solution_clues_by_idx(self, solution, clue_idx):
        clues = []
        for i in clue_idx:
            clues.append(self.get_solution_clue_by_idx(solution, i))
        return clues

    def get_solution_clue_by_idx(self, solution, clue_idx):
        return self.clues_by_solution[solution][clue_idx]


# %%
class HintSet:
    def __init__(
        self,
        puzzle,
        solution,
        clue_bank,
        clue_idx,
        required_insights=set(),
        forbidden_insights=set(),
    ) -> None:
        self.blank_puzzle = puzzle  # assumed to be blank (categories only)
        self.solution = solution
        self.clue_bank = clue_bank
        self.clue_idx = clue_idx
        self.required_insights = required_insights
        self.requires_insight = len(self.required_insights) > 0
        self.forbidden_insights = forbidden_insights
        self.forbids_insight = len(self.forbidden_insights) > 0
        self.applied_puzzle, self.valid, self.loops = SOLVER.apply_hints(
            self.blank_puzzle, self.clues()
        )
        # All clues are for the same solution, so the puzzle should always be valid.
        if len(self.clues()) > 0 and not self.valid:
            print("Invalid puzzle!")
            print("Expected solution")
            print(self.solution)
            print("Clues")
            print(self.clues())
            print("Fast-forwarded grid")
            print(self.applied_puzzle.print_grid())
        assert len(self.clues()) == 0 or self.valid

        if len(self.clues()) > 0 and self.applied_puzzle.is_complete():
            self.eliminate_redundant_clues()

    def eliminate_redundant_clues(self):
        clue_idx = set(self.clue_idx)
        new_clue_idx = deepcopy(clue_idx)
        for i in clue_idx:
            new_clue_idx = new_clue_idx - {i}
            new_applied_puzzle, _, _ = SOLVER.apply_hints(
                self.blank_puzzle,
                self.clue_bank.get_solution_clues_by_idx(self.solution, new_clue_idx),
            )
            if not new_applied_puzzle.is_complete():
                new_clue_idx = new_clue_idx | {i}

        ord_clue_idx = []
        for i in self.clue_idx:
            if i in new_clue_idx:
                ord_clue_idx.append(i)

        self.clue_idx = ord_clue_idx

    def clues(self):
        return self.clue_bank.get_solution_clues_by_idx(self.solution, self.clue_idx)

    def size(self):
        return len(self.clue_idx)

    def follows_insight_requirements(self):
        # Should be solvable without the forbidden insights,
        # and should not be solvable without the required insights
        if not (self.requires_insight or self.forbids_insight):
            return True
        # for insight in self.required_insights:
        #     if not insight.validate(
        #         insight.requirements, self.blank_puzzle, self.clues()
        #     ):
        #         return False
        if not self.valid or not self.applied_puzzle.is_complete():
            return True
        can_solve_without_required = False
        can_solve_without_forbidden = True
        
        if len(self.required_insights) > 0:
            solver = Solver()
            unmissable_insights = solver.unmissable_insights(
                self.blank_puzzle, self.clues()
            )
            for required_insight in self.required_insights:
                can_solve_without_required = (
                    can_solve_without_required
                    or required_insight not in unmissable_insights
                )
        if len(self.forbidden_insights) > 0:
            forbidden_solver = Solver(self.forbidden_insights)
            can_solve_without_forbidden = forbidden_solver.can_solve_without_forbidden(
                self.blank_puzzle, self.clues()
            )

        feasible = not can_solve_without_required and can_solve_without_forbidden
        return feasible

    # The set of insights for which the puzzle is not solvable without the sub dags, even with all others available (checked independently)
    def unmissable_insights(self):
        solver = Solver()
        return solver.unmissable_insights(self.blank_puzzle, self.clues())

    def mutate(self, add_rate):
        clue_copy = deepcopy(self.clue_idx)
        roll = random.random()
        if ((roll < add_rate) and len(clue_copy) <= 20) or len(clue_copy) <= 0:
            if len(clue_copy) > 0 and self.applied_puzzle.is_complete():
                index = random.randint(0, len(clue_copy) - 1)
                del clue_copy[index]
            i = 0
            idx = -1
            while (i == 0 or idx in clue_copy) and i < 100:
                idx = self.clue_bank.get_random_solution_clue_idx(self.solution)
                i += 1
            if idx not in clue_copy:
                clue_copy.append(idx)
            else:
                index = random.randint(0, len(clue_copy) - 1)
                del clue_copy[index]
        elif roll < 0.90:
            index = random.randint(0, len(clue_copy) - 1)
            del clue_copy[index]
        else:
            self.swap_clues()

        return HintSet(
            self.blank_puzzle,
            self.solution,
            self.clue_bank,
            clue_copy,
            self.required_insights,
            self.forbidden_insights,
        )

    def swap_clues(self):
        i = random.randint(0, len(self.clue_idx) - 1)
        j = random.randint(0, len(self.clue_idx) - 1)
        temp = self.clue_idx[i]
        self.clue_idx[i] = self.clue_idx[j]
        self.clue_idx[j] = temp

    def cross_over(self, other):
        clue_idx = self.clue_idx[:] + other.clue_idx[:]
        random.shuffle(clue_idx)
        threshold = math.floor(len(clue_idx) / 2)

        return HintSet(
            self.blank_puzzle,
            self.solution,
            self.clue_bank,
            clue_idx[0:threshold],
            self.required_insights,
            self.forbidden_insights,
        ), HintSet(
            self.blank_puzzle,
            self.solution,
            self.clue_bank,
            clue_idx[threshold : len(clue_idx)],
            self.required_insights,
            self.forbidden_insights,
        )

    def get_clue_counts(self):
        total_counts = {
            "is": 0,
            "not": 0,
            "before": 0,
            "simple_or": 0,
            "compound_or": 0,
        }

        for clue in self.clues():
            kind = next(iter(clue))
            total_counts[kind] += 1

        return total_counts

    def clue_ratios(self):
        counts = self.get_clue_counts()
        values = list(counts.values())
        pairs = combinations(counts.keys(), 2)

        diff_sum = 0
        l = 0

        for first, second in pairs:
            diff_sum += abs(counts[first] - counts[second])
            l += 1

        mad = (diff_sum / l) / (sum(values) / len(values))
        return 0.5 * mad

    def is_feasible(self):
        feasible = (
            len(self.clue_idx) > 0
            and self.valid
            and self.applied_puzzle.is_complete()
            and self.follows_insight_requirements()
        )

        return feasible

    def _violations_fun(self, violations):
        if violations > 10:
            return 0
        elif violations <= 0:
            return 1
        else:
            return 1 - (violations / 10)

    def weighted_feasiblility(self, complete_w):
        complete, _ = self.applied_puzzle.percent_complete()

        return complete_w * complete

    # Fitness for infeasible individuals
    def feasibility(self):
        complete, _ = self.applied_puzzle.percent_complete()

        return (0.2 * complete) + (0.8 * int(self.follows_insight_requirements()))

    def solver_loops(self):
        if len(self.clues()) == 0:
            return 0

        return self.loops

    def clue_size(self):
        return len(self.clues())

    def optimize_func(self):
        if len(self.clues()) == 0:
            return 0

        num_loops = self.loops

        # Maximize number of loops (difficulty) and minimize number of clues (redundancy)
        return (0.5 * min(num_loops, 10) / 10) + (0.5 * (1 - (len(self.clues()) / 20)))


class History:
    def __init__(self):
        self.num_feasible = []
        self.feasible_fitness = []
        self.infeasible_fitness = []

    def update_history(self, feasible, infeasible):
        self.num_feasible.append(len(feasible))

        if len(feasible) == 0:
            self.feasible_fitness.append(0)
        else:
            self.feasible_fitness.append(feasible[0][0])

        if len(infeasible) == 0:
            self.infeasible_fitness.append(0)
        else:
            self.infeasible_fitness.append(infeasible[0][0])


# %%
def random_clue_set(
    puzzle: Puzzle,
    clue_bank: ClueBank,
    solution: str,
    required_insights=set(),
    forbidden_insights=set(),
):
    num = random.randint(1, 5)
    clue_idx = []
    i = 0
    len = 0
    while i < 100 and len < num:
        idx = clue_bank.get_random_solution_clue_idx(solution)
        if idx not in clue_idx:
            clue_idx.append(idx)
            len += 1
        i += 1

    return HintSet(
        puzzle, solution, clue_bank, clue_idx, required_insights, forbidden_insights
    )


# %% [markdown]
# ## Evolution

# %%


def select(population):
    m = sum([c[0] for c in population])
    if m == 0:
        selection_probs = [1 / len(population) for _ in population]
    else:
        selection_probs = [c[0] / m for c in population]
    return population[npr.choice(len(population), p=selection_probs)]


# %%
def _add_child(clues, feasible, infeasible):
    """
    if clue set is valid, add to feasible pop with optmiziation fitness,
    otherwise add to infeasible pop with feasibility fitness
    """
    if clues.is_feasible():
        fitness = clues.optimize_func()
        feasible.append((fitness, clues))
    else:
        fitness = clues.feasibility()
        infeasible.append((fitness, clues))


def evolve(
    puzzle,
    solution,
    generations,
    pop_size,
    x_rate,
    mut_rate,
    add_rate,
    elits,
    required_insights=set(),
    forbidden_insights=set(),
):
    feasible = []
    infeasible = []
    history = History()

    print("initializing...")

    clue_bank = ClueBank(puzzle)
    # Create initial population
    for _ in range(pop_size):
        clues = random_clue_set(
            puzzle, clue_bank, solution, required_insights, forbidden_insights
        )
        _add_child(clues, feasible, infeasible)
        print(f"added child with clues {clues}")

    print(f"generations: {generations}")
    for gen in range(generations):

        new_feasible = []
        new_infeasible = []

        feasible.sort(reverse=True, key=lambda a: a[0])
        infeasible.sort(reverse=True, key=lambda a: a[0])

        history.update_history(feasible, infeasible)

        if gen % 50 == 0:
            print("-" * 40)
            print("GENERATION " + str(gen))
            print("-" * 80)
            if len(infeasible) > 0:
                print("Infeasible")
                print(infeasible[0])
                print(infeasible[0][1].completed_puzzle.print_grid())
                print(infeasible[0][1].completed_puzzle.num_violations())
            if len(feasible) > 0:
                print("feasible:")
                print(feasible[0])
                print(feasible[0][1].completed_puzzle.print_grid())
            print("-" * 80)

        # elitism
        if len(feasible) > 0:
            new_feasible = feasible[:elits]
        if len(infeasible) > 0:
            new_infeasible = infeasible[:elits]

        print("add to pop?")
        # create new population
        while len(new_feasible) + len(new_infeasible) < pop_size:
            print("needs add to pop")
            # Selection
            # Not clear to me how to choose which pop to select from,
            # right now am deciding randomly based on size of two pops

            if decide(len(feasible) / (len(feasible) + len(infeasible))):
                # selecting from feasible
                indiv1 = select(feasible)[1]
                indiv2 = select(feasible)[1]
            else:
                indiv1 = select(infeasible)[1]
                indiv2 = select(infeasible)[1]

            # cross over
            if decide(x_rate):
                print("xover")
                indiv1, indiv2 = indiv1.cross_over(indiv2)

            # mutation
            if decide(mut_rate):
                print("mutate")
                child1 = indiv1.mutate(add_rate)
                child2 = indiv2.mutate(add_rate)
            else:
                print("keep as is")
                child1 = indiv1
                child2 = indiv2

            # add children
            _add_child(child1, new_feasible, new_infeasible)

            if len(new_feasible) + len(new_infeasible) < pop_size:
                _add_child(child2, new_feasible, new_infeasible)

        feasible = new_feasible
        infeasible = new_infeasible
    for child in feasible:
        solver = Solver(required_insights | forbidden_insights)
        assert not solver.can_solve_without_forbidden(
            child.puzzle, child.clues
        ), "can solve without required insights: {}".format(required_insights)
        solver = Solver(forbidden_insights)
        assert solver.can_solve_without_forbidden(
            child.puzzle, child.clues
        ), "can't solve without forbidden insights {}".format(forbidden_insights)
    return feasible, infeasible, history


# %%
if __name__ == "__main__":
    suspects = Category("suspect", ["Scarlet", "White", "Mustard", "Plum"], False)
    weapons = Category("weapon", ["Knife", "Rope", "Candle Stick", "Wrench"], False)
    rooms = Category("room", ["Ball room", "Living Room", "Kitchen", "Study"], False)
    time = Category("hour", ["1:00", "2:00", "3:00", "4:00"], True)

    puzzle = Puzzle([suspects, weapons, rooms, time])

    pop = evolve(
        puzzle, 100, 50, 0.2, 1, 0.5, 2, required_insights=Insight.ALL_INSIGHTS
    )

    file = open("InsightExp/pop.p", "wb")
    pickle.dump(pop, file)
    feasible = pop[0]
    infeasible = pop[1]
    history = pop[2]

    print(feasible)
    print(feasible[0][1].completed_puzzle.print_grid())
    print(len(feasible[0][1].clues))
    print([hint_to_english(clue) for clue in feasible[0][1].clues])
    print("\n\n")
    print(infeasible)
    # plot_history(history, "Insight_Exp")
    """clues = random_clue_set(puzzle) 
    for clue in clues.clues:
        print(clue)
    
    print(clues.clue_ratios())"""

# %%
# if __name__ == "__main__":
#     file = open("Experiement1/pop1.p", "wb")
#     pickle.dump(pop, file)
#     feasible = pop[0]
#     infeasible = pop[1]
#     history = pop[2]

#     print(feasible)
#     print(feasible[0][1].completed_puzzle.print_grid())
#     print(len(feasible[0][1].clues))
#     print([hint_to_english(clue) for clue in feasible[0][1].clues])
#     print("\n\n")
#     print(infeasible)
#     plot_history(history, "Experiement1")

import random
import ultraimport
from copy import deepcopy

ultraimport("__dir__/../LogicPuzzles.py", package="main")
from main.LogicPuzzles import Solver, Insight

class PuzzleAgent:
    Agents = {}
    def __init__(self, name, solver, choose_fn, random_fn):
        self.name = name
        self.solver = solver
        self.choose_fn = choose_fn
        self.random_fn = random_fn
        PuzzleAgent.Agents[name] = self
        pass

    def choose(self, available_moves, curr_state, solution):
        if len(available_moves) == 0:
            return self.random_fn(curr_state, solution)
        return self.choose_fn(available_moves)
    
    def play_puzzle(self, puzzle, solution, hints):
        curr_state = deepcopy(puzzle)
        history = []
        pct_complete, _ = curr_state.percent_complete()
        i = 0
        while pct_complete < 1 and i < 100000:
            _, available_moves = self.solver.get_available_moves(curr_state, hints)
            chosen_move = self.choose(available_moves, curr_state, solution)
            history.append(chosen_move)
            self.solver.apply_multi_move(curr_state, chosen_move)
            i += 1
            pct_complete, _ = curr_state.percent_complete()
        pct_complete, _ = curr_state.percent_complete()
        if pct_complete < 1:
            print("------error getting to complete puzzle------")
            print(pct_complete)
            print(curr_state.print_grid())
            print(curr_state.percent_complete())
            print("------------")
        return history

    # Choose the first move from the available_moves.
    def choose_order(available_moves):
        return available_moves[0]

    # Of the available_moves, chooses the first easiest move.
    def choose_easiest(available_moves):
        easiest = available_moves[0]
        for move in available_moves:
            if move["insight"] < easiest["insight"]:
                easiest = move
        return easiest

    # Of the available_moves, chooses the first hardest move.
    def choose_hardest(available_moves):
        hardest = available_moves[0]
        for move in available_moves:
            if move["insight"] > hardest["insight"]:
                hardest = move
        return hardest

    # Of the available moves, chooses at random.
    def choose_random(available_moves):
        return random.choice(available_moves)
    
    def _format_rand_move(move):
        return {
            "insight": None,
            "moves": [move],
            "repair": False,
            "hint_idx": None,
        }

    # Randomly selects a blank spot on the board to fill with the correct value.
    def random_correct(curr_state, solution):
        loc = PuzzleAgent._rand_blank(curr_state)
        sy = solution.get_symbol(*loc)
        return PuzzleAgent._format_rand_move((loc, sy))

    # Randomly selects a blank spot on the board to fill with 1/4 chance of selecting an O.
    def random_probabilistic(curr_state, _):
        loc = PuzzleAgent._rand_blank(curr_state)
        decider = random.random()
        sy = "X"
        if decider < .25:
            sy = "O"
        return PuzzleAgent._format_rand_move((loc, sy))

    # Randomly selects a blank spot on the board to fill with 1/2 chance of selecting an O
    def random_random(curr_state, _):
        loc = PuzzleAgent._rand_blank(curr_state)
        sy = random.choice(["X", "O"])
        return PuzzleAgent._format_rand_move((loc, sy))

    def _rand_loc(puzzle):
        cats = puzzle.categories

        cat1 = random.choice(cats)
        cat2 = random.choice(cats)
        while cat2 == cat1:
            cat2 = random.choice(cats)
        
        ent1 = random.choice(cat1.entities)
        ent2 = random.choice(cat2.entities)
        
        return (cat1, cat2, ent1, ent2)

    def _rand_blank(curr_state):
        loc = PuzzleAgent._rand_loc(curr_state)
        i = 0
        while curr_state.get_symbol(*loc) != "*" and i < 100000:
            loc = PuzzleAgent._rand_loc(curr_state)
            i += 1
        if curr_state.get_symbol(*loc) != "*":
            print(("------no suitable blank found------"))
            print(curr_state.print_grid())
            print(curr_state.percent_complete())
            print("------------")
        return loc

Solver__NoInsights = Solver(Insight.ALL_INSIGHTS)
Solver__CrossOpenOnly = Solver(Insight.ALL_INSIGHTS - {Insight.CROSS_OUT, Insight.OPENING})
Solver__GridRulesOnly = Solver(Insight.ALL_INSIGHTS - {Insight.CROSS_OUT, Insight.OPENING, Insight.TRANS_ABC_TRUE})
Solver__CrossOpenBasicOnly = Solver(Insight.ALL_INSIGHTS - {Insight.CROSS_OUT, Insight.OPENING, Insight.APPLY_IS, Insight.APPLY_NOT, Insight.APPLY_OR, Insight.APPLY_BEFORE_ONE_SPOT, Insight.APPLY_BEFORE_N_SPOTS, Insight.APPLY_BEFORE_UNDEFINED_SPOTS})
Solver__GridRulesBasicOnly = Solver(Insight.ALL_INSIGHTS - {Insight.CROSS_OUT, Insight.OPENING, Insight.APPLY_IS, Insight.APPLY_NOT, Insight.APPLY_OR, Insight.APPLY_BEFORE_ONE_SPOT, Insight.APPLY_BEFORE_N_SPOTS, Insight.APPLY_BEFORE_UNDEFINED_SPOTS, Insight.TRANS_ABC_TRUE})

PuzzleAgent__RandomCorrect = PuzzleAgent("RandomCorrect", Solver__NoInsights, PuzzleAgent.choose_random, PuzzleAgent.random_correct)
PuzzleAgent__RandomProb = PuzzleAgent("RandomProb", Solver__NoInsights, PuzzleAgent.choose_random, PuzzleAgent.random_probabilistic)
PuzzleAgent__CrossOpenOnly = PuzzleAgent("CrossOpenOnly", Solver__CrossOpenOnly, PuzzleAgent.choose_random, PuzzleAgent.random_probabilistic)
PuzzleAgent__GridRulesOnly = PuzzleAgent("GridRulesOnly", Solver__GridRulesOnly, PuzzleAgent.choose_random, PuzzleAgent.random_probabilistic)
PuzzleAgent__CrossOpenBasicOnly = PuzzleAgent("CrossOpenBasicOnly", Solver__CrossOpenBasicOnly, PuzzleAgent.choose_random, PuzzleAgent.random_probabilistic)
PuzzleAgent__GridRulesBasicOnly = PuzzleAgent("GridRulesBasicOnly", Solver__GridRulesBasicOnly, PuzzleAgent.choose_random, PuzzleAgent.random_probabilistic)
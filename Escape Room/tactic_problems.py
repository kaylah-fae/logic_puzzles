import ultraimport
import random

from tactics_defs import PUZZLE_DEFS

ultraimport("__dir__/../LogicPuzzles.py", package="main")
from main.LogicPuzzles import Solver, Insight

ultraimport("__dir__/../Insights/SolutionMapEliteGeneration.py", package="insights")
from insights.SolutionMapEliteGeneration import map_elite_generate
from insights.SolutionMapElitesVisualization import (
    write_hint_files,
    heat_map,
    get_agg_children_grids,
    get_agg_hint_grids,
    write_summary_json_files,
)
from insights.ExhaustiveGeneration import ExtGenerator

SOLVER = Solver(set(), True)

# 1. APPLY_OR
# 2. APPLY_BEFORE_N_SPOTS
# 3. BEFORE_N_SPOTS_CROSSCHECK
# 4. BEFORE_N_SPOTS_NOINFO

if __name__ == "__main__":
    puzzle_ids = [
        # "games",
        # "birth",
        # "colors",
        # "classes",
        "classes_hub"
    ]

    PUZZLE_DEFS["colors"]["required"] = {Insight.APPLY_OR}
    PUZZLE_DEFS["colors"]["also_allowed"] = set()
    solutions = ExtGenerator.generate_all_solutions(PUZZLE_DEFS["colors"]["puzzle"])
    PUZZLE_DEFS["colors"]["solution"] = random.choice(solutions).print_grid()

    PUZZLE_DEFS["classes"]["required"] = {Insight.APPLY_BEFORE_N_SPOTS}
    PUZZLE_DEFS["classes"]["also_allowed"] = set()
    solutions = ExtGenerator.generate_all_solutions(PUZZLE_DEFS["classes"]["puzzle"])
    PUZZLE_DEFS["classes"]["solution"] = random.choice(solutions).print_grid()

    PUZZLE_DEFS["classes_hub"]["required"] = {Insight.BEFORE_N_SPOTS_NOINFO, Insight.SIMPLE_OR_DIFF_CAT}
    PUZZLE_DEFS["classes_hub"]["also_allowed"] = {Insight.SIMPLE_OR_SAME_CAT, Insight.BEFORE_NOINFO, Insight.APPLY_BEFORE_N_SPOTS, Insight.APPLY_OR}
    solutions = ExtGenerator.generate_all_solutions(PUZZLE_DEFS["classes_hub"]["puzzle"])
    PUZZLE_DEFS["classes_hub"]["solution"] = random.choice(solutions).print_grid()

    PUZZLE_DEFS["games"]["required"] = {Insight.BEFORE_N_SPOTS_NOINFO}
    PUZZLE_DEFS["games"]["also_allowed"] = {Insight.APPLY_BEFORE_N_SPOTS}
    solutions = ExtGenerator.generate_all_solutions(PUZZLE_DEFS["games"]["puzzle"])
    PUZZLE_DEFS["games"]["solution"] = random.choice(solutions).print_grid()
   
    PUZZLE_DEFS["birth"]["required"] = {Insight.BEFORE_N_SPOTS_CROSSCHECK}
    PUZZLE_DEFS["birth"]["also_allowed"] = {Insight.APPLY_BEFORE_N_SPOTS, Insight.BEFORE_N_SPOTS_NOINFO}
    solutions = ExtGenerator.generate_all_solutions(PUZZLE_DEFS["birth"]["puzzle"])
    PUZZLE_DEFS["birth"]["solution"] = random.choice(solutions).print_grid()

    always_allowed = {
        Insight.APPLY_IS,
        Insight.CROSS_OUT,
        Insight.OPENING,
        Insight.APPLY_NOT,
    }
    always_forbidden = {
        Insight.TRANS_SETS,
        Insight.BEFORE_N_SPOTS_SHIFT,
        Insight.TRANS_ABC_FALSE,
        Insight.SIMPLE_OR_DIFF_CAT,
        Insight.BEFORE_DIFF_CAT,
    }

    for puzzle_id in puzzle_ids:
        puzzle_info = PUZZLE_DEFS[puzzle_id]

        # puzzle_info["forbidden"] = (
        #     Insight.ALL_INSIGHTS - puzzle_info["required"] - always_allowed
        # )
        puzzle_info["forbidden"] = set()
        puzzle_info = PUZZLE_DEFS[puzzle_id]

        print(
            f"Generate new puzzles for {puzzle_id} with required insights {puzzle_info['required']} and forbidden {puzzle_info['forbidden']}"
        )
        folder = f"GenTacticsProblems/{puzzle_id}"

        starting = 0
        num_trials = 1
        gen_len = 100
        pop_size = 1000
        cell_capacity = 10
        mut_rate = 0.8
        x_rate = 0.6
        add_rate = 0.5
        elits = 100

        grid = map_elite_generate(
            puzzle_info["puzzle"],
            puzzle_info["solution"],
            folder,
            starting,
            num_trials,
            gen_len,
            pop_size,
            mut_rate,
            x_rate,
            add_rate,
            elits,
            required_insights=puzzle_info["required"],
            forbidden_insights= (always_forbidden - puzzle_info["also_allowed"]) | puzzle_info["forbidden"],
        )

        write_hint_files(folder, num_trials)
        agg_grid = get_agg_hint_grids(folder, num_trials)
        heat_map(
            agg_grid,
            True,
            title="Average Hint Size by Cell",
            ylabel="Gini Coefficent",
            xlabel="Solver loops",
            colorbar_label="Average Hint Size",
            vmin=3,
            savefile=f"{folder}/hintsize_heatmap.png",
        )

        agg_total_grid = get_agg_children_grids(folder, num_trials)
        heat_map(
            agg_total_grid,
            False,
            title="Average Children Produced by Cell",
            ylabel="Gini Coefficent",
            xlabel="Solver loops",
            colorbar_label="Average Children Produced",
            savefile=f"{folder}/children_heatmap.png",
        )

        write_summary_json_files(folder, num_trials)
        print(f"finished generating and saving puzzles for {puzzle_id}")

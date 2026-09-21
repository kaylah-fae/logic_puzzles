from MapElites import evolve
from LogicPuzzles import Puzzle, Category, Insight
import jsonpickle
import random

shapes = Category("shapes", ["Elbow", "Bowtie", "Linguine", "Shell"], False)
# sauces = Category("sauces", ["Tomato", "Alfredo", "Pesto", "Carbonara"], False)
plate = Category("order", ["1", "2", "3", "4"], True)
pasta = Puzzle([shapes, plate])

mL = Category("mL", ["20oz", "40oz", "60oz", "80oz"], True)
plants = Category("plant", ["Potatoes", "Green Onions", "Eggplant", "Broccoli"], False)
water = Puzzle([mL, plants])

order = Category("order", ["1st", "2nd", "3rd", "4th"], True)
method = Category("method", ["whole", "halved", "chopped", "mashed"], False)
ingredient = Category(
    "ingredient", ["Potatoes", "Carrots", "Mushrooms", "Onions"], False
)

soup = Puzzle([order, method, ingredient])

experiments = [
    # {
    #     "folder": "NewEscape/PastaNum",
    #     "puzzle": pasta,
    #     "required_insights": {Insight.APPLY_BEFORE_N_SPOTS},
    #     "forbidden_insights": {
    #         Insight.BEFORE_N_SPOTS_NOINFO,
    #         Insight.BEFORE_N_SPOTS_SHIFT,
    #         Insight.TRANS_ABC_FALSE,
    #         Insight.SIMPLE_OR_DIFF_CAT,
    #         Insight.SIMPLE_OR_SAME_CAT,
    #     },
    # },
    # {
    #     "folder": "NewEscape/PastaNumOR",
    #     "puzzle": pasta,
    #     "required_insights": {Insight.APPLY_BEFORE_N_SPOTS, Insight.APPLY_OR},
    #     "forbidden_insights": {
    #         Insight.BEFORE_N_SPOTS_NOINFO,
    #         Insight.BEFORE_N_SPOTS_SHIFT,
    #         Insight.TRANS_ABC_FALSE,
    #         Insight.SIMPLE_OR_DIFF_CAT,
    #         Insight.SIMPLE_OR_SAME_CAT,
    #     },
    # },
    # {
    #     "folder": "NewEscape/WaterOR",
    #     "puzzle": water,
    #     "required_insights": {
    #         Insight.BEFORE_N_SPOTS_NOINFO,
    #         Insight.SIMPLE_OR_SAME_CAT,
    #     },
    #     "forbidden_insights": {Insight.BEFORE_N_SPOTS_SHIFT, Insight.TRANS_ABC_FALSE, Insight.SIMPLE_OR_DIFF_CAT},
    # },
    {
        "folder": "NewEscape/SoupSimple",
        "puzzle": soup,
        "required_insights": {
            Insight.BEFORE_N_SPOTS_NOINFO, Insight.SIMPLE_OR_DIFF_CAT,
        },
        "forbidden_insights": set(),
    },
]


starting = 0
num_trials = 1
gen_len = 100
pop_size = 300
mut_rate = 0.8
x_rate = 0.6
add_rate = 0.5
elits = 10

for experiment in experiments:
    folder = experiment["folder"]
    puzzle = experiment["puzzle"]
    required_insights = experiment["required_insights"]
    forbidden_insights = experiment["forbidden_insights"]
    for trial in range(starting, num_trials):
        random.seed(trial)
        print("Starting Trial:{}".format(trial))
        elit_grid, infeasible, history = evolve(
            puzzle,
            gen_len,
            pop_size,
            x_rate,
            mut_rate,
            add_rate,
            elits,
            required_insights=required_insights,
            forbidden_insights=forbidden_insights,
        )

        elite_json = jsonpickle.encode(elit_grid)
        elite_file = open(folder + "/map_grid_trial_{}.p".format(trial), "w")
        elite_file.write(elite_json)
        elite_file.close()

        history_json = jsonpickle.encode(history)
        history_file = open(folder + "/history_trial_{}.p".format(trial), "w")
        history_file.write(history_json)
        history_file.close()

        unfes_json = jsonpickle.encode(infeasible)
        unfes_file = open(folder + "/unfeasibles_trial_{}.p".format(trial), "w")
        unfes_file.write(unfes_json)
        unfes_file.close()

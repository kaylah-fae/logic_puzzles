import ultraimport

ultraimport("__dir__/../LogicPuzzles.py", package="main")
from main.LogicPuzzles import Category, Puzzle, Solver

PUZZLE_DEFS = {}

# Sunlight puzzle
HOTEL_DISTANCE = Category("distance", ["1 mi", "3 mi", "5 mi", "10 mi"], True)
HOTEL_NAME = Category(
    "hotel", ["Plaza", "Park", "Inn", "Royal"], False
)
hotel_puzzle = Puzzle([HOTEL_DISTANCE, HOTEL_NAME])

hotel_hints = [
    {"is": [HOTEL_NAME, "Park", HOTEL_DISTANCE, "5 mi"]},
    {"is": [HOTEL_NAME, "Inn", HOTEL_DISTANCE, "3 mi"]},
    {
        "before": [
            HOTEL_NAME,
            "Royal",
            HOTEL_NAME,
            "Inn",
            HOTEL_DISTANCE,
        ]
    },
]
PUZZLE_DEFS["hotel"] = {"puzzle": hotel_puzzle, "hints": hotel_hints}

RACE_NAME = Category("name", ["Patty", "Jon", "Matt", "Candace"], False)
RACE_TIME = Category("time", ["20 min", "40 min", "60 min", "80 min"], True)
race_puzzle = Puzzle([RACE_NAME, RACE_TIME])
race_hints = [
    {
        "before": [
            RACE_NAME,
            "Jon",
            RACE_NAME,
            "Candace",
            RACE_TIME,
        ]
    },
    {"is": [RACE_NAME, "Matt", RACE_TIME, "80 min"]},
    {
        "before": [
            RACE_NAME,
            "Patty",
            RACE_NAME,
            "Matt",
            RACE_TIME,
            1
        ]
    },
]
PUZZLE_DEFS["race"] = {"puzzle": race_puzzle, "hints": race_hints}

ICECREAM_NAME = Category("name", ["Anne", "Bob", "Carrie", "Dylan"], False)
ICECREAM_SCOOPS = Category("scoops", [1, 2, 3, 5], True)
icecream_puzzle = Puzzle([ICECREAM_NAME, ICECREAM_SCOOPS])
icecream_hints = [
    {"simple_or": [ICECREAM_SCOOPS, 3, ICECREAM_SCOOPS, 5, ICECREAM_NAME, "Anne"]},
    {"not": [{"is": [ICECREAM_NAME, "Bob", ICECREAM_SCOOPS, 2]}]},
    {"compound_or": [
        {"is": [ICECREAM_NAME, "Anne", ICECREAM_SCOOPS, 1]},
        {"is": [ICECREAM_NAME, "Dylan", ICECREAM_SCOOPS, 5]},
    ]}
]
PUZZLE_DEFS["icecream"] = {"puzzle": icecream_puzzle, "hints": icecream_hints}

SOLVER = Solver()
if __name__ == "__main__":
    
    for name, info in PUZZLE_DEFS.items():
        print(f"unmissable insights for {name}:")
        print(SOLVER.unmissable_insights(info["puzzle"], info["hints"]))
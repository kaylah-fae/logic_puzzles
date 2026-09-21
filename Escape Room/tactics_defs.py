import ultraimport

ultraimport("__dir__/../LogicPuzzles.py", package="main")
from main.LogicPuzzles import Category, Puzzle

PUZZLE_DEFS = {}

# Class Puzzle
TIMES = Category("times", ["1pm", "2pm", "3pm", "4pm"], True)
CLASSES = Category(
    "class", ["Math", "Science", "English", "History"], False
)
class_puzzle = Puzzle([TIMES, CLASSES])
PUZZLE_DEFS["classes"] = {"puzzle": class_puzzle}

# Game Puzzle
ORDER = Category("order", ["1st", "2nd", "3rd", "4th"], True)
GAMES = Category(
    "game", ["Soccer", "Baseball", "Volleyball", "Tennis"], False
)
game_puzzle = Puzzle([ORDER, GAMES])
PUZZLE_DEFS["games"] = {"puzzle": game_puzzle}

# Game Puzzle
YEAR = Category("year", ["2000", "2001", "2002", "2003"], True)
PERSON = Category(
    "person", ["Kevin", "Lucy", "Mark", "Sarah"], False
)
birth_puzzle = Puzzle([YEAR, PERSON])
PUZZLE_DEFS["birth"] = {"puzzle": birth_puzzle}

# Color Puzzle
PEOPLE = Category("people", ["Alan", "Mary", "John", "Sue"], False)
COLORS = Category(
    "color", ["Red", "Green", "Yellow", "Blue"], False
)
color_puzzle = Puzzle([PEOPLE, COLORS])
PUZZLE_DEFS["colors"] = {"puzzle": color_puzzle}

# Class Puzzle
TIMES = Category("times", ["1pm", "2pm", "3pm", "4pm"], True)
CLASSES = Category(
    "class", ["Math", "Science", "English", "History"], False
)
TEACHERS = Category("teacher", ["Roberts", "Smith", "MacDonald", "Andrews"], False)
class_hub_puzzle = Puzzle([TIMES, CLASSES, TEACHERS])
PUZZLE_DEFS["classes_hub"] = {"puzzle": class_hub_puzzle}
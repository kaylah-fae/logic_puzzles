from LogicPuzzles import Insight, Category
from HintToEnglish import hint_to_english

suspects = Category("suspect", ["Scarlet", "Plum", "Peacock", "White", "Boddy", "Green"], False)
weapons = Category("weapon", ["candlestick", "revolver", "wrench", "rope", "lead pipe", "poison"], False)
rooms = Category("room", ["Library", "Conservatory", "Dining Room", "Study", "Ballroom", "Salon"], False)
times = Category("time", ["6PM", "7PM", "8PM", "9PM", "10PM", "11PM"], True)

categories = [suspects, weapons, rooms, times]

if __name__ == "__main__":
    tactics = list(Insight.ALL_INSIGHTS)
    tactics.sort()
    for tactic in tactics:
        print("----------------------------")
        print(tactic)
        tactic_puzzle, tactic_hints = tactic.gen_min_puzzle(categories)
        print(tactic_puzzle)
        print([hint_to_english(hint) for hint in tactic_hints])
        print("----------------------------")
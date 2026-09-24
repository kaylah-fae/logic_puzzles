import pandas as pd 
import  matplotlib.pyplot as plt 
import json 
import statistics
import statsmodels.api as sm 
from statsmodels.formula.api import ols  
from statsmodels.stats.multicomp import pairwise_tukeyhsd 

action_file = open("action_data.json", "r")
action_data = json.loads(action_file.read())


hub_file = open("one_loop_puzzle1.json", "r")
hub1_data = json.loads(hub_file.read())

hub_file = open("one_loop_puzzle2.json", "r")
hub2_data = json.loads(hub_file.read())

hub_file = open("one_loop_puzzle3.json", "r")
hub3_data = json.loads(hub_file.read())

def get_last_cell_change(actions):

    cell_changes = [a for a in actions if a["type"] == "cellChange"]
    if len(cell_changes) ==  0:
        return None , False
    return cell_changes[-1]["puzzleState"], cell_changes[-1]["correct"]

def num_questions(id):
    if  not id in action_data:

        return 0 
    actions = action_data[id]

    if len(actions)  == 0:
        return  0 

    last_state , correct = get_last_cell_change(actions)

    if last_state is None:
        return 0 

    qs = last_state.count("!")
    qs += last_state.count("?")

    return qs 

def number_correct_truths(id, pid):
    if  not id in action_data:

        return 0 
    actions = action_data[id]

    if len(actions)  == 0:
        return  0 
    last_state , correct = get_last_cell_change(actions)

    if last_state is None:
        return 0 

    if  '2.1' in pid:
        solution = hub1_data["solution"]
    elif '2.2' in pid: 
        solution = hub2_data["solution"]
    else: 
        solution = hub3_data["solution"]

    numCorr = 0 
    i = 0 
    for c in last_state:
        if c == "O":
            if solution[i] == "O":
                numCorr += 1 
    
        i += 1
    

    return  numCorr




gameplay_data = pd.read_csv("gameplay_data.csv")

gameplay_data["totalTime"] = pd.to_numeric(gameplay_data["totalTime"], errors="coerce")

gameplay_data["minutes"] = gameplay_data["totalTime"] / 1000 / 60 






diff_questions = ["The puzzle was cognitively demanding.", "I had to think very hard when playing the puzzle.",
    "The puzzle required a lot of mental gymnastics.", "The puzzle stimulated my brain.", 
    "The puzzle made me draw on all of my mental resources.", "The mental challenges in this puzzle had an impact on how I played.",
]

diff_reverse = [ "This puzzle doesn’t require a lot of mental effort."]

con_questions = [ 
    "I think I am pretty good at this activity", 
    "I think I did pretty well at this activity, compared to other people", 
    "After working at this activity for awhile, I felt pretty competent", 
    "I am satisfied with my performance at this task",
    "I was pretty skilled at this activity"]

con_reversed = ["This was an activity that I couldn't do very well"]

diffs = [] 
cons = [] 
qs = []
for index, row in gameplay_data.iterrows():

    diff_sum = 0 
    for q in diff_questions:
        diff_sum += row[q]

    for q in diff_reverse:
        value = row[q]
        diff_sum += 8 - value


    con_sum = 0 
    for q in con_questions:
        con_sum += row[q]

    for q in con_reversed: 
        con_sum += 8 - row[q] 
    
    diffs.append(diff_sum / (len(diff_questions) + len(diff_reverse)))
    cons.append(con_sum / (len(con_questions) + len(con_reversed)))

    qs.append(num_questions(row["_id"]))



gameplay_data['condition'] =gameplay_data["levelMode"]  + "-" + gameplay_data["promptMode"]
gameplay_data["perceivedDiff"] = diffs 
gameplay_data["perceivedCon"] = cons
gameplay_data["unsureMarks"] = qs




hub_puzzles = gameplay_data[gameplay_data["pid"].str.contains('hub')]

numTruths = []
diffs = [] 
cons = [] 
for index, row in hub_puzzles.iterrows():
    numTruths.append(number_correct_truths(row["_id"],row["pid"])) 




hub_puzzles["numTruths"]  = numTruths

hub_puzzles["totalMarks"] = hub_puzzles["numCorrect"] + hub_puzzles["numIncorrect"]


solved_hubs = hub_puzzles[hub_puzzles["isSolved"] == True]


print(gameplay_data.groupby("pid")["perceivedCon"].mean())


groups = hub_puzzles.groupby("promptMode")

print(groups.size())

print("\n\nUnsureMarks")
print(groups["unsureMarks"].mean())


print("\n\nConfidence")
print(groups["perceivedCon"].mean())

print("\n\nDifficulty")
print(groups["perceivedDiff"].mean())

print("\n\nNumber Correct")
print(groups["numCorrect"].mean())

print("\n\nIs Solved")
print(groups["isSolved"].mean())

print("\n\nNumber Incorrect")
print(groups["numIncorrect"].mean())

print("\n\nNumber Truths")
print(groups["numTruths"].mean())

print("\n\nNumber of Marks")
print(groups["totalMarks"].mean())

print("\n\nTime")
print(groups["minutes"].mean())



"""print("Perceived Difficulty anova")
cw_lm=ols('perceivedDiff ~ C(promptMode) + C(levelMode) + C(promptMode):C(levelMode)', data=hub_puzzles).fit() #Specify C for Categorical
print(sm.stats.anova_lm(cw_lm, typ=2))

tukey = pairwise_tukeyhsd(endog=hub_puzzles["perceivedDiff"],
                          groups=hub_puzzles["condition"],
                          alpha=0.05)
print(tukey)

print("Puzzle Success anova")
cw_lm=ols('numTruths ~ C(promptMode) + C(levelMode) + C(promptMode):C(levelMode)', data=hub_puzzles).fit() #Specify C for Categorical
print(sm.stats.anova_lm(cw_lm, typ=2))

tukey = pairwise_tukeyhsd(endog=hub_puzzles["numTruths"],
                          groups=hub_puzzles["condition"],
                          alpha=0.05)
print(tukey)

print("Perceived Confidence anova")
cw_lm=ols('perceivedCon ~ C(promptMode) + C(levelMode) + C(promptMode):C(levelMode)', data=hub_puzzles).fit() #Specify C for Categorical
print(sm.stats.anova_lm(cw_lm, typ=2))

tukey = pairwise_tukeyhsd(endog=solved_hubs["perceivedCon"],
                          groups=solved_hubs["condition"],
                          alpha=0.05)
print(tukey)

print("Number Incorrect anova")
cw_lm=ols('numIncorrect ~ C(promptMode) + C(levelMode) + C(promptMode):C(levelMode)', data=hub_puzzles).fit() #Specify C for Categorical
print(sm.stats.anova_lm(cw_lm, typ=2))

print("Number Correct anova")
cw_lm=ols('numCorrect ~ C(promptMode) + C(levelMode) + C(promptMode):C(levelMode)', data=hub_puzzles).fit() #Specify C for Categorical
print(sm.stats.anova_lm(cw_lm, typ=2))

tukey = pairwise_tukeyhsd(endog=solved_hubs["numCorrect"],
                          groups=solved_hubs["levelMode"],
                          alpha=0.05)

print(tukey)


print("Number Correct anova")
cw_lm=ols('numCorrect ~ C(promptMode) + C(levelMode) + C(promptMode):C(levelMode)', data=hub_puzzles).fit() #Specify C for Categorical
print(sm.stats.anova_lm(cw_lm, typ=2))"""




print("\ncondition")
print(solved_hubs.groupby("condition").size())
print("\nlevelMode")
print(solved_hubs.groupby("levelMode").size())
print("\npromptMode")
print(solved_hubs.groupby("promptMode").size())
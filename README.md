# Overview
This project is designed to generate and solve logic puzzles, 
as well as label tactics in playtraces of users who solve logic puzzles.

# Related Papers
Papers related to this project are in the Papers folder. 

## Tags

GECCO 2024 - https://github.com/kaylah-fae/logic_puzzles/releases/tag/v1.0.0
AIIDE 2024 - https://github.com/kaylah-fae/logic_puzzles/releases/tag/v2.0.0
AIIDE 2026 - https://github.com/kaylah-fae/logic_puzzles/releases/tag/tv1.0.0

## Data

AIIDE 2026 user data is in the Escape Room folder under "expert_data" (for the author expert) and "user_data" (for the anonymous online study users).

expert_data: e1_kf/*_ground.json

user_data: user_data.csv, action_data.json

# Logic Puzzle Solving
This project defines the structure of logic grid puzzles and defines logic for solving them.

## LogicPuzzle.py 
This file defines the objects and logics for logic puzzles and their solving.

### Category 
A category object is a set of entities, that is either numerical or categorical. To create a new category, you need to provide a title for the category, list of string names for the entities, and whether the category is numerical or categorical.

```
suspects = Category("suspect", ["Ms. Scarlet", "Mrs. White", "Col. Mustard", "Prof. Plum"], False) 
```

### Puzzle 
One you haves a set of categories, you can create an empty puzzle. 

```
puzzle = Puzzle([suspects, weapons, rooms, time]) 
```

These puzzles can be updated using the " answer(self, cat1, cat2, ent1, ent2, new_symbol)" method. This will put the string "new_symbol" in the cell location of ent1 in cat1 and ent2 in cat2. 

Given a partially or completelty solved puzzle, there are several methods that are use full. 

* print_grid: return a string of the grid 
* is_valid: returns true if there are no logical contradictions in the puzzle 
* is_complete: returns true if the puzzle is valid and all cells are filled 

### Hint Grammar 
The hint grammar is defined as a nested dictionary. You can generated a random hint for a given puzzle using the "generate_hint(puzzle)" function. This hint will be returned as a dictionary, but can be translated to a string in English using "hint_to_english" function in "HintToEnglish.py" 

### Insight
This class provides logic for the tactics associated with solving logic puzzles. The Solver labels its moves with relevant tactics. Tactics are organized in a DAG and provided a total ordering as a fallback.

### Solver
The Solver can apply logic to the Puzzle grid. Optionally, it may be forbidden to use certain tactics.

#### apply_hint
This function finds all cell changes that can be made for the given hint and returns them in a list.
It can also apply those changes directly if the "apply" flag is set to True.

#### fast_forward and apply_hints
Two different ways of making as many changes as are possible to the grid state with the current hints.
fast_forward is simpler and does so by repeatedly applying all available moves. 
apply_hints is used to find the "loops" measure of difficulty by repeatedly looping over all hints and applying all their changes. "loops" is the number of times the whole hint list is visited.

#### get_available_moves
Get all moves that are currently possible according to the solver.

#### unmissable_insights
Find which tactics must be used in any solution to a given puzzle.

#### can_solve_without
Check whether a puzzle can be solved without using a given tactic or its descendents.

# Tactic Discovery
This project provides a function for labelling tactics in user data.

## Escape Room/insight_recovery.py
Functions for labelling tactics in user data.

### recover_moves
Function for labelling tactics on a set of user moves formatted as (time, raw_str, rec_moves) where time is the time the move was made (since the start of the puzzle), raw_str is how the move was initially saved by the online study interface, and rec_moves is a list of cell changes made by the move in the format of (loc, sy) - loc being the grid location and sy being the new grid symbol.

# Logic Puzzle Generation
This project includes a genetic algorithm for generating logic puzzles.

## Evolution.py 

### apply_hints(puzzle, hints)
This is the main solver for logic puzzles. This functions takes in a puzzle and and list of hints, and attempts to solve the puzzle using the hints. It will create a copy of the puzzle and update it with any logic contained in the hints. If this puzzle copy has empty space that means the puzzle was unsolvable. Note the returned puzzle may still not be valid. 

### Hint Set 
This class the individuals for evolution. There are three important attributes in hint set: 
* hints: a list of hints (given at intialization)
* puzzle: an empty puzzle state (given at initalization)
* completed_puzzle: a puzzle state which was attempted to be solved with hints 

There are also several important methods in hint set. 

#### mutate(add_rate)
Returns a new hint set that is mutated once. There are two types of mutation that can occur 

* addition: a new random hint is added 
* deletion: a random hint is removed 

The probability of the mutation being addition is specified with the add_rate parameter. However, if there are over 20 hints only deletion will be chosen. 

#### cross_over(other) 
Crossover combines the hint lists of two puzzle and randomly shuffles them between two children. Each child gets an equal number of hints (except if there is an odd number). 

#### is_valid()
Returns true if this hint set represents a solvable puzzle. 

#### feasiblity()
This is the fitness function for infeasible (unsolvable) puzzles. It will return a number between 0 and 1, where 1 represents a solvable puzzle. There are three components to this fitness function: 

* completion: percentage of filled-in cells 
* validity: percentages of rows with exactly one "O" 
* violaitons: number of transitive violations (lower numbers are rewarded)

#### optimize_fun()
This is the fitness function for feasible (solvable) puzzles. This deines the optimization criteria for the puzzle. Several fitness functions are present, and can be uncommented out to change. 

### evolve(puzzle, generations, pop_size, x_rate, mut_rate, add_rate, elits)
This is the function for the FI-2Pop genetic algorithm that generated new puzzles. 

Parameters: 
* puzzle: a blank puzzle to generate hints for 
* generations: number of generations to run for 
* pop_size: the size of population (this will be the sum of the feasible and infeasible populations)
* x_rate: rate of cross over 
* mut_rate: ratio of children to mutate 
* add_rate: ratio of mutations that should be addition 
* elits: number of elites to keep in each population 

Returns: 
* feasible: the feasible population at the last generation
* infeasible: the infeasible popuation at the last generation 
* history: a history object that tracks fitness over time 

Note: the feasible and infeasible populations are returned as list of tuples where the first item in the tuple is the fitness and the second item is the HintSet 

## MapElites.py

### EliteGrid 

Data structure for representing the map elite grid. Some important parameters and methods are: 

* grid: a list of lists representing the grid. Each cell either contains ``None'' or a hintSet object 

* addChild: Children are added to the grid with the addChild method. To add a child a row (based on solution) and column (based on solver loops) are determined. The child is added if this cell is empty or the new child is at least as small in terms of hint size. 

* select: returns a random child in the grid 

* getFitnessGrid: return the fitness (hint size) of children in the grid (or -1 if cell is empty)

 ### History 
 This object tracks various values throughout evolution history 

 ### evolve 

 Runs contrained map-elites evolition 

 *inputs* 

 * puzzle: the puzzle being generated 
 *  generations: number of generations to run 
 *  pop_size: opulation size
 *  x_rate: cross over rate 
 *  mut_rate: mutation rate 
 *  add_rate: ratio of add mutations 
 *  elits: number elites (for infeasible pop)

 *outputs* 

 * feasibleGrid: the mapElites grid of all feasible children in last generation 
 * infeasiblePopulation: list of infeasible children in last generation 
* history: history object across evolution 


# Puzzle Garden Backend
This project can serve as a backend logic puzzle generator for Puzzle Garden.

## Run the backend locally 

### Step 1: Install Python 
Install python onto your computer. This project was based on python version 3.10.12 

https://www.python.org/ 

### Step 2: Install MongoDB 

Following the instructions to install Mongo on your computer. 

https://www.mongodb.com/docs/manual/installation/ 

Make sure a MongoDB instance is running before starting 

### Step 3: Download Code and Install Packages 
Install code onto your computer and go to that directory in your terminal. 

Start a python virtual environment with the following code: 

```
python3 -m venv
```

Run the environment with the following command 

```
source venv/bin/activate 
```

Install all the necessary packages: 

```
pip install flask==3.1.0
pip install flask_cors==5.0.0
pip install jsonpickle==3.0.2
pip install pymongo==4.11.1
```

### Load data 
If you want to add a user, add the data.json file to the main code directory. Then run the following code (with the virtual environment active): 

```
python LoadData.py
```

### Run main.py 
In the code directory run the code to launch the database: 

```
python main.py
```

The flask server should now be running on localhost:3000 

## Hosting on a VM 

### Setting up VM  
We mostly followed this tutorial: https://medium.com/@adityaarya1/deploy-a-flask-application-to-azure-vm-with-a-ssl-certificate-d2960c50783d 

The main steps are: 

1. Create a VM 
2. Set up the code as you would locally 
3. Set up a Gunicorn instance to run the falsk server
4. Set up a Nginx server 
5. User certbox to run on https 



### Updating VM once set up 

* Step 1: SSH into vm 
* step 2: cd into logic_puzzle
* step 3: pull latest code 
* step 4: reload systemctl 

```sudo systemctl daemon-reload```

* step 5: re-start the gunicorn service 

```sudo systemctl restart logic_puzzle_app.service``` 

If there is an error you can check with 

```sudo systemctl status logic_puzzle_app.service``` 

Or for more detail logs, check the journal with (where 200 is the number of lines to print): 

```sudo journalctl -u logic_puzzle_app.service -n 200```


You can find/modify the Gunicorn configuration with: 

### Running a new experiment 
New experiments can be run by modifying the "Experiments.py" file. At the top, several contains are defined. Most important is the "folder" which tells the program where to put experiement data. We recommend creating a new folder for each experiment run. You can also modify the puzzle to generate puzzles with different themes. Note that currently puzzles are required to have at least three categories, one of which must be numeric. 

After the experiement finishes running, you will need to run the "DataVisualisation.py" file, with the updated folder. This will produce "hint.txt" and "solutions.txt" files, which contain the hints and solutions for your generated puzzles. 

### Running the Flask API Server
The Flask API server can be run using the command line with command ```python main.py```.
To start a mock database, start MongoDB, then run command ```python mock-db.py```.

## Important Files 

### Database.py 
Functions to manage the MonogDB database 

### main.py 
End points for the flask API. 



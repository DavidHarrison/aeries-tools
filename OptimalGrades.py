#!/usr/bin/python2

import math

import Move
import NeededGrade

# 4 decimal place float accuracy
FLOAT_ACCURACY = 4

#vector distance to move on non calculated assignments
#   on each step of optimization
MOVE_DISTANCE = 10 
#number of moves on each dimension
#   (total moves = MOVES_PER_DIMENSION**(dimensions-1)
#   including non-unique moves)
MOVE_SPECIFICITY = 5

# define dictionary keywords for assignment and category dictionaries
## assignment keywords
### the name of the category the assignment is part of
ASSIGNMENT_CATEGORY = 'category'
### the name of the assignment (short description)
# TODO, identify assignments by assignment number
ASSIGNMENT_NAME = 'description'

## gradebook categories keywords
### the percentage of the category as it stands in Aeries
CATEGORY_PERCENT = 'grade percent'

'''
optimal way to get target_percent with assignments, given gradebook_categories
    target_percent: float (probably 0-100)
    assignments: list of assignment dictionaries (from aeries-api)
    gradebook_categories: list of category dictionaries from the gradebook
        (with or without weighting) (from aeries-api)
'''
def optimalGrades(target_percent, assignments, gradebook_categories):
    assignment = assignments[len(assignments) - 1]
    #get a list of scores such that each score will be roughly the same, which fits to target grade
    print "Getting start scores"
    start_scores = getStartScores(target_percent, assignment, assignments, gradebook_categories)
    print "Start scores: " + str(start_scores)
    #init a move generator class instance
    #print "initing move gen"
    move_generator = Move.Move(target_percent, assignment, gradebook_categories, assignments)
    move_generator.initMoveDeltas(len(assignments), MOVE_SPECIFICITY)
    #print "optimizing"
    optimal_assignment_percents = optimize(target_percent, assignments,
                                            start_scores,
                                            gradebook_categories,
                                            move_generator)
    #print "making dict"
    optimal_scores_dict = toDict(assignments, optimal_assignment_percents)
    return optimal_scores_dict

#works, getNeededPercent does not
def getStartScores(target_percent, assignment, assignments, gradebook_categories):
    i = 0
    while True:
        assignment_percents = [i] * (len(assignments) - 1)
        needed_percent = NeededGrade.getNeededPercent(target_percent,
                                                        assignment,
                                                        gradebook_categories,
                                                        assignments=assignments,
                                                        assignment_percents=assignment_percents)
        if floatEquals(i, needed_percent):
            break
        # TODO, find a safer increment algorithm
        i += (needed_percent - i) / 10.0
    return assignment_percents + [needed_percent]

def floatEquals(float1, float2):
    if round(float1, FLOAT_ACCURACY) == round(float2, FLOAT_ACCURACY):
        return True
    else:
        return False

def toDict(assignments, assignment_percents):
    scores_dict = {}
    i = 0
    for assignment in assignments:
        scores_dict[assignment[ASSIGNMENT_NAME]] = assignment_percents[i]
        i += 1
    return scores_dict

def optimize(target_percent, assignments, current_position, gradebook_categories, move_generator):
    current_cost = getCost(current_position, assignments, gradebook_categories)
    while True:
        moves = move_generator.getMoves(current_position, MOVE_DISTANCE)
        next_move = getMinCostMove(moves, assignments, gradebook_categories)
        next_cost = getCost(next_move, assignments, gradebook_categories)
        if current_cost <= next_cost:
            print "minima"
            print "cost: " + str(current_cost)
            return current_position
        else:
            #print "move: " + str(next_move)
            #print "cost: " + str(next_cost)
            current_position = next_move
            current_cost = next_cost

def getMinCostMove(moves, assignments, gradebook_categories):
    min_cost_move = None
    for move in moves:
        move_cost = getCost(move, assignments, gradebook_categories)
        if min_cost_move == None or move_cost < min_cost_move_cost:
            min_cost_move = move
            min_cost_move_cost = move_cost
    return min_cost_move

'''
vector distance squared (no need to root) from the averages for the
    assignment categories
'''
def getCost(position, assignments, gradebook_categories):
    cost = 0
    for score in position:
        score_assignment = assignments[position.index(score)]
        score_category_average = getAssignmentCategoryAverage(
                                                score_assignment,
                                                gradebook_categories)
        cost += (float(score) - score_category_average)**2
    return cost

def getAssignmentCategoryAverage(assignment, gradebook_categories):
    assignment_category = assignment[ASSIGNMENT_CATEGORY]
    category = NeededGrade.getCategory(assignment_category, gradebook_categories)
    category_average = float(category[CATEGORY_PERCENT])
    return category_average

#!/usr/bin/python2

import math

import Move
import NeededGrade

# define dictionary keywords for assignment and category dictionaries
## assignment keywords
### the name of the category the assignment is part of
ASSIGNMENT_CATEGORY = 'category'

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
    '''
    set start_percent to the abitrary (and hopefully close-ish) target_percent
    '''
    start_percent = target_percent
    assignment_scores = []
    i = 0
    '''
    for each assignment (excepting the last), give it a starting score of start_percent
    '''
    while i < len(assignments) - 1:
        assignment_scores.append(str(start_percent))
        i += 1
    assignment = assignments[len(assignments) - 1]
    '''
    set the last score to the percent needed to get exactly target_percent with
        other assignments as start_percent
    '''
    needed_percent = NeededGrade.getNeededPercent(target_percent, assignment,
                                                    gradebook_categories,
                                                    assignments=assignments,
                                                    assignment_scores=assignment_scores)
    assignment_scores.append(str(needed_percent))
    optimal_assignment_scores = optimize(target_percent, assignments,
                                            assignment_scores,
                                            gradebook_categories)
    optimal_scores_dict = {}
    i = 0
    for assignment in assignments:
        optimal_scores_dict[assignment[ASSIGNMENT_NAME]] = optimal_assignment_scores[i]
        i += 1
    return optimal_scores_dict

def optimize(target_percent, assignments, current_position, gradebook_categories):
    blank_move = []
    moves = Move.getMoves(blank_move, current_position, target_percent,
                            assignments, gradebook_categories)
    next_move = getMinCostMove(moves, assignments, gradebook_categories)
    next_cost = getCost(next_move, assignments, gradebook_categories)
    current_cost = getCost(current_position, assignments, gradebook_categories)
    if current_cost <= next_cost:
        print "minima"
        print "cost: " + str(current_cost)
        return current_position
    else:
        print "move: " + str(next_move)
        print "cost: " + str(next_cost)
        return optimize(target_percent, assignments, next_move, gradebook_categories)

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
    category = getCategory(assignment_category, gradebook_categories)
    category_average = float(category[CATEGORY_PERCENT])
    return category_average

#!/usr/bin/python2 

import math

import Move
import GradeCalculator
import Constants as c

STARTING_MOVE_DISTANCE = 10.0
MIN_MOVE_DISTANCE = 0.001

#vector distance to move on non calculated assignments
#   on each step of optimization
MOVE_DISTANCE = 0.1
#angles around a circle for each dimension
MOVE_SPECIFICITY = 3

#how many places to compare a decimal to
DECIMAL_COMPARE = 4

#dependent assignment index
DEPENDENT_INDEX = 0

#optimal way to get target_percent with assignments, given gradebook_categories
#    target_percent: decimal string (probably 0-100)
#    assignments: list of assignment dictionaries (from aeries-api)
#    gradebook_categories: list of category dictionaries from the gradebook
#        (with or without weighting) (from aeries-api)
# **Takes a lot of time after 6 assignments**
# in one test 5: 0.68s, 6: 1.40s, 7: 13.62s, 8: 27.70s, 9: 91.01s, 10: 276.05s
# in another (newer test) 5: 2.60s, 6: 8.95s, 7, 27.39s, 8: 99.61s, 9: 284.71s 10: 844.24s, 11: 4393.25s
def optimalGrades(target_percent, assignments, gradebook_categories):
    grade_calculator = GradeCalculator.GradeCalculator(gradebook_categories)
    grade_calculator.set(target_percent=target_percent, assignments=assignments,
                         dependent_assignment_index=DEPENDENT_INDEX)
    #get a list of scores such that each score will be roughly the same, which fits to target grade
    start_scores = getStartScores(grade_calculator)
    print "Start scores: " + str(start_scores)
    #init a move generator class instance
    dimensions = len(assignments)
    move_generator = Move.Move(dimensions, MOVE_SPECIFICITY)
    #print "optimizing"
    optimal_assignment_percents = optimize(start_scores, STARTING_MOVE_DISTANCE,
                                           grade_calculator, move_generator,
                                           assignments, gradebook_categories)
    optimal_scores_dict = toDict(assignments, optimal_assignment_percents)
    return optimal_scores_dict

def getStartScores(grade_calculator):
    #both are arbitrary staring points (chosen for relative speed,
    #   though time for this step is fairly insignificant)
    independent_percent = grade_calculator.target_percent
    assignments = grade_calculator.assignments
    dependent_assignment = assignments[DEPENDENT_INDEX]
    increment = 10.0
    while True:
        assignment_scores = makeAssignmentScores(independent_percent,
                                                 assignments)
        grade_calculator.set(assignment_scores=assignment_scores)
        needed_score = grade_calculator.getNeededScore()
        needed_score = float(needed_score)
        needed_percent = percent(dependent_assignment, needed_score)
        #if they are the same to DECIMAL_COMPARE digits, break
        if round(independent_percent, DECIMAL_COMPARE) == round(needed_percent, DECIMAL_COMPARE):
            break
        new_direction = (needed_percent - independent_percent) / abs(needed_percent - independent_percent)
        #if increment changes sign
        if increment / new_direction < 0:
            #cut increment in half, and reverse it
            increment /= -2
        independent_percent += increment
    assignment_scores[DEPENDENT_INDEX] = needed_score
    return assignment_scores

def makeAssignmentScores(percent, assignments):
    assignment_scores = []
    for independent_assignment in assignments:
        assignment_scores.append(score(independent_assignment, percent))
    return assignment_scores

# returns the score given on the assignment given the percent (will not be exact)
def score(assignment, percent):
    max_points = float(assignment[c.ASSIGNMENT_MAX_POINTS])
    score = max_points * percent / 100.0
    return score

# returns the percent recieved on the assignment given the score (will not be exact)
def percent(assignment, score):
    max_points = float(assignment[c.ASSIGNMENT_MAX_POINTS])
    try:
        percent = score / max_points * 100.0
    except ZeroDivisionError:
        return 0
    return percent

# return a dictionary with keywords of the assignment's ASSIGNMENT_NAME and a value of the score
def toDict(assignments, assignment_scores):
    scores_dict = {}
    i = 0
    for assignment in assignments:
        scores_dict[assignment[c.ASSIGNMENT_NAME]] = assignment_scores[i]
        i += 1
    return scores_dict

def optimize(current_position, move_distance, grade_calculator, move_generator, assignments, gradebook_categories):
    #print "move distance:  "  + str(move_distance)
    current_cost = getCost(current_position, assignments, gradebook_categories)
    while True:
        moves = move_generator.getMoves(current_position, move_distance)
        moves = fitToGrade(moves, grade_calculator)
        next_move = getMinCostMove(moves, assignments, gradebook_categories)
        next_cost = getCost(next_move, assignments, gradebook_categories)
        if current_cost <= next_cost:
            new_move_distance = move_distance / 10.0
            if new_move_distance < MIN_MOVE_DISTANCE:
                #print "minima"
                #print "cost: " + str(current_cost)
                return current_position
            else:
                return optimize(current_position, new_move_distance,
                                grade_calculator, move_generator,
                                assignments, gradebook_categories)
        else:
            #print "move: " + str(next_move)
            #print "cost: " + str(next_cost)
            current_position = next_move
            current_cost = next_cost

def fitToGrade(moves, grade_calculator):
    copy_moves = list(moves)
    for move in copy_moves:
        grade_calculator.set(assignment_scores=move)
        needed_score = grade_calculator.getNeededScore()
        move[DEPENDENT_INDEX] = needed_score
    return copy_moves

def getMinCostMove(moves, assignments, gradebook_categories):
    min_cost_move = None
    for move in moves:
        move_cost = getCost(move, assignments, gradebook_categories)
        if min_cost_move == None or move_cost < min_cost_move_cost:
            min_cost_move = move
            min_cost_move_cost = move_cost
    return min_cost_move

#vector distance squared (no need to root) from the averages for the
#    assignment categories
def getCost(position, assignments, gradebook_categories):
    cost = 0.0
    for score in position:
        assignment = assignments[position.index(score)]
        try:
            assignment_percent = percent(assignment, float(score))
        #a purely extra credit assignment
        #TODO, find a reasonable cost for these assignments
        except ZeroDivisionError:
            distance = 0
        else:
            category_average_percent = getAssignmentCategoryAverage(assignment, gradebook_categories) * 100
            #print "category average percent: " + str(category_average_percent)
            distance = assignment_percent - category_average_percent
        #TODO, find reasonable cost power
        #absolute value is only necessary for odd powers
        cost += math.fabs(distance**2)
    return cost

def getAssignmentCategoryAverage(assignment, gradebook_categories):
    assignment_category = assignment[c.ASSIGNMENT_CATEGORY]
    category = getCategory(assignment_category, gradebook_categories)
    #TODO, cleanup (quick fix)
    try:
        category_average_percent = float(category[c.CATEGORY_SCORE_POINTS]) / float(category[c.CATEGORY_MAX_POINTS])
    except ZeroDivisionError:
        return 0
    return category_average_percent

def getCategory(category_name, categories):
    for category in categories:
        if category[c.CATEGORY_NAME] == category_name:
            return category

#!/usr/bin/python2
try:
    import simplejson as json
except ImportError:
    import json
import codecs
import math
from decimal import Decimal
from fractions import Fraction

import OptimalGrades
import GradeCalculator
import Move
import Constants as c
import Tests

def loadData(file_name):
    f = codecs.open(file_name, 'r', encoding='utf-8')
    python_data = json.load(f)
    return python_data

def testNeededGrade(data):
    for test in Tests.ASSIGNMENT_TESTS:
        gradebook = data[test['gradebook'] - 1]
        dependent_assignment_index = test['assignment']
        try:
            assignment_numbers = test['assignments']
        except:
            assignments = None
            assignment_scores = None
        else:
            assignments = []
            assignment_scores = []
            for assignment_number in assignment_numbers:
                assignment = gradebook[c.GRADEBOOK_ASSIGNMENTS][assignment_number - 1]
                assignments.append(assignment)
                assignment_score = str(assignment[c.ASSIGNMENT_SCORE_POINTS])
                if assignment_score == '':
                    assignment_score = '0'
                assignment_scores.append(assignment_score)
        gradebook_categories = gradebook[c.GRADEBOOK_CATEGORIES]
        target_percent = test['percent']
        print "Assignment scores: " + str(assignment_scores)
        grade_calculator = GradeCalculator.GradeCalculator(gradebook_categories)
        grade_calculator.set(target_percent=target_percent, assignments=assignments,
                             dependent_assignment_index=dependent_assignment_index,
                             assignment_scores=assignment_scores)
        needed_score = grade_calculator.getNeededScore()
        needed_score = grade_calculator.decimal(Fraction(needed_score))
        TWOPLACES = Decimal(10) ** -2
        print "Needed score of " + str(needed_score.quantize(TWOPLACES)) + " on assignment " + assignments[dependent_assignment_index][c.ASSIGNMENT_NAME]

def testMoveDeltas():
    move_generator = Move.Move()
    move_deltas = move_generator.getMoveDeltas(Tests.DIMENSIONS, Tests.MOVE_SPECIFICITY)
    for delta in move_deltas:
        vector_distance = vectorDistance(delta)
        #print "vector distance " + str(vector_distance)
        if not move_generator.floatEquals(vector_distance, 1.0):
            print "Coordinate " + str(delta) + " failed with a distance of " + str(vector_distance)
    print "finished"

def vectorDistance(coordinate):
    vector_distance_squared = 0
    for dimension in coordinate:
        vector_distance_squared += float(dimension)**2
    return math.sqrt(vector_distance_squared)

def testOptimalGrades(data):
        for test in Tests.OPTIMIZATION_TESTS:
        gradebook = data[test['gradebook'] - 1]
        assignments = []
        for assignment_number in test['assignments']:
            assignments.append(gradebook[c.GRADEBOOK_ASSIGNMENTS][assignment_number - 1])
        gradebook_categories = gradebook[c.GRADEBOOK_CATEGORIES]
        target_percent = test['percent']
        optimal_scores = OptimalGrades.optimalGrades(target_percent,
                                                        assignments,
                                                        gradebook_categories)
        for assignment in assignments:
            assignment_score = float(optimal_scores[assignment[c.ASSIGNMENT_NAME]])
            #assignment_percent = OptimalGrades.percent(assignment, assignment_score)
            message = "Suggested score of "
            message += "{0:.2f}".format(round(assignment_score, 2))
            message += " on assignment "
            message += assignment[c.ASSIGNMENT_NAME]
            print message

data = loadData('test-data.json')
#testNeededGrade(data)
#testMoveDeltas()
testOptimalGrades(data)

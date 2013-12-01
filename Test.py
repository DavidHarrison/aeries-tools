#!/usr/bin/python2
try:
    import simplejson as json
except ImportError:
    import json
import codecs
import pprint

import OptimalGrades
import NeededGrade
import Move

GRADEBOOK_ASSIGNMENTS = 'entries'
GRADEBOOK_CATEGORIES =  'weighting'
ASSIGNMENT_NAME = 'description'

def loadData(file_name):
    f = codecs.open(file_name, 'r', encoding='utf-8')
    python_data = json.load(f)
    return python_data

def testNeededGrade(data):
    tests = [
                #fill with test cases of format:
                #{'gradebook': 1, 'assignment': 23, 'percent': 90},
            ]
    for test in tests:
        gradebook = data[test['gradebook'] - 1]
        assignment = gradebook[GRADEBOOK_ASSIGNMENTS][test['assignment'] - 1]
        gradebook_categories = gradebook[GRADEBOOK_CATEGORIES]
        target_percent = test['percent']
        needed_percent = NeededGrade.getNeededPercent(target_percent, assignment, gradebook_categories)
        #pp = pprint.PrettyPrinter(indent=4)
        #print "on assignment "
        #pp.pprint(assignment)
        #print "with gradebook categories "
        #pp.pprint(gradebook_categories)
        print "Needed grade of " + "{0:.2f}".format(round(needed_percent, 2)) + "% on assignment " + assignment[ASSIGNMENT_NAME]

def testMoveDeltas():
    #constructor is not relevant
    move_generator = Move.Move(None, None, None, None)
    maximum_vector_distance = 1
    dimensions = 8
    move_specificity = 5
    move_generator.initMoveDeltas(dimensions, move_specificity)
    move_deltas = move_generator.base_move_deltas
    pp = pprint.PrettyPrinter(indent=4)
    print "Move deltas: "
    pp.pprint(move_deltas)
    print "Length of move deltas: " + str(len(move_deltas))

def testOptimalGrades(data):
    tests = [
                #fill with test cases of format:
                #{
                #    'gradebook': 3,
                #    'assignments': [6,7,9,10,8],
                #    'percent': 90
                #},
            ]
    for test in tests:
        gradebook = data[test['gradebook'] - 1]
        assignments = []
        for assignment_number in test['assignments']:
            assignments.append(gradebook[GRADEBOOK_ASSIGNMENTS][assignment_number - 1])
        gradebook_categories = gradebook[GRADEBOOK_CATEGORIES]
        target_percent = test['percent']
        optimal_grades = OptimalGrades.optimalGrades(target_percent,
                                                        assignments,
                                                        gradebook_categories)
        for assignment in assignments:
            assignment_score = float(optimal_grades[assignment[ASSIGNMENT_NAME]])
            message = "Suggested grade of "
            message += "{0:.2f}".format(round(assignment_score, 2))
            message += "% on assignment "
            message += assignment[ASSIGNMENT_NAME]
            print message

#reads data from test-data.json in the local library (downloaded using aeries-api)
data = loadData('test-data.json')
#testNeededGrade(data)
#testMoveDeltas()
testOptimalGrades(data)

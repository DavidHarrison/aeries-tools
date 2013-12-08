#!/usr/bin/python2

# define dictionary keywords for gradebook, assignment and category dictionaries

## gradebook keywords
### list of assignments
GRADEBOOK_ASSIGNMENTS =     'entries'
### list of categories
GRADEBOOK_CATEGORIES =      'weighting'

## assignment keywords
### how many points were recieved on the assignment ('my points')
ASSIGNMENT_SCORE_POINTS =           'recieved points'
### the maximum points (without extra-credit) that can be scored on the assignment ('out of' points)
ASSIGNMENT_MAX_POINTS =             'max points'
### the percent recieved on the assignment (rounded to two decimal places)
ASSIGNMENT_PERCENT =                'percent'
### the assignment number (not necessarily continuous)
ASSIGNMENT_NUMBER =                 'assignment number'
### the name of the category the assignment is part of
ASSIGNMENT_CATEGORY =               'category'
### whether or not the assignment grading is complete as a string Yes/No
ASSIGNMENT_GRADING_COMPLETE =       'grading complete'
### the string values for whether or not the assignment has been graded
ASSIGNMENT_GRADING_COMPLETE_TRUE =  'Yes'
ASSIGNMENT_GRADING_COMPLETE_FALSE = 'No'
### assignment name/short description
ASSIGNMENT_NAME =                   'description'

## gradebook categories keywords
### the name of the gradebook category
CATEGORY_NAME =         'name'
### the weight of the category (when all categories are active)
CATEGORY_WEIGHT =       'weight percent'
### how many points were recieved in the category
CATEGORY_SCORE_POINTS = 'recieved points'
### the max points of the category as it stands in Aeries
CATEGORY_MAX_POINTS =   'max points'
### name of the category for gradebook totals
TOTAL_CATEGORY =        'Total'
### the percentage of the category as it stands in Aeries
CATEGORY_PERCENT =      'grade percent'

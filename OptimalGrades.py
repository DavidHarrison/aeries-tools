#!/usr/bin/python2

# define dictionary keywords for assignment and category dictionaries
## assignment keywords
### how many points were recieved on the assignment ('my points')
ASSIGNMENT_SCORE_POINTS = 'recieved points'
### the maximum points (without extra-credit) that can be scored on the assignment ('out of' points)
ASSIGNMENT_MAX_POINTS = 'max points'
### the name of the assignment
ASSIGNMENT_NAME = 'name'
### the name of the category the assignment is part of
ASSIGNMENT_CATEGORY = 'category'
### whether or not the assignment grading is complete as a string Yes/No
ASSIGNMENT_GRADING_COMPLETE = 'grading complete'
### the string values for whether or not the assignment has been graded
ASSIGNMENT_GRADING_COMPLETE_TRUE = 'Yes'
ASSIGNMENT_GRADING_COMPLETE_FALSE = 'No'

## gradebook categories keywords
### the name of the gradebook category
CATEGORY_NAME = 'name'
### the weight of the category (when all categories are active)
CATEGORY_WEIGHT = 'weight percent'
### how many points were recieved in the category
CATEGORY_SCORE_POINTS = 'max points'
### the max points of the category as it stands in Aeries
CATEGORY_MAX_POINTS = 'recieved points'
### name of the category for gradebook totals
TOTAL_CATEGORY = 'Total'

# optimal way to get target_percent with assignments, given gradebook_categories
#   target_percent: float (probably 0-100)
#   assignments: list of assignment dictionaries (from aeries-api)
#   gradebook_categories: list of category dictionaries from the gradebook
#       (with or without weighting) (from aeries-api)
def optimalGrades(target_percent, assignments, gradebook_categories):
#Minimizing the cost of the set of percentages
    '''
    1.  determine a reasonable starting grade set (eg target grade for all
        but last assignment (for which the grade will be calculated))
    '''
    # set start_percent to the abitrary (and hopefully close-ish) target_percent
    start_percent = target_percent
    assignment_scores = []
    i = 0
    # for each assignment (excepting the last), give it a starting score of start_percent
    while i < len(assignments) - 1:
        assignment_scores.append(str(start_percent))
        i += 1
    '''
    set the last score to the percent needed to get exactly target_percent with
        other assignments as start_percent
    '''
    needed_percent = getNeededPercent(target_percent, assignment, assignments, assignment_scores, gradebook_categories)))
    assignment_scores.append(str(needed_percent))
    optimal_assignment_scores = optimize(target_percent, assignments, assignment_scores, gradebook_categories)
    optimal_scores_dict = {}
    i = 0
    for assignment in assignments
        optimal_scores_dict[assignment[ASSIGNMENT_NAME]] = optimal_assignment_scores[i]
        i += 1
    return optimal_scores_dict

# TODO: what to do if the gradebook is not weighted (treat it as one large category?)
def getNeededPercent(target_percent, assignment, assignments, assignment_scores, gradebook_categories):
    min_percent = getMinPercent(assignments, gradebook_categories)
    other_assignment_deltas = getOtherAssignmentDeltas(assignments, assignment_scores, gradebook_categories, assignment)
    overall_assignment_weight = getAssignmentWeight(assignment, assignments, gradebook_categories)
    overall_delta_needed = target_percent - min_percent - other_assignment_deltas
    score_neeeded = overall_delta_needed/overall_assignment_weight

def getMinPercent(assignments, gradebook_categories):
    min_percent = 0
    for category in assignments:
        if category[CATEGORY_NAME] == TOTAL_CATEGORY:
            continue
        category_weight = getCategoryWeight(category[CATEGORY_NAME], assignments, gradebook_categories)
        min_category_percent = getMinCategoryPercent(assignment[CATEGORY_NAME], assignments, gradebook_categories)
        min_percent += category_weight * min_category_percent
    return min_percent

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
get the actual weight of the category (may differ from the one given in the
    table if some categories are inactive)
'''
def getCategoryWeight(category_name, assignments, gradebook_categories):
    '''
    if weighting is not used, treat all categories as one large category (with
        weight of 100%/1)
    '''
    if not isWeightingUsed(gradebook_categories):
        return 1
    else:
        category = getCategory(category_name, gradebook_categories)
        total_weighting_used = getWeightingUsed(assignments, gradebook_categories)
        category_weight = getGivenCategoryWeight(category)
        category_weight = category_weight / total_weighting_used
        return category_weight

'''
return whether or not the gradebook is weighted (if it has weights attached to
    categories)
'''
def isWeightingUsed(gradebook_categories):
    test_category = gradebook_categories[0]
    try:
        if test_category[CATEGORY_WEIGHT] in [None, '']:
            return False
        else:
            return True
    except:
        return False

# return the category dictionary of name category_name from the list of categories
def getCategory(category_name, gradebook_categories):
    for category in categories:
        if category[CATEGORY_NAME] == category_name:
            return category

'''
return the amount of weighting used in total by all categories (if all
    categories are active, this should be 1 (100%))
'''
def getWeightingUsed(assignments, gradebook_categories):
    weighting_used = 0
    for category in gradebook_categories:
        if category[CATEGORY_NAME] == TOTAL_CATEGORY:
            continue
        elif not isCategoryActive(category):
            continue
        else:
            category_weight = getGivenCategoryWeight(category)
            weightin_used += category_weight

# return whether or not the category is active (has non-zero assignments in it)
def isCategoryActive(category):
    if category[CATEGORY_MAX_POINTS] == 0:
        return False
    else:
        return True

'''
return the categories weight (as given on the weighting table, not necessarily
    the one used) as a decimal
'''
def getGivenCategoryWeight(category):
    return float(category[CATEGORY_WEIGHT]) / 100
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''
return the minimum percentage possible in the category if all assignments in
    assignments recieve a zero
'''
def getMinCategoryPercent(category_name, assignments, gradebook_categories):
    category = getCategory(category_name, gradebook_categories)
    current_category_score_points = float(category[CATEGORY_SCORE_POINTS])
    current_category_max_points = float(category[CATEGORY_MAX_POINTS])
    for assignment in assignments:
        if assignment[ASSIGNMENT_CATEGORY] = category_name:
            '''
            if the assignment is already graded, remove is points from those
                recieved (but not max points) to give it a score of zero
            '''
            if isAssignmentGraded(assignment):
                current_category_score_points -= float(ASSIGNMENT[ASSIGNMENT_SCORE_POINTS])
            '''
            if the assignment has not yet been graded, add its max points to the
                categories max points and do not add any score points to add the
                assignment with a score of zero
            '''
            else:
                current_category_max_points += float(ASSIGNMENT[ASSIGNMENT_SCORE_POINTS])
        else:
            continue
    min_category_percent = category_score_points / category_max_points
    return min_category_percent

def isAssignmentGraded(assignment):
    if assignment[GRADING_COMPLETE] == ASSIGNMENT_GRADING_COMPLETE_TRUE:
        return True
    elif assignment[ASSIGNMENT_GRADING_COMPLETE] == ASSIGNMENT_GRADING_COMPLETE_FALSE:
        return False
    else:
        print "Undefined value for grading completion: " + str(assignment[ASSIGNMENT_GRADING_COMPLETE])
        raise

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''
return the change in the total grade made by all assignments other than assignment
    (with scores assignment_scores, where each of the indices of in assignments and
    assignment_scores align)
'''
def getOtherAssignmentDeltas(assignments, assignment_scores, gradebook_categories, exclude_assignment):
    total_assignment_delta = 0
    i = 0
    for assignment in assignents:
        if assignment[ASSIGNMENT_NAME] == exclude_assignment[ASSIGNMENT_NAME]:
            continue
        else
            assignment_delta = getAssignmentDelta(assignment, assignment_scores[i], gradebook_categories):
            total_assignment_delta += assignment_delta
        i += 1
    return total_assignment_delta

'''
return the change made to the total grade by assignment (with score assignment_score)
'''
def getAssignmentDelta(assignment, assignment_score, assignments, gradebook_categories):
    overall_assignment_weight = getAssignmentWeight(assignment, assignments, gradebook_categories):
    assignment_delta = assignment_score * overall_assignment_weight

'''
get the overall weight of the assignment (for each point on the assignment,
weight points change in the overall grade (weight will be <= 1))
'''
def getAssignmentWeight(assignment, assignments, gradebook_categories):
    asignment_category = assignment[ASSIGNMENT_CATEGORY]
    category_weight = getCategoryWeight(assignment_category, gradebook_categories)
    category = gradebook_categories[assignment_category]
    assignment_weight_in_category = getAssignmentWeightInCategory(assignments, category)

def getAssignmentWeightInCategory(assignments, category):
    category_max = float(category[CATEGORY_MAX_POINTS])
    for assignment in assignments:
        if not isAssignmentGraded(assignment):
            category_max += float(assignment[ASSIGNMENT_MAX_POINTS])
    '''
    for each percent on the assignment, how many points will the category grade
        change
    '''
    assignment_weight_in_category = 1 / category_max
    return assignment_weight_in_category






#===============================================================================
def optimize
    '''
    2.  get a set of possible changes (each moving a constant vector
        distance from the current point/set) (+/- for 2 assignments, circle
        for 3 assignments, sphere for 4 assignments etc.) (dimensions =
        assignments - 1 (one assignment grade must be calculated in order to
        keep the set meeting the target grade))
    '''
    '''
    3.  for each of this set of changes, calculate the last position needed
        to keep the final grade at the target grade
    '''
    '''
    4.  calculate the cost for each of the possible new positions
    '''
    '''
    5.  find the position with the lowest cost
        -   if the current position is the lowest, return this value, as it
            at least a local minima (and ideally, not far from the absolute
            minima in cost)
        -   if the lowest cost is another position, move to it and repeat
            steps 2-5
    '''

#!/usr/bin/python2

# define dictionary keywords for assignment and category dictionaries
## assignment keywords
### how many points were recieved on the assignment ('my points')
ASSIGNMENT_SCORE_POINTS = 'recieved points'
### the maximum points (without extra-credit) that can be scored on the assignment ('out of' points)
ASSIGNMENT_MAX_POINTS = 'max points'
### the name of the assignment
ASSIGNMENT_NAME = 'description'
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
CATEGORY_SCORE_POINTS = 'recieved points'
### the max points of the category as it stands in Aeries
CATEGORY_MAX_POINTS = 'max points'
### name of the category for gradebook totals
TOTAL_CATEGORY = 'Total'

def getNeededPercent(target_percent, assignment, gradebook_categories,
                        assignments=None, assignment_scores=None):
    if assignments == None:
        assignments = [assignment]
    if assignment_scores == None:
        assignment_scores = []
    min_percent = getMinPercent(assignments, gradebook_categories)
    other_assignment_deltas = getOtherAssignmentDeltas(assignments,
                                                        assignment_scores,
                                                        gradebook_categories,
                                                        assignment)
    overall_assignment_weight = getAssignmentWeight(assignment, assignments,
                                                    gradebook_categories)
    overall_delta_needed = target_percent - min_percent - other_assignment_deltas
    score_needed = overall_delta_needed / overall_assignment_weight
    assignment_max_points = float(assignment[ASSIGNMENT_MAX_POINTS])
    try:
        percent_needed = score_needed / assignment_max_points
    except ZeroDivisionError:
        return None
    return percent_needed

def getMinPercent(assignments, gradebook_categories):
    min_percent = 0
    for category in gradebook_categories:
        category_name = category[CATEGORY_NAME]
        if category_name == TOTAL_CATEGORY:
            continue
        assignment_categories = getAssignmentCategories(assignments)
        if isCategoryActive(category) or category_name in assignment_categories:
            category_weight = getCategoryWeight(category[CATEGORY_NAME],
                                                assignments,
                                                gradebook_categories)
            min_category_percent = getMinCategoryPercent(category[CATEGORY_NAME],
                                                            assignments,
                                                            gradebook_categories)
            category_share = category_weight * min_category_percent
            min_percent += category_share
    return min_percent

def getAssignmentCategories(assignments):
    assignment_categories = []
    for assignment in assignments:
        category_name = assignment[ASSIGNMENT_CATEGORY]
        if not category_name in assignment_categories:
            assignment_categories.append(category_name)
    return assignment_categories

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
        given_category_weight = getGivenCategoryWeight(category)
        category_weight = given_category_weight / total_weighting_used
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

'''
return the category dictionary of name category_name from the list of categories
'''
def getCategory(category_name, gradebook_categories):
    for category in gradebook_categories:
        if category[CATEGORY_NAME] == category_name:
            return category

'''
return the amount of weighting used in total by all categories (if all
    categories are active, this should be 1 (100%))
'''
def getWeightingUsed(assignments, gradebook_categories):
    weighting_used = 0
    for category in gradebook_categories:
        category_name = category[CATEGORY_NAME]
        assignment_categories = getAssignmentCategories(assignments)
        if category_name == TOTAL_CATEGORY:
            continue
        elif (not isCategoryActive(category)) and (not category_name in assignment_categories):
            continue
        else:
            category_weight = getGivenCategoryWeight(category)
            weighting_used += category_weight
    return weighting_used

'''
return whether or not the category is active (has non-zero assignments in it)
'''
def isCategoryActive(category):
    if float(category[CATEGORY_MAX_POINTS]) == 0:
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
    category_score_points = float(category[CATEGORY_SCORE_POINTS])
    category_max_points = float(category[CATEGORY_MAX_POINTS])
    for assignment in assignments:
        if assignment[ASSIGNMENT_CATEGORY] == category_name:
            '''
            if the assignment is already graded, remove is points from those
                recieved (but not max points) to give it a score of zero
            '''
            if isAssignmentGraded(assignment):
                category_score_points -= float(assignment[ASSIGNMENT_SCORE_POINTS])

            #if the assignment has not yet been graded, add its max points to the
            #   categories max points and do not add any score points to add the
            #   assignment with a score of zero
            else:
                category_max_points += float(assignment[ASSIGNMENT_MAX_POINTS])
        else:
            continue
    min_category_percent = (category_score_points / category_max_points) * 100
    return min_category_percent

def isAssignmentGraded(assignment):
    if assignment[ASSIGNMENT_GRADING_COMPLETE] == ASSIGNMENT_GRADING_COMPLETE_TRUE:
        return True
    elif assignment[ASSIGNMENT_GRADING_COMPLETE] == ASSIGNMENT_GRADING_COMPLETE_FALSE:
        return False
    else:
        print "Undefined value for grading completion: " + str(assignment[ASSIGNMENT_GRADING_COMPLETE])
        raise

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''
return the change in the total grade made by all assignments other than
    assignment (with scores assignment_scores, where each of the indices of in
    assignments and assignment_scores align)
'''
def getOtherAssignmentDeltas(assignments, assignment_scores, gradebook_categories,
        exclude_assignment):
    total_assignment_delta = 0
    i = 0
    for assignment in assignments:
        if assignment[ASSIGNMENT_NAME] == exclude_assignment[ASSIGNMENT_NAME]:
            continue
        else:
            assignment_score = float(assignment_scores[i])
            assignment_delta = getAssignmentDelta(assignment,
                                                    assignment_score,
                                                    assignments,
                                                    gradebook_categories)
            total_assignment_delta += assignment_delta
        i += 1
    return total_assignment_delta

'''
return the change made to the total grade by assignment
    (with score assignment_score)
'''
def getAssignmentDelta(assignment, assignment_score, assignments,
                        gradebook_categories):
    overall_assignment_weight = getAssignmentWeight(assignment, assignments,
                                                    gradebook_categories)
    assignment_delta = assignment_score * overall_assignment_weight
    return assignment_delta

'''
get the overall weight of the assignment (for each point on the assignment,
weight points change in the overall grade (weight will be <= 1))
'''
def getAssignmentWeight(assignment, assignments, gradebook_categories):
    assignment_category = assignment[ASSIGNMENT_CATEGORY]
    category_weight = getCategoryWeight(assignment_category, assignments, gradebook_categories)
    category = getCategory(assignment_category, gradebook_categories)
    if not isWeightingUsed(gradebook_categories):
        total_points_max = getTotalPointsMax(assignments, gradebook_categories)
        assignment_weight_in_category = 1.0 / total_points_max
    else:
        assignment_weight_in_category = getAssignmentWeightInCategory(assignments, category)
    assignment_weight = assignment_weight_in_category * category_weight
    return assignment_weight

def getTotalPointsMax(assignments, gradebook_categories):
    total_points_max = 0
    for category in gradebook_categories:
        category_name = category[CATEGORY_NAME]
        if category_name == TOTAL_CATEGORY:
            continue
        if isCategoryActive(category):
            total_points_max += float(category[CATEGORY_MAX_POINTS])
    for assignment in assignments:
        if not isAssignmentGraded(assignment):
            total_points_max += float(assignment[ASSIGNMENT_MAX_POINTS])
    return total_points_max

def getAssignmentWeightInCategory(assignments, category):
    category_max = float(category[CATEGORY_MAX_POINTS])
    for assignment in assignments:
        if not isAssignmentGraded(assignment):
            category_max += float(assignment[ASSIGNMENT_MAX_POINTS])
    '''
    for each percent on the assignment, how many points will the category grade
        change
    '''
    assignment_weight_in_category = 1.0 / category_max
    return assignment_weight_in_category

#!/usr/bin/python2

# vector distance to move on each step of optimization
## 0.1 percent
OPTIMIZATION_DISTANCE = .1
## adjust each score with MOVES_PER_SCORE increments
## (is multiplied by each following score meaning that ultimately there will be MOVES_PER_SCORE**(scores - 1) (accounting for the one score that is calculated, and thus fixed relative to the others)
MOVES_PER_SCORE = 10

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
### the percentage of the category as it stands in Aeries
CATEGORY_PERCENT = 'percent'
### name of the category for gradebook totals
TOTAL_CATEGORY = 'Total'

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
    '''
    set the last score to the percent needed to get exactly target_percent with
        other assignments as start_percent
    '''
    needed_percent = getNeededPercent(target_percent, assignment,
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

def getNeededPercent(target_percent, assignment, gradebook_categories,
                        assignments=None, assignment_scores=None):
    if assignments == None:
        assignments = [assignment]
    if assignment_scores == None:
        assignment_scores = []
    # works so far
    min_percent = getMinPercent(assignments, gradebook_categories)
    #print "min percent: " + str(min_percent)
    # works so far
    other_assignment_deltas = getOtherAssignmentDeltas(assignments,
                                                        assignment_scores,
                                                        gradebook_categories,
                                                        assignment)
    #print "other assignment deltas: " + str(other_assignment_deltas)
    overall_assignment_weight = getAssignmentWeight(assignment, assignments,
                                                    gradebook_categories)
    #print "overall assignment weight: " + str(overall_assignment_weight)
    # works so far
    overall_delta_needed = target_percent - min_percent - other_assignment_deltas
    #print "over delta needed: " + str(overall_delta_needed)
    score_needed = overall_delta_needed / overall_assignment_weight
    assignment_max_points = float(assignment[ASSIGNMENT_MAX_POINTS])
    percent_needed = score_needed / assignment_max_points
    return percent_needed

def getMinPercent(assignments, gradebook_categories):
    min_percent = 0
    for category in gradebook_categories:
        category_name = category[CATEGORY_NAME]
        if category_name == TOTAL_CATEGORY:
            continue
        assignment_categories = getAssignmentCategories(assignments)
        if isCategoryActive(category) or category_name in assignment_categories:
            #print "Adding category: " + category[CATEGORY_NAME]
            # works so far
            category_weight = getCategoryWeight(category[CATEGORY_NAME],
                                                assignments,
                                                gradebook_categories)
            #print "Category weight: " + str(category_weight)
            # works so far
            min_category_percent = getMinCategoryPercent(category[CATEGORY_NAME],
                                                            assignments,
                                                            gradebook_categories)
            category_share = category_weight * min_category_percent
            #print "Category share: " + str(category_share)
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
        # works so far
        category = getCategory(category_name, gradebook_categories)
        #print "Category: " + category[CATEGORY_NAME]
        # works so far
        total_weighting_used = getWeightingUsed(assignments, gradebook_categories)
        #print "Total weighting used: " + str(total_weighting_used)
        given_category_weight = getGivenCategoryWeight(category)
        #print "Given category weight: " + str(given_category_weight)
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
    #print "Category score points: " + str(category_score_points)
    category_max_points = float(category[CATEGORY_MAX_POINTS])
    #print "Category max points: " + str(category_max_points)
    for assignment in assignments:
        if assignment[ASSIGNMENT_CATEGORY] == category_name:
            '''
            if the assignment is already graded, remove is points from those
                recieved (but not max points) to give it a score of zero
            '''
            if isAssignmentGraded(assignment):
                #print "Removing " + str(assignment[ASSIGNMENT_SCORE_POINTS]) + " score points from active assignment: " + assignment[ASSIGNMENT_NAME]
                category_score_points -= float(assignment[ASSIGNMENT_SCORE_POINTS])

            #if the assignment has not yet been graded, add its max points to the
            #   categories max points and do not add any score points to add the
            #   assignment with a score of zero
            else:
                #print "Adding " + str(assignment[ASSIGNMENT_MAX_POINTS]) + " max points from inactive assignment: " + assignment[ASSIGNMENT_NAME]
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
            assignment_delta = getAssignmentDelta(assignment,
                                                    assignment_scores[i],
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
    # works so far
    assignment_category = assignment[ASSIGNMENT_CATEGORY]
    #print "Assignment category: " + assignment_category
    # works so far
    category_weight = getCategoryWeight(assignment_category, assignments, gradebook_categories)
    #print "Category weight: " + str(category_weight)
    # works so far
    category = getCategory(assignment_category, gradebook_categories)
    #print "Category: " + category[CATEGORY_NAME]
    # works so far
    if not isWeightingUsed(gradebook_categories):
        #print "Weighting not used"
        total_points_max = getTotalPointsMax(assignments, gradebook_categories)
        #print "Total points max: " + str(total_points_max)
        assignment_weight_in_category = 1.0 / total_points_max
    else:
        #print "Weighting used"
        # works so far
        assignment_weight_in_category = getAssignmentWeightInCategory(assignments, category)
        #print "Assignment weight in category: " + str(assignment_weight_in_category)
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

#===============================================================================

def optimize(target_percent, assignments, current_position, gradebook_categories):
    blank_move = {}
    moves = getMoves(blank_move, current_position, OPTIMIZATION_DISTANCE)
    next_move = getMinCostMove(moves, assignments, gradebook_categories)
    next_cost = getCost(next_move, assignments, gradebook_categories)
    current_cost = getCost(current_position)
    if current_cost < next_cost:
        return current_position
    else:
        return optimize(target_percent, assignments, next_move, gradebook_categories)

def getMoves(partial_move, current_position, remaining_vector_distance,
                target_percent, assignments, gradebook_categories):
    try:
        if len(partial_move) == len(current_position) - 1:
            final_assignment = assignments[len(assignments)-1]
            needed_percent = getNeededPercent(target_percent, final_assignment,
                                                gradebook_categories,
                                                assignments=assignments,
                                                assignments_scores=partial_move)
            final_move = partial_move.append(needed_percent)
            '''
            return final_move as a list so that it can be added to a list
            '''
            return [final_move]
    except:
        pass
    for move in current_moves:
        increment = 2 * remaining_vector_distance / (MOVES_PER_SCORE - 1)
        new_moves = []
        i = -1 * remaing_vector_distance
        '''
        relative safe float comparison, making sure i does not exceed
            remaining_vector_distance by more an increment or more
        '''
        while remaining_vector_distance - i > -1 * (0.5 * increment):
            '''
            current_position at the index of the next score to be added
                to partial_move
            '''
            current_score_value = current_position[len(partial_move)]
            '''
            the adjusted score
            '''
            new_score_value = current_score_value + i
            '''
            copy partial_move and put in a distance for the current variable
            '''
            new_partial_move = list(partial_move).append(new_score_value)
            '''
            intentional use of += to put all moves on the same level
            '''
            new_distance_left = Math.sqrt(remaining_vector_distance**2 - i**2)
            new_moves += getMoves(new_partial_move, current_position,
                                    new_distance_left)
            '''
            increment i so that it will loop through MOVES_PER_SCORE times
            '''
            i += increment
            return new_moves

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
        cost += (score - score_category_average)**2
    return cost

def getAssignmentCategoryAverage(assignment, gradebook_categories):
    assignment_category = assignment[ASSIGNMENT_CATEGORY]
    category = getCategory(assignment_category, gradebook_categories)
    category_average = category[CATEGORY_PERCENT]
    return category_average

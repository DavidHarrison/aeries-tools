#!/usr/bin/python2

from fractions import Fraction
from decimal import Decimal

import Constants as c

class GradeCalculator:

#===============================================================================
## INITIALIZATION

    global categories
    global target_percent
    global assignments
    global dependent_assignment_index
    global assignment_scores
    global assignment_weights
    global assignment_deltas
    global minimum_percent
    global other_assignment_deltas

    def __init__(self, gradebook_categories):
        self.categories = gradebook_categories
        
    def set(self, target_percent=None, assignments=None,
            dependent_assignment_index=None, assignment_scores=None):

        if target_percent != None:
            self.target_percent = Fraction(str(target_percent))

        if assignments != None:
            self.assignments = assignments
            self.assignment_weights = []
            i = 0
            while i < len(self.assignments):
                weight = self.assignmentWeight(i)
                self.assignment_weights.append(weight)
                i += 1

        if dependent_assignment_index != None:
            self.dependent_assignment_index = dependent_assignment_index

        if assignment_scores != None:
            self.assignment_scores = []
            self.assignment_deltas = []
            i = 0
            while i < len(assignment_scores):
                score = Fraction(str(assignment_scores[i]))
                self.assignment_scores.append(score)
                delta = self.assignmentDelta(i)
                self.assignment_deltas.append(delta)
                i += 1
            self.minimum_percent = self.minPercent()
            self.other_assignment_deltas = self.otherAssignmentDeltas()

#===============================================================================
## ASSIGNMENT WEIGHTS

    #get the overall weight of the assignment (for each point on the assignment,
    #weight points change in the overall grade (weight will be <= 1))
    def assignmentWeight(self, assignment_index):
        assignment = self.assignments[assignment_index]
        assignment_category = assignment[c.ASSIGNMENT_CATEGORY]
        category = self.getCategory(assignment_category)
        category_weight = self.categoryWeight(category)
        if not self.isWeightingUsed():
            gradebook_max_points = self.gradebookMaxPoints()
            assignment_weight = Fraction('1.0') / gradebook_max_points
        else:
            assignment_weight_in_category = self.assignmentWeightInCategory(category)
            assignment_weight = assignment_weight_in_category * category_weight
        return assignment_weight

    #return the category dictionary of name category_name from the list of categories
    def getCategory(self, category_name):
        for category in self.categories:
            if category[c.CATEGORY_NAME] == category_name:
                return category

    #returns the actual weight of the category (may differ from the one given in the
    #    table if some categories are inactive)
    def categoryWeight(self, category):
        #if the gradebook is unweighted, return the percent of the total points that
        #   the category max makes up
        if not self.isWeightingUsed():
            gradebook_max_points = self.gradebookMaxPoints()
            category_max_points = self.categoryPoints(category)['max']
            category_weight = category_max_points / gradebook_max_points
        #if the gradebook is active, divide its weight by the amount of weigting active
        #   (0-1)
        else:
            total_weighting_used = self.weightingUsed()
            #the weight given with the category (its weight when all categories are active)
            given_category_weight = self.givenCategoryWeight(category)
            category_weight = given_category_weight / total_weighting_used
        return category_weight

    #the weight of the category given in the table (its weight when all categories are active)
    def givenCategoryWeight(self, category):
        given_category_weight = Fraction(category[c.CATEGORY_WEIGHT]) / Fraction('100.0')
        return given_category_weight
    
    #return whether or not the gradebook is weighted (if it has weights attached to categories)
    def isWeightingUsed(self):
        test_category = self.categories[0]
        try:
            if test_category[c.CATEGORY_WEIGHT] in [None, '']:
                return False
            else:
                return True
        except:
            return False

    #return the total number of points in the the gradebook (used for unweighted gradebooks)
    def gradebookMaxPoints(self):
        total_category = self.getCategory(c.TOTAL_CATEGORY)
        gradebook_max_points = Fraction(total_category[c.CATEGORY_MAX_POINTS])
        for assignment in self.assignments:
            if not self.isAssignmentGraded(assignment):
                gradebook_max_points += Fraction(assignment[c.ASSIGNMENT_MAX_POINTS])
        return gradebook_max_points

    #return whether or not the assignment has been graded
    def isAssignmentGraded(self, assignment):
        if assignment[c.ASSIGNMENT_GRADING_COMPLETE] == c.ASSIGNMENT_GRADING_COMPLETE_TRUE:
            return True
        elif assignment[c.ASSIGNMENT_GRADING_COMPLETE] == c.ASSIGNMENT_GRADING_COMPLETE_FALSE:
            return False
        else:
            print "Undefined value for grading completion: " + str(assignment[c.ASSIGNMENT_GRADING_COMPLETE])
            raise

    #return a dictionary of the points (scored, max) at it minimum configuration
    #   (all assignments in assignments recieve a 0)
    def categoryPoints(self, category):
        category_score_points = Fraction(category[c.CATEGORY_SCORE_POINTS])
        category_max_points = Fraction(category[c.CATEGORY_MAX_POINTS])
        for assignment in self.assignments:
            if assignment[c.ASSIGNMENT_CATEGORY] == category[c.CATEGORY_NAME]:
                #if the assignment is already graded, remove is points from those
                #    recieved (but not max points) to give it a score of zero
                if self.isAssignmentGraded(assignment):
                    category_score_points -= Fraction(assignment[c.ASSIGNMENT_SCORE_POINTS])
                #if the assignment has not yet been graded, add its max points to the
                #   categories max points and do not add any score points to add the
                #   assignment with a score of zero
                else:
                    category_max_points += Fraction(assignment[c.ASSIGNMENT_MAX_POINTS])
            else:
                continue
        return  {
                    'score': category_score_points,
                    'max': category_max_points
                }

    #return the amount of weighting used in total by all categories (if all
    #    categories are active, this should be 1 (100%))
    def weightingUsed(self):
        weighting_used = Fraction('0.0')
        for category in self.categories:
            category_name = category[c.CATEGORY_NAME]
            assignment_categories = self.getAssignmentCategories()
            if category_name == c.TOTAL_CATEGORY:
                continue
            elif (not self.isCategoryActive(category)) and (not category_name in assignment_categories):
                continue
            else:
                given_category_weight = self.givenCategoryWeight(category)
                weighting_used += given_category_weight
        return weighting_used

    #returns a list of all categories that any assignment is part of
    def getAssignmentCategories(self):
        assignment_categories = []
        for assignment in self.assignments:
            category_name = assignment[c.ASSIGNMENT_CATEGORY]
            if not category_name in assignment_categories:
                assignment_categories.append(category_name)
        return assignment_categories

    #return whether or not the category is active (has graded non-zero (max point) assignments in it)
    def isCategoryActive(self, category):
        #if the category has points in it
        if Fraction(category[c.CATEGORY_MAX_POINTS]) != Fraction('0.0'):
            return True
        #if a non-zero assignment will be added to the category for the calculation
        for assignment in self.assignments:
            assignment_category = assignment[c.ASSIGNMENT_CATEGORY]
            category_name = category[c.CATEGORY_NAME]
            assignment_max_points = Fraction(assignment[c.ASSIGNMENT_MAX_POINTS])
            if assignment_category == category_name and assignment_max_points != Fraction('0.0'):
                return True
        #otherwise, return False
        return False

    #return the percent change in the category 1 point in the assignment makes
    #   at the categories minimum percent configuration
    #   (all assignments in assignments have been graded (and recieved a 0))
    def assignmentWeightInCategory(self, category):
        category_max = Fraction(category[c.CATEGORY_MAX_POINTS])
        for assignment in self.assignments:
            if not self.isAssignmentGraded(assignment):
                category_max += Fraction(assignment[c.ASSIGNMENT_MAX_POINTS])
        #for each percent on the assignment, how many points will the category grade
        #    change
        assignment_weight_in_category = Fraction('1.0') / category_max
        return assignment_weight_in_category

#===============================================================================
## ASSIGNMENT DELTAS

    #return the change made to the total grade by assignment
    #    (with score assignment_score)
    def assignmentDelta(self, assignment_index):
        assignment_weight = self.assignment_weights[assignment_index]
        assignment_score = self.assignment_scores[assignment_index]
        assignment_delta = assignment_score * assignment_weight * 100
        return assignment_delta

    #the sum of assignment deltas not including assignment at self.dependent_assignment_index
    def otherAssignmentDeltas(self):
        i = 0
        other_assignment_deltas = 0
        for delta in self.assignment_deltas:
            if i != self.dependent_assignment_index:
                other_assignment_deltas += delta
            i += 1
        return other_assignment_deltas

#===============================================================================
## SCORE CALCULATION

    def minPercent(self):
        min_percent = 0
        for category in self.categories:
            if category[c.CATEGORY_NAME] != c.TOTAL_CATEGORY and self.isCategoryActive(category):
                min_percent += self.minCategoryPercent(category) * self.categoryWeight(category)
        return min_percent

    def minCategoryPercent(self, category):
        category_points = self.categoryPoints(category)
        return category_points['score'] / category_points['max'] * 100

#===============================================================================
## SCORE CALCULATION

    def getNeededScore(self):
        self.assureVariablesInitialized()
        #the percent if all assignments were to recieve 0 points
        min_percent = self.minimum_percent
        #the change in the min_percent when assignments have assignment_scores
        #   (should give a value from 0-100 under normal circumstances)
        other_assignment_deltas = self.other_assignment_deltas
        #how many points change in the overall grade per point change in the assignment
        assignment_weight = self.assignment_weights[self.dependent_assignment_index]
        #how much of a change in grade percent is needed, accounting for points in assignment_scores
        delta_needed = self.target_percent - min_percent - other_assignment_deltas
        #the number of points needed on the assignment
        points_needed = (delta_needed / assignment_weight) / Fraction('100.0')
        points_needed = self.decimal(points_needed)
        return str(points_needed)

    def assureVariablesInitialized(self):
        #make sure the following variables have been initialized
        assert self.categories
        assert self.target_percent
        assert self.assignments
        #if self.depenendent_assignment_index is not initialized, set it to 0
        try:
            assert self.dependent_assignment_index
        except AssertionError:
            self.dependent_assignment_index = 0
        #if assignment_scores is not initialized set it to a blank list
        try:
            assert self.assignment_scores
        except AssertionError:
            self.assignment_scores = []

    def getNeededPercent(self):
        needed_score = self.getNeededScore()
        assignment = self.assignments[self.dependent_assignment_index]
        assignment_max_points = Fraction(assignment[c.ASSIGNMENT_MAX_POINTS])
        try:
            needed_percent = needed_score / assignment_max_points * Fraction('100.0')
        except ZeroDivisionError:
            return 'N/A (out of zero points)'
        needed_percent = decimal(needed_percent)
        return str(needed_percent)
    
    #convert a Fraction to a Decimal (approximate)
    def decimal(self, fraction):
        return Decimal(fraction.numerator) / Decimal(fraction.denominator)

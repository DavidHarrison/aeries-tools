#!/usr/bin/python2

import math

import NeededGrade

class Move:

    global FLOAT_ACCURACY

    global base_move_deltas
    global target_percent
    global assignment
    global gradebook_categories
    global assignments

    # TODO, fix, will only work if assignment is the last element of assignments
    def __init__(self, target_percent, assignment, gradebook_categories, assignments):
        self.target_percent = target_percent
        self.assignment = assignment
        self.gradebook_categories = gradebook_categories
        self.assignments = assignments
        self.FLOAT_ACCURACY = 4

    def initMoveDeltas(self, dimensions, move_specificity):
        # remove a dimension, which will be calculated
        dimensions -= 1
        self.base_move_deltas = self.getMoveDeltas(dimensions, move_specificity)

    def getMoves(self, current_position, maximum_delta):
        base_moves = self.applyDeltas(current_position, self.base_move_deltas, maximum_delta)
        moves = self.applyCalculatedAssignment(base_moves)
        return moves

    def applyDeltas(self, base_position, move_deltas, maximum_delta):
        moves = []
        for delta in move_deltas:
            move = self.applyDelta(base_position, delta, maximum_delta)
            moves.append(move)
        return moves

    def applyDelta(self, base_position, delta, maximum_delta):
        copy_position = list(base_position)
        i = 0
        while i < len(delta):
            copy_position[i] = str(float(copy_position[i]) + delta[i]*maximum_delta)
            i += 1
        return copy_position

    def applyCalculatedAssignment(self, base_moves):
        copy_moves = list(base_moves)
        last_dimension = len(base_moves[0]) - 1
        for move in copy_moves:
            needed_score = NeededGrade.getNeededPercent(self.target_percent,
                                                        self.assignment,
                                                        self.gradebook_categories,
                                                        assignments=self.assignments,
                                                        assignment_percents=move)
            move[last_dimension] = needed_score
        return copy_moves

    # TODO, remove repeated moves from their source
    def getMoveDeltas(self, dimensions, move_specificity):
        move_deltas = self.firstLevelMoveDeltas(dimensions)
        specificity = 1
        while specificity < move_specificity:
            specificity += 1
            adjacent_point_pairs = self.getAdjacentPointPairs(move_deltas)
            for pair in adjacent_point_pairs:
                new_move = self.getEdgeMidpoint(pair)
                # removes repeated moves
                if not new_move in move_deltas:
                    move_deltas.append(new_move)
        return move_deltas
    
    def firstLevelMoveDeltas(self, dimensions):
        i = 0
        first_level_deltas = []
        while i < dimensions:
            j = 0
            move_plus = []
            move_minus = []
            while j < dimensions:
                if j == i:
                    move_plus.append(1.0)
                    move_minus.append(-1.0)
                else:
                    move_plus.append(0.0)
                    move_minus.append(0.0)
                j += 1
            first_level_deltas.append(move_plus)
            first_level_deltas.append(move_minus)
            i += 1
        return first_level_deltas

    def getAdjacentPointPairs(self, move_deltas):
        adjacent_point_pairs = []
        done_points = []
        for point in move_deltas:
            adjacent_points = self.getAdjacentPoints(point, move_deltas)
            for adjacent_point in adjacent_points:
                if not (adjacent_point in done_points):
                    adjacent_point_pairs.append([point, adjacent_point])
            done_points.append(point)
        return adjacent_point_pairs

    # TODO, get points not on the same dimensional band as the center_point
    #   (need to allow a range of distances, with the greatest being the furthest
    #   adjacent point)
    def getAdjacentPoints(self, center_point, all_points):
        min_distance = None
        for point in all_points:
            if point == center_point:
                continue
            point_distance = self.distance(center_point, point)
            if min_distance == None or self.floatLess(point_distance, min_distance):
                min_distance = point_distance
                adjacent_points = [point]
            if self.floatEquals(point_distance, min_distance):
                adjacent_points.append(point)
        return adjacent_points

    def distance(self, point1, point2):
        distance_squared = 0
        dimension = 0
        while dimension < len(point1):
            distance_squared += (point1[dimension] - point2[dimension])**2 
            dimension += 1
        return math.sqrt(distance_squared)

    def floatLess(self, float1, float2):
        if (not self.floatEquals(float1, float2)) and float1 < float2:
            return True
        else:
            return False

    def floatEquals(self, float1, float2):
        if round(float1, self.FLOAT_ACCURACY) == round(float2, self.FLOAT_ACCURACY):
            return True
        else:
            return False

    def getEdgeMidpoint(self, pair):
        point1 = pair[0]
        point2 = pair[1]
        midpoint = []
        i = 0
        while i < len(point1):
            average_coordinate = (point1[i] + point2[i]) / 2
            midpoint.append(average_coordinate)
            i += 1
        edge_midpoint = self.getClosestEdgePoint(midpoint)
        return edge_midpoint

    # TODO, calculate rather than guess and check for solution
    def getClosestEdgePoint(self, internal_point):
        edge_point = list(internal_point)
        distance = 1
        #far too slow
        #distance_increment = 1 / 10**self.FLOAT_ACCURACY
        distance_increment = .001
        while self.distanceFromOrigin(edge_point) < 1:
            distance += distance_increment
            dimension = 0
            while dimension < len(edge_point):
                edge_point[dimension] *= distance
                dimension += 1
        return edge_point

    def distanceFromOrigin(self, point):
        origin = []
        for dimension in point:
            origin.append(0)
        return self.distance(origin, point)

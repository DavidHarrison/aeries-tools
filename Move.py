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

    def getMoveDeltas(self, num_dimensions, move_specificity):
        delta_angles = []
        dimension_num = 0
        blank_coord = []
        #last part of the coordinate is the radius (in this case 1)
        num_angles = num_dimensions - 1
        polar_coords = self.getAngles(blank_coord, num_angles, move_specificity)
        cartesian_coords = []
        for coord in polar_coords:
            #base radius
            coord.append(1)
            #print "Polar Coord: " + str(coord)
            cartesian_coords.append(self.cartesian(coord))
        return cartesian_coords

    def getAngles(self, partial_coord, num_angles, moves_per_angle):
        if len(partial_coord) == num_angles:
            return [partial_coord]
        coords = []
        angle_increment = 2 * math.pi / moves_per_angle
        angle = 0
        while self.floatLess(angle, 2 * math.pi):
            coord = list(partial_coord)
            coord.append(angle)
            coords += self.getAngles(coord, num_angles, moves_per_angle)
            angle += angle_increment
        return coords

    def cartesian(self, polar_coordinate):
        #length of a polar and cartesian coordinates are the same
        num_dimensions = len(polar_coordinate)
        #number of angles in the polar coordinate
        num_angles = num_dimensions - 1
        #radius is the last element of the polar coordinate
        radius = polar_coordinate[num_dimensions - 1]
        cartesian_coordinate = []
        dimension = 0
        while dimension < num_dimensions:
            d_vector = radius
            i = 0
            #multiply by every cosine up to the 
            while i < num_angles - dimension:
                d_vector *= math.cos(polar_coordinate[i])
                i += 1
            #if not the first dimension, which is entirely cosine
            if dimension != 0:
                #multiply the vector by the sine of the num_angles - dimension
                d_vector *= math.sin(polar_coordinate[num_angles - dimension])
            cartesian_coordinate.append(d_vector)
            dimension += 1
        return cartesian_coordinate

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

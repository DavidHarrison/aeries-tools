#!/usr/bin/python2

import math

class Move:

    global base_move_deltas

    #create and store a list of deltas in all directions for dimensions,
    #   with move_specificity angles per (dimensions - 1)
    #   (unit object (circle, sphere, etc.) made with trig and base radius of 1)
    def __init__(self, dimensions, move_specificity):
        self.base_move_deltas = self.getMoveDeltas(dimensions, move_specificity)

    #return the move with all base deltas applied, multplied by the maxium delta
    def getMoves(self, current_position, maximum_delta):
        moves = self.applyDeltas(current_position, self.base_move_deltas, maximum_delta)
        return moves

    #apply the base deltas to a list of positions
    def applyDeltas(self, base_position, move_deltas, maximum_delta):
        moves = []
        for delta in move_deltas:
            move = self.applyDelta(base_position, delta, maximum_delta)
            moves.append(move)
        return moves

    #apply the base deltas to a position
    def applyDelta(self, base_position, delta, maximum_delta):
        copy_position = list(base_position)
        i = 0
        while i < len(delta):
            copy_position[i] = str(float(copy_position[i]) + delta[i] * maximum_delta)
            i += 1
        return copy_position

    #get the base moves around a unit (circle, sphere, etc.)
    def getMoveDeltas(self, num_dimensions, move_specificity):
        delta_angles = []
        blank_coord = []
        #last part of the coordinate is the radius (in this case 1)
        num_angles = num_dimensions - 1
        polar_coords = self.getAngles(blank_coord, num_angles, move_specificity)
        cartesian_coords = []
        for coord in polar_coords:
            #base radius
            coord.append(1.0)
            #print "Polar Coord: " + str(coord)
            cartesian_coords.append(self.cartesian(coord))
        return cartesian_coords

    #get the angles around the unit (circle, sphere, etc.)
    def getAngles(self, partial_coord, num_angles, moves_per_angle):
        if len(partial_coord) == num_angles:
            return [partial_coord]
        coords = []
        angle_increment = 2.0 * math.pi / moves_per_angle
        angle = 0.0
        while angle < 2.0 * math.pi:
            coord = list(partial_coord)
            coord.append(angle)
            coords += self.getAngles(coord, num_angles, moves_per_angle)
            angle += angle_increment
        return coords

    #transform polar_coordinate into cartesian coordinates
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
            #vector for the current dimension
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

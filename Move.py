#!/usr/bin/python2

import math

import NeededGrade

#-------------------------------------------------------------------------------

class Move:

    global base_move_deltas
    global target_percent
    global assignment
    global gradebook_categories
    global assignments

    def __init__(target_percent, assignment, gradebook_categories, assignments):
        self.target_percent = target_percent
        self.assignment = assignment
        self.gradebook_categories = gradebook_categories
        self.assignemnts = self.assignemnts

    def initMoveDeltas(self, maximum_vector_distance, dimensions,
                        moves_per_dimension):
        blank_move = []
        self.base_move_deltas = getMoveDeltas(blank_move,
                                                maximum_vector_distance,
                                                dimensions,
                                                moves_per_dimension)

    def getMoves(self, current_position)
        base_moves = applyDeltas(current_position, self.base_move_deltas)
        moves = applyCalculatedAssignment(base_moves)
        return moves

    def applyDeltas(base_position, move_deltas):
        moves = []
        for delta in move_deltas:
            move = applyDelta(base_position, delta)
            moves.append(move)
        return moves

    def applyDelta(base_position, delta):
        copy_position = list(base_position)
        i = 0
        while i < len(delta):
            copy_position[i] += delta[i]
        return copy_position

    def applyCalculatedAssignment(base_moves):
        copy_moves = list(base_moves)
        for move in copy_moves:
            needed_score = NeededGrade.getNeededPercent(self.target_percent,
                                                        self.assignment,
                                                        self.gradebook_categories,
                                                        assignments=self.assignments,
                                                        assignment_scores=move):
            move.append(needed_score)
        return copy_moves

    def getMoveDeltas(self, partial_move, remaining_vector_distance,
                        dimensions, moves_per_dimension):
        if len(partial_move) == dimensions:
            # return partial_move as the only one in a list of moves
            return [partial_move]
        move_deltas = []
        i = 0
        increment = math.pi / (moves_per_dimension - 1)
        # relatively safe float comparision,
        #   making sure that i does not exceed moves_per_dimension
        while (math.pi - i) < (0.5 * increment):
            #copy partial move
            new_partial_move = list(partial_move)
            # multiply the remaining distance by a value ranging from -1 to +1
            #   (cosine's range from 0 to pi)
            dimension_delta = math.cos(i) * remaining_vector_distance
            new_remaining_vector_distance = getRemainingDistance(
                                                remaining_vector_distance,
                                                dimension_delta)
            new_partial_move.append(move_delta)
            #keeps all moves on the same level of list
            move_delta += getMoveDeltas(partial_move)
            i += increment
        return move_deltas

    # use Pythagorean theorem to calculate the remaining leg,
    #   which is the new remaining_vector_distance
    def getRemainingDistance(self, current_remaining_distance, subtract_distance):
        try:
            new_remaining_vector_distance = math.sqrt(current_remaining_distance**2 - subtract_distance**2)
        #if math.sqrt fails because it was operating on a negative number,
        #   subtract_distance must be larger than current_remaining_distance
        #   assume that this is attributable to float calculation error and
        #   two are the same
        except ValueError:
            new_remaining_vector_distance = 0.0
        return new_remaining_vector_distance

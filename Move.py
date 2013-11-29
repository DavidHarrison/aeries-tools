#!/usr/bin/python2

import math

import NeededGrade

class Move:

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

    def initMoveDeltas(self, maximum_vector_distance, dimensions,
                        moves_per_dimension):
        blank_move = []
        # remove a dimension, which will be calculated
        dimensions -= 1
        self.base_move_deltas = self.getMoveDeltas(blank_move,
                                                    maximum_vector_distance,
                                                    dimensions,
                                                    moves_per_dimension)

    def getMoves(self, current_position):
        base_moves = self.applyDeltas(current_position, self.base_move_deltas)
        moves = self.applyCalculatedAssignment(base_moves)
        return moves

    def applyDeltas(self, base_position, move_deltas):
        moves = []
        for delta in move_deltas:
            move = self.applyDelta(base_position, delta)
            moves.append(move)
        return moves

    def applyDelta(self, base_position, delta):
        copy_position = list(base_position)
        i = 0
        while i < len(delta):
            copy_position[i] = str(float(copy_position[i]) + delta[i])
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
                                                        assignment_scores=move)
            move[last_dimension] = needed_score
        return copy_moves

    # TODO, use function that will give same values for each dimension
    #   currently, the function should work, and gives a range of -1 to 1
    #   for each dimension, though not with the same intervals
    def getMoveDeltas(self, partial_move, remaining_vector_distance,
                        dimensions, moves_per_dimension):
        if len(partial_move) == dimensions - 1:
            final_move = list(partial_move)
            final_move.append(round(remaining_vector_distance, 4))
            # return partial_move as the only one in a list of moves
            return [final_move]
        move_deltas = []
        percent = -1
        increment = 2.0 / (float(moves_per_dimension) - 1.0)
        # relatively safe float comparision,
        #   making sure that the number of repetitions does not
        #   exceed moves_per_dimension
        while (1 - percent) > -(0.5*increment):
            #copy partial move
            new_partial_move = list(partial_move)
            # multiply the remaining distance by a value ranging from -1 to +1
            #   (cosine's range from 0 to pi)
            dimension_delta = round(percent * remaining_vector_distance, 4)
            new_remaining_vector_distance = self.getRemainingDistance(
                                                remaining_vector_distance,
                                                dimension_delta)
            new_partial_move.append(dimension_delta)
            #keeps all moves on the same level of list
            move_deltas += self.getMoveDeltas(new_partial_move,
                                                new_remaining_vector_distance,
                                                dimensions,
                                                moves_per_dimension)
            percent += increment
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

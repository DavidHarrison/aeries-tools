# Optimal Grades
- Calculate the optimal grades (as defined relative to distance squared from the average for the category) for a given set of assignments for achieving a target grade

## Calculate the grade given assignment grades

	P_target = P_min + Delta P_min_total

P_target - target percentage (given)

P_min - minimum percentage when all assignments from the given set have been graded (meaning that each assignment recieves a score of 0%)

	P_min = sum(P_c_X)

P_c_X - the minimum final percentage in a category X (including all assignments and assuming that they recieve a score of 0)

Delta P_min_total - the total change in the grade (from all assignments in the given set)

	Delta P_min_total = sum(P_min_X)

Delta P_min_X - change in the final grade resulting from the assignments grade X, with base point of P_min

	Delta P_min_X = W_eff_X x S_X

W_eff_X - the effective weight of the assignment X (how many percentage points change in the total for each changed in the assignment)

	W_eff_X - W_c x W_a

W_c - actual weight of the category

	W_c = theoretical weight * (1/weighting used (including all currently active and assignment set categories))

W_a - the weight of the assignment in the category 

	W_a = max points of the assignment / max points of category (including assignments in set)

S_X - score (in percent) of assignment X (given in assignment)

## Cost of a set of percentages for the assignment set

	D = sqrt(sum((S_X - A_c_X)^2)) #sqrt can be dropped given that D is being minimized

D - the cost (given by the distance of the scores from their averages) of the percentage set for the assignment set (will be minimized)

S_X - see above

A_c_X - the average grade (in percent) for the category as it stands (do not assume scores for ungraded assignments) (given)

## Minimizing the cost of the set of percentages

1. determine a reasonable starting grade set (eg target grade for all but last assignment (for which the grade will be calculated))
2. get a set of possible changes (each moving a constant vector distance from the current point/set) (+/- for 2 assignments, circle for 3 assignments, sphere for 4 assignments etc.) (dimensions = assignments - 1 (one assignment grade must be calculated in order to keep the set meeting the target grade))
3. for each of this set of changes, calculate the last position needed to keep the final grade at the target grade
4. calculate the cost for each of the possible new positions
5. find the position with the lowest cost
	- if the current position is the lowest, return this value, as it at least a local minima (and ideally, not far from the absolute minima in cost)
	- if the lowest cost is another position, move to it and repeat steps 2-5

## Calculating possible moves

- all vectors should be of the same given length
1. find all possibilities for the first dimension's move
2. make a list of all of these moves
3. for each list, find the second possibilities moves, do this recursively until all dimensions (excepting the calculated one) have been found

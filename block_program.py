#!/usr/bin/python
"""	Nathaniel Lim
	
	Block Problem: with a nice Dynamic Programming Solution
	
	When you run:  ./block_program.py 48 10
	It prints the number of ways you can pile up 10 layers of blocks with each layer 48 units long comprised of 3 x 1 and 4.5 x 1 unit blocks such that adjacent layers do no have inter-block junctions at the same positions.
	
	Timing Results:

		nathaniel@nathaniel-MXC062:~$ time ./block_program.py 48 10
		806844323190414

		real	0m5.524s
		user	0m2.392s
		sys	    0m0.176s
"""

import os
import sys
import threading
import time

# Misc. functions:
"""
	blocksLeft: 	a list of widths of blocks yet to be used to fufill the desired total width
	currentOrder:	a list of widths of blocks already chosen
	
	returns (recursively) all the possible ways blocks of the two different widths can be ordered, given 
		the choices already made
"""
def permutations(blocksLeft, currentOrder):
	if len(blocksLeft) == 0:
		return currentOrder
	elif not (w1 in blocksLeft):
		return [currentOrder + blocksLeft]
	elif not (w2 in blocksLeft):
		return [currentOrder + blocksLeft]
	else:
		first_blocksLeft, second_blocksLeft =  blocksLeft[:], blocksLeft[:]
		first_currentOrder, second_currentOrder = currentOrder[:], currentOrder[:]		
		#Choose a 3.0 width block
		first_blocksLeft.remove(w1)
		first_currentOrder.append(w1)		
		#Choose a 4.5 width block
		second_blocksLeft.remove(w2)
		second_currentOrder.append(w2)
		#Add up the permutations when you make these choices, and return	
		return permutations(first_blocksLeft, first_currentOrder) + permutations(second_blocksLeft, second_currentOrder)
"""
	Generates a list of block widths, from the number of each type	
	Calls permutations on this list, and an empty list (no choices yet)
"""
def get_permutations(n1, n2):
	blockList = []
	for i in range(1, n1+1): blockList.append(w1)
	for i in range(1, n2+1): blockList.append(w2)
	return permutations(blockList, [])

""" 	Converts to a different representation of a row:  List of block widths --> List of block ends	"""	
def end_spots(row):
	out = []
	for i in range(0, len(row)):
		if i == 0:
			out.append(row[i])
		else:
			out.append(out[i-1] + row[i]) 
	return out


""" A Thread that performs the final step in creating one of the rows of: adj_valid_matrix """
class MatrixBuilder(threading.Thread):
	def __init__(self, row):
		threading.Thread.__init__(self)
		self.row = row
	def run(self):
		#Look up collision points for a given row,
		adj_valid_matrix[self.row] = set(range(0, len(all_ordered_ways) -1))
		for c in row_to_cps[self.row]:
			#Remove all rows that have these collision point from the adj_valid_matrix
			adj_valid_matrix[self.row] -= cp_to_rows[c]


""" --------------Program Starts ----------------- """
program_start = time.time()
#print "Start:\t%f" % program_start

d = 1.0
w1 = 3.0
w2 = 4.5
verbose = True


""" block_program.py [W] [H] [-v]  """
if len(sys.argv) < 3: 
	sys.exit('Please Rerun and Enter:  \n\t [Width] [Height] \nof the desired panel as floating point numbers')
if len(sys.argv) > 3:
	if sys.argv[3] == '-v':
		verbose = True
depth = float(sys.argv[2])
width = float(sys.argv[1])
layers = int(depth/d)

max3  = int(width/3) + 1
max45 = int(width/4.5) + 1
""" Create a Dictionary:  Desired Row Width --> List of tuples: (num 3.0 blocks, num 4.5 blocks) """
rowways = {}
for i in range(0, max3):
	for j in range(0, max45):
		total = w1*i + w2*j
		if not (total in rowways):
			rowways[total] = []
		rowways[total].append((i, j))

if verbose: print str(width) + ": " + str(rowways[width])
if verbose: print "Max 3 Blocks %d, Max 4.5 Blocks %d" % (max3, max45)
""" With the Desired Row Width: Collect all the permutations from all the possible (n1, n2) tuples """
""" And create two dictionaries: Collision Point --> list(Rows), Row --> list(Collision Points)    """
all_ordered_ways = []
cp_to_rows = {}
row_to_cps = {}
if not (width in rowways.keys()):
	sys.exit("0")
label = 0
for w in rowways[width]:			
	for x in get_permutations(w[0], w[1]):
		all_ordered_ways.append(x)
		#update maps
		es = end_spots(x)
		row_to_cps[label] = set(es)
		row_to_cps[label].remove(width)
		for i in range(0, len(es) -1 ):
			c = es[i]
			if not (c in cp_to_rows.keys()): cp_to_rows[c] = set([])
			cp_to_rows[c].add(label)
		label+=1

#Add a blank row
row_to_cps[len(all_ordered_ways)] = set([])
all_ordered_ways.append([])
	

if len(all_ordered_ways) <= 1: 
	sys.exit("There are no solutions")
else: one_row_ways = (len(all_ordered_ways)-1)
last_col = len(all_ordered_ways) - 1

m_build_start = time.time()
if verbose: print 'Time to build rows: ' + str(time.time() - program_start)

collide_points = cp_to_rows.keys()

""" Initialize the Adjacency Valid Matrix """
adj_valid_matrix = {}



""" Run a thread on each row, removing invalid rows to be next to in the Adjacency Valid Matrix """ 
all_threads = list(MatrixBuilder(r) for r in range(0, len(all_ordered_ways)))
for t in all_threads: t.start()
for t in all_threads: t.join()	
if verbose: print 'Time to build adj_valid_matrix: ' + str(time.time() - program_start)
""" Do a Dynamic Programming Algorithm,  Example Problem Table Created for Arguments:   15.0   5.0

			Previous Row Type (Represents a permutation)
		-------------------------------------------------------------------------
		| 	||  0	|   1	|   2	|   3	|   4	|   5	|   6	| Blank	|
		_________________________________________________________________________
		-------------------------------------------------------------------------
	   L	|   1	||  1	|   1	|   1	|   1	|   1	|   1	|   1	|   7	|
	   a	-------------------------------------------------------------------------
	   y	|   2	||  2	|   1	|   0	|   1	|   1	|   2	|   1	|   8	|
	   e	-------------------------------------------------------------------------
	   r	|   3	||  3	|   2	|   0	|   1	|   2	|   3	|   1	|   12	|
		-------------------------------------------------------------------------
		|   4	||  5	|   3	|   0	|   1	|   3	|   5	|   1	|   18	|
		-------------------------------------------------------------------------
		|   5	||  8	|   5	|   0	|   1	|   5	|   8	|   1	|   28	|
		-------------------------------------------------------------------------
"""
solver_start = time.time()
prob_table = {}
if layers > 0:
	""" Initialize the Problem Map """
	for i in range(1, layers + 1):
		prob_table[i] = {}
		for j in range(0, len(all_ordered_ways)):
			prob_table[i][j] = 0		
	prob_table[1][last_col] = 0
	""" Special (Base) Cases: 	
		1 Layer, Previous Row Specified: 	Ways = 1
		1 Layer, Blank Row Specified:		Ways = num(row_types)
	"""
	for j in range(0, last_col):
		prob_table[1][j] = 1
		prob_table[1][last_col] += 1
	""" General Case:			
		n > 1 Layers, Previous Row Specified:
			Sum up the Ways over all the VALID adjacent row_types as previous row, with n - 1 layers
		n > 1 Layers, Blank Previous Row Specifed: 
			Sum up the ways over all row_types specified, with n layers
	"""
	for i in range(2, layers +1):		
		for j in range(0, last_col):
			these_ways = 0	
			for k in adj_valid_matrix[j]:
				these_ways += prob_table[i-1][k]	
			prob_table[i][j] = these_ways
			prob_table[i][last_col] += these_ways
	
	print "%s" % prob_table[layers][last_col]
	if verbose: 
		print "Computing using DP Took: " +  str(time.time() - solver_start) + " seconds"
		print "Whole Program took: " +  str(time.time() - program_start) + " seconds"
else: 
	print "%s" % 0


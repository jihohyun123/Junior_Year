"""
COMS W4701 Artificial Intelligence - Homework 2 Programming

In this assignment you will implement and compare different
search strategies for solving the n-Puzzle, which is a generalization
of the 8 puzzle to squares of arbitrary size.

@author: Ji Ho Hyun (jh3888)
"""

import time

def state_to_string(state):
    row_strings = [" ".join([str(cell) for cell in row]) for row in state]
    return "\n".join(row_strings)


def swap_cells(state, i1, j1, i2, j2):
    """
    Returns a new state with the cells (i1,j1) and (i2,j2) swapped. 
    """
    value1 = state[i1][j1]
    value2 = state[i2][j2]
    
    new_state = []
    for row in range(len(state)): 
        new_row = []
        for column in range(len(state[row])): 
            if row == i1 and column == j1: 
                new_row.append(value2)
            elif row == i2 and column == j2:
                new_row.append(value1)
            else: 
                new_row.append(state[row][column])
        new_state.append(tuple(new_row))
    return tuple(new_state)


def get_successors(state):
    """
    This function returns a list of possible successor states resulting
    from applicable actions. 
    The result should be a list containing (Action, state) tuples. 
    For example [("Up", ((1, 4, 2),(0, 5, 8),(3, 6, 7))), 
                 ("Left",((4, 0, 2),(1, 5, 8),(3, 6, 7)))] 
    """
    child_states = []

    for row in range(len(state)):
        for column in range(len(state[row])):
            if state[row][column] == 0:
                if column < len(state)-1: # Left
                    new_state = swap_cells(state, row,column, row, column+1)
                    child_states.append(("Left",new_state))
                if column > 0: # Right
                    new_state = swap_cells(state, row,column, row, column-1)
                    child_states.append(("Right",new_state))
                if row < len(state)-1:   #Up
                    new_state = swap_cells(state, row,column, row+1, column)
                    child_states.append(("Up",new_state))
                if row > 0: # Down
                    new_state = swap_cells(state, row,column, row-1, column)
                    child_states.append(("Down", new_state))
                break
    return child_states

            
def goal_test(state):
    """
    Returns True if the state is a goal state, False otherwise. 
    """    
    counter = 0
    for row in state:
        for cell in row:
            if counter != cell:
                return False
            counter += 1
    return True

   
def bfs(state):
    """
    Breadth first search.
    Returns four values: A path (list of actions), path cost, the number of states expanded,
    and the maximum size of the frontier.
    You should also have two mutable data structures:
    - The frontier of nodes to expand (operating as a queue in BFS)
    - A set of nodes already expanded
    """
    states_expanded = 0
    max_frontier = 0
    frontier = []
    explored = set()
    #YOUR CODE HERE
    frontier_set = set()
    frontier.append(['', state, ''])
    frontier_set.add(state)
    max_frontier = 0
    while True:
        if not frontier:
            return None, 0, states_expanded, max_frontier
        if len(frontier) > max_frontier:
            max_frontier = len(frontier)
        cur = frontier.pop(0)
        frontier_set.remove(cur[1])
        if goal_test(cur[1]) == True:
            results = cur[2]+cur[0]
            path = []
            for y in results.split():
                path.append(y)
            return path, len(path), states_expanded, max_frontier    
        states_expanded = states_expanded + 1
        explored.add(cur[1])
        poss = get_successors(cur[1])
        for x in poss:
            if x[1] not in explored and x[1] not in frontier_set:
                y = []
                y.append(x[0])
                y.append(x[1])
                y.append(cur[2]+cur[0] + ' ')
                frontier.append(y)
                frontier_set.add(x[1])
            else:
                continue
    

    #  return path, path cost, num states expanded, max size of frontier
    return None, 0, states_expanded, max_frontier # No solution found
                               
     
def dfs(state):
    """
    Depth first search.
    Returns four values: A path (list of actions), path cost, the number of states expanded,
    and the maximum size of the frontier.
    You should also have two mutable data structures:
    - The frontier of nodes to expand (operating as a queue in BFS)
    - A set of nodes already expanded
    """
    states_expanded = 0
    max_frontier = 0
    frontier = []
    explored = set()
    #YOUR CODE HERE
    frontier_set = set()
    frontier.append(state)
    frontier_set.add(state)
    max_frontier = 0
    ancestry = dict()
    while True:
        if not frontier:
            return None, 0, states_expanded, max_frontier
        if len(frontier) > max_frontier:
            max_frontier = len(frontier)
        cur = frontier.pop()
        frontier_set.remove(cur)
        if goal_test(cur) == True:
            count = 0
            moves = []
            
            while True:
                #print(ancestry[cur])
                moves.append((ancestry[cur])[1])
                count +=1
                cur = (ancestry[cur])[0]
               
                if cur == (state):
                    break         
            #print(moves)
            moves.reverse()
            return moves, count, states_expanded, max_frontier
        
        states_expanded = states_expanded + 1
        explored.add(cur)
        poss = get_successors(cur)
        for x in poss:
            if x[1] not in explored and x[1] not in frontier_set:               
                frontier.append(x[1])
                frontier_set.add(x[1])
                ancestry.update({x[1] : (cur, x[0])})
            else:
                continue

    
    #  return path, path cost, num states expanded, max size of frontier
    return None, 0, states_expanded, max_frontier # No solution found


def misplaced_heuristic(state):
    """
    Returns the number of misplaced tiles.
    """
    counter = 0
    misplaced = 0
    for row in state:
        for cell in row:
            if cell == 0:
                cell = cell    
            elif counter != cell:
                misplaced += 1
            counter += 1
    return misplaced

    #YOUR CODE HERE
    #return 0 # replace this


def manhattan_heuristic(state):
    """
    For each misplaced tile, compute the Manhattan distance between the current
    position and the goal position. Then return the sum of all distances.
    """
        
    # YOUR CODE HERE
    correct = {}
    distance = 0
    solution = ((0, 1, 2),
              (3, 4, 5), 
              (6, 7, 8)) 
    y = 1
    for row in solution:
        x = -1
        for cell in row:
            correct.update({cell: (x, y)})
            x += 1
        y -= 1
    y2 = 1
    for row in state:
        x2 = -1
        for cell in row:
            if cell == 0:
                x2 += 1
            else:
                manhat = correct[cell]
                d = (abs(manhat[0] - x2), abs(manhat[1] - y2))
                distance = distance + d[0] + d[1]
                x2 += 1
        y2 -= 1

    return distance # replace this


def astar(state, heuristic):
    """
    A-star search.
    Returns four values: A path (list of actions), path cost, the number of states expanded,
    and the maximum size of the frontier.
    You should also have two mutable data structures:
    - The frontier of nodes to expand (operating as a queue in BFS)
    - A set of nodes already expanded
    """
    # Use these modules to maintain a priority queue
    from heapq import heappush
    from heapq import heappop

    states_expanded = 0
    max_frontier = 0
    frontier = []
    explored = set()
    #YOUR CODE HERE
    
    frontier_set = set()
    heappush(frontier, (heuristic(state), state, 0))
    frontier_set.add(state)
    max_frontier = 0
    ancestry = dict()
    while True:
        if not frontier:
            return None, 0, states_expanded, max_frontier
        if len(frontier) > max_frontier:
            max_frontier = len(frontier)
        cur = heappop(frontier)
        frontier_set.remove(cur[1])
        if goal_test(cur[1]) == True:
            count = 0
            moves = []
            action = cur[1]
            while True:
                moves.append((ancestry[action])[1])
                count +=1
                action = (ancestry[action])[0]   
                if action == (state):
                    break
            moves.reverse()         
            return moves, cur[2], states_expanded, max_frontier
        
        states_expanded = states_expanded + 1
        explored.add(cur[1])
        poss = get_successors(cur[1])
        for x in poss:
            if x[1] not in explored and x[1] not in frontier_set:               
                heappush(frontier, (heuristic(x[1]) + cur[2], x[1], cur[2]+1))
                frontier_set.add(x[1])
                ancestry.update({x[1] : (cur[1], x[0])})
            else:
                continue
    

    
    #  return path, path cost, num states expanded, max size of frontier
    return None, 0, states_expanded, max_frontier # No solution found


def print_result(path_cost, states_expanded, max_frontier):
    """
    Helper function to format test output.
    """
    print("Cost of path: {}".format(path_cost))
    print("States expanded: {}".format(states_expanded))
    print("Max frontier size: {}".format(max_frontier))



if __name__ == "__main__":

    #Easy test case
    test_state = ((1, 4, 2),
                  (0, 5, 8), 
                  (3, 6, 7))  
    #test_state = ((8, 1, 2),
    #              (0, 4, 3), 
    #              (7, 6, 5))  

    #More difficult test case
    test_state = ((7, 2, 4),
                  (5, 0, 6), 
                  (8, 3, 1))  
    
    print(state_to_string(test_state))
    print()

    print("====BFS====")
    start = time.time()
    path, path_cost, states_expanded, max_frontier = bfs(test_state)
    end = time.time()
    print("Path to goal: {}".format(path))
    print_result(path_cost, states_expanded, max_frontier)
    print("Total time: {0:.3f}s".format(end-start))

    print() 
    print("====DFS====")
    start = time.time()
    path, path_cost, states_expanded, max_frontier = dfs(test_state)
    end = time.time()
    print_result(path_cost, states_expanded, max_frontier)
    print("Total time: {0:.3f}s".format(end-start))
    
    print() 
    print("====A* (Misplaced Tiles Heuristic)====") 
    start = time.time()
    path, path_cost, states_expanded, max_frontier = astar(test_state, misplaced_heuristic)
    end = time.time()
    print("Path to goal: {}".format(path))
    print_result(path_cost, states_expanded, max_frontier)
    print("Total time: {0:.3f}s".format(end-start))

    print() 
    print("====A* (Total Manhattan Distance Heuristic)====") 
    start = time.time()
    path, path_cost, states_expanded, max_frontier = astar(test_state, manhattan_heuristic)
    end = time.time()
    print("Path to goal: {}".format(path))
    print_result(path_cost, states_expanded, max_frontier)
    print("Total time: {0:.3f}s".format(end-start))


from classes import *


class Solver:

    def __init__(self, iterations, tabu_tenure, first_x, goalfunction, verbosity=10):
        self.iterations = iterations
        self.tabu_tenure = tabu_tenure
        self.first_x = first_x
        self.goalfunction = goalfunction
        self.verbosity = verbosity

    def local_search(self, path):

        # read the pathname (a csv file) as an instance object
        instance = Instance(path)

        # intitialize the instance with a sorting rule
        instance.initialize(rule='EDD')

        # make a solution object from the initialized instance object
        # the solution object contains methods for efficiently calculating the goalfunction value
        current_solution = Solution(instance_df=instance.instance, rule=self.goalfunction)
        current_solution_numpy = current_solution.instance.values

        # make a solution memory object (this saves the search path)
        first_x_memory = []
        tabu_memory = []
        solution_path = []

        # initialize the tabu search operator, the operator is the move type and the move strategy
        operator = Operator(n=instance.n, move_type='swap', first_x=self.first_x)

        # initialize the local search object, this object contains methods to perform moves
        localsearch = LocalSearch(move_type='swap', rule=self.goalfunction)
        # calculate the first solution value
        first_goal = current_solution.calculate_goal_numpy(current_solution_numpy)
        best_solution_found = first_goal.copy()

        starttime = time.time()
        solution_path.append((first_goal, 0))
        # local search
        for it in range(self.iterations):

            ts = time.time() - starttime
            verbose = False
            if it % self.verbosity == 0:
                verbose = True

            if verbose:
                print(it, 'time: ', ts)

            # initialize a local memory, this will be wiped every iteration
            local_memory = []
            first_x_memory = []
            best_move = None  # no best move found by default
            best_goal = None

            # start evaluating the local neighbourhood
            for move in operator.movepool:

                goalval = localsearch.evaluate_neighbour(move=move, current_solution=current_solution_numpy)
                # Add each move to the local memory
                local_memory.append((goalval, move))  # list append most efficient in python vs numpy

                # check if the local neighbour is better than the current solution
                if goalval < solution_path[-1][0]:  # list indexing most efficient in python vs numpy
                    # check tabu status
                    if move in tabu_memory:
                        # check if the move leads to a better solution ever found,
                        if goalval < best_solution_found:
                            # ASPIRATION
                            best_move = move
                            best_goal = goalval
                            first_x_memory.append((best_goal, best_move))  # using normal lists has best efficiency for append and pop
                            best_solution_found = goalval

                            # break the search if the max amount of improvements is found
                            if len(first_x_memory) >= self.first_x:
                                break
                        # if the move is tabu and not better than the best found => No aspiration
                        else:
                            continue
                    else:
                        # The move is not on the tabu list, and can be accepted
                        best_move = move
                        best_goal = goalval
                        first_x_memory.append((best_goal, best_move))

                        # break the search if the max amount of improvement is found
                        if len(first_x_memory) >= self.first_x:
                            break

            # we are at the end of the local neighbourhood, check if an improving solution has been found
            if best_move is None:
                print('LOCAL OPTIMUM')
                # if no best move is found, then we are in a local optimum
                local_memory = sorted(local_memory, key=lambda key: key[0])  # sorted in increasing order
                while True:
                    best_move = local_memory[0][1]

                    if best_move not in tabu_memory:
                        best_goal = local_memory[0][0]
                        print('best move:', best_move, 'best goal: ', best_goal)
                        break
                    else:
                        local_memory.pop(0)

            # if the best move is not None, then we must evaluate the improvement memory
            if len(first_x_memory) > 0:
                # take the best move from the improvement memory
                first_x_memory = sorted(first_x_memory, key=lambda key: key[0])
                # all the moves in the improvement memory are already checked for tabu status
                best_move = first_x_memory[0][1]
                best_goal = first_x_memory[0][0]

            # we need to update the current solution with the best local neighbour
            current_solution_numpy = localsearch.perform_move(best_move, current_solution_numpy)
            solution_path.append((best_goal, ts))  # add the timestamp to the solution path
            # add the chosen move to the tabu memory
            tabu_memory.append(best_move)
            # remove an element from the tabu list if the tenure is exceeded
            if len(tabu_memory) >= self.tabu_tenure:
                tabu_memory.pop(0)

        return solution_path

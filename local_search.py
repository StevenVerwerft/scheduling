from classes import *


class Solver:

    def __init__(self, iterations, tabu_tenure, first_x, goalfunction, verbosity=None, n_time=None, random_order=False):
        self.iterations = iterations
        self.tabu_tenure = tabu_tenure
        self.first_x = first_x
        self.goalfunction = goalfunction  # e.g. Lmax
        self.verbosity = verbosity
        self.n_time = n_time
        self.random_order = random_order

    def local_search(self, path):

        if self.n_time is None:
            stopping_crit = 'iterations'
            max_time = np.inf

        elif self.n_time is not None:
            stopping_crit = 'time'
            max_time = int(self.n_time)

        # read the pathname of the instance
        instance = Instance(pathname=path)
        instance.initialize(rule='EDD')  # initializes the instance
        n = instance.get_instance_size()

        # get the first solution in array format
        current_solution = instance.get_current_solution_ndarray()

        # initialize the global memories
        tabu_memory = []
        solution_path = []

        # initialize the local search object (contains methods for goalfunction calculation and move application)
        localsearch = LocalSearch(move_type='swap', rule=self.goalfunction, n=n)
        movepool = localsearch.generate_movepool()

        # get the first solution
        first_goalvalue = localsearch.calculate_goal(current_solution=current_solution)
        best_found = first_goalvalue.copy()
        solution_path.append((first_goalvalue, 0))  # first goalvalue and intitial timestamp
        print(solution_path[-1][0])
        starttime = time.time()

        # perform the local search
        it = 0

        while True:  # stopping criterion at the end
            ts = time.time() - starttime
            verbose = False
            if self.verbosity is not None:
                if it % self.verbosity == 0:
                    verbose = True
            if verbose:
                print('it: ', it, 'time: ', round(ts, 2), 'goalfunction: ', round(solution_path[-1][0], 2))

            # initialize local memories
            local_memory = []
            first_x_memory = []

            best_move, best_goal = None, None

            for move in movepool:

                goalval = localsearch.evaluate_neighbour(move=move, current_solution=current_solution)
                local_memory.append((goalval, move))

                # if local neighbour better than current solution
                if goalval < solution_path[-1][0]:

                    # check if the move is on the tabu list
                    if move in tabu_memory:
                        # move is tabu
                        # check if aspiration criterion is met
                        if goalval < best_found:
                            # ASPIRATION
                            first_x_memory.append((goalval, move))

                            # check if the max length of first x memory is reached
                            if len(first_x_memory) >= self.first_x:
                                break  # break the local search and choose a new current solution

                            else:  # if aspiration and first x memory not full
                                continue  # continue to next move
                        else:
                            # move is tabu and no aspiration => continue to next move
                            continue

                    else:  # move is not tabu and improving => add to first x memory
                        first_x_memory.append((goalval, move))

                        # check if the first x memory is full
                        if len(first_x_memory) >= self.first_x:
                            break  # break the local search and choose a new current solution

                        else:  # if move improving and first x memory is not full
                            continue  # continue to the next move

            # end of local search

            # case 1: No best move is found => no improvement found => Local Optimum
            if best_move is None and len(first_x_memory) == 0:
                # local optimum
                local_memory = sorted(local_memory, key=lambda key: key[0])  # sort ascending on goalvalue

                while True:
                    # pick first solution from local memory that is not tabu
                    best_goal, best_move = local_memory[0][0], local_memory[0][1]

                    if best_move in tabu_memory:
                        # if move tabu, take second best
                        local_memory.pop(0)
                        continue
                    else:
                        # if move not tabu, break
                        break

            # case 2: At least one improvement is found => Take best solution from improvement memory
            if len(first_x_memory) > 0:
                # no local optimum
                first_x_memory = sorted(first_x_memory, key=lambda key: key[0])  # sort ascending on goalvalues
                best_goal, best_move = first_x_memory[0][0], first_x_memory[0][1]

            # end the iteration => update the current solution and tabu list
            current_solution = localsearch.perform_move(move=best_move, current_solution=current_solution)
            solution_path.append((best_goal, ts))
            tabu_memory.append(best_move)
            it += 1
            if self.random_order:
                # make a split point in the movepool and swap halves
                split = random.randint(0, len(movepool)-1)
                first = movepool[0: split]
                last = movepool[split:]
                last.extend(first)
                movepool = last

            # case 3: the goalvalue reaches optimality => lateness, tardiness, earliness = 0
            if best_goal <= 0:
                break  # break the tabu search

            # case 4: when the stopping criterium is true
            if stopping_crit == 'time':
                if ts >= max_time:
                    break
            if stopping_crit == 'iterations':
                if it >= self.iterations:
                    break

        return solution_path

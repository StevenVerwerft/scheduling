# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import time
import itertools
import datetime
import random
import os
import subprocess
# fix for MACOSX GUI crash
import sys

if sys.platform == 'darwin':
    import matplotlib

    matplotlib.use("TkAgg")  # use this backend to prevent macosX bug
    import matplotlib.pyplot as plt
    from tkinter import *
# Step 1: read the instance


class Instance:

    def __init__(self, pathname):
        self.pathname = pathname
        self.instance = pd.read_csv(pathname, sep=';', index_col=0)
        self.instance['permutation'] = np.arange(len(self.instance))
        self.instance = self.instance[['p_times', 'S_times', 'd_dates', 'groups', 'r_dates', 'permutation']]
        self.n = len(self.instance)

    def EDD(self):
        self.instance = self.instance.sort_values(by='d_dates')

    def ERD(self):
        self.instance = self.instance.sort_values(by='r_dates')

    def initialize(self, rule='EDD'):
        # this should result in a permutation that can be passed to the solution class
        if rule == 'EDD':
            self.EDD()
        elif rule == 'ERD':
            self.ERD()
        else:
            print('not a valid option')


class Solution:

    def __init__(self, instance_df, rule='Lmax'):
        self.instance = instance_df  # this is a dataframe of the instance
        self.permutation = self.instance.permutation  # get the current schedule from the instance dataframe
        self.instance_nd_array = self.instance.values  # convert the current schedule from a dataframe to nd array
        self.n = len(self.instance)
        self.rule = rule
        self.goaldic = self.calculate_goal()

    def calculate_goal_numpy(self, input_nd_array=None):

        n = self.n
        instance_nd_array = self.instance_nd_array

        if input_nd_array is not None:
            instance_nd_array = input_nd_array
            n = len(input_nd_array)

        blocks = np.ones(n)
        blocks[1:] = np.where(instance_nd_array[:-1, 3] == instance_nd_array[1:, 3], 0, 1)  # groups
        total_time = instance_nd_array[:, 0] + blocks * instance_nd_array[:, 1]
        completion_time = np.cumsum(total_time)
        earliness = np.maximum(instance_nd_array[:, 2] - completion_time, 0)
        tardiness = np.maximum(completion_time - instance_nd_array[:, 2], 0)
        lateness = earliness + tardiness


        Lmax, Tmax, Emax, Ltot, Ttot, Etot, Lnum, Tnum, Enum = 9*[None]

        if self.rule == 'Lmax':
            Lmax = self.goalfunction(array=lateness)
        elif self.rule == 'Tmax':
            Tmax = self.goalfunction(array=tardiness)
        elif self.rule == 'Emax':
            Emax = self.goalfunction(array=earliness)
        elif self.rule == 'Ltot':
            Ltot = self.goalfunction(array=lateness)
        elif self.rule == 'Ttot':
            Ttot = self.goalfunction(array=tardiness)
        elif self.rule == 'Etot':
            Etot = self.goalfunction(array=earliness)
        elif self.rule == 'Lnum':
            Lnum = self.goalfunction(array=lateness)
        elif self.rule == 'Tnum':
            Tnum = self.goalfunction(array=tardiness)
        elif self.rule == 'Enum':
            Enum = self.goalfunction(array=earliness)

        goaldic = {'Lmax': Lmax, 'Ltot': Ltot, 'Tmax': Tmax, 'Ttot': Ttot, 'Tnum': Tnum,
                   'Emax': Emax, 'Etot': Etot, 'Enum': Enum}

        return goaldic[self.rule]

    def calculate_goal(self, input_instance=None):

        if input_instance is None:
            __instance = self.instance.__deepcopy__()
        else:
            __instance = input_instance

        blocks = np.ones(len(__instance))
        blocks[1:] = np.where(__instance.groups.values[:-1] == __instance.groups.values[1:], 0, 1)
        __instance['g_sequence'] = blocks
        __instance['total_time'] = __instance.p_times + __instance.g_sequence * __instance.S_times
        __instance['completion_time'] = np.cumsum(__instance.total_time)
        __instance['earliness'] = np.maximum(__instance.d_dates - __instance.completion_time, 0)
        __instance['tardiness'] = np.maximum(__instance.completion_time - __instance.d_dates, np.zeros(len(__instance)))
        __instance['lateness'] = __instance.earliness + __instance.tardiness

        # calculate goalfunctions

        Lmax, Tmax, Emax, Ltot, Ttot, Etot, Lnum, Tnum, Enum = 9*[None]

        if self.rule == 'Lmax':
            Lmax = self.goalfunction(array=__instance.lateness)
        elif self.rule == 'Tmax':
            Tmax = self.goalfunction(array=__instance.tardiness)
        elif self.rule == 'Emax':
            Emax = self.goalfunction(array=__instance.earliness)
        elif self.rule == 'Ltot':
            Ltot = self.goalfunction(array=__instance.lateness)
        elif self.rule == 'Ttot':
            Ttot = self.goalfunction(array=__instance.tardiness)
        elif self.rule == 'Etot':
            Etot = self.goalfunction(array=__instance.earliness)
        elif self.rule == 'Lnum':
            Lnum = self.goalfunction(array=__instance.lateness)
        elif self.rule == 'Tnum':
            Tnum = self.goalfunction(array=__instance.tardiness)
        elif self.rule == 'Enum':
            Enum = self.goalfunction(array=__instance.earliness)

        goaldic = {'Lmax': Lmax, 'Ltot': Ltot, 'Tmax': Tmax, 'Ttot': Ttot, 'Tnum': Tnum,
                   'Emax': Emax, 'Etot': Etot, 'Enum': Enum}

        return goaldic[self.rule]

    def update_goal(self):
        self.goaldic = self.calculate_goal()

    def goalfunction(self, array):

        if self.rule in ['Lmax', 'Tmax', 'Emax']:
            return array.max()
        elif self.rule in ['Ltot', 'Ttot', 'Etot']:
            return array.sum()
        elif self.rule in ['Lnum', 'Tnum', 'Enum']:
            return np.count_nonzero(array)
        else:
            print('specify rule')
            print('rule = {\'max\', \'sum\', \'num\'}')
            return None


class Operator:

    def __init__(self, n, move_type='insert', first_x=5):
        """
        :param move_type: insert or swap
        :param first_x: amount of improvements
        :param n: size of the instance
        """
        self.move_type = move_type
        self.first_x = first_x
        self.n = n
        self.movepool = self.generate_movepool()
        print('length movepool: ', len(self.movepool))

    def generate_movepool(self):

        if self.move_type == 'swap':
            return [(i, j) for i in range(self.n - 1) for j in range(i+1, self.n)]
        if self.move_type == 'insert':
            return [i for i in itertools.permutations(range(self.n), 2)]

    def perform_move(self, pair, instance_object, move_type=None):

        if move_type is None:
            move_type = self.move_type

        if move_type not in ['swap', 'insert']:
            print('move type not implemented \n move type = swap | insert')
            return None

        if move_type == 'insert':
            return self.insert(pair=pair, instance_object=instance_object)
        elif move_type == 'swap':
            return self.swap(pair=pair, instance_object=instance_object)

    def swap(self, pair, instance_object):

        # swaps items on position x and y in instance object
        x, y = pair[0], pair[1]
        __instance = instance_object.instance.__deepcopy__()

        __instance.iloc[x, :], __instance.iloc[y, :] = \
            instance_object.instance.iloc[y, :], instance_object.instance.iloc[x, :]

        return __instance

    def insert(self, pair, instance_object):
        # inserts item on position x on position y
        x, y = pair[0], pair[1]
        __instance = instance_object.instance.values.__deepcopy__()

        # use numpy for the insert move
        values = __instance.values
        row = values[x]
        temp_values = np.delete(values, x, 0)  # delete this row from the ndarray
        temp_values = np.insert(temp_values, y, row, 0)  # insert the row on position y
        __instance.loc[:, :] = temp_values

        return __instance


class LocalSearch:

    def __init__(self, move_type, rule):
        self.move_type = move_type
        self.rule = rule

    def evaluate_neighbour(self, move, current_solution):
        """

        :param move: the move type to be performed on the current solution
        :param current_solution: an ndarray representation of the current solution
        :return: the goalfunction (and tabustatus)
        """
        x, y = move[0], move[1]
        local_solution = current_solution.copy()  # faster than deepcopy!

        if self.move_type == 'swap':
            # copy necessary to prevent overwriting of one of the swap rows
            local_solution[x, :], local_solution[y, :] = local_solution[y, :], local_solution[x, :].copy()
            goalvalue = self.calculate_goal_numpy(current_solution=local_solution)
            return goalvalue

        if self.move_type == 'insert':
            pass

    def perform_move(self, move, current_solution):
        x, y = move[0], move[1]
        current_solution = current_solution.copy()

        if self.move_type == 'swap':
            current_solution[x, :], current_solution[y, :] = current_solution[y, :], current_solution[x, :].copy()
            return current_solution

        if self.move_type == 'insert':
            pass

    def calculate_goal_numpy(self, current_solution):

        n = len(current_solution)
        blocks = np.ones(n)
        blocks[1:] = np.where(current_solution[:-1, 3] == current_solution[1:, 3], 0, 1)  # groups
        total_time = current_solution[:, 0] + blocks * current_solution[:, 1]
        completion_time = np.cumsum(total_time)
        earliness = np.maximum(current_solution[:, 2] - completion_time, 0)
        tardiness = np.maximum(completion_time - current_solution[:, 2], 0)
        lateness = earliness + tardiness

        Lmax, Tmax, Emax, Ltot, Ttot, Etot, Lnum, Tnum, Enum = 9 * [None]

        if self.rule == 'Lmax':
            Lmax = self.goalfunction(array=lateness)
        elif self.rule == 'Tmax':
            Tmax = self.goalfunction(array=tardiness)
        elif self.rule == 'Emax':
            Emax = self.goalfunction(array=earliness)
        elif self.rule == 'Ltot':
            Ltot = self.goalfunction(array=lateness)
        elif self.rule == 'Ttot':
            Ttot = self.goalfunction(array=tardiness)
        elif self.rule == 'Etot':
            Etot = self.goalfunction(array=earliness)
        elif self.rule == 'Lnum':
            Lnum = self.goalfunction(array=lateness)
        elif self.rule == 'Tnum':
            Tnum = self.goalfunction(array=tardiness)
        elif self.rule == 'Enum':
            Enum = self.goalfunction(array=earliness)

        goaldic = {'Lmax': Lmax, 'Ltot': Ltot, 'Tmax': Tmax, 'Ttot': Ttot, 'Tnum': Tnum,
                   'Emax': Emax, 'Etot': Etot, 'Enum': Enum}

        return goaldic[self.rule]

    def goalfunction(self, array):

        if self.rule in ['Lmax', 'Tmax', 'Emax']:
            return array.max()
        elif self.rule in ['Ltot', 'Ttot', 'Etot']:
            return array.sum()
        elif self.rule in ['Lnum', 'Tnum', 'Enum']:
            return np.count_nonzero(array)
        else:
            print('specify rule')
            print('rule = {\'max\', \'sum\', \'num\'}')
            return None


class SolutionItem:

    def __init__(self, goalvalue, timestamp, move_pair, move_type):
        self.goalvalue = goalvalue
        self.timestamp = timestamp
        self.move_pair = move_pair
        self.move_type = move_type

    def __str__(self):
        return'Solution(goal: {0}, ts: {1}, pair: {2}, type: {3})'.format(self.goalvalue,
                                                                          self.timestamp,
                                                                          self.move_pair,
                                                                          self.move_type)

    def __repr__(self):
        return str(self)


class Memory:

    def __init__(self, max_length=None):
        self.memory = []
        self.max_length = max_length

    def append(self, item):
        self.memory.append(item)

    def delete(self, item):
        try:
            self.memory.remove(item)
        except ValueError:
            print('item not in memory')
            pass

    def delete_first(self):
        self.memory.pop(0)

    def delete_random(self):
        self.memory.pop(np.random.randint(0, len(self.memory)))

    def wipe_memory(self):
        self.memory = []


class SolutionMemory(Memory):

    def __init__(self, max_length=None):
        self.best_solution = None
        super().__init__(max_length)

    def append(self, SolutionItem):

        # If the memory is empty, the first added solution is the best
        if self.best_solution is None:
            self.best_solution = SolutionItem

        if SolutionItem.goalvalue < self.best_solution.goalvalue:
            self.best_solution = SolutionItem

        self.memory.append(SolutionItem)

    def wipe_memory(self):
        self.best_solution = None
        self.memory = []


if False:
    path = 'test_instances/test2/replicate_1.csv'

    instance = Instance(path)  # read the instance from the selected path
    instance.initialize(rule='EDD')  # initialize the schedule by the EDD rule

    # create the first solution
    # when the solution object initializes, its goalvalue is calculated by default
    rule = 'Tmax'
    current_solution = Solution(instance_df=instance.instance, rule=rule)

    # initialize memory object for local search
    SOLUTION_MEMORY = Memory()

    # initialize operator object for local search
    OPERATOR = Operator(n=instance.n, move_type='swap', first_x=1)
    FIRST_X_MEMORY = SolutionMemory(max_length=OPERATOR.first_x)
    start_time = time.time()
    max_iter = 1000

    solution_path = []
    first_goal = current_solution.calculate_goal_numpy()
    solution_path.append(first_goal)
    tabu_memory = []
    current_solution_numpy = current_solution.instance.values

    for it in range(max_iter):
        ts = time.time() - start_time
        verbose = False
        if it % 5 == 0:
            verbose = True

        if verbose:
            print(it, ts)
        # search until better solution is found
        LOCALSEARCH = LocalSearch(move_type=OPERATOR.move_type, rule=rule)
        local_memory = []
        best_move = None  # by default no best move is found

        for move in OPERATOR.movepool:

            goalval = LOCALSEARCH.evaluate_neighbour(move=move, current_solution=current_solution_numpy)
            local_memory.append((goalval, move))

            if goalval < solution_path[-1]:
                # check if best move is tabu
                if move in tabu_memory:
                     continue
                else:
                    best_move = move
                    best_goal = goalval

        if best_move is None:
            print('LOCAL OPTIMUM')
            local_memory = sorted(local_memory, key=lambda x: x[0])
            while True:
                candidate = local_memory[0]
                if candidate[1] in tabu_memory:
                    local_memory.pop(0)
                    continue
                else:
                    best_move = candidate[1]
                    best_goal = candidate[0]
                    break

        # replace current solution by the best solution found in the local neighbourhood
        if verbose:
            print('best move', best_move)
            print('best goal', best_goal)

        current_solution_numpy = LOCALSEARCH.perform_move(move=best_move, current_solution=current_solution_numpy)
        solution_path.append(best_goal)

        # update tabulist
        if len(tabu_memory) > int(len(OPERATOR.movepool)*0.10):
            tabu_memory.pop(0)
        tabu_memory.append(best_move)


    plt.plot(np.arange(len(solution_path)), solution_path)
    plt.show()
    quit()

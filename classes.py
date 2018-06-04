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

if sys.platform == 'win32':
    import matplotlib.pyplot as plt
    from tkinter import *

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

    def get_current_solution_ndarray(self):
        return self.instance.values

    def get_instance_size(self):
        return self.n


class Solution:

    def __init__(self, instance_df, rule='Lmax'):
        self.instance = instance_df  # this is a dataframe of the instance
        self.permutation = self.instance.permutation  # get the current schedule from the instance dataframe
        self.instance_nd_array = self.instance.values  # convert the current schedule from a dataframe to nd array
        self.n = len(self.instance)
        self.rule = rule

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
                   'Emax': Emax, 'Etot': Etot, 'Enum': Enum, 'Lnum': Lnum}

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


class LocalSearch:

    def __init__(self, move_type, rule, n):
        self.move_type = move_type
        self.rule = rule
        self.n = n

    def generate_movepool(self):

        if self.move_type == 'swap':
            return [(i, j) for i in range(self.n - 1) for j in range(i+1, self.n)]

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
            goalvalue = self.calculate_goal(current_solution=local_solution)
            return goalvalue

        if self.move_type == 'insert':
            pass

    def perform_move(self, move, current_solution):
        x, y = move[0], move[1]
        current_solution = current_solution.copy()

        if self.move_type == 'swap':
            current_solution[x, :], current_solution[y, :] = current_solution[y, :], current_solution[x, :].copy()
            return current_solution

    def calculate_goal(self, current_solution):

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

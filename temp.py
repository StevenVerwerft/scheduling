from local_search import *
from classes import *

solver = Solver(iterations=100, tabu_tenure=1, first_x=1, goalfunction='Tmax', verbosity=10, n_time=60,
                random_order=False)

solution_path = solver.local_search(path='very_large/replicate_5.csv')

times = [solution[1] for solution in solution_path]
goals = [solution[0] for solution in solution_path]

import matplotlib.pyplot as plt
plt.plot(times, goals)
plt.show()
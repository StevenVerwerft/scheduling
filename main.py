from classes import *
from local_search import Solver
import sys


class GUI_starter(Frame):

    def __init__(self, parent, **options):
        self.parent = parent
        Frame.__init__(self, parent, **options)
        self.pack()
        self.n_iterations = 300
        self.n_time = 60
        self.tabu_tenure = int(self.n_iterations * .1)
        self.first_x = 5

        # radiobutton row for goalfunction

        row = Frame(self)
        label = Label(row, width=15, text='Goalfunction')
        container = Frame(row)
        self.rule = StringVar()
        options = ['Lmax', 'Emax', 'Tmax', 'Lnum', 'Tnum', 'Enum']

        row.pack(expand=YES, fill=BOTH)
        label.pack(side=LEFT)
        container.pack(side=RIGHT, fill=X, expand=YES)
        for opt in options:
            Radiobutton(container, text=opt, command=(lambda: self.onPress(self.rule)),
                        variable=self.rule, value=opt).pack(side=LEFT, expand=YES)

        self.rule.set('Tmax')

        # entry for number of iterations

        row = Frame(self)
        label = Label(row, width=15, text='Iterations')
        self.iterations_entry = Entry(row)
        self.iterations_entry.insert(0, self.n_iterations)
        row.pack(fill=X)
        label.pack(side=LEFT)
        self.iterations_entry.pack(side=LEFT)
        self.iterations_entry.bind('<Return>', self.submit)

        # entry for time

        row = Frame(self)
        label = Label(row, width=15, text='Time')
        self.time_entry = Entry(row)
        self.time_entry.insert(0, self.n_time)
        row.pack(fill=X)
        label.pack(side=LEFT)
        self.time_entry.pack(side=LEFT)
        self.time_entry.bind('<Return>', self.submit)

        # entry for tabu tenure

        row = Frame(self)
        label = Label(row, width=15, text='Tabu Tenure')
        self.tabu_tenure_entry = Entry(row)
        self.tabu_tenure_entry.insert(0, self.tabu_tenure)
        row.pack(fill=X)
        label.pack(side=LEFT)
        self.tabu_tenure_entry.pack(side=LEFT)

        # entry for first x

        row = Frame(self)
        label = Label(row, width=15, text='First X')
        self.first_x_entry = Entry(row)
        self.first_x_entry.insert(0, self.first_x)
        row.pack(fill=X)
        label.pack(side=LEFT)
        self.first_x_entry.pack(side=LEFT)


        # submitrow

        submitrow = Frame(self)
        submitbtn = Button(submitrow, text='submit', command=self.submit)
        printbtn = Button(submitrow, text='print', command=self.print)
        submitrow.pack(fill=X, expand=YES)
        submitbtn.pack()
        printbtn.pack()

    def submit(self):
        self.update()
        self.parent.quit()

    def update(self):
        self.n_iterations = int(self.iterations_entry.get())
        self.n_time = int(self.time_entry.get())
        self.first_x = int(self.first_x_entry.get())
        self.tabu_tenure = int(self.tabu_tenure_entry.get())

    def get_items(self):

        self.update()
        dic = {

            'n_iterations': self.n_iterations,
            'time': self.n_time,
            'first_x': self.first_x,
            'tabu_tenure': self.tabu_tenure,
        }

        return dic

    def print(self):

        dic = self.get_items()
        for key, value in dic.items():
            print(key, value)

    def onPress(self, var):
        print('pressed on something: ', var.get())

root = Tk()
root.title('Local Search Initiator - Single Machine permutation flowshop')
GUI = GUI_starter(parent=root)  # start the GUI

# Put GUI Window on top of current window
root.lift()
root.after_idle(root.attributes, '-topmost', False)
root.mainloop()
root.destroy()

n = GUI.n_iterations
n_time = GUI.n_time
tabu_tenure = GUI.tabu_tenure
first_x = GUI.first_x
goalfunction = GUI.rule.get()

solution_df = pd.DataFrame(columns=['id', 'goalfunction', 'time', 'first x', 'tabu tenure', 'size', 'random order'])

if sys.argv[1]:
    output_name = sys.argv[1]
else:
    output_name = 'output.csv'
for random_order in [True, False]:

    for x_length in [1, 5, 10]:

        for tabu_length in [10, 50, 100]:

            for instance_size_dir in ['small_instances', 'medium_instances', 'large_instances']:

                for instance_path in os.listdir(os.path.abspath(instance_size_dir)):

                    path = os.path.join(instance_size_dir, instance_path)
                    solver = Solver(iterations=1000, tabu_tenure=tabu_length, first_x=x_length,
                                    goalfunction=goalfunction, verbosity=100, n_time=60, random_order=random_order)
                    solution_path = solver.local_search(path=path)

                    # create the long format of the experiment
                    goalvals = [solution[0] for solution in solution_path]
                    times = [solution[1] for solution in solution_path]
                    id = [instance_path for solution in solution_path]
                    firstx = [x_length for solution in solution_path]
                    tabu = [tabu_length for solution in solution_path]
                    randoms = [str(random_order) for solution in solution_path]
                    sizes = [instance_size_dir for solution in solution_path]

                    dicdf = pd.DataFrame({'id': id, 'goalfunction': goalvals, 'time': times, 'first x': firstx,
                                          'tabu tenure': tabu, 'size': sizes, 'random order': randoms})
                    solution_df = solution_df.append(dicdf)

solution_df.to_csv(output_name, sep=',', index=False)
quit()

from classes import *
from local_search import Solver


class GUI_starter(Frame):

    def __init__(self, parent, **options):
        self.parent = parent
        Frame.__init__(self, parent, **options)
        self.pack()
        self.n_iterations = 200
        self.tabu_tenure = int(self.n_iterations * .5)
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

        self.rule.set('Lmax')

        # entry for number of iterations

        row = Frame(self)
        label = Label(row, width=15, text='Iterations')
        self.iterations_entry = Entry(row)
        self.iterations_entry.insert(0, self.n_iterations)
        row.pack(fill=X)
        label.pack(side=LEFT)
        self.iterations_entry.pack(side=LEFT)
        self.iterations_entry.bind('<Return>', self.submit)

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
        self.first_x = int(self.first_x_entry.get())
        self.tabu_tenure = int(self.tabu_tenure_entry.get())

    def get_items(self):

        self.update()
        dic = {

            'n_iterations': self.n_iterations,
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


replicates = os.listdir('test_instances')

root = Tk()
root.title('Local Search Initiator - Single Machine permutation flowshop')
GUI = GUI_starter(parent=root)  # start the GUI

# Put GUI Window on top of current window
root.lift()
root.after_idle(root.attributes, '-topmost', False)
root.mainloop()
root.destroy()

n = GUI.n_iterations
tabu_tenure = GUI.tabu_tenure
first_x = GUI.first_x
goalfunction = GUI.rule.get()


path = os.path.abspath('test_instances3/replicate_5.csv')
solver = Solver(iterations=n, tabu_tenure=tabu_tenure, first_x=first_x, goalfunction=goalfunction, verbosity=5)
solution_path = solver.local_search(path=path)

goalvals = [solution[0] for solution in solution_path]
times = [solution[1] for solution in solution_path]

plt.plot(times, goalvals)
plt.show()


import numpy as np
import pandas as pd
import os
# fix for MACOSX GUI crash
import sys

if sys.platform == 'darwin':
    import matplotlib

    matplotlib.use("TkAgg")  # use this backend to prevent macosX bug
    import matplotlib.pyplot as plt
    import matplotlib.colors as colors
    import matplotlib.cm as cmx
    import seaborn as sns
    from tkinter import *
import matplotlib.pyplot as plt
from tkinter import *
"""
This script will generate an instance for the single machine scheduling case.
"""

# regular entries
entry_options = {
    'replicates': 5,
    'n': 80,
    'm': 1,
    'release times': 1,
    'processing lower': 1,
    'processing upper': 500,
    'setuptime lower': 0.25,
    'setuptime upper': 0.75,
}


class Generator(Frame):

    def __init__(self, parent, general_entries, **options):

        self.parent = parent
        Frame.__init__(self, parent, **options)
        self.general_entries = general_entries  # dictionary with labels and values
        self.pack()
        self.n_replicates = 1
        self.entries = []

        for (fieldname, fieldvalue) in self.general_entries.items():
            row = Frame(self)
            lab = Label(row, width=15, text=fieldname)
            ent = Entry(row)
            ent.insert(0, fieldvalue)
            row.pack(side=TOP, fill=X)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT)
            ent.focus()
            ent.bind('<Return>', self.submit)
            self.entries.append(ent)

        # radiobuttons tardiness
        if False:
            # radiobutton row for tardiness factor T
            row = Frame(self)
            label = Label(row, width=15, text='tardiness (T)')
            container = Frame(row)
            self.tardiness_factor = DoubleVar()
            options = [0.0, 0.2, 0.4, 0.6]

            row.pack(expand=YES, fill=BOTH)
            label.pack(side=LEFT)
            container.pack(side=RIGHT, fill=X, expand=YES)
            for opt in options:
                Radiobutton(container, text=opt, command=(lambda: self.onPress(self.tardiness_factor)),
                            variable=self.tardiness_factor, value=opt).pack(side=LEFT, expand=YES)
            self.tardiness_factor.set(0.5)

        # slider for tardiness factor T
        row = Frame(self)
        label = Label(row, width=15, text='tardiness (T)')
        container = Frame(row)

        row.pack(expand=YES, fill=BOTH)
        label.pack(side=LEFT)
        container.pack(side=RIGHT, fill=X, expand=YES)
        self.tardiness_factor = Scale(container, from_=0.0, to=2, digits=3, resolution=0.1, orient=HORIZONTAL)
        self.tardiness_factor.pack(expand=YES)

        # radiobuttons spread
        if False:
            # radiobutton row for spread parameter R
            row = Frame(self)
            label = Label(row, width=15, text='spread (R)')
            container = Frame(row)
            self.spread_param = DoubleVar()
            options = [0.0, 0.3, 0.6]

            row.pack(expand=YES, fill=BOTH)
            label.pack(side=LEFT)
            container.pack(side=RIGHT, expand=YES, fill=X)
            for opt in options:
                Radiobutton(container, text=opt, command=(lambda: self.onPress(self.spread_param)),
                            variable=self.spread_param, value=opt).pack(side=LEFT, expand=YES)
            self.spread_param.set(0.3)

        # slider for tardiness factor T
        row = Frame(self)
        label = Label(row, width=15, text='spread (R)')
        container = Frame(row)

        row.pack(expand=YES, fill=BOTH)
        label.pack(side=LEFT)
        container.pack(side=RIGHT, fill=X, expand=YES)
        self.spread_param = Scale(container, from_=0.0, to=2, digits=3, resolution=0.1, orient=HORIZONTAL)
        self.spread_param.pack(expand=YES)

        # radiobutton row for grouping parameter G
        if False:
            row = Frame(self)
            label = Label(row, width=15, text='grouping (g)')
            container = Frame(row)
            self.group_param = DoubleVar()
            options = [0.1, 0.3, 0.9]

            row.pack(expand=YES, fill=BOTH)
            label.pack(side=LEFT)
            container.pack(side=RIGHT, fill=X, expand=YES)
            for opt in options:
                Radiobutton(container, text=opt, command=(lambda: self.onPress(self.group_param)),
                            variable=self.group_param, value=opt).pack(side=LEFT, expand=YES)
            self.group_param.set(0.1)

        # slider for tardiness factor T
        row = Frame(self)
        label = Label(row, width=15, text='grouping (g)')
        container = Frame(row)

        row.pack(expand=YES, fill=BOTH)
        label.pack(side=LEFT)
        container.pack(side=RIGHT, fill=X, expand=YES)
        self.group_param = Scale(container, from_=0.0, to=1.0, digits=3, resolution=0.01, orient=HORIZONTAL)
        self.group_param.pack(expand=YES)

        # savepath
        row = Frame(self)
        label = Label(row, width=15, text='save path')
        self.save_path = Entry(row)
        self.save_path.insert(0, 'test_instances/')
        row.pack(side=TOP, fill=X)
        label.pack(side=LEFT)
        self.save_path.pack(side=RIGHT)

        # final row to submit
        submitrow = Frame(self)
        quitbtn = Button(submitrow, text='Quit', command=self.parent.quit)
        submitbtn = Button(submitrow, text='Submit', command=self.submit)
        plotbtn = Button(submitrow, text='Plot', command=self.plot)
        savebtn = Button(submitrow, text='Save', command=self.save)

        submitrow.pack(fill=X, expand=YES)
        quitbtn.pack(side=LEFT, expand=YES)
        submitbtn.pack(side=RIGHT, expand=YES)
        plotbtn.pack(side=TOP, expand=YES)
        savebtn.pack(side=TOP, expand=YES)

    def submit(self, event=None):
        self.update()
        self.parent.quit()

    def update(self, event=None):
        for entry, name in zip(self.entries, self.general_entries.keys()):
            self.general_entries.update({name: float(entry.get())})

        self.n_replicates = int(self.general_entries['replicates'])

    def onPress(self, var):
        print('pressed on something: ', var.get())

    def save(self):
        self.update()
        path = self.save_path.get()  # get the path from the entry

        abs_path = os.path.join(os.getcwd(), path)

        try:
            if os.path.exists(abs_path):
                print('directory exists!')
            else:
                os.mkdir(abs_path)
                print('just made a subdirectory!')
        except:
            print('something went wrong with the directory...')

        for i in range(1, self.n_replicates+1):
            print('saving replicate {} to path {}'.format(i, path))
            name = 'replicate_{}.csv'.format(i)
            print('replicate_name = {}'.format(name))
            df, P = self.construct_instance()
            df.to_csv(os.path.join(abs_path, name), sep=';')

    def plot(self):

        df, P = self.construct_instance()
        plt.vlines(x=df.d_dates, ymin=0, ymax=df.p_times, color='grey', alpha=.4)
        points = plt.scatter(df.d_dates, df.p_times, c=df.groups, cmap='RdBu', s=15)
        plt.colorbar(points, ticks=list(set(df.groups)))

        plt.xlim(0, P)
        plt.xlabel('Due dates')
        plt.ylabel('Processing times')
        plt.show()

    def construct_instance(self):
        self.update()
        # construct the instance (for plotting)
        n = int(self.general_entries['n'])
        self.n_replicates = int(self.general_entries['replicates'])
        p_times = np.random.uniform(self.general_entries['processing lower'],
                                    self.general_entries['processing upper'],
                                    n)

        s_times = np.random.uniform(self.general_entries['setuptime lower'],
                                    self.general_entries['setuptime upper'],
                                    n)
        S_times = p_times * s_times
        g = self.group_param.get()
        nG = max(int(n * g), 1)  # minimal one family
        grouping = np.random.randint(0, nG, n)
        P = np.sum(p_times) + np.sqrt(g) * np.sum(S_times)
        T = self.tardiness_factor.get()
        R = self.spread_param.get()
        d_l, d_u = max(0, 1 - T - R / 2.0) * P, max(1, 1 - T + R / 2.0) * P
        d_dates = np.random.uniform(d_l, d_u, n)

        r_dates = np.asarray([np.random.uniform(0, d_dates[i] - p_times[i] - S_times[i]) for i in range(n)])

        df = pd.DataFrame({'p_times': p_times, 'S_times': S_times, 'groups': grouping,
                           'd_dates': d_dates, 'r_dates': r_dates})
        return df, P  # dataframe and makespan


root = Tk()
root.title('Instance generator - Single Machine permutation flowshop')
GUI = Generator(parent=root, general_entries=entry_options)  # start the GUI

# Put GUI Window on top of current window
root.lift()
root.after_idle(root.attributes, '-topmost', False)
root.mainloop()

data, makespan = GUI.construct_instance()
print(data.head(25))
print(data.p_times.mean())
root.destroy()


quit


if False:
    replicates = GUI.general_entries['replicates']
    n = int(GUI.general_entries['n'])
    # generate the processing times for each  job
    # p_i ~ U(p_l, p_u)
    p_l, p_u = GUI.general_entries['processing lower'], GUI.general_entries['processing upper']
    p_times = np.random.uniform(p_l, p_u, n)

    # generate the setup times for each job
    s_l, s_u = GUI.general_entries['setuptime lower'], GUI.general_entries['setuptime upper']
    s_times = np.random.uniform(s_l, s_u, n)
    S_times = p_times * s_times


    # Calculate the amount of job families for the problem
    g = GUI.group_param.get()
    nG = int(n*g)
    groups = np.random.randint(0, nG, n)

    # Calculate the makespan for the problem
    P = np.sum(p_times) + np.sqrt(g)*np.sum(S_times)

    # alternative makespan approximation based on total average setup time
    # averaged over all possible predecessors
    base = np.sum(S_times)
    P2 = np.sum(p_times) + np.sum([(base - jobtime) / float(n-1) for jobtime in S_times]) * np.sqrt(g)

    # Due date lower and upper bound => make this dynamic
    T = GUI.tardiness_factor.get()
    R = GUI.spread_param.get()

    d_l = max(0, (1 - T - R/2.0))*P
    d_u = min(1, (1 - T + R/2.0))*P

    d_dates = np.random.uniform(d_l, d_u, n)

    # calculate upper bound for the release dates (due date - processing time - setup time)
    r_times_u = d_dates - p_times - S_times
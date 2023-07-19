import matplotlib.pyplot as plt
import pandas as pd
from database.database_manager import AzureDatabaseManager
from matplotlib import gridspec
# import packages and modules
import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from pandas.plotting import table
from sklearn import preprocessing
from views.selector import SelectFunctionality, SelectGene


class Group:
    def __init__(self, group_name, table_name, participants=None):
        if participants is None:
            participants = []
        self.group_name = group_name
        self.table_name = table_name
        self.azure = AzureDatabaseManager('shiba')
        self.participants = participants

    def get_participants_names(self):
        names = []
        for p in self.participants:
            names.append(p.individual)
        return names

    def analyze(self):
        functionality_selection = SelectFunctionality()
        functionality_selection.create()
        functionality_selection.wait_window()
        functionality = functionality_selection.ans
        if functionality:
            labels = self.get_participants_names()
            columns = ['individual', 'total_sequences', 'unique_sequences', 'shannon', 'simpson']
            df = pd.DataFrame(columns=columns)
            # Define the new row to be added
            for p in self.participants:
                di = p.diversity_indices['cdr3aa'][functionality]
                new_row = {'individual': p.individual, 'total_sequences': di['total sequences'],
                           'unique_sequences': di['unique sequences'], 'shannon': di['shannon'],
                           'simpson': di['simpson']}
                df.loc[len(df)] = new_row
            data = df.values[:, 1:]
            val1 = columns[1:]
            val5 = plt.cm.plasma(np.linspace(0, 0.5, len(labels)))
            val7 = np.arange(len(data)) + 0.3
            val8 = 0.4
            fig = plt.figure(figsize=(12, 8), tight_layout=True)
            fig.canvas.manager.set_window_title('Analyze')
            fig.suptitle(f"{self.group_name} ({self.table_name})'s Diversity Indices {functionality}",
                         fontweight="bold")
            gs = gridspec.GridSpec(3, 2)
            # total_sequences
            ax1 = fig.add_subplot(gs[0, 0])
            p1 = ax1.bar(val7, data[:, 0], val8, color=val5)
            ax1.bar_label(p1, labels=data[:, 0], label_type='edge', fontsize=8, color='black', weight='bold')
            ax1.set_xticks([])
            plt.title(val1[0])
            # unique_sequences
            ax2 = fig.add_subplot(gs[0, 1])
            p2 = ax2.bar(val7, data[:, 1], val8, color=val5)
            ax2.bar_label(p2, labels=data[:, 1], label_type='edge', fontsize=8, color='black', weight='bold')
            ax2.set_xticks([])
            plt.title(val1[1])
            # shannon
            ax3 = fig.add_subplot(gs[1, 0])
            data1 = np.around(list(data[:, 2]), decimals=4)
            p3 = ax3.bar(val7, data1, val8, color=val5)
            ax3.bar_label(p3, labels=data1, label_type='edge', fontsize=8, color='black', weight='bold')
            ax3.set_xticks([])
            plt.title(val1[2])
            # simpson
            ax4 = fig.add_subplot(gs[1, 1])
            data1 = np.around(list(data[:, 3]), decimals=4)
            p4 = ax4.bar(val7, data1, val8, color=val5)
            ax4.bar_label(p4, labels=data1, label_type='edge', fontsize=8, color='black', weight='bold')
            ax4.set_xticks([])
            plt.title(val1[3])
            ax5 = fig.add_subplot(gs[2, :])
            ax5.axis('off')
            bar_table = ax5.table(cellText=df.values, colLabels=columns, loc='center', cellLoc='center')
            for i in range(len(labels)):
                cell = bar_table[i + 1, 0]
                cell.set_facecolor(val5[i])
            plt.show()


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

    def get_participants_data(self):
        data = pd.DataFrame(
            columns=["Individual", "pro unique seq", "pro total seq", "pro simpson's D", "pro shannon's H",
                     "unpro unique seq", "unpro total seq", "unpro simpson's D", "unpro shannon's H"])
        for p in self.participants:
            pro_di = p.diversity_indices['productive']
            unpro_di = p.diversity_indices['unproductive']
            row = {"Individual": p.individual,
                   "pro unique seq": pro_di['unique sequences'],
                   "pro total seq": pro_di['total sequences'],
                   "pro simpson's D": pro_di['simpson'],
                   "pro shannon's H": pro_di['shannon'],
                   "unpro unique seq": unpro_di['unique sequences'],
                   "unpro total seq": unpro_di['total sequences'],
                   "unpro simpson's D": unpro_di['simpson'],
                   "unpro shannon's H": unpro_di['shannon']}
            data.loc[len(data)] = row
        return data

    def analyze(self):
        functionality_selection = SelectFunctionality()
        functionality_selection.wait_window()
        functionality = functionality_selection.ans
        if functionality:
            labels = self.get_participants_names()
            columns = ['individual', 'total_sequences', 'unique_sequences', 'shannon', 'simpson']
            df = pd.DataFrame(columns=columns)
            # Define the new row to be added
            for p in self.participants:
                di = p.diversity_indices[functionality]
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
            ax1 = fig.add_subplot(gs[0, 0])  # total_sequences
            ax2 = fig.add_subplot(gs[0, 1])  # unique_sequences
            ax3 = fig.add_subplot(gs[1, 0])  # shannon
            ax4 = fig.add_subplot(gs[1, 1])  # simpson
            for i, ax in enumerate([ax1, ax2, ax3, ax4]):
                data1 = np.around(list(data[:, i]), decimals=4)
                p1 = ax.bar(val7, data1, val8, color=val5)
                ax.bar_label(p1, labels=data1, label_type='edge', fontsize=8, color='black', weight='bold')
                ax.set_xticks(val7, labels=labels)
                plt.setp(ax.get_xticklabels(), fontsize=8)
                plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
                plt.title(val1[i])
            ax5 = fig.add_subplot(gs[2, :])
            ax5.axis('off')
            bar_table = ax5.table(cellText=df.values, colLabels=columns, loc='center', cellLoc='center')
            for i in range(len(labels)):
                cell = bar_table[i + 1, 0]
                cell.set_facecolor(val5[i])
            plt.show()

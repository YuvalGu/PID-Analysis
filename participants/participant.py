import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
from random import randint
import squarify
import mplcursors
from database.database_manager import AzureDatabaseManager
from scipy.stats import entropy
import numpy as np


class Participant:
    def __init__(self, chain, individual):
        self.azure = AzureDatabaseManager('shiba')
        self.individual = individual
        self.table_name = chain
        self.diversity_indices = {}
        self.pro_df, self.unpro_df = self.get_data()
        for col in ['cdr3aa', 'jgene', 'dgene', 'vgene']:
            self.diversity_indices[col] = self._calculate_diversity_indices(col)

    def analyze(self):
        # create a figure
        fig = plt.figure(figsize=(15, 8))
        fig.canvas.manager.set_window_title('Analyze')
        fig.suptitle(f'{self.individual} Analyze')
        gs = gridspec.GridSpec(1, 4)
        # tree map
        ax1 = plt.subplot(gs[0, :-1])
        self._create_tree_map(ax1)
        # statistics:
        ax2 = plt.subplot(gs[0, -1])
        self._diversity_indices(ax2)
        plt.show()

    def _create_tree_map(self, ax):
        colors = []
        for i in range(len(self.pro_df.index)):
            colors.append('#%06X' % randint(0, 0xFFFFFF))
        squarify.plot(sizes=self.pro_df['total'], color=colors, ax=ax)
        cursor = mplcursors.cursor(hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f"cdr3aa:{self.pro_df['cdr3aa'].iloc[sel.target.index]}\ntotal: {self.pro_df['total'].iloc[sel.target.index]}\n"))
        ax.axis('off')

    def _diversity_indices(self, ax):
        di = self.diversity_indices['cdr3aa']['productive']
        text = f"Unique sequences: {di['unique sequences']}\n\nTotal sequences: {di['total sequences']}\n\nShannon: " \
               f"{di['shannon']}\n\nSimpson: {di['simpson']}\n"
        ax.axis('off')
        ax.text(0, 0.6, s=text, fontsize=15)

    def get_data(self):
        data = self.azure.get_participant_data(self.table_name, self.individual)
        data = data.sort_values(by=['total'])
        data1 = data.query("functionality=='productive'")[['cdr3aa', 'jgene', 'dgene', 'vgene', 'total']]
        data1 = data1.reset_index(drop=True)
        data2 = data.query("functionality=='unproductive'")[['cdr3aa', 'jgene', 'dgene', 'vgene', 'total']]
        data2 = data2.reset_index(drop=True)
        return data1, data2

    def _calculate_diversity_indices(self, col):
        di_dict = {'productive': {}, 'unproductive': {}}
        total_sequences = self.pro_df['total'].sum()
        unique_sequences = len(pd.unique(self.pro_df[col]))
        # Convert abundance to probabilities
        probabilities = self.pro_df['total'].to_numpy() / np.sum(self.pro_df['total'].values)
        # Calculate Shannon index
        shannon = entropy(list(probabilities), base=2)
        # Calculate Simpson index
        simpson = np.sum(probabilities ** 2)
        di_dict['productive'] = {'total sequences': total_sequences, 'unique sequences': unique_sequences,
                                 'shannon': shannon, 'simpson': simpson}
        total_sequences = self.unpro_df['total'].sum()
        unique_sequences = len(pd.unique(self.unpro_df[col]))
        # Convert abundance to probabilities
        probabilities = self.unpro_df['total'].to_numpy() / np.sum(self.unpro_df['total'].values)
        # Calculate Shannon index
        shannon = entropy(list(probabilities), base=2)
        # Calculate Simpson index
        simpson = np.sum(probabilities ** 2)
        di_dict['unproductive'] = {'total sequences': total_sequences, 'unique sequences': unique_sequences,
                                   'shannon': shannon, 'simpson': simpson}
        return di_dict

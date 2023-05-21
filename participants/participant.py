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
        self.unique_sequences = 0
        self.total_sequences = 0
        self.shannon = 0
        self.simpson = 0
        self.df = None

    # def create_columns(self):
    #     self.data['chain'] = self.table_name
    #     self.data['individual'] = self.individual

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
        data = self.azure.get_participant_data(self.individual, self.table_name)
        data = data.sort_values(by=['total'])
        data = data.reset_index(drop=True)
        self.df = data
        colors = []
        for i in range(len(data.index)):
            colors.append('#%06X' % randint(0, 0xFFFFFF))
        squarify.plot(sizes=data['total'], color=colors, ax=ax)
        cursor = mplcursors.cursor(hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f"cdr3aa:{data['cdr3aa'].iloc[sel.target.index]}\ntotal: {data['total'].iloc[sel.target.index]}\n"))
        ax.axis('off')

    def _diversity_indices(self, ax):
        self.total_sequences = self.df['total'].sum()
        self.unique_sequences = len(pd.unique(self.df['cdr3aa']))
        # Convert abundance to probabilities
        probabilities = self.df['total'].to_numpy() / np.sum(self.df['total'].values)
        # Calculate Shannon index
        self.shannon = entropy(list(probabilities), base=2)
        # Calculate Simpson index
        self.simpson = np.sum(probabilities ** 2)
        ax.axis('off')
        ax.text(0, 0.6,
                s=f'Unique sequences: {self.unique_sequences}\n\nTotal sequences: {self.total_sequences}\n\nShannon: {self.shannon}\n\nSimpson: {self.simpson}\n',
                fontsize=15)

    def get_individual(self):
        return self.individual

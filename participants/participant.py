import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
from random import randint
import squarify
import mplcursors
from database.database_manager import AzureDatabaseManager
from views.loading_frame import LoadingFrame
from views.selector import SelectData
from scipy.stats import entropy
import numpy as np
import tkinter
import tkinter.messagebox
import customtkinter


class Participant:
    def __init__(self, chain, individual):
        self.azure = AzureDatabaseManager('shiba')
        self.individual = individual
        self.table_name = chain
        self.pro_df, self.unpro_df = self.get_data()
        self.diversity_indices = None
        self._calculate_diversity_indices()
        self.genes = {'productive': {}, 'unproductive': {}}
        self.cols = ['jgene', 'vgene']
        if not self.table_name == 'TRG':
            self.cols += ['dgene']
        for col in self.cols:
            self.genes['productive'][col], self.genes['unproductive'][col] = self._calculate_gene_data(col)

    def analyze(self):
        # loading = LoadingFrame()
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
        self._show_diversity_indices(ax2)
        plt.show()
        # loading.close_loading_window()

    def _create_tree_map(self, ax):
        colors = []
        for i in range(len(self.pro_df.index)):
            colors.append('#%06X' % randint(0, 0xFFFFFF))
        squarify.plot(sizes=self.pro_df['total'], color=colors, ax=ax)
        cursor = mplcursors.cursor(hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f"cdr3aa:{self.pro_df['cdr3aa'].iloc[sel.target.index]}\ntotal: {self.pro_df['total'].iloc[sel.target.index]}\n"))
        ax.axis('off')
        ax.set_title('TreeMap')

    def _show_diversity_indices(self, ax):
        di = self.diversity_indices['productive']
        text = f"Unique sequences: {di['unique sequences']}\n\nTotal sequences: {di['total sequences']}\n\nShannon: " \
               f"{di['shannon']}\n\nSimpson: {di['simpson']}\n"
        ax.axis('off')
        ax.set_title('Diversity Indices - productive')
        ax.text(0, 0.6, s=text, fontsize=15)

    def get_data(self):
        data = self.azure.get_participant_data(self.table_name, self.individual)
        data = data.sort_values(by=['total'])
        data1 = data.query("functionality=='productive'")[['cdr3aa', 'jgene', 'dgene', 'vgene', 'total']]
        data1 = data1.reset_index(drop=True)
        data2 = data.query("functionality=='unproductive'")[['cdr3aa', 'jgene', 'dgene', 'vgene', 'total']]
        data2 = data2.reset_index(drop=True)
        return data1, data2

    def export_to_excel(self):
        data_selection = SelectData(self.cols)
        data_selection.wait_window()
        if data_selection.ans:
            # Ask the user to choose the save location and file name
            file_path = customtkinter.filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                                   filetypes=[("Excel Files", "*.xlsx")])
            if file_path:
                if data_selection.ans == 'diversity indices':
                    data = pd.DataFrame(self.diversity_indices).reset_index()
                else:
                    keys = data_selection.ans.split(" ")
                    gene = keys[0]
                    functionality = keys[1]
                    data = pd.DataFrame(self.genes[functionality][gene])
                try:
                    # Write the DataFrame to the Excel file
                    data.to_excel(file_path, index=False)
                    tkinter.messagebox.showinfo(title='SUCCESS', message=f'data exported successfully')
                except Exception as e:
                    tkinter.messagebox.showerror(title="ERROR exporting the data\n", message=str(e))

    def _calculate_diversity_indices(self):
        self.diversity_indices = {'productive': {}, 'unproductive': {}}
        total_sequences = self.pro_df['total'].sum()
        unique_sequences = len(pd.unique(self.pro_df['cdr3aa']))
        # Convert abundance to probabilities
        probabilities = self.pro_df['total'].to_numpy() / np.sum(self.pro_df['total'].values)
        # Calculate Shannon index
        shannon = entropy(list(probabilities), base=2)
        # Calculate Simpson index
        simpson = np.sum(probabilities ** 2)
        self.diversity_indices['productive'] = {'total sequences': total_sequences,
                                                'unique sequences': unique_sequences, 'shannon': shannon,
                                                'simpson': simpson}
        total_sequences = self.unpro_df['total'].sum()
        unique_sequences = len(pd.unique(self.unpro_df['cdr3aa']))
        # Convert abundance to probabilities
        probabilities = self.unpro_df['total'].to_numpy() / np.sum(self.unpro_df['total'].values)
        # Calculate Shannon index
        shannon = entropy(list(probabilities), base=2)
        # Calculate Simpson index
        simpson = np.sum(probabilities ** 2)
        self.diversity_indices['unproductive'] = {'total sequences': total_sequences,
                                                  'unique sequences': unique_sequences, 'shannon': shannon,
                                                  'simpson': simpson}

    def _calculate_gene_data(self, col):
        # Remove rows containing 'or' in col
        self.pro_df = self.pro_df[~self.pro_df[col].str.contains(' or ')]
        self.unpro_df = self.unpro_df[~self.unpro_df[col].str.contains(' or ')]
        pro_grouped_df = self.pro_df.groupby(col).agg(unique=(col, 'size'), total=('total', 'sum')).reset_index()
        unpro_grouped_df = self.unpro_df.groupby(col).agg(unique=(col, 'size'), total=('total', 'sum')).reset_index()
        return pro_grouped_df, unpro_grouped_df

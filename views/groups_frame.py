import tkinter
import tkinter.messagebox
import customtkinter
import mplcursors
from database.database_manager import AzureDatabaseManager
from azure.kusto.data.exceptions import KustoError
from participants.group import Group
from views.creator import GroupCreator
from views.selector import SelectFunctionality, SelectGene
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os


class GroupFrame(customtkinter.CTk):
    def __init__(self, root, table_names, p_frame):
        super().__init__()
        self.root = root
        self.p_frame = p_frame
        self.azure = AzureDatabaseManager('shiba')
        self.groups = {}
        self.groups_frame = customtkinter.CTkFrame(self.root, width=420)
        self.groups_frame.grid(row=0, column=2, rowspan=4, columnspan=2, padx=(0, 20), pady=(20, 20), sticky="nsew")
        self.groups_frame.rowconfigure(0, weight=15)
        self.groups_frame.rowconfigure(1, weight=1)
        self.image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons')
        self.names = {}
        self.widgets = {}
        self.table_names = table_names
        self.tab_frames = {}
        self.tabview = None
        self.create_tab_views()
        for table_name in self.table_names:
            self.names[table_name] = self.azure.get_groups_names_by_table(table_name)
            self.groups[table_name] = {}
            self.widgets[table_name] = {}
            for group_name in self.names[table_name]:
                self.add_group(group_name, table_name, self.azure.get_participants_from_group(group_name, table_name))

    def create_tab_views(self):
        self.tabview = customtkinter.CTkTabview(self.groups_frame, width=460)
        self.tabview.grid(row=0, column=2, padx=(20, 10), pady=0, sticky="nsew")
        for table in self.table_names:
            self.create_tab(table)
        self.create_analyze_groups()

    def create_analyze_groups(self):
        analyze_groups_frame = customtkinter.CTkFrame(self.groups_frame)
        analyze_groups_frame.grid(row=1, column=2, padx=(20, 10), sticky="nsew")
        analyze_groups_frame.grid_columnconfigure((0, 1), weight=1)
        heat_map_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "heatmap.png")), size=(20, 20))

        heat_map_button = customtkinter.CTkButton(master=analyze_groups_frame, text="heat map", image=heat_map_icon,
                                                  anchor="center", fg_color='#188e99', hover_color='#0f5c63',
                                                  command=self.show_heat_map, height=20, width=20)
        heat_map_button.grid(row=0, column=0, padx=(10, 0), pady=(0, 20), ipadx=0, ipady=0, sticky="se")
        scatter_graph_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "scattergraph.png")),
                                                    size=(20, 20))

        scatter_graph_button = customtkinter.CTkButton(master=analyze_groups_frame, text="scatter plot",
                                                       image=scatter_graph_icon, anchor="center",
                                                       fg_color='#188e99', hover_color='#0f5c63',
                                                       command=self.show_scatter_plot, height=20, width=20)
        scatter_graph_button.grid(row=0, column=1, padx=(10, 0), pady=(0, 20), ipadx=0, ipady=0, sticky="sw")

    def create_tab(self, name):
        self.tabview.add(name)

        # Create a canvas widget inside the tab
        canvas = customtkinter.CTkCanvas(self.tabview.tab(name))
        canvas.pack(side='left', fill='both', expand=True)

        # Create a frame inside the canvas for the buttons
        frame = customtkinter.CTkFrame(canvas)

        # Add a scrollbar to the canvas
        scrollbar = customtkinter.CTkScrollbar(self.tabview.tab(name), orientation='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')

        canvas.configure(yscrollcommand=scrollbar.set)

        # Configure the canvas to scroll the frame
        canvas.create_window((0, 0), window=frame, anchor='nw')

        # Function to update the scroll region
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            canvas.itemconfigure(frame_id, width=canvas.winfo_width())

        # Configure the scroll region and frame size when the canvas size changes
        frame_id = canvas.create_window((0, 0), window=frame, anchor='nw')
        canvas.bind('<Configure>', configure_scroll_region)
        self.change_canvas_color(name)
        self.tab_frames[name] = frame

    def change_all_canvas_color(self):
        for table in self.table_names:
            self.change_canvas_color(table)

    def change_canvas_color(self, table):
        canvas = self.tabview.tab(table).winfo_children()[0]
        if table in self.widgets and len(list(self.widgets[table])) != 0:
            colors = self.widgets[table][list(self.widgets[table])[0]][0].cget('fg_color')
        else:
            colors = self.tabview.tab(table).cget("fg_color")
        if customtkinter.get_appearance_mode() == 'Light':
            canvas.configure(bg=colors[0], highlightbackground=colors[0])
        elif customtkinter.get_appearance_mode() == 'Dark' or 'System':
            canvas.configure(bg=colors[1], highlightbackground=colors[1])

    def edit_item(self, table, old_group_name):
        old_members = self.groups[table][old_group_name].get_participants_names()
        creator = GroupCreator(table, old_group_name, old_members, True)
        creator.wait_window()
        if creator.valid:
            members = self.p_frame.get_participants(creator.members)
            group = Group(creator.group_name, creator.table_name, members)
            if not old_group_name == creator.group_name:
                self.widgets[table][creator.group_name] = self.widgets[table][old_group_name]
                self.widgets[table][creator.group_name][0].winfo_children()[0].configure(text=creator.group_name)
                del self.widgets[table][old_group_name]
            del self.groups[table][old_group_name]
            self.groups[table][creator.group_name] = group

    def remove_item(self, table, group):
        answer = tkinter.messagebox.askyesno(title='confirmation\n',
                                             message=f'Are you sure you want to delete {group} from database?')
        if answer:
            try:
                self.azure.delete_group(table, group)
                for frame in self.widgets[table][group]:
                    frame.destroy()
                del self.groups[table][group]
                del self.widgets[table][group]
                tkinter.messagebox.showinfo(title='SUCCESS',
                                            message=f'group {group} has been successfully removed')
            except KustoError as e:
                tkinter.messagebox.showerror(title="Couldn't delete from DB\n", message=str(e))

    def add_item(self, table, group):
        frame = self.tab_frames[table]
        row = len(frame.winfo_children())
        delete_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "delete.png")), size=(20, 20))
        edit_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "edit.png")), size=(20, 20))
        analyze_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "analyze.png")), size=(20, 20))
        export_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "export.png")), size=(20, 20))
        f = customtkinter.CTkFrame(master=frame)
        f.pack(fill="both", expand=True)
        checkbox = customtkinter.CTkCheckBox(master=f, text=group)
        checkbox.grid(row=row, column=0, padx=(10, 0), pady=(0, 20))
        delete_button = customtkinter.CTkButton(master=f, text="", image=delete_icon,
                                                anchor="center",
                                                fg_color='#E88E8E', hover_color='#BA7272',
                                                command=lambda: self.remove_item(table, group), height=20, width=20)
        delete_button.grid(row=row, column=1, padx=(20, 0), pady=(0, 20), ipadx=0, ipady=0)

        edit_button = customtkinter.CTkButton(master=f, text="", image=edit_icon,
                                              anchor="center",
                                              fg_color='#97C5FF', hover_color='#799ECC',
                                              command=lambda: self.edit_item(table, group), height=20, width=20)
        edit_button.grid(row=row, column=2, padx=(10, 0), pady=(0, 20), ipadx=0, ipady=0)

        g_button = customtkinter.CTkButton(master=f, text="", image=analyze_icon,
                                           anchor="center",
                                           fg_color='#FFF1AD', hover_color='#CCC18A',
                                           command=lambda: self.show_group_data(table, group), height=20, width=20)
        g_button.grid(row=row, column=3, padx=(10, 0), pady=(0, 20))
        export_button = customtkinter.CTkButton(master=f, text="", image=export_icon,
                                                anchor="center",
                                                fg_color='#ACE8C0', hover_color='#8ABA9A',
                                                command=lambda: self.export_to_excel(table, group), height=20, width=20)
        export_button.grid(row=row, column=4, padx=(10, 0), pady=(0, 20))
        self.widgets[table][group].append(f)

    def add_group(self, group_name, table_name, members):
        participants_list = self.p_frame.get_participants(members)
        group = Group(group_name, table_name, participants_list)
        self.groups[table_name][group_name] = group
        self.widgets[table_name][group_name] = []
        self.add_item(table_name, group_name)

    def export_to_excel(self, table_name, group_name):
        # Ask the user to choose the save location and file name
        file_path = customtkinter.filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                               filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            try:
                group = self.groups[table_name][group_name]
                data = group.get_participants_data()
                # Write the DataFrame to the Excel file
                data.to_excel(file_path, index=False)
                tkinter.messagebox.showinfo(title='SUCCESS', message=f'Group {group_name} data exported successfully')
            except Exception as e:
                tkinter.messagebox.showerror(title="ERROR exporting the data\n", message=str(e))

    def show_group_data(self, table, name):
        self.groups[table][name].analyze()

    def show_scatter_plot(self):
        table = self.tabview.get()
        selected_groups = self.get_selected_groups(table)
        if len(selected_groups) < 2:
            tkinter.messagebox.showerror(title='Error\n', message=f'Please select at least 2 groups')
            return
        functionality = self.get_functionality()
        if not functionality:
            return
        all_markers = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'x',
                       'D', 'd', '|', '_', ]
        group_markers = {}
        di = {'total sequences': {}, 'unique sequences': {}, 'shannon': {}, 'simpson': {}}
        for i, group in enumerate(selected_groups):
            group_markers[group.group_name] = all_markers[i] if len(all_markers) > i else 'o'
            for graph in di.keys():
                di[graph][group.group_name] = []
            for p in group.participants:
                for graph in di.keys():
                    di[graph][group.group_name].append(
                        p.diversity_indices[functionality][graph])
        fig, axs = plt.subplots(2, 2)
        fig.canvas.manager.set_window_title('Scatter Plot')
        fig.suptitle(f"{table}'s Groups Diversity Indices - {functionality}", fontweight="bold")
        # Flatten the axs array so that we can loop through each subplot
        axs = axs.ravel()
        for i, key in enumerate(di.keys()):
            self.create_diversity_index_plot(axs[i], di[key], group_markers, key)
        # Adjust layout to avoid overlapping labels
        plt.tight_layout()
        # Show the plot
        plt.show()

    def show_heat_map(self):
        table = self.tabview.get()
        selected_groups = self.get_selected_groups(table)
        if len(selected_groups) < 2:
            tkinter.messagebox.showerror(title='Error\n', message=f'Please select at least 2 groups')
            return
        functionality = self.get_functionality()
        if not functionality:
            return
        # Initialize variables to store heatmap data
        # genes = selected_groups[0].participants[0].cols
        gene = self.get_gene(selected_groups[0].participants[0].cols)
        if not gene:
            return
        # heat_data = {gene: {'total': pd.DataFrame(), 'unique': pd.DataFrame()} for gene in genes}
        heat_data = {'total': pd.DataFrame(), 'unique': pd.DataFrame()}
        line_indices = []
        i = 0
        for group in selected_groups:
            line_indices.append(i)
            i += len(group.participants)
            for participant in group.participants:
                name = participant.individual
                # for gene in genes:
                data = participant.genes[functionality][gene]
                total_series_to_merge = pd.Series(data['total'].values, index=data[gene].values)
                # Convert the series to a numeric data type
                total_series_to_merge = pd.to_numeric(total_series_to_merge, errors='coerce')
                # Convert the series to a float data type
                total_series_to_merge = total_series_to_merge.astype(float)
                unique_series_to_merge = pd.Series(data['unique'].values, index=data[gene].values)
                # Convert the series to a numeric data type
                unique_series_to_merge = pd.to_numeric(unique_series_to_merge, errors='coerce')
                # Convert the series to a float data type
                unique_series_to_merge = unique_series_to_merge.astype(float)
                if heat_data['total'].empty:
                    heat_data['total'][name] = total_series_to_merge
                    heat_data['unique'][name] = unique_series_to_merge
                else:
                    heat_data['total'] = heat_data['total'].merge(total_series_to_merge.rename(name),
                                                                  left_index=True, right_index=True,
                                                                  how='inner')
                    heat_data['unique'] = heat_data['unique'].merge(total_series_to_merge.rename(name),
                                                                    left_index=True, right_index=True,
                                                                    how='inner')
        # Plot heatmaps for total data
        # for i, gene in enumerate(genes):
        self.create_heat_map_plot(heat_data, gene, functionality, line_indices)
        # plt.tight_layout()
        plt.tight_layout(rect=[0, 0, 0.9, 1])
        # Show the plot
        # plt.show(block=False)
        plt.show()

    def create_diversity_index_plot(self, ax, groups, group_markers, title):
        x_positions = np.arange(len(groups)) * 2
        for i, (group_name, values) in enumerate(groups.items()):
            marker_style = group_markers.get(group_name, 'o')  # Default to circle marker if group has no marker defined
            x_vals = x_positions[i] + np.random.rand(
                len(values)) * 0.2 - 0.1  # Add random jitter for better visualization
            ax.scatter(x_vals, values, marker=marker_style, label=group_name)
        ax.set_xticks(x_positions, labels=groups.keys())
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        ax.set_ylabel(title)
        # Connect the mplcursors event to the on_hover function
        mplcursors.cursor(hover=True)

    def create_heat_map_plot(self, heat_gene, gene, functionality, line_indices):
        fig, axs = plt.subplots(1, 2, figsize=(15, 8))
        fig.canvas.manager.set_window_title('Heatmap')
        self.create_heat_map(heat_gene['total'], axs[0], f'{functionality} {gene} - Total', line_indices)
        self.create_heat_map(heat_gene['unique'], axs[1], f'{functionality} {gene} - Unique', line_indices)

    def create_heat_map(self, heat_data, ax, title, line_indices):
        # Create the heatmap
        im = ax.imshow(heat_data, cmap='Blues', aspect='auto')

        # Set ticks and labels for x-axis and y-axis
        ax.set_xticks(np.arange(len(heat_data.columns)))
        ax.set_yticks(np.arange(len(heat_data.index)))
        ax.set_xticklabels(heat_data.columns)
        ax.set_yticklabels(heat_data.index)

        # Rotate the x-axis labels for better visibility
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # Show all ticks and tick labels for both axes
        plt.tick_params(axis='both', which='both', length=0)

        # Add colorbar
        cbar = ax.figure.colorbar(im, ax=ax)

        # Function to format the tooltip text using mplcursors
        def on_hover(event):
            index, col = int(event.index[0]), int(event.index[1])
            value = int(heat_data.iat[index, col])
            label = heat_data.index[index]
            column_name = heat_data.columns[col]
            color_number = int(value * 255)  # Scale value to 0-255 for RGB representation
            event.annotation.set_text(
                f'Gene: {label}\nParticipant: {column_name}\nValue: {value}\nColor Number: {color_number}'
            )

        # Connect the mplcursors event to the on_hover function
        mplcursors.cursor(hover=True).connect("add", on_hover)

        # Set the plot title
        ax.set_title(title)

        # Highlight specific lines on the heatmap if required (line_indices)
        if line_indices:
            for i in line_indices[1:]:
                ax.axvline(x=i - 0.5, color='black', lw=1)

    def get_selected_groups(self, tab):
        selected = []
        for group_name in self.widgets[tab].keys():
            checkbox = self.widgets[tab][group_name][0].winfo_children()[0]
            if checkbox.get():
                selected.append(self.groups[tab][checkbox.cget('text')])
        return selected

    def get_functionality(self):
        functionality_selection = SelectFunctionality()
        functionality_selection.wait_window()
        return functionality_selection.ans

    def get_gene(self, genes):
        gene_selection = SelectGene(genes)
        gene_selection.wait_window()
        return gene_selection.ans

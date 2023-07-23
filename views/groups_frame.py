import tkinter
import tkinter.messagebox
import customtkinter
from database.database_manager import AzureDatabaseManager
from azure.kusto.data.exceptions import KustoError
from participants.group import Group
from views.creator import GroupCreator
from views.selector import SelectFunctionality
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import os


class GroupFrame(customtkinter.CTk):
    def __init__(self, root, table_names, p_frame):
        super().__init__()
        self.root = root
        self.p_frame = p_frame
        self.azure = AzureDatabaseManager('shiba')
        self.groups = {}
        self.groups_frame = customtkinter.CTkFrame(self.root, width=500)
        self.groups_frame.grid(row=0, column=2, rowspan=4, columnspan=2, padx=(20, 20), pady=(20, 20), sticky="nsew")
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
        self.tabview = customtkinter.CTkTabview(self.groups_frame, width=500)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        for table in self.table_names:
            self.create_tab(table)
        self.create_analyze_groups()

    def create_analyze_groups(self):
        analyze_groups_frame = customtkinter.CTkFrame(self.groups_frame)
        analyze_groups_frame.grid(row=1, column=2, padx=(20, 0), sticky="nsew")
        analyze_groups_frame.grid_columnconfigure((0, 1), weight=1)
        heat_map_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "heatmap.png")), size=(20, 20))

        heat_map_button = customtkinter.CTkButton(master=analyze_groups_frame, text="heat map", image=heat_map_icon,
                                                  anchor="center", fg_color='#188e99', hover_color='#0f5c63',
                                                  command=lambda: print("sssss"), height=20, width=20)
        heat_map_button.grid(row=0, column=0, padx=(10, 0), pady=(0, 20), ipadx=0, ipady=0, sticky="se")
        scatter_graph_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "scattergraph.png")),
                                                    size=(20, 20))

        scatter_graph_button = customtkinter.CTkButton(master=analyze_groups_frame, text="scatter graph",
                                                       image=scatter_graph_icon, anchor="center",
                                                       fg_color='#188e99', hover_color='#0f5c63',
                                                       command=self.show_scatter_graph, height=20, width=20)
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
        creator.create()
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
        f = customtkinter.CTkFrame(master=frame)
        f.pack(fill="both", expand=True)
        checkbox = customtkinter.CTkCheckBox(master=f, text=group)
        checkbox.grid(row=row, column=0, padx=(10, 0), pady=(0, 20))
        delete_button = customtkinter.CTkButton(master=f, text="", image=delete_icon,
                                                anchor="center",
                                                fg_color='#ff0004', hover_color='#d10407',
                                                command=lambda: self.remove_item(table, group), height=20, width=20)
        delete_button.grid(row=row, column=1, padx=0, pady=(0, 20), ipadx=0, ipady=0)

        edit_button = customtkinter.CTkButton(master=f, text="", image=edit_icon,
                                              anchor="center",
                                              fg_color='#0525f5', hover_color='#0319a8',
                                              command=lambda: self.edit_item(table, group), height=20, width=20)
        edit_button.grid(row=row, column=2, padx=(10, 0), pady=(0, 20), ipadx=0, ipady=0)

        g_button = customtkinter.CTkButton(master=f, text="", image=analyze_icon,
                                           anchor="center",
                                           fg_color='#63e83a', hover_color='#47ab29',
                                           command=lambda: self.show_group_data(table, group), height=20, width=20)
        g_button.grid(row=row, column=3, padx=(10, 0), pady=(0, 20))
        self.widgets[table][group].append(f)

    def add_group(self, group_name, table_name, members):
        participants_list = self.p_frame.get_participants(members)
        group = Group(group_name, table_name, participants_list)
        self.groups[table_name][group_name] = group
        self.widgets[table_name][group_name] = []
        self.add_item(table_name, group_name)

    def show_group_data(self, table, name):
        self.groups[table][name].analyze()

    def show_scatter_graph(self):
        table = self.tabview.get()
        selected_groups = self.get_selected_groups(table)
        if len(selected_groups) < 2:
            tkinter.messagebox.showerror(title='Error\n', message=f'Please select at least 2 groups')
            return
        functionality_selection = SelectFunctionality()
        functionality_selection.create()
        functionality_selection.wait_window()
        functionality = functionality_selection.ans
        if functionality:
            all_markers = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', 's', 'p', '*', 'h', 'H', '+', 'x',
                           'D', 'd', '|', '_', ]
            group_markers = {}
            diversity_indices = {'total sequences': {}, 'unique sequences': {}, 'shannon': {}, 'simpson': {}}
            for i, group in enumerate(selected_groups):
                group_markers[group.group_name] = all_markers[i] if len(all_markers) > i else 'o'
                for graph in diversity_indices.keys():
                    diversity_indices[graph][group.group_name] = []
                for p in group.participants:
                    for graph in diversity_indices.keys():
                        diversity_indices[graph][group.group_name].append(
                            p.diversity_indices['cdr3aa'][functionality][graph])
            fig, axs = plt.subplots(2, 2)
            fig.suptitle(f"{table}'s Groups Diversity Indices - {functionality}", fontweight="bold")
            # Flatten the axs array so that we can loop through each subplot
            axs = axs.ravel()
            for i, key in enumerate(diversity_indices.keys()):
                self.create_diversity_index_plot(axs[i], diversity_indices[key], group_markers, key)
            # Adjust layout to avoid overlapping labels
            plt.tight_layout()
            # Show the plot
            plt.show()

    def create_diversity_index_plot(self, ax, groups, group_markers, title):
        x_positions = np.arange(len(groups)) * 2
        for i, (group_name, values) in enumerate(groups.items()):
            marker_style = group_markers.get(group_name, 'o')  # Default to circle marker if group has no marker defined
            x_vals = x_positions[i] + np.random.rand(
                len(values)) * 0.2 - 0.1  # Add random jitter for better visualization
            ax.scatter(x_vals, values, marker=marker_style, label=group_name)
        ax.set_xticks(x_positions, labels=groups.keys())
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                 rotation_mode="anchor")
        ax.set_ylabel(title)

    def get_selected_groups(self, tab):
        selected = []
        for group_name in self.widgets[tab].keys():
            checkbox = self.widgets[tab][group_name][0].winfo_children()[0]
            if checkbox.get():
                selected.append(self.groups[tab][checkbox.cget('text')])
        return selected

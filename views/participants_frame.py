import tkinter
import tkinter.messagebox
import tkinter.ttk
import customtkinter
from database.database_manager import AzureDatabaseManager
from PIL import Image
import os
from participants.participant import Participant


class ParticipantFrame(customtkinter.CTk):
    def __init__(self, root, table_names, grid=None):
        super().__init__()
        self.root = root
        self.azure = AzureDatabaseManager('shiba')
        self.grid = grid
        self.image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons')
        self.tabview = None
        self.tabs = {}
        self.p_frames = []
        self.table_names = table_names
        self.widgets = {}
        self.participants = {}
        self.create_all_participants()
        self.create_tab_views()

    def create_all_participants(self):
        for table in self.table_names:
            names = self.azure.get_participants_names_from_table(table)
            for name in names:
                self.participants[name] = Participant(table, name)

    def create_tab_views(self):
        self.tabview = customtkinter.CTkTabview(self.root, width=500)
        self.tabview.grid(row=0, column=1, rowspan=4, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.create_info_tabs()
        # add tabs
        for tab_info in self.tabs:
            self.create_tab(tab_info)

    def create_info_tabs(self):
        controls = [name for name in self.participants.keys() if name.startswith("C_")]
        patients = [name for name in self.participants.keys() if not name.startswith("C_")]
        self.tabs = [{'name': 'Patients', 'col_tab': 0, 'row_tab': 0, 'values': patients},
                     {'name': 'Controls', 'col_tab': 1, 'row_tab': 0, 'values': controls}]
        for table in self.table_names:
            if table == 'IGH_new':
                table = 'IGH'
            names = [name for name in self.participants.keys() if table in name]
            tab_info = {'name': table, 'col_tab': len(self.tabs), 'row_tab': 0, 'values': names}
            self.tabs.append(tab_info)
        self.tabs.append(
            {'name': 'All', 'col_tab': len(self.tabs), 'row_tab': 0, 'values': self.participants.keys()})

    def create_tab1(self, tab_info):
        # create scrollable frame
        name = tab_info['name']
        values = tab_info['values']
        self.tabview.add(name)
        # self.tabview(name).grid(row=0, column=1, rowspan=4, padx=(20, 0), pady=(20, 20), sticky="nsew")
        # self.tabview.tab(name).grid_columnconfigure(tab_info["col_tab"])  # configure grid of individual tabs
        scrollable_frame = customtkinter.CTkScrollableFrame(self.tabview.tab(name))
        scrollable_frame.grid(row=0, column=1, rowspan=8, columnspan=2, sticky="nsew")
        # scrollable_frame.grid(row=0, column=0, rowspan=8, columnspan=2)
        # scrollable_frame.grid_columnconfigure(0, weight=250)
        # scrollable_frame.grid_columnconfigure((1, 2), weight=1)
        image_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "delete.png")), size=(20, 20))
        for i, p in enumerate(values):
            if not self.widgets.get(p):
                self.widgets[p] = {}
            self.widgets[p][name] = customtkinter.CTkFrame(master=scrollable_frame)
            self.widgets[p][name].grid(row=i, column=0, rowspan=4, columnspan=2)
            p_button = customtkinter.CTkButton(master=self.widgets[p][name], text=p, anchor="center",
                                               command=lambda: self.show_participant(p))
            p_button.grid(row=i, column=0, padx=10, pady=(0, 20))
            delete_button = customtkinter.CTkButton(master=self.widgets[p][name], text="", image=image_icon,
                                                    anchor="center",
                                                    fg_color='#ff0004', hover_color='#d10407',
                                                    command=lambda: self.remove_item(p), height=20, width=20)
            delete_button.grid(row=i, column=1, padx=0, pady=(0, 20), ipadx=0, ipady=0)
            # self.p_frames.append(self.widgets[p][name])
            # if self.widgets.get(p):
            #     self.widgets[p].append(self.p_frames[-1])
            # else:
            #     self.widgets[p] = [self.p_frames[-1]]

    def create_tab(self, tab_info):
        # create scrollable frame
        name = tab_info['name']
        values = tab_info['values']
        self.tabview.add(name)

        # Create a canvas widget inside the tab
        canvas = customtkinter.CTkCanvas(self.tabview.tab(name))
        # canvas.grid(column=0, row=0, side="left", fill="both", expand=True)
        canvas.pack(side='left', fill='both', expand=True)

        # Create a frame inside the canvas for the buttons
        # frame = tkinter.ttk.Frame(canvas)
        frame = customtkinter.CTkFrame(canvas)

        # Add a scrollbar to the canvas
        # scrollbar = tkinter.ttk.Scrollbar(self.tabview.tab(name), orient='vertical', command=canvas.yview)
        scrollbar = customtkinter.CTkScrollbar(self.tabview.tab(name), orientation='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        canvas.configure(yscrollcommand=scrollbar.set, bg=self.tabview.tab(name).cget("fg_color")[1])
        # canvas.configure(yscrollcommand=scrollbar.set)

        # Configure the canvas to scroll the frame
        canvas.create_window((0, 0), window=frame, anchor='nw')

        # Function to update the scroll region
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox('all'))

        # Configure the scroll region when the frame size changes
        frame.bind('<Configure>', configure_scroll_region)

        image_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "delete.png")), size=(20, 20))
        for i, p in enumerate(values):
            if not self.widgets.get(p):
                self.widgets[p] = {}
            self.widgets[p][name] = customtkinter.CTkFrame(master=frame)
            self.widgets[p][name].grid(row=i, column=0, rowspan=4, columnspan=2, pady=(0, 20))
            p_button = customtkinter.CTkButton(master=self.widgets[p][name], text=p, anchor="center",
                                               command=lambda: self.show_participant(p))
            p_button.grid(row=i, column=0, padx=10, pady=(0, 20))
            delete_button = customtkinter.CTkButton(master=self.widgets[p][name], text="", image=image_icon,
                                                    anchor="center",
                                                    fg_color='#ff0004', hover_color='#d10407',
                                                    command=lambda: self.remove_item(p), height=20, width=20)
            delete_button.grid(row=i, column=1, padx=0, pady=(0, 20), ipadx=0, ipady=0)
            # self.p_frames.append(self.widgets[p][name])
            # if self.widgets.get(p):
            #     self.widgets[p].append(self.p_frames[-1])
            # else:
            #     self.widgets[p] = [self.p_frames[-1]]

    def remove_item(self, individual):
        answer = tkinter.messagebox.askyesno(title='confirmation\n',
                                             message=f'Are you sure you want to delete {individual} from database?')
        if answer:
            del self.participants[individual]
            # todo: remove from DB
            self.tabview.destroy()
            self.create_tab_views()

    def add_item(self, participant, df=None):
        # todo: add to DB
        # self.azure.insert_participant(df, participant.table_name)
        self.participants[participant.get_individual()] = participant
        self.tabview.destroy()
        self.create_tab_views()

    def get_relevant_tabs(self, individual):
        tabs = [self.tabview.tab('All')]
        table_name = ''
        if individual.startswith("C_"):
            tabs.append(self.tabview.tab("Controls"))
        else:
            tabs.append(self.tabview.tab("Patients"))
        for table in self.table_names:
            if table in individual:
                tabs.append(self.tabview.tab(table))
                table_name = table
                break
        return table_name, tabs

    def get_relevant_tab_names(self, individual):
        tabs = ['All']
        table_name = ''
        if individual.startswith("C_"):
            tabs.append('Controls')
        else:
            tabs.append('Patients')
        for table in self.table_names:
            if table in individual:
                tabs.append(table)
                table_name = table
                break
        return table_name, tabs

    def remove_item1(self, individual):
        for tab in self.widgets[individual].keys():
            self.widgets[individual][tab].destroy()
            # widget.destroy()
        # table_name, tabs = self.get_relevant_tab_names(individual)
        # for tab in tabs:
        #     frame = self.widgets[tab][individual]
        #     if frame:
        #         frame.destroy()
        # for widget in frame.winfo_children():
        #     widget.destroy()
        # todo: remove from DB
        # for tab in tabs:
        #     ss = tab.winfo_children()[0].winfo_children()[0].winfo_children()[0].winfo_children()
        #     for s in ss:
        #         if s._text == individual:
        #             s.destroy()
        #             break
        #     # s = tab.winfo_children()
        pass

    def clear(self):
        for widget_tuple in self.widgets:
            widget_tuple[0].destroy()
        self.widgets.clear()

    def show_participant(self, individual):
        self.participants[individual].analyze()

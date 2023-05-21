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
        self.p_frames = []
        self.table_names = table_names
        self.widgets = {}
        self.names = self.azure.get_all_participants_names()
        self.tab_frames = {}
        self.participants = {}
        self.create_tab_views()
        self.create_all_participants()

    def create_all_participants(self):
        for name in self.names:
            self.add_participant(name)

    def create_tab_views(self):
        self.tabview = customtkinter.CTkTabview(self.root, width=500)
        self.tabview.grid(row=0, column=1, rowspan=4, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.create_tab('Patients')
        self.create_tab('Controls')
        for table in self.table_names:
            if table == 'IGH_new':
                table = 'IGH'
            self.create_tab(table)
        self.create_tab('All')

    def create_tab(self, name):
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
        self.tab_frames[name] = frame

    def remove_item(self, individual):
        answer = tkinter.messagebox.askyesno(title='confirmation\n',
                                             message=f'Are you sure you want to delete {individual} from database?')
        if answer:
            del self.participants[individual]
            # todo: remove from DB
            for frame in self.widgets[individual]:
                frame.destroy()
            # self.tabview.destroy()
            # self.create_tab_views()

    def add_item(self, frame, p):
        row = len(frame.winfo_children())
        image_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "delete.png")), size=(20, 20))
        f = customtkinter.CTkFrame(master=frame)
        f.grid(row=row, column=0, pady=(0, 20))
        p_button = customtkinter.CTkButton(master=f, text=p, anchor="center",
                                           command=lambda: self.show_participant(p))
        p_button.grid(row=row, column=0, padx=10, pady=(0, 20))
        delete_button = customtkinter.CTkButton(master=f, text="", image=image_icon,
                                                anchor="center",
                                                fg_color='#ff0004', hover_color='#d10407',
                                                command=lambda: self.remove_item(p), height=20, width=20)
        delete_button.grid(row=row, column=1, padx=0, pady=(0, 20), ipadx=0, ipady=0)
        self.widgets[p].append(f)

    def add_participant(self, individual):
        table, tab_names = self.get_relevant_tab_names(individual)
        self.participants[individual] = Participant(table, individual)
        self.widgets[individual] = []
        for tab in tab_names:
            self.add_item(self.tab_frames[tab], individual)

    def get_relevant_tab_names(self, individual):
        tabs = ['All']
        table_name = ''
        if individual.startswith("C_"):
            tabs.append('Controls')
        else:
            tabs.append('Patients')
        for table in self.table_names:
            if table == 'IGH_new':
                table = 'IGH'
            if table in individual:
                tabs.append(table)
                table_name = table
                break
        return table_name, tabs

    def show_participant(self, individual):
        self.participants[individual].analyze()

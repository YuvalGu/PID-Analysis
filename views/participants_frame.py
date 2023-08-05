import tkinter
import tkinter.messagebox
import tkinter.ttk
import customtkinter
from database.database_manager import AzureDatabaseManager
from PIL import Image
import os
from participants.participant import Participant
from views.knn_results import KnnResults
from model.knn import Knn
from azure.kusto.data.exceptions import KustoError


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
        self.tab_names = ['Patients', 'Controls'] + self.table_names + ['All']
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
        self.tabview = customtkinter.CTkTabview(self.root)
        self.tabview.grid(row=0, column=1, rowspan=4, padx=(20, 0), pady=(0, 20), sticky="nsew")
        for name in self.tab_names:
            self.create_tab(name)

    def create_tab(self, name):
        self.tabview.add(name)

        # Create a canvas widget inside the tab
        canvas = customtkinter.CTkCanvas(self.tabview.tab(name))
        canvas.pack(side='left', fill='both', expand=True)
        # Create a frame inside the canvas for the buttons
        frame = customtkinter.CTkFrame(canvas)

        # Add a scrollbar to the canvas
        # scrollbar = tkinter.ttk.Scrollbar(self.tabview.tab(name), orient='vertical', command=canvas.yview)
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

    def remove_item(self, individual):
        answer = tkinter.messagebox.askyesno(title='confirmation\n',
                                             message=f'Are you sure you want to delete {individual} from database?')
        if answer:
            table_name, _ = self.get_relevant_tab_names(individual)
            try:
                self.azure.delete_participant(table_name, individual)
                self.azure.delete_participant_from_group(individual)
                for frame in self.widgets[individual]:
                    frame.destroy()
                del self.widgets[individual]
                del self.participants[individual]
                tkinter.messagebox.showinfo(title='SUCCESS',
                                            message=f'participant {individual} has been successfully removed')
            except KustoError as e:
                tkinter.messagebox.showerror(title="Couldn't delete from DB\n", message=str(e))

    def add_item(self, frame, p):
        row = len(frame.winfo_children())
        image_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "delete.png")), size=(20, 20))
        export_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "export.png")), size=(20, 20))
        f = customtkinter.CTkFrame(master=frame)
        f.pack(fill="both", expand=True)
        p_button = customtkinter.CTkButton(master=f, text=p, anchor="center",
                                           command=lambda: self.show_participant(p))
        p_button.grid(row=row, column=0, padx=10, pady=(0, 20))
        delete_button = customtkinter.CTkButton(master=f, text="", image=image_icon,
                                                anchor="center",
                                                fg_color='#E88E8E', hover_color='#BA7272',
                                                command=lambda: self.remove_item(p), height=20, width=20)
        delete_button.grid(row=row, column=1, padx=0, pady=(0, 20), ipadx=0, ipady=0)
        export_button = customtkinter.CTkButton(master=f, text="", image=export_icon, anchor="center",
                                                fg_color='#ACE8C0', hover_color='#8ABA9A',
                                                command=lambda: self.participants[p].export_to_excel(), height=20,
                                                width=20)
        export_button.grid(row=row, column=2, padx=(10, 0), pady=(0, 20))

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
            if table in individual:
                tabs.append(table)
                table_name = table
                break
        return table_name, tabs

    def show_participant(self, individual):
        self.participants[individual].analyze()

    def get_participants(self, individuals):
        participants_list = []
        for individual in individuals:
            participants_list.append(self.participants[individual])
        return participants_list

    def show_knn(self, table, names, individual, k):
        target_participant = self.participants[individual]
        participants_list = []
        for name in names:
            participants_list.append(self.participants[name])
        knn = Knn(participants_list, k)

        # Find the k-nearest neighbors of the target participant
        k_nearest_neighbors, distances = knn.find_k_nearest_neighbors(target_participant)

        # Extract true labels and predicted labels for validation
        true_labels = [1 if participant is target_participant else 0 for participant in participants_list]
        predicted_labels = [1 if participant in k_nearest_neighbors else 0 for participant in participants_list]

        # Calculate validation metrics
        accuracy, precision, recall, f1 = knn.calculate_metrics(true_labels, predicted_labels)
        validation_metrics = {'Accuracy': accuracy, 'Precision': precision, 'Recall': recall, 'F1': f1}

        KnnResults(target_participant, self.get_participants(k_nearest_neighbors), validation_metrics, distances)

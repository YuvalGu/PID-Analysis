import tkinter
import tkinter.messagebox
import customtkinter
import pandas as pd
from database.database_manager import AzureDatabaseManager
from azure.kusto.data.exceptions import KustoError


class ParticipantCreator(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.participant = None
        self.participant_data = None
        # todo: get options from json file - not hardcoded
        self.options = ['IGH', 'TRB', 'TRG']
        # self.get_table_options()

        # upload frame parameters
        self.file_path = None
        self.file_label = None
        self.cell = None
        self.chain = None
        self.file_button = None
        self.control_box = None
        self.apply_button = None

    def create(self):
        # configure window
        self.title("Upload Participant")
        self.geometry(f"{450}x{225}")

        # configure grid layout (5x2)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=2)

        # on top
        self.lift()
        self.attributes("-topmost", True)

        # check if control
        self.control_box = customtkinter.CTkCheckBox(master=self, text='Control')
        self.control_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Enter type of cell
        self.cell = customtkinter.CTkEntry(self, placeholder_text="Enter type of cell")
        self.cell.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        #  Choose/Enter chain
        self.chain = customtkinter.CTkComboBox(self, values=self.options)
        self.chain.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.chain.set("Choose/Enter chain")

        # Choose file
        self.file_button = customtkinter.CTkButton(self, command=self.choose_file, text='Choose csv file',
                                                   fg_color='#4d4d4d', text_color=("gray", "#DCE4EE"))
        self.file_button.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Apply button
        self.apply_button = customtkinter.CTkButton(master=self, border_width=2,
                                                    text='Apply', command=self.apply)
        self.apply_button.grid(row=4, column=1, columnspan=2, sticky="nsew")

    def choose_file(self):
        self.attributes("-topmost", False)
        self.file_path = customtkinter.filedialog.askopenfilename()
        self.attributes("-topmost", True)
        self.file_button.grid(row=3, column=0, columnspan=1, sticky="nsew", padx=10, pady=10)
        customtkinter.CTkLabel(master=self, text=self.file_path).grid(row=3, column=1, columnspan=1, padx=10, pady=10)

    def apply(self):
        valid = True
        azure = AzureDatabaseManager('shiba')
        chain_ans = self.chain.get()
        cell_ans = self.cell.get()
        prefix = 'C_' if self.control_box.get() == 1 else ''
        individual = f'{prefix}{cell_ans}_{chain_ans}'
        # validate chain:
        if chain_ans == "Choose/Enter chain" or chain_ans == '':
            tkinter.messagebox.showerror(title='Invalid Chain\n', message='Error: Please enter chain')
            valid = False

        # validate cell:
        elif cell_ans == "Enter type of cell" or cell_ans == '':
            tkinter.messagebox.showerror(title='Invalid Cell\n', message='Error: Please enter cell')
            valid = False

        # validate file
        elif not self.file_path or not self.file_path.lower().endswith('csv'):
            self.file_path = None
            tkinter.messagebox.showerror(title='Invalid File\n', message='Error: Invalid file.\n Please choose '
                                                                         'csv file')
            valid = False

        # check if exists in database
        elif azure.participant_exists(individual, chain_ans):
            tkinter.messagebox.showerror(title='Already Exists\n',
                                         message=f'Error: {individual} already exists in database')
            valid = False

        if valid:
            try:
                self.participant_data = pd.read_csv(self.file_path, encoding="ISO-8859-1")
                self.participant_data['chain'] = chain_ans
                self.participant_data['individual'] = individual
                azure.insert_participant(self.participant_data, chain_ans)
                self.participant = individual
                tkinter.messagebox.showinfo(title='SUCCESS',
                                            message=f'participant {individual} has been successfully added')
            except UnicodeDecodeError as e:
                tkinter.messagebox.showerror(title="Couldn't read csv file\n", message=str(e))
            except KustoError as e:
                tkinter.messagebox.showerror(title="Couldn't insert to DB\n", message=str(e))
        self.destroy()


class GroupCreator(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.azure = AzureDatabaseManager('shiba')
        self.participants = self.azure.get_all_participants_names()

        # create frame parameters
        self.group_name = None
        self.p_checkbox = []
        self.apply_button = None

    def create(self):
        # configure window
        self.title("Create Group")
        self.geometry(f"{450}x{300}")

        # configure grid layout (3x2)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=2)

        # on top
        self.lift()
        self.attributes("-topmost", True)

        # Enter group name
        self.group_name = customtkinter.CTkEntry(self, placeholder_text="Enter group name")
        self.group_name.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        scrollable_frame = customtkinter.CTkScrollableFrame(self)
        scrollable_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        for name in self.participants:
            checkbox = customtkinter.CTkCheckBox(master=scrollable_frame, text=name)
            checkbox.grid(row=len(self.p_checkbox), column=0, pady=(20, 0), padx=(20, 0), sticky="w")
            self.p_checkbox.append(checkbox)

        # Apply button
        self.apply_button = customtkinter.CTkButton(master=self, border_width=2,
                                                    text='Apply', command=self.apply)
        self.apply_button.grid(row=2, column=1, sticky="nsew")

    def apply(self):
        valid = True
        group_name_ans = self.group_name.get()

        # validate group name:
        if group_name_ans == "Enter group name" or group_name_ans == '':
            tkinter.messagebox.showerror(title='Invalid name\n', message='Error: Please enter group name')
            valid = False

        # check if exists in database
        elif self.azure.group_exists(group_name_ans):
            tkinter.messagebox.showerror(title='Already Exists\n',
                                         message=f'Error: {group_name_ans} already exists in database')
            valid = False

        # check if at least 2 participants:
        members = []
        for check_box in self.p_checkbox:
            if check_box.get():
                members.append(check_box.cget('text'))
        if len(members) < 2:
            tkinter.messagebox.showerror(title='Invalid Group\n',
                                         message=f'Error: please choose at least 2 participants')
            valid = False

        if valid:
            try:
                # todo: insert group to database
                # self.azure.insert_group() parameters: group name ans list of individuals
                self.group = group_name_ans
                tkinter.messagebox.showinfo(title='SUCCESS',
                                            message=f'Group {group_name_ans} has been successfully added')
            except KustoError as e:
                tkinter.messagebox.showerror(title="Couldn't insert to DB\n", message=str(e))
        self.destroy()

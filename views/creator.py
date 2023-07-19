import tkinter
import tkinter.messagebox
import customtkinter
import pandas as pd
from database.database_manager import AzureDatabaseManager
from participants.participant import Participant
from participants.group import Group
from azure.kusto.data.exceptions import KustoError


class ParticipantCreator(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.participant = None
        self.participant_data = None
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
                azure.insert_data(self.participant_data, chain_ans)
                self.participant = individual
                tkinter.messagebox.showinfo(title='SUCCESS',
                                            message=f'participant {individual} has been successfully added')
            except UnicodeDecodeError as e:
                tkinter.messagebox.showerror(title="Couldn't read csv file\n", message=str(e))
            except KustoError as e:
                tkinter.messagebox.showerror(title="Couldn't insert to DB\n", message=str(e))
        self.destroy()


class GroupCreator(customtkinter.CTkToplevel):
    def __init__(self, table_name, group_name=None, members=None, edit=False):
        super().__init__()
        if members is None:
            members = []
        self.azure = AzureDatabaseManager('shiba')
        self.table_name = table_name
        # create frame parameters
        self.members = members
        self.group_name = group_name
        self.edit = edit
        self.p_checkbox = []
        self.valid = True
        self.group_entry = None
        self.apply_button = None
        self.participants = self.azure.get_participants_names_from_table(table_name)

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
        self.group_entry = customtkinter.CTkEntry(self, placeholder_text="Enter group name")
        # self.group_entry = customtkinter.CTkEntry(self)
        if self.edit:
            self.group_entry.insert(0, self.group_name)
        # else:
        #     self.group_entry.insert(0, "Enter group name")
        self.group_entry.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        scrollable_frame = customtkinter.CTkScrollableFrame(self)
        scrollable_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        for name in self.participants:
            checkbox = customtkinter.CTkCheckBox(master=scrollable_frame, text=name)
            checkbox.grid(row=len(self.p_checkbox), column=0, pady=(20, 0), padx=(20, 0), sticky="w")
            if self.edit and name in self.members:
                checkbox.select()
            self.p_checkbox.append(checkbox)

        # Apply button
        self.apply_button = customtkinter.CTkButton(master=self, border_width=2,
                                                    text='Apply', command=self.apply)
        self.apply_button.grid(row=2, column=1, sticky="nsew")

    def apply(self):
        self.group_name = self.group_entry.get()
        self.members = []
        for check_box in self.p_checkbox:
            if check_box.get():
                self.members.append(check_box.cget('text'))

        # validate group name:
        if self.group_name == "Enter group name" or self.group_name == '':
            tkinter.messagebox.showerror(title='Invalid name\n', message='Error: Please enter group name')
            self.valid = False

        # check if exists in database
        elif not self.edit and self.azure.group_exists(self.group_name, self.table_name):
            tkinter.messagebox.showerror(title='Already Exists\n',
                                         message=f'Error: {self.group_name} already exists in database')
            self.valid = False

        # check if at least 2 participants:
        elif len(self.members) < 2:
            tkinter.messagebox.showerror(title='Invalid Group\n',
                                         message=f'Error: please choose at least 2 participants')
            self.valid = False
        if self.valid:
            try:
                group_df = pd.DataFrame(columns=['group_name', 'table_name', 'individual'])
                for individual in self.members:
                    group_df.loc[len(group_df)] = {'group_name': self.group_name, 'table_name': self.table_name,
                                                   'individual': individual}
                if self.edit:
                    self.azure.delete_group(self.table_name, self.group_name)
                self.azure.insert_data(group_df, 'groups')
                tkinter.messagebox.showinfo(title='SUCCESS',
                                            message=f'Group {self.group_name} has been successfully added')
            except KustoError as e:
                tkinter.messagebox.showerror(title="Couldn't insert to DB\n", message=str(e))
                self.group = None
        self.destroy()


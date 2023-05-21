import tkinter
import tkinter.messagebox
import customtkinter
import pandas as pd
from participants.participant import Participant
from database.database_manager import AzureDatabaseManager


class ParticipantCreator(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.participant = None
        self.participant_data = None
        # todo: get options from json file - not hardcoded
        self.options = ['IGH_new', 'TRB', 'TRG']
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
            self.participant_data = pd.read_csv(self.file_path, encoding="ISO-8859-1")
            self.participant_data['chain'] = chain_ans
            self.participant_data['individual'] = individual
            self.participant = Participant(chain_ans, individual)
            # todo: insert data to in DB
            # tkinter.messagebox.showerror(title='DB Error\n',
            #                              message=f"couldn't insert participant {individual} to Database")
        self.destroy()

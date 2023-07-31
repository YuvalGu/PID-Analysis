import tkinter
import tkinter.messagebox
import customtkinter
from database.database_manager import AzureDatabaseManager


class SelectChain(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.chain = ['IGH', 'TRB', 'TRG']
        # create frame parameters
        self.table = None
        self.radio_var = tkinter.IntVar(value=0)
        # configure window
        self.title("Choose Chain")
        self.geometry(f"{250}x{150}")

        # Get the current mouse position
        mouse_x, mouse_y = self.winfo_pointerx(), self.winfo_pointery()

        # Calculate the window position relative to the mouse
        window_x = mouse_x - 125  # Adjust this value to change the window's horizontal position
        window_y = mouse_y - 75  # Adjust this value to change the window's vertical position

        # Set the window position
        self.geometry(f"+{window_x}+{window_y}")

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=2)

        # on top
        self.lift()
        self.attributes("-topmost", True)

        radio_button_1 = customtkinter.CTkRadioButton(master=self, text=self.chain[0], variable=self.radio_var, value=0)
        radio_button_1.grid(row=0, column=0, padx=(10, 0), sticky="w")
        radio_button_2 = customtkinter.CTkRadioButton(master=self, text=self.chain[1], variable=self.radio_var, value=1)
        radio_button_2.grid(row=1, column=0, padx=(10, 0), sticky="w")
        radio_button_3 = customtkinter.CTkRadioButton(master=self, text=self.chain[2], variable=self.radio_var, value=2)
        radio_button_3.grid(row=2, column=0, padx=(10, 0), sticky="w")

        # Apply button
        self.apply_button = customtkinter.CTkButton(master=self, border_width=2, text='Apply', command=self.apply)
        self.apply_button.grid(row=3, column=1, sticky="nsew")

    def apply(self):
        i = self.radio_var.get()
        self.table = self.chain[i]
        self.destroy()


class SelectFunctionality(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.functionality = ['productive', 'unproductive']
        # create frame parameters
        self.ans = None
        self.radio_var = tkinter.IntVar(value=0)
        # configure window
        self.title("Choose Functionality")
        self.geometry(f"{250}x{150}")

        # Get the current mouse position
        mouse_x, mouse_y = self.winfo_pointerx(), self.winfo_pointery()

        # Calculate the window position relative to the mouse
        window_x = mouse_x - 125  # Adjust this value to change the window's horizontal position
        window_y = mouse_y - 75  # Adjust this value to change the window's vertical position

        # Set the window position
        self.geometry(f"+{window_x}+{window_y}")

        # configure grid layout (4x2)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=2)

        # on top
        self.lift()
        self.attributes("-topmost", True)
        radio_button_1 = customtkinter.CTkRadioButton(master=self, text=self.functionality[0], variable=self.radio_var,
                                                      value=0)
        radio_button_1.grid(row=0, column=0, padx=(10, 0), sticky="w")
        radio_button_2 = customtkinter.CTkRadioButton(master=self, text=self.functionality[1], variable=self.radio_var,
                                                      value=1)
        radio_button_2.grid(row=1, column=0, padx=(10, 0), sticky="w")

        # Apply button
        self.apply_button = customtkinter.CTkButton(master=self, border_width=2, text='Apply', command=self.apply)
        self.apply_button.grid(row=2, column=1, sticky="nsew")

    def apply(self):
        i = self.radio_var.get()
        self.ans = self.functionality[i]
        self.destroy()


class SelectGene(customtkinter.CTkToplevel):
    def __init__(self, genes=None):
        super().__init__()
        if genes is None:
            genes = ['jgene', 'dgene', 'vgene']
        self.genes = genes
        # create frame parameters
        self.ans = None
        self.radio_var = tkinter.IntVar(value=0)

        # configure window
        self.title("Choose Gene")
        self.geometry(f"{270}x{150}")

        # Get the current mouse position
        mouse_x, mouse_y = self.winfo_pointerx(), self.winfo_pointery()

        # Calculate the window position relative to the mouse
        window_x = mouse_x - 125  # Adjust this value to change the window's horizontal position
        window_y = mouse_y - 75  # Adjust this value to change the window's vertical position

        # Set the window position
        self.geometry(f"+{window_x}+{window_y}")

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=2)

        # on top
        self.lift()
        self.attributes("-topmost", True)

        for i, gene in enumerate(self.genes):
            radio_button_1 = customtkinter.CTkRadioButton(master=self, text=gene, variable=self.radio_var, value=i)
            radio_button_1.grid(row=i, column=0, padx=(10, 0), sticky="w")

        # Apply button
        self.apply_button = customtkinter.CTkButton(master=self, border_width=2, text='Apply', command=self.apply)
        self.apply_button.grid(row=len(self.genes), column=1, sticky="nsew")

    def apply(self):
        i = self.radio_var.get()
        self.ans = self.genes[i]
        self.destroy()


class SelectData(customtkinter.CTkToplevel):
    def __init__(self, genes=None):
        super().__init__()
        if genes is None:
            genes = ['jgene', 'dgene', 'vgene']
        self.genes = genes
        self.values = ['diversity indices']
        for gene in self.genes:
            self.values.append(f'{gene} productive')
            self.values.append(f'{gene} unproductive')
        # create frame parameters
        self.ans = None
        self.radio_var = tkinter.IntVar(value=0)

        # configure window
        self.title("Choose data type")
        if len(self.genes) == 3:
            self.geometry(f"{300}x{310}")
        else:
            self.geometry(f"{300}x{250}")

        # Get the current mouse position
        mouse_x, mouse_y = self.winfo_pointerx(), self.winfo_pointery()

        # Calculate the window position relative to the mouse
        window_x = mouse_x - 125  # Adjust this value to change the window's horizontal position
        window_y = mouse_y - 75  # Adjust this value to change the window's vertical position

        # Set the window position
        self.geometry(f"+{window_x}+{window_y}")

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        # on top
        self.lift()
        self.attributes("-topmost", True)

        for i, value in enumerate(self.values):
            radio_button_1 = customtkinter.CTkRadioButton(master=self, text=value, variable=self.radio_var, value=i)
            radio_button_1.grid(row=i, column=0, padx=(10, 0), pady=(10, 0), sticky="w")

        # Apply button
        self.apply_button = customtkinter.CTkButton(master=self, border_width=2, text='Apply', command=self.apply)
        self.apply_button.grid(row=len(self.values), column=1, sticky="nsew")

    def apply(self):
        i = self.radio_var.get()
        self.ans = self.values[i]
        self.destroy()


class SelectParticipant(customtkinter.CTkToplevel):
    def __init__(self, table_name):
        super().__init__()
        self.azure = AzureDatabaseManager('shiba')
        self.table_name = table_name
        # create frame parameters
        self.p_radio = []
        self.k = None
        self.p = None
        self.valid = False
        self.names = self.azure.get_participants_names_from_table(table_name)
        self.radio_var = tkinter.IntVar(value=0)

        # configure window
        self.title("Choose Participant")
        self.geometry(f"{450}x{300}")

        # Get the current mouse position
        mouse_x, mouse_y = self.winfo_pointerx(), self.winfo_pointery()

        # Calculate the window position relative to the mouse
        window_x = mouse_x - 125  # Adjust this value to change the window's horizontal position
        window_y = mouse_y - 75  # Adjust this value to change the window's vertical position

        # Set the window position
        self.geometry(f"+{window_x}+{window_y}")

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=2)

        # on top
        self.lift()
        # self.attributes("-topmost", True)

        self.search_entry = customtkinter.CTkEntry(self, placeholder_text="Search...")
        self.search_entry.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10)
        self.search_entry.bind("<KeyRelease>", self.check)

        scrollable_frame = customtkinter.CTkScrollableFrame(self)
        scrollable_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        for i, name in enumerate(self.names):
            radio = customtkinter.CTkRadioButton(master=scrollable_frame, text=name, variable=self.radio_var, value=i)
            self.p_radio.append(radio)
        self.update_list(self.p_radio)

        # Enter K
        self.k_entry = customtkinter.CTkEntry(self,
                                              placeholder_text=f"Enter a number between 1 to {len(self.names) - 1}")
        self.k_entry.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Apply button
        self.apply_button = customtkinter.CTkButton(master=self, border_width=2,
                                                    text='Apply', command=self.apply)
        self.apply_button.grid(row=3, column=1, sticky="nsew")

    def update_list(self, data):
        for radio in self.p_radio:
            radio.grid_remove()
        for i, radio in enumerate(data):
            radio.grid(row=i, column=0, pady=(20, 0), padx=(20, 0), sticky="w")

    def check(self, e):
        typed = self.search_entry.get()
        data = []
        if typed == '':
            data = self.p_radio
        else:
            for radio in self.p_radio:
                if typed.lower() in radio.cget('text').lower():
                    data.append(radio)
        self.update_list(data)

    def apply(self):
        self.k = self.k_entry.get()
        if self.k.isnumeric() and 1 <= int(self.k) < len(self.names):
            self.k = int(self.k)
            i = self.radio_var.get()
            self.p = self.names[i]
            self.valid = True
        else:
            tkinter.messagebox.showerror(title='Invalid number\n',
                                         message=f'Error: Please enter a number between 1 and {len(self.names) - 1}')
        self.destroy()

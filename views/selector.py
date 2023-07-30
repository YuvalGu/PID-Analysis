import tkinter
import tkinter.messagebox
import customtkinter


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

        # configure grid layout (4x2)
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

        # configure grid layout (4x2)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=2)

        # on top
        self.lift()
        self.attributes("-topmost", True)

        for i, gene in enumerate(self.genes):
            radio_button_1 = customtkinter.CTkRadioButton(master=self, text=gene, variable=self.radio_var, value=i)
            radio_button_1.grid(row=i, column=0, padx=(10, 0), sticky="w")
        # radio_button_2 = customtkinter.CTkRadioButton(master=self, text=self.genes[1], variable=self.radio_var, value=1)
        # radio_button_2.grid(row=1, column=0, padx=(10, 0), sticky="w")
        # radio_button_3 = customtkinter.CTkRadioButton(master=self, text=self.genes[2], variable=self.radio_var, value=2)
        # radio_button_3.grid(row=2, column=0, padx=(10, 0), sticky="w")

        # Apply button
        self.apply_button = customtkinter.CTkButton(master=self, border_width=2, text='Apply', command=self.apply)
        self.apply_button.grid(row=len(self.genes), column=1, sticky="nsew")

    def apply(self):
        i = self.radio_var.get()
        self.ans = self.genes[i]
        self.destroy()

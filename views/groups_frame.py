import tkinter
import customtkinter
from database.database_manager import AzureDatabaseManager
from PIL import Image
import os


class GroupFrame(customtkinter.CTk):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.azure = AzureDatabaseManager('shiba')
        self.groups = {}
        self.groups_frame = customtkinter.CTkFrame(self.root, width=500)
        self.groups_frame.grid(row=0, column=2, rowspan=4, columnspan=2, padx=(20, 20), pady=(20, 20), sticky="nsew")
        # self.groups_frame.grid(row=0, column=2, padx=(20, 0), rowspan=3, sticky="nsew")

    def add_group(self, name):
        pass

import tkinter
import tkinter.ttk
import tkinter.messagebox
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


class GroupFrame1(customtkinter.CTk):
    # tabs view
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.azure = AzureDatabaseManager('shiba')
        self.groups = {}
        self.tabview = customtkinter.CTkTabview(self.root, width=500)
        self.tabview.grid(row=0, column=1, rowspan=4, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.tabview.add("Tab 1")
        self.tabview.tab("Tab 1").configure(fg_color="#ffffff")
        # self.tabview.tab('Tab 1').grid(column=0, columnspan=2, sticky="nsew")
        self.tabview.add("Tab 2")
        self.tabview.add("Tab 3")
        canvas = tkinter.Canvas(self.tabview.tab("Tab 1"))
        scrollbar = tkinter.Scrollbar(self.tabview.tab("Tab 1"), orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        canvas.configure(yscrollcommand=scrollbar.set)



        # scrollable_frame = customtkinter.CTkScrollableFrame(self.tabview.tab("Tab 1"))
        # scrollable_frame.grid()
        # scrollable_frame.configure(fg_color="#FF0000")

        for i in range(0, 20):
            main_button_1 = customtkinter.CTkButton(master=canvas, fg_color="transparent",
                                                    border_width=2, text_color=("gray10", "#DCE4EE"))
            main_button_1.grid(row=i, column=0, padx=(20, 20), pady=(20, 0), columnspan=1, sticky="nsew")
        #     main_button_2 = customtkinter.CTkButton(master=scrollable_frame, fg_color="transparent",
        #                                             border_width=2, text_color=("gray10", "#DCE4EE"))
        #     main_button_2.grid(row=i, column=1, padx=(20, 20), pady=(20, 0), columnspan=1, sticky="nsew")

            # main_button_1 = customtkinter.CTkButton(master=self.tabview.tab("Tab 1"), fg_color="transparent",
            #                                          border_width=2, text_color=("gray10", "#DCE4EE"))
            # main_button_1.grid(row=i, column=0, padx=(20, 20), pady=(20, 0), columnspan=1, sticky="nsew")
            # main_button_2 = customtkinter.CTkButton(master=self.tabview.tab("Tab 1"), fg_color="transparent",
            #                                          border_width=2, text_color=("gray10", "#DCE4EE"))
            # main_button_2.grid(row=i, column=1, padx=(20, 20), pady=(20, 0), columnspan=1, sticky="nsew")


class GroupFrame2(customtkinter.CTk):
    # tabs view
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.tabview = customtkinter.CTkTabview(self.root, width=500)
        self.tabview.grid(row=0, column=1, rowspan=4, padx=(20, 0), pady=(20, 20), sticky="nsew")

        # Create a tab and add it to the notebook
        # tab = ttk.Frame(notebook)
        self.tabview.add("1")
        self.tabview.add("2")
        self.tabview.add("3")

        # Create a canvas widget inside the tab
        canvas = tkinter.Canvas(self.tabview.tab("1"))
        canvas.pack(side='left', fill='both', expand=True)

        # Create a frame inside the canvas for the buttons
        frame = tkinter.ttk.Frame(canvas)

        # Add a scrollbar to the canvas
        scrollbar = tkinter.ttk.Scrollbar(self.tabview.tab("1"), orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')
        canvas.configure(yscrollcommand=scrollbar.set)

        # Configure the canvas to scroll the frame
        canvas.create_window((0, 0), window=frame, anchor='nw')

        # Function to update the scroll region
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox('all'))

        # Configure the scroll region when the frame size changes
        frame.bind('<Configure>', configure_scroll_region)

        # Add buttons to the frame
        for i in range(20):
            main_button_1 = customtkinter.CTkButton(master=frame, fg_color="transparent",
                                                    border_width=2, text_color=("gray10", "#DCE4EE"))
            main_button_1.grid(row=i, column=0, padx=(20, 20), pady=(20, 0), columnspan=1, sticky="nsew")
        # button = customtkinter.CTkButton(frame, text=f'Button {i+1}')
        # button.pack(pady=5)

        # Start the main loop


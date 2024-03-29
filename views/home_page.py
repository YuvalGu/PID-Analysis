import tkinter
import tkinter.messagebox
import customtkinter
from views.creator import ParticipantCreator, GroupCreator
from views.selector import SelectChain, SelectParticipant
from views.participants_frame import ParticipantFrame
from views.groups_frame import GroupFrame
from PIL import Image
import os


class HomePage(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.file_label = None
        self.title("PID Analysis")
        self.iconbitmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons\\pid.ico'))
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        # self.grid_rowconfigure(3, weight=0)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons')
        self.logo_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "logo.png")), size=(100, 100))
        self.logo = customtkinter.CTkButton(master=self.sidebar_frame, text="", image=self.logo_icon, anchor="center",
                                            height=50, width=50, fg_color=self.sidebar_frame.cget("fg_color"),
                                            hover_color=self.sidebar_frame.cget("fg_color"))
        self.logo.grid(row=0, column=0, padx=20)

        self.add_participant_button = customtkinter.CTkButton(self.sidebar_frame, command=self.add_participant,
                                                              text='Add Participant')
        self.add_participant_button.grid(row=1, column=0, padx=20, pady=10)
        self.create_group_button = customtkinter.CTkButton(self.sidebar_frame, command=self.create_group,
                                                           text='Create Group')
        self.create_group_button.grid(row=2, column=0, padx=20, pady=10)
        self.classify_button = customtkinter.CTkButton(self.sidebar_frame, command=self.classify,
                                                       text='Classify')
        self.classify_button.grid(row=3, column=0, padx=20, pady=10)

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                                       values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                               values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")

        # create participant list
        self.participant_frame = ParticipantFrame(self, ['IGH', 'TRB', 'TRG'])

        # create group list
        self.group_frame = GroupFrame(self, ['IGH', 'TRB', 'TRG'], self.participant_frame)

        # set default values
        # self.create_group_button.configure(state="disabled")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
        self.participant_frame.change_all_canvas_color()
        self.group_frame.change_all_canvas_color()

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def create_group(self):
        table_selection = SelectChain()
        table_selection.wait_window()
        t = table_selection.table
        if t:
            group_creator = GroupCreator(t)
            group_creator.wait_window()
            if group_creator.valid:
                self.group_frame.add_group(group_creator.group_name, group_creator.table_name, group_creator.members)

    def add_participant(self):
        """
        1. create participant
        2. if succeed - add the participant to the frame
        """
        participant_creator = ParticipantCreator()
        participant_creator.wait_window()
        p = participant_creator.participant
        if p:
            self.participant_frame.add_participant(p)

    def classify(self):
        table_selection = SelectChain()
        table_selection.wait_window()
        t = table_selection.table
        if t:
            select_participant = SelectParticipant(t)
            select_participant.wait_window()
            if select_participant.valid:
                self.participant_frame.show_knn(t, select_participant.names, select_participant.p, select_participant.k)

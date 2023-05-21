import tkinter
import tkinter.messagebox
import customtkinter
import pandas as pd
from views.creator import ParticipantCreator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from views.participants_frame import ParticipantFrame
from views.groups_frame import GroupFrame, GroupFrame1, GroupFrame2
from participants.participant import Participant
import participants.participant


class HomePage(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Participant('IGH_new', 'DOCK8_5887_IGH').analyze()

        # configure window
        self.file_label = None
        self.title("Home Page")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        # self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure((1, 2), weight=1)
        self.grid_rowconfigure(3, weight=0)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="PID Analysis",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.add_participant_button = customtkinter.CTkButton(self.sidebar_frame, command=self.add_participant,
                                                              text='Add Participant')
        self.add_participant_button.grid(row=1, column=0, padx=20, pady=10)
        self.create_group_button = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event,
                                                           text='Create Group')
        self.create_group_button.grid(row=2, column=0, padx=20, pady=10)
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

        # # create main entry and button
        # self.entry = customtkinter.CTkEntry(self, placeholder_text="CTkEntry")
        # self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        #
        # self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2,
        #                                              text_color=("gray10", "#DCE4EE"))
        # self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # create participant list
        self.participant_frame = ParticipantFrame(self, ['IGH_new', 'TRB', 'TRG'])
        # self.participant_frame = GroupFrame2(self)

        # create group list
        self.group_frame = GroupFrame(self)

        # set default values
        self.create_group_button.configure(state="disabled")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")

    def add_participant(self):
        """
        1. create participant
        2. if succeed
            a) add the participant to the frame
            b) add to database
        :param p_type: p - patient, c - control
        """
        participant_creator = ParticipantCreator()
        participant_creator.create()
        participant_creator.wait_window()
        p = participant_creator.participant
        if p:
            self.participant_frame.add_item(p)
            # self.participant_frame.add_item(participant_creator.participant)
            # participant_creator.participant.create_tree_map_using_plt()
            # todo: participant_frame.add_item(paticipant), add to db!

import tkinter
import tkinter.messagebox
import customtkinter
from views.creator import ParticipantCreator
from views.participants_frame import ParticipantFrame
from views.groups_frame import GroupFrame, GroupFrame1, GroupFrame2


class HomePage(customtkinter.CTk):
    def __init__(self):
        super().__init__()

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

        # create participant list
        self.participant_frame = ParticipantFrame(self, ['IGH', 'TRB', 'TRG'])
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
        2. if succeed - add the participant to the frame
        """
        participant_creator = ParticipantCreator()
        participant_creator.create()
        participant_creator.wait_window()
        p = participant_creator.participant
        if p:
            self.participant_frame.add_participant(p)

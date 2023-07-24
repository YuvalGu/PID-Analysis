import customtkinter
from PIL import Image
import os


class LoadingFrame(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Loading")
        self.geometry(f"{200}x{200}")
        self.configure(fg_color="#6c6c78")
        self.grid_rowconfigure((1, 2, 3), weight=1)
        self.grid_columnconfigure((1, 2, 3), weight=1)
        self.image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons')
        loading_icon = Image.open(os.path.join(self.image_path, "loading.png"))
        my_image = customtkinter.CTkImage(light_image=loading_icon, dark_image=loading_icon, size=(60, 60))
        button = customtkinter.CTkButton(self, image=my_image, text="Loading...", fg_color='#6c6c78',
                                         hover_color='#6c6c78', text_color="#000000")
        button.grid(row=1, column=1, ipadx=0, ipady=0, sticky="NSEW")
        label = customtkinter.CTkLabel(master=self, text="Please wait\n while the plot is being generated",
                                       text_color="#000000")
        label.grid(row=2, column=1, ipadx=0, ipady=0, sticky="nsew")
        # Make the window resizable false
        self.resizable(False, False)
        # on top
        self.lift()
        self.attributes("-topmost", True)

    def close_loading_window(self):
        self.destroy()

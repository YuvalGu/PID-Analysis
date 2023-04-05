import tkinter as tk
import customtkinter
from views.home_page import HomePage
from views.complex_example import AppExample


class App():
    def __init__(self):
        self.home_page = HomePage()
        self.home_page.mainloop()
        # self.example = AppExample()
        # self.example.mainloop()


app = App()
app.mainloop()

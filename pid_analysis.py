from views.home_page import HomePage


class App:
    def __init__(self):
        self.home_page = HomePage()
        self.home_page.mainloop()


app = App()

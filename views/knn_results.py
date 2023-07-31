import customtkinter
from PIL import Image
import os


class KnnResults(customtkinter.CTkToplevel):
    def __init__(self, participant, k_nearest_neighbors, validation_metrics):
        super().__init__()
        self.k = len(k_nearest_neighbors)
        self.title("Results")
        self.geometry(f"{550}x{450}")
        self.image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons')
        person_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "person.png")), size=(20, 20))
        export_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "export.png")), size=(20, 20))
        label = customtkinter.CTkLabel(master=self,
                                       text=f"{self.k} most similar to {participant.individual}"
                                            f" according to KNN algorithm", font=('Helvetica', 18, 'bold'))
        label.grid(row=0, column=0, columnspan=3, sticky="nw", padx=(10, 0))
        # target participant
        f = customtkinter.CTkFrame(master=self)
        f.grid(row=1, column=0, pady=10, padx=(10, 0), sticky="w")
        person_button = customtkinter.CTkButton(master=f, text="", image=person_icon, anchor="center", height=20,
                                                width=20, fg_color=f.cget("fg_color"), hover_color=f.cget("fg_color"))
        person_button.grid(row=0, column=0, padx=(10, 0), sticky="nw")
        name = customtkinter.CTkLabel(master=f, text=participant.individual,
                                      font=customtkinter.CTkFont(size=13, weight="bold"))
        name.grid(row=0, column=1, padx=(10, 0), sticky="nw")
        export_button = customtkinter.CTkButton(master=f, text="", image=export_icon,
                                                anchor="center",
                                                fg_color='#ACE8C0', hover_color='#8ABA9A',
                                                command=lambda: participant.export_to_excel(), height=20,
                                                width=20)
        export_button.grid(row=0, column=2, padx=(10, 0), sticky="nw")
        # knn results
        scrollable_frame = customtkinter.CTkScrollableFrame(self)
        scrollable_frame.grid(row=2, column=0, columnspan=3, padx=(10, 0), sticky="nsew")
        for i, p in enumerate(k_nearest_neighbors):
            person_button = customtkinter.CTkButton(master=scrollable_frame, text="", image=person_icon,
                                                    anchor="center", height=20,
                                                    width=20, fg_color=scrollable_frame.cget("fg_color"),
                                                    hover_color=scrollable_frame.cget("fg_color"))
            person_button.grid(row=i, column=0, padx=(10, 0), pady=(0, 20), sticky="nw")
            name = customtkinter.CTkLabel(master=scrollable_frame, text=p.individual)
            name.grid(row=i, column=1, padx=(10, 0), pady=(0, 20), sticky="nw")
            export_button = customtkinter.CTkButton(master=scrollable_frame, text="", image=export_icon,
                                                    anchor="center",
                                                    fg_color='#ACE8C0', hover_color='#8ABA9A',
                                                    command=lambda: p.export_to_excel(), height=20,
                                                    width=20)
            export_button.grid(row=i, column=2, padx=(10, 0), pady=(0, 20), sticky="nw")
        # validation metrics
        label = customtkinter.CTkLabel(master=self, text="Validation metrics:")
        label.grid(row=3, column=0, sticky="nw", padx=(10, 0))
        for i, (k, v) in enumerate(validation_metrics.items()):
            label = customtkinter.CTkLabel(master=self, text=f"{k}: {v}")
            label.grid(row=i + 4, column=0, sticky="nw", padx=(15, 0))
        # on top
        self.lift()

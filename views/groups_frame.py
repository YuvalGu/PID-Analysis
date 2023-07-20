import tkinter
import tkinter.messagebox
import customtkinter
from database.database_manager import AzureDatabaseManager
from azure.kusto.data.exceptions import KustoError
from participants.group import Group
from views.creator import GroupCreator
from PIL import Image
import os


class GroupFrame(customtkinter.CTk):
    def __init__(self, root, table_names, p_frame):
        super().__init__()
        self.root = root
        self.p_frame = p_frame
        self.azure = AzureDatabaseManager('shiba')
        self.groups = {}
        self.groups_frame = customtkinter.CTkFrame(self.root, width=500)
        self.groups_frame.grid(row=0, column=2, rowspan=4, columnspan=2, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons')
        self.names = {}
        self.widgets = {}
        self.table_names = table_names
        self.tab_frames = {}
        self.tabview = None
        self.create_tab_views()
        for table_name in self.table_names:
            self.names[table_name] = self.azure.get_groups_names_by_table(table_name)
            self.groups[table_name] = {}
            self.widgets[table_name] = {}
            for group_name in self.names[table_name]:
                self.add_group(group_name, table_name, self.azure.get_participants_from_group(group_name, table_name))

    def create_tab_views(self):
        self.tabview = customtkinter.CTkTabview(self.root, width=500)
        self.tabview.grid(row=0, column=2, rowspan=4, padx=(20, 0), pady=(20, 20), sticky="nsew")
        for table in self.table_names:
            self.create_tab(table)

    def create_tab(self, name):
        self.tabview.add(name)

        # Create a canvas widget inside the tab
        canvas = customtkinter.CTkCanvas(self.tabview.tab(name))
        canvas.pack(side='left', fill='both', expand=True)

        # Create a frame inside the canvas for the buttons
        frame = customtkinter.CTkFrame(canvas)

        # Add a scrollbar to the canvas
        scrollbar = customtkinter.CTkScrollbar(self.tabview.tab(name), orientation='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')

        canvas.configure(yscrollcommand=scrollbar.set)

        # Configure the canvas to scroll the frame
        canvas.create_window((0, 0), window=frame, anchor='nw')

        # Function to update the scroll region
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox('all'))
            canvas.itemconfigure(frame_id, width=canvas.winfo_width())

        # Configure the scroll region and frame size when the canvas size changes
        frame_id = canvas.create_window((0, 0), window=frame, anchor='nw')
        canvas.bind('<Configure>', configure_scroll_region)
        self.change_canvas_color(name)
        self.tab_frames[name] = frame

    def change_all_canvas_color(self):
        for table in self.table_names:
            self.change_canvas_color(table)

    def change_canvas_color(self, table):
        canvas = self.tabview.tab(table).winfo_children()[0]
        if table in self.widgets and len(list(self.widgets[table])) != 0:
            colors = self.widgets[table][list(self.widgets[table])[0]][0].cget('fg_color')
        else:
            colors = self.tabview.tab(table).cget("fg_color")
        if customtkinter.get_appearance_mode() == 'Light':
            canvas.configure(bg=colors[0], highlightbackground=colors[0])
        elif customtkinter.get_appearance_mode() == 'Dark' or 'System':
            canvas.configure(bg=colors[1], highlightbackground=colors[1])

    def edit_item(self, table, old_group_name):
        old_members = self.groups[table][old_group_name].get_participants_names()
        creator = GroupCreator(table, old_group_name, old_members, True)
        creator.create()
        creator.wait_window()
        if creator.valid:
            members = self.p_frame.get_participants(creator.members)
            group = Group(creator.group_name, creator.table_name, members)
            if not old_group_name == creator.group_name:
                self.widgets[table][creator.group_name] = self.widgets[table][old_group_name]
                del self.widgets[table][old_group_name]
            del self.groups[table][old_group_name]
            self.groups[table][creator.group_name] = group

    def remove_item(self, table, group):
        answer = tkinter.messagebox.askyesno(title='confirmation\n',
                                             message=f'Are you sure you want to delete {group} from database?')
        if answer:
            try:
                self.azure.delete_group(table, group)
                for frame in self.widgets[table][group]:
                    frame.destroy()
                del self.groups[table][group]
                del self.widgets[table][group]
                tkinter.messagebox.showinfo(title='SUCCESS',
                                            message=f'group {group} has been successfully removed')
            except KustoError as e:
                tkinter.messagebox.showerror(title="Couldn't delete from DB\n", message=str(e))

    def add_item(self, table, group):
        frame = self.tab_frames[table]
        # todo: change to -1
        row = len(frame.winfo_children())
        delete_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "delete.png")), size=(20, 20))
        edit_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "edit.png")), size=(20, 20))
        analyze_icon = customtkinter.CTkImage(Image.open(os.path.join(self.image_path, "analyze.png")), size=(20, 20))
        f = customtkinter.CTkFrame(master=frame)
        f.pack(fill="both", expand=True)
        checkbox = customtkinter.CTkCheckBox(master=f, text=group)
        checkbox.grid(row=row, column=0, padx=(10, 0), pady=(0, 20))
        delete_button = customtkinter.CTkButton(master=f, text="", image=delete_icon,
                                                anchor="center",
                                                fg_color='#ff0004', hover_color='#d10407',
                                                command=lambda: self.remove_item(table, group), height=20, width=20)
        delete_button.grid(row=row, column=1, padx=0, pady=(0, 20), ipadx=0, ipady=0)

        edit_button = customtkinter.CTkButton(master=f, text="", image=edit_icon,
                                              anchor="center",
                                              fg_color='#0525f5', hover_color='#0319a8',
                                              command=lambda: self.edit_item(table, group), height=20, width=20)
        edit_button.grid(row=row, column=2, padx=(10, 0), pady=(0, 20), ipadx=0, ipady=0)

        g_button = customtkinter.CTkButton(master=f, text="", image=analyze_icon,
                                           anchor="center",
                                           fg_color='#63e83a', hover_color='#47ab29',
                                           command=lambda: self.show_group_data(table, group), height=20, width=20)
        g_button.grid(row=row, column=3, padx=(10, 0), pady=(0, 20))
        # todo: change row of calaculate button to row+1
        self.widgets[table][group].append(f)

    def add_group(self, group_name, table_name, members):
        participants_list = self.p_frame.get_participants(members)
        group = Group(group_name, table_name, participants_list)
        self.groups[table_name][group_name] = group
        self.widgets[table_name][group_name] = []
        self.add_item(table_name, group_name)

    def show_group_data(self, table, name):
        self.groups[table][name].analyze()

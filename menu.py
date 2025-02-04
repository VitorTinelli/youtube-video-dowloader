import tkinter as tk
from tkinter import filedialog
import os
import json

with open('configurations/configurations.json', 'r') as config_file:
    config = json.load(config_file)

global_folder_path = config['folder_path']

def set_folder_path(new_path):
    global global_folder_path
    global_folder_path = new_path
    config['folder_path'] = new_path
    with open('configurations/configurations.json', 'w') as config_file:
        json.dump(config, config_file)

def get_folder_path():
    return global_folder_path

class Menu(tk.Menu):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master

        self.menu = tk.Menu(self.master)
        self.master.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Options", menu=self.file_menu)
        self.file_menu.add_command(label="Mudar Pasta", command=self.change_folder)
        self.file_menu.add_command(label="Sair", command=self.master.quit)

        if not get_folder_path():
            self.change_folder()

    def change_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            set_folder_path(folder_selected)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Menu Example")
    menu = Menu(root)
    root.mainloop()
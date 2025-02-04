import tkinter as tk
from tkinter import ttk
from menu import Menu
from baixarVideo import baixarVideo
import threading
import re

class Main:
    def __init__(self, master=None):
        self.master = master
        self.master.title("Main Application")
        self.master.geometry("720x360")

        self.menu = Menu(self.master)

        self.url_button = tk.Button(self.master, text="URL", command=self.open_url, width=20, height=2)
        self.url_button.pack(expand=True)

    def open_url(self):
        self.new_window = tk.Toplevel(self.master)
        self.new_window.title("Enter URL")
        self.new_window.geometry("720x360")  

        self.url_entry = tk.Entry(self.new_window)
        self.url_entry.pack(pady=20)

        self.submit_button = tk.Button(self.new_window, text="Submit", command=self.submit_url, width=20, height=2)
        self.submit_button.pack(pady=10)

        self.progress = ttk.Progressbar(self.new_window, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=20)

    def progress_callback(self, d):
        if d['status'] == 'downloading':
            p = d['_percent_str']
            p = re.sub(r'\x1b\[[0-9;]*m', '', p)
            p = p.replace('%', '')
            self.master.after(0, self.update_progress, float(p))

    def update_progress(self, value):
        self.progress['value'] = value
        self.new_window.update_idletasks()

    def submit_url(self):
        url = self.url_entry.get()
        download_thread = threading.Thread(target=baixarVideo, args=(url, self.progress_callback))
        download_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = Main(master=root)
    root.mainloop()
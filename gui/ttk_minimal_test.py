import tkinter as tk
from tkinter import ttk

def on_click():
    print("Button clicked!")

root = tk.Tk()
root.title("ttk Minimal Test")
root.geometry("400x200")

label = ttk.Label(root, text="This is a ttk Label")
label.pack(pady=10)

entry = ttk.Entry(root)
entry.pack(pady=10)

button = ttk.Button(root, text="Click Me", command=on_click)
button.pack(pady=10)

root.mainloop() 
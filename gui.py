import tkinter as tk
from tkinter import ttk
import subprocess
import os

from tkinter import scrolledtext

def execute_command(event=None):
    command = command_entry.get()
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    output, _ = process.communicate()
    current_directory = os.getcwd()  # Get the current working directory

    # Enable the output_text widget for modifications
    output_text.config(state="normal")
    
    # Insert the command output
    output_text.insert(tk.END, f" {current_directory} >> {command}\n")
    output_text.insert(tk.END, output)
    output_text.insert(tk.END, "\n")
    
    # Disable the output_text widget to prevent further modifications
    output_text.config(state="disabled")
    
    command_entry.delete(0, tk.END)  # Clear the command entry after execution
      # Scroll to the bottom
    output_text.see(tk.END)
    if command == 'cls':
        # Clear the output text
        output_text.config(state="normal")
        output_text.delete("1.0", tk.END)
        output_text.config(state="disabled")
        

def show_context_menu(event):
    # Create a context menu
    context_menu = tk.Menu(window, tearoff=0)
    context_menu.add_command(label="Option 1", command=lambda: print("Option 1 selected"))
    context_menu.add_command(label="Option 2", command=lambda: print("Option 2 selected"))
    context_menu.add_command(label="Option 3", command=lambda: print("Option 3 selected"))
    # Display the context menu at the clicked position
    context_menu.post(event.x_root, event.y_root)
# Create the main window
window = tk.Tk()
window.title("UI Window")

# Create the command line
command_entry = tk.Entry(window ,bg="black",fg="#00FF41",font=("Consolas", 12))
command_entry.grid(row=4, column=0, columnspan=5, sticky="nsew", padx=10, pady=(2, 10))
command_entry.bind("<Return>", execute_command)  # Bind the Return key to the execute_command function


window.geometry("800x800")
screen_width = window.winfo_screenwidth()

# Create the buttons
button1 = tk.Button(window, text="Button 1" ,background="red")
button1.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

button2 = tk.Button(window, text="Button 2" ,background="blue")
button2.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

button3 = tk.Button(window, text="Button 3",background="green")
button3.grid(row=0, column=2, padx=10, pady=5, sticky="ew")

button4 = tk.Button(window, text="Button 4",background="yellow")
button4.grid(row=0, column=3, padx=10, pady=5, sticky="ew")

button5 = tk.Button(window, text="Button 5",background="orange")
button5.grid(row=0, column=4, padx=10, pady=5, sticky="ew")

# Configure grid weights and column span to center the buttons
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_columnconfigure(2, weight=1)
window.grid_columnconfigure(3, weight=1)
window.grid_columnconfigure(4, weight=1)
window.grid_rowconfigure(2, weight=1)

# Create the table
table = ttk.Treeview(window, columns=("column1", "column2", "column3", "column4", "column5"),show="headings")
table.configure(style="Custom.Treeview")
style = ttk.Style(window)
style.configure("Custom.Treeview", background="lightgray")
table.heading("column1", text="Column 1", anchor="center")
table.heading("column2", text="Column 2", anchor="center")
table.heading("column3", text="Column 3", anchor="center")
table.heading("column4", text="Column 4", anchor="center")
table.heading("column5", text="Column 5", anchor="center")

# Set the stretch option for each column
table.column("column1", stretch=True)
table.column("column2", stretch=True)
table.column("column3", stretch=True)
table.column("column4", stretch=True)
table.column("column5", stretch=True)

# Insert dummy data into the table
for i in range(20):
    table.insert("", tk.END, values=("Value 1", "Value 2", "Value 3", "Value 4", "Value 5"))
    table.bind("<Button-3>", show_context_menu, add="+")

table.grid(row=2, column=0, columnspan=5, padx=10,pady=10, sticky="nsew")
scrollbar = tk.Scrollbar(window, orient="vertical", command=table.yview)
scrollbar.grid(row=2, column=5, sticky="ns")
table.configure(yscrollcommand=scrollbar.set)



# Create the command output text area (console) with a scrollbar
output_text = scrolledtext.ScrolledText(window, state="disabled", bg="black", fg="#00FF41", font=("Consolas", 12))
output_text.grid(row=3, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")

# Configure grid weights to make the table and command output text area expandable
window.grid_columnconfigure(0, weight=1)
window.grid_rowconfigure(2, weight=1)
window.grid_rowconfigure(4, weight=1)

# Start the main event loop
window.mainloop()
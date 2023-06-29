import tkinter as tk

def update_values():
    global var1, var2, var3
    try:
        var1 = int(entry1.get())
        var2 = int(entry2.get())
        var3 = int(entry3.get())
        label.config(text="Values updated!")
    except ValueError:
        label.config(text="Invalid input!")

# Create the main window
window = tk.Tk()
window.title("Variable Setter")

# Create and place the entry fields
entry1 = tk.Entry(window)
entry1.pack()
entry2 = tk.Entry(window)
entry2.pack()
entry3 = tk.Entry(window)
entry3.pack()

# Create the update button
button = tk.Button(window, text="Update", command=update_values)
button.pack()

# Create the status label
label = tk.Label(window, text="")
label.pack()

# Start the main loop
window.mainloop()

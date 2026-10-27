import tkinter as tk 

root = tk.Tk() #Creates The Main Window Open 
root.title("MY GUI")
root.geometry("400x400")

label = tk.Label(root , text = "Hello World")
label.place(x=200,y=200)

button = tk.Button(root,text="Click me", command = lambda : label.config(text="Button cliked"))
button.place(x=250,y=250)
root.mainloop() 

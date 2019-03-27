
from tkinter import *
 

root = Tk()
width = 1000
height = 1000
root.title("Annotation tool")
root.geometry(str(width) + 'x' + str(height))
mainframe = Frame(root)
mainframe.grid(column=0, row=0, sticky=("nsew"))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame = Frame(mainframe)
frame.grid(column=2, row=1, sticky=("nsew"))
mainframe.columnconfigure(2, weight=1)
mainframe.rowconfigure(1, weight=1)
canvas = Canvas(frame, relief = FLAT, background = "black", width=width, height=height)
canvas.place(x=0, y=0)

node_key_bindings = {
    'q': "QUERY",
    'w': "SUBJECT",
    'e': "OBJECT",
}

current_node_type = node_key_bindings['q']
current_selection = None

def select(btn):
    global current_selection
    if current_selection == None:
        current_selection = btn
    else:
        x1, y1 = current_selection.winfo_x(), current_selection.winfo_y()
        x2, y2 = btn.winfo_x(), btn.winfo_y()

        canvas.create_line(x1, y1, x2, y2, width=10, fill='white')
        current_selection = None
    

def set_node_type(event):
    current_node_type = node_key_bindings[event.keysym]

def create_node(x, y, node_type):
    # canvas.create_line(event.x, event.y, event.x + 4, event.y, width=10, fill='white')
    btn = Button(frame, text=node_type)
    btn.place(x=x, y=y)
    btn.bind("<Button-1>", lambda event: select(btn))

tokens = "What is the oldest son of Barack Obama?".split()


canvas.bind("<Button-1>", lambda event: create_node(event.x, event.y, current_node_type))
canvas.bind("<Key>", set_node_type)

# canvas.bind("<Motion>", )
for index, token in enumerate(tokens):
    create_node(x=width * (index / len(tokens)), y = height - 100, node_type=token)

create_node(x=width // 2, y=100, node_type='QUERY')

root.mainloop()
"""
    Desktop app for manual annotation of questions with constituency trees
"""
from tkinter import *
import json
import os
import sys

sys.path.insert(0, os.getcwd())
from annotator.constants import INPUT_FILE_PATH, OUTPUT_FILE_PATH
from services.tasks import run_task, Task
from services.parser.syntax_checker import SyntaxChecker
from services.parser.constants import GRAMMAR_FILE_PATH
from common.query_tree import QueryTree, NodeType

SYNTAX_CHECKER = SyntaxChecker(GRAMMAR_FILE_PATH)
settings = {
    '''
    Key bindings for selecting the node type
    '''
    'symbol_vs_node_type': {
        'f3': NodeType.GREATER,
        'f2': NodeType.FILTER,
        'f1': NodeType.CONDITION,
        '9':  NodeType.ISA,
        '8':  NodeType.EXISTS,
        '7':  NodeType.COMPARE,
        '6':  NodeType.RELATION_EXISTS,
        '5':  NodeType.INTERSECTION,
        '4':  NodeType.UNION,
        '3':  NodeType.COUNT,
        '2':  NodeType.EQUAL,
        '1':  NodeType.ARGNTH,
        'q':  NodeType.QUERY,
        'e':  NodeType.ENTITY,
        't':  NodeType.TYPE,
        'r':  NodeType.RELATION
    },
    '''
    Key bindings for commands
    '''
    'symbol_vs_command': {
        'z': "UNDO",
        'x': "SAVE_AND_NEXT",
        'c': "REDO",
    },
    'window_width': 1000,
    'window_height': 500,
}

class Node:
    def __init__(self, type, widget, token=None):
        self.type = type
        self.token = token
        self.widget = widget
    def export(self):
        return {
            'type': self.type,
            'token': self.token,
            'id': hex(id(self))
            }

class Edge:
    def __init__(self, source, destination, widget_id):
        self.source = source
        self.destination = destination
        self.widget_id = widget_id
    def export(self):
        return {
            'source': hex(id(self.source)),
            'destination': hex(id(self.destination)),
            }



state = {
    'node_type': 'QUERY',
    'selection': None,
    'nodes': [],
    'edges': [],
    'actions': [],
    'widgets_vs_nodes': {},
    'ids_vs_edges': {},
    'current_example_index': 0,
}

root = Tk()
root.title("Annotation tool")
root.geometry(str(settings['window_width']) + 'x' + str(settings['window_height']))
mainframe = Frame(root)
mainframe.grid(column=0, row=0, sticky=("nsew"))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame = Frame(mainframe)
frame.grid(column=2, row=1, sticky=("nsew"))
mainframe.columnconfigure(2, weight=1)
mainframe.rowconfigure(1, weight=1)
canvas = Canvas(frame, relief = FLAT, background = "black", width=settings['window_width'], height=settings['window_height'])
canvas.focus_set()
canvas.place(x=0, y=0)

def undo():
    last_action = state['actions'].pop()

    if last_action == 'create_node':
        node = state['nodes'].pop()
        node.widget.destroy()
    if last_action == 'create_edge':
        edge = state['edges'].pop()
        canvas.delete(edge.widget_id)

def delete(btn):
    for node in state['nodes']:
        if node.widget == btn:
            state['nodes'].remove(node)
            btn.destroy()
            break
    
    edges_to_keep = []
    for edge in state['edges']:
        if edge.source.widget == btn or edge.destination.widget == btn:
            canvas.delete(edge.widget_id)
        else:
            edges_to_keep.append(edge)
        
    state['edges'] = edges_to_keep


    state['selection'] = None

def to_tree(node):
    children = [edge.destination for edge in state['edges'] if edge.source == node]
    result = {}
    result['type'] = node.type.value
    if children:
        result['children'] = [to_tree(child) for child in children if child.type != NodeType.TOKEN]
        tokens = [child for child in children if child.type == NodeType.TOKEN]
        if tokens:
            tokens_node = {
                'type': NodeType.TOKENS.value,
                'tokens': [node.token for node in tokens]
            }
            result['children'].append(tokens_node)
            

    return result

def save(tree):
        
    with open(OUTPUT_FILE_PATH, 'r', encoding='utf-8') as output_file:
        example_array = json.load(output_file)
    
        if example_array == None:
            example_array = []

        data = {
            'dataset': 'qald-8',
            'index': state['example_index'],
            'tree': tree
        }

        example_array.append(data)

    with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as output_file:
        json.dump(example_array, output_file)


def reset():
    for node in state['nodes']:
        node.widget.destroy()
    
    for edge in state['edges']:
        canvas.delete(edge.widget_id)

    state['node_type'] = 'QUERY'
    state['selection'] = None
    state['nodes'] = []
    state['edges'] = []
    state['actions'] = []
    state['widgets_vs_nodes'] = {}
    state['ids_vs_edges'] = {}
    state['example_index'] = -1

def redo():
    reset()
    init(*state['examples'][state['current_example_index'] - 1])

def next():
    reset()
    init(*state['examples'][state['current_example_index']])
    state['current_example_index'] += 1

def error():
    print("ERROR: tree does not validate grammar")

def select(btn):
    global state
    if state['selection'] == None:
        state['selection'] = btn
        btn.configure(background="red")
    elif state['selection'] != btn:
        create_edge(state['selection'], btn)
        state['selection'].configure(background="white")
        state['selection'] = None
    else:
        state['selection'].configure(background="white")
        state['selection'] = None
    canvas.focus_set()

def validate(tree):
    return SYNTAX_CHECKER.validate(QueryTree.from_dict(tree))

def on_key(event):
    key = event.keysym.lower()
    if key in settings['symbol_vs_command']:
        command = settings['symbol_vs_command'][key]
        if command == 'UNDO':
            undo()
        elif command == 'SAVE_AND_NEXT':
            root = [node for node in state['nodes'] if node.type == NodeType.ROOT][0]
            tree = to_tree(root)
            if tree and validate(tree):
                save(tree)
                next()
            else:
                error()
        elif command == 'REDO':
            redo()

    elif key in settings['symbol_vs_node_type']:
        node_type = settings['symbol_vs_node_type'][key]
        set_node_type(node_type)
    else:
        pass
    canvas.focus_set()


def set_node_type(node_type):
    state['node_type'] = node_type

def create_edge(source_btn, destination_btn):
    source = state['widgets_vs_nodes'][source_btn]
    destination = state['widgets_vs_nodes'][destination_btn]
    x1, y1 = source_btn.winfo_x(), source_btn.winfo_y()
    x2, y2 = destination_btn.winfo_x(), destination_btn.winfo_y()

    edge_id = canvas.create_line(x1, y1, x2, y2, width=10, fill='white')
    edge = Edge(source, destination, edge_id)
    state['edges'].append(edge)
    state['ids_vs_edges'][edge_id] = edge
    state['actions'].append('create_edge')    

def create_node(x, y, node_type, token=None):
    btn_text = state['tokens'][token] if node_type == NodeType.TOKEN else node_type.value
    btn = Button(frame, text=btn_text)
    btn.place(x=x, y=y)
    btn.bind("<Button-1>", lambda event: select(btn))
    btn.bind("<Button-3>", lambda event: delete(btn))
    node = Node(node_type, btn, token)
    state['nodes'].append(node)
    state['widgets_vs_nodes'][btn] = node
    state['actions'].append('create_node')

def init(index, text):
    state['tokens'] = tokens = run_task(Task.TOKENIZE, text)
    state['example_index'] = index
    canvas.bind("<Button-1>", lambda event: create_node(event.x, event.y, state['node_type']))
    canvas.bind("<Key>", on_key)

    for index, token in enumerate(tokens):
        create_node(x=settings['window_width'] * (index / len(tokens)), y = settings['window_height'] - 100, node_type=NodeType.TOKEN, token=index)

    create_node(x=settings['window_width'] // 2, y=100, node_type=NodeType.ROOT)
    canvas.focus_set()


def main():
    state['examples'] = [line.split('|') for line in open(INPUT_FILE_PATH, 'r', encoding='utf-8').readlines()]
    with open(OUTPUT_FILE_PATH, 'r', encoding='utf-8') as output_file:
        example_array = json.load(output_file)
        if example_array == None:
            state['current_example_index'] = 0
        else:
            state['current_example_index'] = len(example_array)

    next()
    root.mainloop()


main()
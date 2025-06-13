import os

def print_tree(start_path, indent=""):
    for item in os.listdir(start_path):
        if item == "__pycache__" or item == ".git" or item == "venv":
            continue
        path = os.path.join(start_path, item)
        print(indent + "|-- " + item)
        if os.path.isdir(path):
            print_tree(path, indent + "    ")

print_tree(".")

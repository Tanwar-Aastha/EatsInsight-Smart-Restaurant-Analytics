import os
import logging
from pathlib import Path

while True:
    project_name = input("Enter the project name: ")
    if project_name != "":
        break

# list of required project files
project_files = [
    f"{project_name}/__init__.py",
    f"{project_name}/components/__init__.py",
    f"{project_name}/pipeline.py/__init__.py",
    f"notebook/data_preprocessing.ipynb",
    f"{project_name}/logger.py",
    f"{project_name}/exception.py",
    f"{project_name}/utils.py",
    f"setup.py",
    f"requirements.txt",
    f"app.py"
]

for filepth in project_files:
    file_path = Path(filepth)  # converting string into path

    file_dir, file_name = os.path.split(file_path)   # splittting the path into directory and file 

    # creating the file directory
    if file_dir != "":
        os.makedirs(file_dir, exist_ok=True)

    # creating the files
    if (not os.path.exists(file_name) or os.path.getsize(file_name)==0):
        with open (file_path, 'w') as file:
            pass
    else:
        logging.info(f"These files already exists at {file_path}") 
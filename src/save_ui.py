from pathlib import Path

from PyQt6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QMessageBox, QVBoxLayout, QPushButton, QDialog, QLineEdit, QColorDialog
)

from foil_data import FoilUtils, NACA_4_Standard_AirFoil, AirFoil, NACA_5_Standard_Airfoil

import standards

import re

INVALID_CHARS = r'[<>:"/\\|?*\n\r\t]'

RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}



class SaveProject(QDialog):
     
    def __init__(self):

        super().__init__()

        self.setWindowTitle("Save Project")

        self.resize(350, 300)

        self.file_path = ""

        self.color = "#4CAF50"

        self.setStyleSheet("""

            QDialog {

                background-color: #20252B;

                border-radius: 15px;

            }

            QLabel {

                color: white;
                font-size: 13px;

            }

            QLineEdit {

                background-color: rgba(255,255,255,0.08);
                color: white;
                border-radius: 8px;
                padding: 8px;
                border: 1px solid rgba(255,255,255,0.10);

            }

        """)

        self.layout: QVBoxLayout = QVBoxLayout(self)

        self.path_layout = QHBoxLayout()

        self.path_input = QLineEdit()

        self.path_input.setPlaceholderText("Enter the path to a directory")

        self.browse_btn = QPushButton("BROWSE")

        self.browse_btn.clicked.connect(self.browse)

        self.browse_btn.setStyleSheet("""
            QPushButton {

                background-color: black;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px;
            }

            QPushButton:hover {

                background-color: #222222;
            }

            QPushButton:pressed {

                background-color: #444444;
            }
        """)

        self.name_input = QLineEdit()

        self.name_input.setPlaceholderText("Enter project name")

        self.add_btn = QPushButton("SAVE")

        self.add_btn.setStyleSheet("""
            QPushButton {

                background-color: black;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px;
            }

            QPushButton:hover {

                background-color: #222222;
            }

            QPushButton:pressed {

                background-color: #444444;
            }
        """)

        self.add_btn.clicked.connect(self.save_project)

        self.path_layout.addWidget(self.path_input)

        self.path_layout.addWidget(self.browse_btn)

        self.layout.addLayout(self.path_layout)

        self.layout.addWidget(self.name_input)

        self.layout.addWidget(self.add_btn)


    def browse(self) -> None:
        
        file_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        if file_path:
              
            self.path_input.setText(file_path)

            self.file_path = file_path

            self.browse_btn.setText("Change File")

    
    @staticmethod
    def is_valid_filename(name: str) -> bool:

    
        if not name.strip():
            return False

    
        if re.search(INVALID_CHARS, name):
            return False

    
        if name.endswith(" ") or name.endswith("."):
            return False

    
        stem = Path(name).stem.upper()
        if stem in RESERVED_NAMES:
            return False

        return True



    def save_project(self) -> None:

        self.file_path = self.path_input.text()

        if not self.name_input.text() or not SaveProject.is_valid_filename(self.name_input.text()):

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Project Name Invalid")

            msg.setText("The project name is not a valid name. Enter a project name with no special characters.")

            msg.exec()

            return
        
        self.project_name = self.name_input.text()
            

        if not Path(self.file_path).exists() or not Path(self.file_path).is_dir():

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Invalid Folder Path")

            msg.setText("The path given is invalid. Please check if the folder exists or if the path corresponds to a folder.")

            msg.exec()

            return
        
        self.accept()




class LoadProject(QDialog):
     
    def __init__(self):

        super().__init__()

        self.setWindowTitle("Load Project")

        self.resize(350, 300)

        self.file_path = ""

        self.color = "#4CAF50"

        self.setStyleSheet("""

            QDialog {

                background-color: #20252B;

                border-radius: 15px;

            }

            QLabel {

                color: white;
                font-size: 13px;

            }

            QLineEdit {

                background-color: rgba(255,255,255,0.08);
                color: white;
                border-radius: 8px;
                padding: 8px;
                border: 1px solid rgba(255,255,255,0.10);

            }

        """)

        self.layout: QVBoxLayout = QVBoxLayout(self)

        self.path_layout = QHBoxLayout()

        self.path_input = QLineEdit()

        self.path_input.setPlaceholderText("Enter the path to a directory")

        self.browse_btn = QPushButton("BROWSE")

        self.browse_btn.clicked.connect(self.browse)

        self.browse_btn.setStyleSheet("""
            QPushButton {

                background-color: black;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px;
            }

            QPushButton:hover {

                background-color: #222222;
            }

            QPushButton:pressed {

                background-color: #444444;
            }
        """)

        self.add_new_btn = QPushButton("LOAD")

        self.add_new_btn.setStyleSheet("""
            QPushButton {

                background-color: black;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 8px;
            }

            QPushButton:hover {

                background-color: #222222;
            }

            QPushButton:pressed {

                background-color: #444444;
            }
        """)

        self.add_new_btn.clicked.connect(self.load_project)

        self.path_layout.addWidget(self.path_input)

        self.path_layout.addWidget(self.browse_btn)

        self.layout.addLayout(self.path_layout)

        self.layout.addWidget(self.add_new_btn)


    def browse(self) -> None:
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a file", "", "JSON Files (*.json)")
        
        if file_path:
              
            self.path_input.setText(file_path)

            self.file_path = file_path

            self.browse_btn.setText("Change File")




    def load_project(self) -> None:

        self.file_path = self.path_input.text()
            
        if not Path(self.file_path).exists():

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Invalid File Path")

            msg.setText("The path given is invalid. Please check if the file exists.")

            msg.exec()

            return
        
        self.accept()

        



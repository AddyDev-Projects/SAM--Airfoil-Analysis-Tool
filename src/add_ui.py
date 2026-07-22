from pathlib import Path

from PyQt6.QtWidgets import (
    QFileDialog, QFrame, QHBoxLayout, QMessageBox, QVBoxLayout, QPushButton, QDialog, QLineEdit, QColorDialog
)

from foil_data import FoilUtils, NACA_4_Standard_AirFoil, AirFoil, NACA_5_Standard_Airfoil

from typing import cast

import standards


class AddNACA4StandardFoil(QDialog):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Add Standard NACA 4 Digit Airfoil")

        self.resize(350, 250)

        self.setStyleSheet("""

            QDialog {
                           
                background-color: #20252B;
                           
                border-radius: 15px;

                           
                           
            }




        """)


        layout = QVBoxLayout(self)

        self.naca_num_input = QLineEdit()
        self.naca_num_input.setPlaceholderText("NACA Number (e.g. 2412)")

        self.naca_num_input.setStyleSheet("""
                                      
            QLineEdit {
                color: white;
                font-size: 14px;
                background: transparent;
            }

        """)

        self.re_start_input = QLineEdit()
        self.re_start_input.setPlaceholderText("Reynolds Number (e.g. 100000)")

        self.re_start_input.setStyleSheet("""
                                      
            QLineEdit {
                color: white;
                font-size: 14px;
                background: transparent;
            }

        """)

        self.re_stop_num_input = QLineEdit()
        self.re_stop_num_input.setPlaceholderText("Reynolds Number (e.g. 100000)")

        self.re_stop_num_input.setStyleSheet("""
                                      
            QLineEdit {
                color: white;
                font-size: 14px;
                background: transparent;
            }

        """)

        self.re_step_input = QLineEdit()
        self.re_step_input.setPlaceholderText("Reynolds Number Step (e.g. 10000)")

        self.re_step_input.setStyleSheet("""
                                      
            QLineEdit {
                color: white;
                font-size: 14px;
                background: transparent;
            }

        """)

        color_layout = QHBoxLayout()

        self.color_preview = QFrame()

        self.color_preview.setFixedSize(40, 40)

        self.color_preview.setStyleSheet(f"""
            QFrame {{
                background-color: {self.selected_color if hasattr(self, 'selected_color') else '#4CAF50'};
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.15);
            }}
        """)

        self.color_btn = QPushButton("CHOOSE COLOR")
        
        self.color_btn.clicked.connect(self.pick_color)

        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: black;
                color: white;
                border-radius: 12px;
                font-weight: bold;
                padding: 8px;
                border: none;
            }}

            QPushButton:hover {{
                background-color: #222222;
            }}

            QPushButton:pressed {{
                background-color: #444444;
            }}
        """)

        color_layout.addWidget(self.color_preview)

        color_layout.addWidget(self.color_btn)

        self.add_btn = QPushButton("ADD")

        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: black;
                color: white;
                border-radius: 12px;
                padding: 8px;
                font-weight: bold;
                border: none;
            }}

            QPushButton:hover {{
                background-color: #222222;
            }}

            QPushButton:pressed {{
                background-color: #444444;
            }}
        """)

        self.add_btn.clicked.connect(self.add_foil)

        layout.addWidget(self.naca_num_input)
        layout.addWidget(self.re_start_input)
        layout.addWidget(self.re_stop_num_input)
        layout.addWidget(self.re_step_input)
        layout.addLayout(color_layout)
        layout.addStretch()
        layout.addWidget(self.add_btn)


    def pick_color(self) -> None:

        color = QColorDialog.getColor()

        if color.isValid():

            self.selected_color = color.name()

            self.color_preview.setStyleSheet(f"""
            QFrame {{
                background-color: {self.selected_color if hasattr(self, 'selected_color') else '#4CAF50'};
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.15);
            }}
        """)

            self.color_btn.setText("Color Selected")

    def add_foil(self) -> None:

        naca_num = self.naca_num_input.text() if self.naca_num_input.text() else "2412"

        re_start = self.re_start_input.text() if self.re_start_input.text() else "100000"

        re_stop = self.re_stop_num_input.text() if self.re_stop_num_input.text() else "100000"

        re_step = self.re_step_input.text() if self.re_step_input.text() else "10000"

        color = self.selected_color if hasattr(self, 'selected_color') else "#4CAF50"

        try:
             
            re_start = float(re_start)

            re_stop = float(re_stop)

            re_step = float(re_step)

        except:

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Invalid Reynolds Number")

            msg.setText("Reynolds numbers and step must be valid numbers.")

            msg.exec()

            return

        try:

            m, p, t = FoilUtils.generate_naca_4_foil_data(naca_num)

        except:

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Invalid NACA Number")

            msg.setText("The NACA number entered is not valid. Please enter a valid 4 digit NACA number.")

            msg.exec()

            return
    

        steps = int((float(re_stop) - float(re_start)) / float(re_step)) + 1

        if steps > standards.MAX_RE_STEPS:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Too Many Points")
    
                msg.setText("The number of points to be generated is too high. Please reduce the Reynolds number range or increase the step.")
    
                msg.exec()
    
                return
        
        if float(re_start) > float(re_stop):

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Invalid Reynolds Range")
    
                msg.setText("The starting Reynolds number must be less than the stopping Reynolds number.")
    
                msg.exec()
    
                return
        
        if float(re_step) <= 0:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Invalid Step")
    
                msg.setText("The Reynolds number step must be a positive integer.")
    
                msg.exec()
    
                return

        valid = False

        re_stop = cast(float, re_stop)

        re_start = cast(float, re_start)

        re_step = cast(float, re_step)

        if m*100 > 0 and m*100 < 9:

            if p*10 > 0 and p*10 < 9:

                if t*100 > 0 and t*100 < 40:

                    valid = True

                    print(f"Adding NACA {naca_num} with Reynolds range {re_start} to {re_stop} and step {re_step} with color {color}")

                    self.foil_data = NACA_4_Standard_AirFoil(naca_num, re_start, re_stop, re_step, color) 


                    self.accept()

        if not valid:

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Invalid Input")

            msg.setText("NACA digits are not valid")

            msg.exec()



class AddCustomFoil(QDialog):
     
    def __init__(self):

        super().__init__()

        self.setWindowTitle("Add a Custom Airfoil")

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

        self.path_input.setPlaceholderText("Enter a file path")

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

        self.color_layout = QHBoxLayout()

        self.color_preview = QFrame()

        self.color_preview.setFixedSize(40, 40)

        self.color_preview.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.15);
            }}
        """)

        self.color_btn = QPushButton("PICK COLOR")

        self.color_btn.setStyleSheet("""
            QPushButton {

                background-color: black;
                color: white;
                border-radius: 10px;
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

        self.color_btn.clicked.connect(self.pick_color)

        self.color_layout.addWidget(self.color_preview)

        self.color_layout.addWidget(self.color_btn)

        self.name_input = QLineEdit()

        self.re_start_input = QLineEdit()

        self.re_stop_input = QLineEdit()

        self.re_step_input = QLineEdit()

        self.add_btn = QPushButton("ADD")

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

        self.add_btn.clicked.connect(self.add_foil)

        self.name_input.setPlaceholderText("Enter the name of the foil")

        self.re_start_input.setPlaceholderText("Reynolds Number (e.g. 100000)")

        self.re_stop_input.setPlaceholderText("Reynolds Number (e.g. 100000)")

        self.re_step_input.setPlaceholderText("Reynolds Number Step (e.g. 10000)")

        self.path_layout.addWidget(self.path_input)

        self.path_layout.addWidget(self.browse_btn)

        self.layout.addLayout(self.path_layout)

        self.layout.addLayout(self.color_layout)

        self.layout.addWidget(self.name_input)

        self.layout.addWidget(self.re_start_input)

        self.layout.addWidget(self.re_stop_input)

        self.layout.addWidget(self.re_step_input)

        self.layout.addWidget(self.add_btn)





    def browse(self) -> None:
        
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Airfoil", "", "DAT Files (*.dat)")
        
        if file_path:
              
            self.path_input.setText(file_path)

            self.file_path = file_path

            self.browse_btn.setText("Change File")

    def pick_color(self) -> None:
         
        color = QColorDialog.getColor()

        if color.isValid():

            self.color = color.name()

            self.color_preview.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.color};
                    border-radius: 10px;
                    border: 1px solid rgba(255,255,255,0.15);
                }}
            """)


    def add_foil(self) -> None:


        if not self.name_input.text():
             
            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Empty Name")

            msg.setText("Enter a valid name for your airfoil")

            msg.exec()

            return
        
        if not self.file_path or  not Path(self.file_path).exists():
             
            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Invalid File")

            msg.setText("The file path you entered is invalid or doesn't exist")

            msg.exec()

            return



        re_start = self.re_start_input.text() if self.re_start_input.text() else "100000"

        re_stop = self.re_stop_input.text() if self.re_stop_input.text() else "100000"

        re_step = self.re_step_input.text() if self.re_step_input.text() else "10000"

        steps = int((float(re_stop) - float(re_start)) / float(re_step)) + 1


        try:
             
            re_start = float(re_start)

            re_stop = float(re_stop)

            re_step = float(re_step)

        except:

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Invalid Reynolds Number")

            msg.setText("Reynolds numbers and step must be valid numbers.")

            msg.exec()

            return
        

        if steps > standards.MAX_RE_STEPS:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Too Many Points")
    
                msg.setText("The number of points to be generated is too high. Please reduce the Reynolds number range or increase the step.")
    
                msg.exec()
    
                return
        
        if float(re_start) > float(re_stop):

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Invalid Reynolds Range")
    
                msg.setText("The starting Reynolds number must be less than the stopping Reynolds number.")
    
                msg.exec()
    
                return
        
        if float(re_step) <= 0:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Invalid Step")
    
                msg.setText("The Reynolds number step must be a positive integer.")
    
                msg.exec()
    
                return
        
        self.foil_data = AirFoil(self.name_input.text(), re_start, re_stop, re_step, self.color, file_path=self.file_path)

        self.accept()

        


class AddNACA5StandardFoil(QDialog):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Add Standard NACA 5 Digit Airfoil")

        self.resize(350, 250)

        self.setStyleSheet("""

            QDialog {
                           
                background-color: #20252B;
                           
                border-radius: 15px;

                           
                           
            }




        """)


        layout = QVBoxLayout(self)

        self.naca_num_input = QLineEdit()
        self.naca_num_input.setPlaceholderText("NACA Number (e.g. 23012)")

        self.naca_num_input.setStyleSheet("""
                                      
            QLineEdit {
                color: white;
                font-size: 14px;
                background: transparent;
            }

        """)

        self.re_start_input = QLineEdit()
        self.re_start_input.setPlaceholderText("Reynolds Number (e.g. 100000)")

        self.re_start_input.setStyleSheet("""
                                      
            QLineEdit {
                color: white;
                font-size: 14px;
                background: transparent;
            }

        """)

        self.re_stop_num_input = QLineEdit()
        self.re_stop_num_input.setPlaceholderText("Reynolds Number (e.g. 100000)")

        self.re_stop_num_input.setStyleSheet("""
                                      
            QLineEdit {
                color: white;
                font-size: 14px;
                background: transparent;
            }

        """)

        self.re_step_input = QLineEdit()
        self.re_step_input.setPlaceholderText("Reynolds Number Step (e.g. 10000)")

        self.re_step_input.setStyleSheet("""
                                      
            QLineEdit {
                color: white;
                font-size: 14px;
                background: transparent;
            }

        """)

        color_layout = QHBoxLayout()

        self.color_preview = QFrame()

        self.color_preview.setFixedSize(40, 40)

        self.color_preview.setStyleSheet(f"""
            QFrame {{
                background-color: {self.selected_color if hasattr(self, 'selected_color') else '#4CAF50'};
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.15);
            }}
        """)

        self.color_btn = QPushButton("CHOOSE COLOR")
        
        self.color_btn.clicked.connect(self.pick_color)

        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: black;
                color: white;
                border-radius: 12px;
                font-weight: bold;
                padding: 8px;
                border: none;
            }}

            QPushButton:hover {{
                background-color: #222222;
            }}

            QPushButton:pressed {{
                background-color: #444444;
            }}
        """)

        color_layout.addWidget(self.color_preview)

        color_layout.addWidget(self.color_btn)

        self.add_btn = QPushButton("ADD")

        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: black;
                color: white;
                border-radius: 12px;
                padding: 8px;
                font-weight: bold;
                border: none;
            }}

            QPushButton:hover {{
                background-color: #222222;
            }}

            QPushButton:pressed {{
                background-color: #444444;
            }}
        """)

        self.add_btn.clicked.connect(self.add_foil)

        layout.addWidget(self.naca_num_input)
        layout.addWidget(self.re_start_input)
        layout.addWidget(self.re_stop_num_input)
        layout.addWidget(self.re_step_input)
        layout.addLayout(color_layout)
        layout.addStretch()
        layout.addWidget(self.add_btn)


    def pick_color(self) -> None:

        color = QColorDialog.getColor()

        if color.isValid():

            self.selected_color = color.name()

            self.color_preview.setStyleSheet(f"""
            QFrame {{
                background-color: {self.selected_color if hasattr(self, 'selected_color') else '#4CAF50'};
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.15);
            }}
        """)

            self.color_btn.setText("Color Selected")

    def add_foil(self) -> None:

        naca_num = self.naca_num_input.text() if self.naca_num_input.text() else "23012"

        re_start = self.re_start_input.text() if self.re_start_input.text() else "100000"

        re_stop = self.re_stop_num_input.text() if self.re_stop_num_input.text() else "100000"

        re_step = self.re_step_input.text() if self.re_step_input.text() else "10000"

        color = self.selected_color if hasattr(self, 'selected_color') else "#4CAF50"

        try:
             
            re_start = float(re_start)

            re_stop = float(re_stop)

            re_step = float(re_step)

        except:

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Invalid Reynolds Number")

            msg.setText("Reynolds numbers and step must be valid numbers.")

            msg.exec()

            return

        if not FoilUtils.check_naca_5(naca_num):

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Invalid NACA Number")

            msg.setText("The NACA number entered is not valid. Please enter a valid 5 digit NACA number.")

            msg.exec()

            return
    

        steps = int((float(re_stop) - float(re_start)) / float(re_step)) + 1

        if steps > standards.MAX_RE_STEPS:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Too Many Points")
    
                msg.setText("The number of points to be generated is too high. Please reduce the Reynolds number range or increase the step.")
    
                msg.exec()
    
                return
        
        if float(re_start) > float(re_stop):

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Invalid Reynolds Range")
    
                msg.setText("The starting Reynolds number must be less than the stopping Reynolds number.")
    
                msg.exec()
    
                return
        
        if float(re_step) <= 0:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Invalid Step")
    
                msg.setText("The Reynolds number step must be a positive integer.")
    
                msg.exec()
    
                return

        print(f"Adding NACA {naca_num} with Reynolds range {re_start} to {re_stop} and step {re_step} with color {color}")

        self.foil_data = NACA_5_Standard_Airfoil(naca_num, re_start, re_stop, re_step, color) 


        self.accept()





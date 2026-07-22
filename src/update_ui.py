from __future__ import annotations

# --- Imports for GUI ---
from PyQt6.QtWidgets import (
    QFrame, QFrame, QHBoxLayout, QMessageBox, QSlider, QVBoxLayout, QPushButton, QLabel, QDialog, QLineEdit, QColorDialog, QComboBox, QWidget
)

from PyQt6.QtCore import pyqtSignal, Qt


# --- Import for standards used across all files ---
import standards


# --- Imports for foil data ---
from foil_data import NACA_4_Standard_AirFoil, AirFoil, NACA_5_Standard_Airfoil

from foil_data import FoilUtils


# --- Imports for type annnotations
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING: # To prevent circular imports

    from support_widgets import AirfoilCard



class ISliderBar(QWidget):

    """
    
    Custom widget to allow the user to slide or type to set values. The input box is updated as soon as the user slides the slider
    and leaves it. The input box allows the user to enter values to update them.

    Attributes:
        minimum (int): The minimum allowable value for the slider.
        maximum (int): The maximum allowable value for the slider.
        step (int): The change in value per unit movement.
        slider (QSlider): The slider bar GUI element.
        input (QLineEdit): The QLineEdit to allow the user to enter values.
    
    """

    valueChanged = pyqtSignal(float)

    def __init__(
        self,
        minimum=0,
        maximum=100,
        step=1,
        default=0
    ):
        
        """

        Initializes the ISliderBar.

        Args:
            minimum (int): The minumum value allowed on the slider.
            maximum (int): The maximum value allowed on the slider.
            step (int): The change in value per unit of movement on the slider.
            default (int): The default value on the slider.

        """


        super().__init__()

        self.minimum = minimum

        self.maximum = maximum

        self.step = step

        layout = QHBoxLayout(self)

        self.slider = QSlider(Qt.Orientation.Horizontal)

        self.slider.setMinimum(minimum)

        self.slider.setMaximum(maximum)

        self.slider.setValue(default)

        self.input = QLineEdit(str(default))

        self.input.setFixedWidth(70)

        layout.addWidget(self.slider)

        layout.addWidget(self.input)

        self.slider.sliderReleased.connect(
            self.slider_changed
        )

        self.input.editingFinished.connect(
            self.input_changed
        )

    def slider_changed(self) -> None:

        """
        
        The method called when the slider value has changed.

        """

        value = self.slider.value()

        self.input.setText(str(value))

        self.valueChanged.emit(value)

    def input_changed(self) -> None:

        """
        
        The method called when the input box edit process finishes.

        """

        try:

            value = float(self.input.text())

        except ValueError:

            return

        value = max(self.minimum, value)

        value = min(self.maximum, value)

        self.slider.setValue(int(value))

        self.valueChanged.emit(value)
    



class UpdateNACA4StandardFoil(QDialog):

    def __init__(self, foil_data: NACA_4_Standard_AirFoil):

        super().__init__()

        self.foil_data = foil_data

        self.setWindowTitle("Update Standard NACA 4 Digit Airfoil")

        self.resize(350, 500)

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

        layout = QVBoxLayout(self)


        digit1_label = QLabel("First NACA Digit")

        self.digit1_slider = ISliderBar(
            minimum=0,
            maximum=9,
            default=int(self.foil_data.naca_num[0])
        )

        layout.addWidget(digit1_label)

        layout.addWidget(self.digit1_slider)


        digit2_label = QLabel("Second NACA Digit")

        self.digit2_slider = ISliderBar(
            minimum=0,
            maximum=9,
            default=int(self.foil_data.naca_num[1])
        )

        layout.addWidget(digit2_label)

        layout.addWidget(self.digit2_slider)


        digit3_label = QLabel("Third NACA Digit")

        self.digit3_slider = ISliderBar(
            minimum=0,
            maximum=9,
            default=int(self.foil_data.naca_num[2])
        )

        layout.addWidget(digit3_label)

        layout.addWidget(self.digit3_slider)


        digit4_label = QLabel("Fourth NACA Digit")

        self.digit4_slider = ISliderBar(
            minimum=0,
            maximum=9,
            default=int(self.foil_data.naca_num[3])
        )

        layout.addWidget(digit4_label)

        layout.addWidget(self.digit4_slider)


        self.re_start_input = QLineEdit()

        self.re_start_input.setPlaceholderText(f"Re start(default: {self.foil_data.reynolds_num_start})")

        self.re_end_input = QLineEdit()

        self.re_end_input.setPlaceholderText(f"Re end(default: {self.foil_data.reynolds_num_stop})")

        self.re_step_input = QLineEdit()

        self.re_step_input.setPlaceholderText(f"Re step(default: {self.foil_data.reynolds_num_step})")

        color_layout = QHBoxLayout()

        self.color_preview = QFrame()

        self.color_preview.setFixedSize(40, 40)

        self.color_preview.setStyleSheet(f"""
            QFrame {{
                background-color: {self.foil_data.color};
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.15);
            }}
        """)

        self.color_btn = QPushButton("PICK COLOR")

        self.color_btn.setFixedHeight(40)

        self.color_btn.setStyleSheet("""
            QPushButton {

                background-color: black;
                color: white;
                font-weight: bold;
                border-radius: 10px;
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

        color_layout.addWidget(self.color_preview)

        color_layout.addWidget(self.color_btn)

        layout.addLayout(color_layout)

        layout.addWidget(self.re_start_input)

        layout.addWidget(self.re_end_input)

        layout.addWidget(self.re_step_input)

        self.update_btn = QPushButton("UPDATE")

        self.update_btn.setFixedHeight(45)

        self.update_btn.setStyleSheet("""
            QPushButton {

                background-color: black;
                color: white;
                font-weight: bold;
                border-radius: 12px;
            }

            QPushButton:hover {

                background-color: #222222;
            }

            QPushButton:pressed {

                background-color: #444444;
            }
        """)

        self.update_btn.clicked.connect(self.update_foil_data)

        layout.addWidget(self.update_btn)





    def pick_color(self) -> None:

        color = QColorDialog.getColor()

        if color.isValid():

            self.foil_data.color = color.name()

            self.color_preview.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.foil_data.color};
                    border-radius: 10px;
                    border: 1px solid rgba(255,255,255,0.15);
                }}
            """)

    def update_foil_data(self) -> None:

        fail = False

        self.foil_data.naca_num = f"{self.digit1_slider.slider.value()}{self.digit2_slider.slider.value()}{self.digit3_slider.slider.value()}{self.digit4_slider.slider.value()}"

        self.foil_data.name = f"NACA {self.foil_data.naca_num}"

        re_start = self.re_start_input.text() if self.re_start_input.text() else self.foil_data.reynolds_num_start

        re_stop = self.re_end_input.text() if self.re_end_input.text() else self.foil_data.reynolds_num_stop

        re_step = self.re_step_input.text() if self.re_step_input.text() else self.foil_data.reynolds_num_step


        if self.re_start_input.text():

            try:

                re_start = float(re_start)

            except ValueError:

                fail = True

        if self.re_end_input.text():

            try:

                re_stop = float(re_stop)

            except ValueError:

                fail = True

        if self.re_step_input.text():

            try:

                re_step = float(re_step)

            except ValueError:

                fail = True

        re_stop = cast(float, re_stop)

        re_start = cast(float, re_start)

        re_step = cast(float, re_step)

        steps = (re_stop - re_start) / re_step + 1

        if steps > standards.MAX_RE_STEPS:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Too Many Points")
    
                msg.setText("The number of points to be generated is too high. Please reduce the Reynolds number range or increase the step.")
    
                msg.exec()
    
                return
        
        if re_start > re_stop:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Invalid Reynolds Range")
    
                msg.setText("The starting Reynolds number must be less than the stopping Reynolds number.")
    
                msg.exec()
    
                return
        
        if re_step <= 0:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Invalid Step")
    
                msg.setText("The Reynolds number step must be a positive number.")
    
                msg.exec()
    
                return

        if fail:

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Invalid Input")

            msg.setText("Please enter valid numbers for the Reynolds number parameters.")

            msg.exec()

        else:

            self.foil_data.reynolds_num_start = re_start

            self.foil_data.reynolds_num_stop = re_stop

            self.foil_data.reynolds_num_step = re_step

            self.accept()



class UpdateCustomFoil(QDialog):

    def __init__(self, foil_data: AirFoil):

        super().__init__()

        self.foil_data = foil_data

        self.setWindowTitle("Update Custom Airfoil")

        self.resize(350, 300)

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

        layout = QVBoxLayout(self)

        self.re_start_input = QLineEdit()

        self.re_start_input.setPlaceholderText(f"Re start(default: {self.foil_data.reynolds_num_start})")

        self.re_end_input = QLineEdit()

        self.re_end_input.setPlaceholderText(f"Re end(default: {self.foil_data.reynolds_num_stop})")

        self.re_step_input = QLineEdit()

        self.re_step_input.setPlaceholderText(f"Re step(default: {self.foil_data.reynolds_num_step})")

        color_layout = QHBoxLayout()

        self.color_preview = QFrame()

        self.color_preview.setFixedSize(40, 40)

        self.color_preview.setStyleSheet(f"""
            QFrame {{
                background-color: {self.foil_data.color};
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.15);
            }}
        """)

        self.color_btn = QPushButton("PICK COLOR")

        self.color_btn.setFixedHeight(40)

        self.color_btn.setStyleSheet("""
            QPushButton {

                background-color: black;
                color: white;
                font-weight: bold;
                border-radius: 10px;
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

        color_layout.addWidget(self.color_preview)

        color_layout.addWidget(self.color_btn)

        layout.addLayout(color_layout)

        layout.addWidget(self.re_start_input)

        layout.addWidget(self.re_end_input)

        layout.addWidget(self.re_step_input)

        self.update_btn = QPushButton("UPDATE")

        self.update_btn.setFixedHeight(45)

        self.update_btn.setStyleSheet("""
            QPushButton {

                background-color: black;
                color: white;
                font-weight: bold;
                border-radius: 12px;
            }

            QPushButton:hover {

                background-color: #222222;
            }

            QPushButton:pressed {

                background-color: #444444;
            }
        """)

        self.update_btn.clicked.connect(self.update_foil_data)

        layout.addWidget(self.update_btn)


    def pick_color(self) -> None:

        color = QColorDialog.getColor()

        if color.isValid():

            self.foil_data.color = color.name()

            self.color_preview.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.foil_data.color};
                    border-radius: 10px;
                    border: 1px solid rgba(255,255,255,0.15);
                }}
            """)


    def update_foil_data(self) -> None:

        fail = False

        re_start = self.re_start_input.text() if self.re_start_input.text() else self.foil_data.reynolds_num_start

        re_stop = self.re_end_input.text() if self.re_end_input.text() else self.foil_data.reynolds_num_stop

        re_step = self.re_step_input.text() if self.re_step_input.text() else self.foil_data.reynolds_num_step


        if self.re_start_input.text():

            try:

                re_start = float(re_start)

            except ValueError:

                fail = True

        if self.re_end_input.text():

            try:

                re_stop = float(re_stop)

            except ValueError:

                fail = True

        if self.re_step_input.text():

            try:

                re_step = float(re_step)

            except ValueError:

                fail = True


        re_stop = cast(float, re_stop)

        re_start = cast(float, re_start)

        re_step = cast(float, re_step)

        steps = (re_stop - re_start) / re_step + 1

        if steps > standards.MAX_RE_STEPS:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Too Many Points")
    
                msg.setText("The number of points to be generated is too high. Please reduce the Reynolds number range or increase the step.")
    
                msg.exec()
    
                return
        
        if re_start > re_stop:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Invalid Reynolds Range")
    
                msg.setText("The starting Reynolds number must be less than the stopping Reynolds number.")
    
                msg.exec()
    
                return
        
        if re_step <= 0:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Invalid Step")
    
                msg.setText("The Reynolds number step must be a positive number.")
    
                msg.exec()
    
                return

        if fail:

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Invalid Input")

            msg.setText("Please enter valid numbers for the Reynolds number parameters.")

            msg.exec()

        else:

            self.foil_data.reynolds_num_start = re_start

            self.foil_data.reynolds_num_stop = re_stop

            self.foil_data.reynolds_num_step = re_step

            self.accept()

class UpdateNACA5StandardFoil(QDialog):

    def __init__(self, foil_data: NACA_5_Standard_Airfoil):

        super().__init__()

        self.foil_data = foil_data

        self.setWindowTitle("Update Standard NACA 4 Digit Airfoil")

        self.resize(350, 500)

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

        layout = QVBoxLayout(self)


        digit2_label = QLabel("Second NACA Digit")

        self.digit2_slider = ISliderBar(
            minimum=1,
            maximum=5,
            default=int(self.foil_data.naca_num[1])
        )

        layout.addWidget(digit2_label)

        layout.addWidget(self.digit2_slider)


        digit3_label = QLabel("Third NACA Digit")

        self.digit3_slider = ISliderBar(
            minimum=0,
            maximum=1,
            default=int(self.foil_data.naca_num[2])
        )

        layout.addWidget(digit3_label)

        layout.addWidget(self.digit3_slider)


        digit4_label = QLabel("Fourth NACA Digit")

        self.digit4_slider = ISliderBar(
            minimum=0,
            maximum=4,
            default=int(self.foil_data.naca_num[3])
        )

        layout.addWidget(digit4_label)

        layout.addWidget(self.digit4_slider)

        digit5_label = QLabel("Fifth NACA Digit")

        self.digit5_slider = ISliderBar(
            minimum=0,
            maximum=9,
            default=int(self.foil_data.naca_num[4])
        )

        layout.addWidget(digit5_label)

        layout.addWidget(self.digit5_slider)


        self.re_start_input = QLineEdit()

        self.re_start_input.setPlaceholderText(f"Re start(default: {self.foil_data.reynolds_num_start})")

        self.re_end_input = QLineEdit()

        self.re_end_input.setPlaceholderText(f"Re end(default: {self.foil_data.reynolds_num_stop})")

        self.re_step_input = QLineEdit()

        self.re_step_input.setPlaceholderText(f"Re step(default: {self.foil_data.reynolds_num_step})")

        color_layout = QHBoxLayout()

        self.color_preview = QFrame()

        self.color_preview.setFixedSize(40, 40)

        self.color_preview.setStyleSheet(f"""
            QFrame {{
                background-color: {self.foil_data.color};
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.15);
            }}
        """)

        self.color_btn = QPushButton("PICK COLOR")

        self.color_btn.setFixedHeight(40)

        self.color_btn.setStyleSheet("""
            QPushButton {

                background-color: black;
                color: white;
                font-weight: bold;
                border-radius: 10px;
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

        color_layout.addWidget(self.color_preview)

        color_layout.addWidget(self.color_btn)

        layout.addLayout(color_layout)

        layout.addWidget(self.re_start_input)

        layout.addWidget(self.re_end_input)

        layout.addWidget(self.re_step_input)

        self.update_btn = QPushButton("UPDATE")

        self.update_btn.setFixedHeight(45)

        self.update_btn.setStyleSheet("""
            QPushButton {

                background-color: black;
                color: white;
                font-weight: bold;
                border-radius: 12px;
            }

            QPushButton:hover {

                background-color: #222222;
            }

            QPushButton:pressed {

                background-color: #444444;
            }
        """)

        self.update_btn.clicked.connect(self.update_foil_data)

        layout.addWidget(self.update_btn)





    def pick_color(self) -> None:

        color = QColorDialog.getColor()

        if color.isValid():

            self.foil_data.color = color.name()

            self.color_preview.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.foil_data.color};
                    border-radius: 10px;
                    border: 1px solid rgba(255,255,255,0.15);
                }}
            """)

    def update_foil_data(self) -> None:

        fail = False

        naca_num = f"2{self.digit2_slider.slider.value()}{self.digit3_slider.slider.value()}{self.digit4_slider.slider.value()}{self.digit5_slider.slider.value()}"


        if not FoilUtils.check_naca_5(naca_num):

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Invalid NACA digits")

            msg.setText("Please enter a valid NACA 5-digit number.")

            msg.exec()

        self.foil_data.naca_num = naca_num

        self.foil_data.name = f"NACA {self.foil_data.naca_num}"

        re_start = self.re_start_input.text() if self.re_start_input.text() else self.foil_data.reynolds_num_start

        re_stop = self.re_end_input.text() if self.re_end_input.text() else self.foil_data.reynolds_num_stop

        re_step = self.re_step_input.text() if self.re_step_input.text() else self.foil_data.reynolds_num_step


        if self.re_start_input.text():

            try:

                re_start = float(re_start)

            except ValueError:

                fail = True

        if self.re_end_input.text():

            try:

                re_stop = float(re_stop)

            except ValueError:

                fail = True

        if self.re_step_input.text():

            try:

                re_step = float(re_step)

            except ValueError:

                fail = True

        re_stop = cast(float, re_stop)

        re_start = cast(float, re_start)

        re_step = cast(float, re_step)

        steps = (re_stop - re_start) / re_step + 1

        if steps > standards.MAX_RE_STEPS:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Too Many Points")
    
                msg.setText("The number of points to be generated is too high. Please reduce the Reynolds number range or increase the step.")
    
                msg.exec()
    
                return
        
        if re_start > re_stop:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Invalid Reynolds Range")
    
                msg.setText("The starting Reynolds number must be less than the stopping Reynolds number.")
    
                msg.exec()
    
                return
        
        if re_step <= 0:

                msg = QMessageBox(self)
    
                msg.setIcon(QMessageBox.Icon.Critical)
    
                msg.setWindowTitle("Invalid Step")
    
                msg.setText("The Reynolds number step must be a positive number.")
    
                msg.exec()
    
                return

        if fail:

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Invalid Input")

            msg.setText("Please enter valid numbers for the Reynolds number parameters.")

            msg.exec()

        else:

            self.foil_data.reynolds_num_start = re_start

            self.foil_data.reynolds_num_stop = re_stop

            self.foil_data.reynolds_num_step = re_step

            self.accept()     





class UpdateAlphaBounds(QDialog):


    def __init__(self, airfoil_cards: list[AirfoilCard], card: AirfoilCard|None):

        super().__init__()

        self.bounds = (standards.DEFAULT_START_ALPHA, standards.DEFAULT_STOP_ALPHA, standards.DEFAULT_STEP_ALPHA)

        self.airfoil_cards = airfoil_cards

        airfoil_cards_names = [card.name for card in self.airfoil_cards]

        if card != None:

            self.card_index = airfoil_cards_names.index(card.name)

            foil_data = self.airfoil_cards[self.card_index].foil_data

            self.bounds = (foil_data.alpha_num_start, foil_data.alpha_num_stop, foil_data.alpha_num_step)

        else:

            self.card_index = 0


        self.setWindowTitle("Update Alpha Bounds For The Plots")

        self.resize(350, 300)

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

        layout = QVBoxLayout(self)

        foil_selection_layout = QHBoxLayout()

        foil_selection_label = QLabel("SELECT THE AIRFOIL")

        foil_selection_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)

        self.foil_selection_combo = QComboBox()

        self.foil_selection_combo.addItems(airfoil_cards_names)

        self.foil_selection_combo.setCurrentIndex(self.card_index)

        self.foil_selection_combo.setStyleSheet("""
QComboBox {
    background-color: rgba(30, 30, 30, 0.75);
    color: white;

    border-radius: 10px;
    padding: 6px 10px;

    border: 1px solid rgba(255,255,255,0.08);
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #20252B;
    color: white;

    selection-background-color: rgba(255,255,255,0.10);

    border-radius: 8px;
}
""")
        
        foil_selection_layout.addWidget(foil_selection_label)
        
        foil_selection_layout.addWidget(self.foil_selection_combo)

        self.alpha_start_input = QLineEdit()

        self.alpha_start_input.setPlaceholderText(f"Enter the start alpha value (default: {self.bounds[0]})")

        self.alpha_end_input = QLineEdit()

        self.alpha_end_input.setPlaceholderText(f"Enter the end alpha value (default: {self.bounds[1]})")

        self.alpha_step_input = QLineEdit()

        self.alpha_step_input.setPlaceholderText(f"Enter the step value (default: {self.bounds[2]})")

        self.update_btn = QPushButton("UPDATE")

        self.update_btn.setFixedHeight(45)

        self.update_btn.setStyleSheet("""
            QPushButton {

                background-color: black;
                color: white;
                font-weight: bold;
                border-radius: 12px;
            }

            QPushButton:hover {

                background-color: #222222;
            }

            QPushButton:pressed {

                background-color: #444444;
            }
        """)

        self.update_btn.clicked.connect(self.update_alpha)



        layout.addLayout(foil_selection_layout)

        layout.addWidget(self.alpha_start_input)

        layout.addWidget(self.alpha_end_input)

        layout.addWidget(self.alpha_step_input)

        layout.addWidget(self.update_btn)


    def update_alpha(self) -> None:

        self.card_index = self.foil_selection_combo.currentIndex()

        alpha_start = self.alpha_start_input.text() if self.alpha_start_input.text() else self.bounds[0]

        alpha_end = self.alpha_end_input.text() if self.alpha_end_input.text() else self.bounds[1]

        alpha_step = self.alpha_step_input.text() if self.alpha_step_input.text() else self.bounds[2]

        fail = False

        try:

            alpha_start = int(alpha_start)

            alpha_end = int(alpha_end)

            alpha_step = int(alpha_step)

            if alpha_end <= alpha_start or alpha_step <= 0:

                raise ValueError

        
        except:

            fail = True


        if fail:

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Invalid alpha bounds")

            msg.setText("The bounds for alpha are invalid")

            msg.exec()

            return
        
        alpha_end = cast(int, alpha_end)

        alpha_start = cast(int, alpha_start)

        alpha_step = cast(int, alpha_step)
        
        
        steps = ((alpha_end - alpha_start) / alpha_step) + 1
        

        
        if steps > standards.MAX_ALPHA_POINTS:

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("Too many alpha point")

            msg.setText(f"The number of alpha points must not exceed the limit of {standards.MAX_ALPHA_POINTS}")

            msg.exec()

            return
        


        self.bounds = (alpha_start, alpha_end, alpha_step)

        self.update_info = (self.card_index, self.bounds)

        self.accept()




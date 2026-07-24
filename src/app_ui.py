import sys

import copy

from PyQt6.QtWidgets import (
    QApplication, QGridLayout, QMainWindow, QMenuBar, QMessageBox, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QScrollArea, QMenu, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
import numpy as np

from PyQt6 import QtGui

from PyQt6.QtGui import QAction


from numpy.typing import NDArray

import standards

import json

from collections import deque

from typing import Callable, Any, cast

from add_ui import AddNACA4StandardFoil, AddCustomFoil, AddNACA5StandardFoil

from collect_data import DataUtils

from pathlib import Path

from save_ui import SaveProject, LoadProject



from support_widgets import AirfoilCard, PlotWidget, ProgressDialog

from foil_data import FoilUtils, AirFoil, NACA_4_Standard_AirFoil, NACA_5_Standard_Airfoil
from update_ui import UpdateAlphaBounds

from support_models import Worker, PlotBlock


"""

I haven't added documentation for every file, will do it soon. For now, I am just adding docstrings to the main files.


"""




class LeftPanel(QWidget):

    airfoil_updated = pyqtSignal(object)

    airfoil_deleted = pyqtSignal(int)

    airfoil_visibility_toggle = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self.cards = []

        main_layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }

            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
                             

QScrollBar:vertical {
    background: rgba(255, 255, 255, 0.05);
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.35);
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.50);
}

QScrollBar::handle:vertical:pressed {
    background: rgba(255, 255, 255, 0.65);
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
    background: transparent;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
}


QScrollBar:horizontal {
    background: rgba(255, 255, 255, 0.05);
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background: rgba(255, 255, 255, 0.35);
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: rgba(255, 255, 255, 0.50);
}

QScrollBar::handle:horizontal:pressed {
    background: rgba(255, 255, 255, 0.65);
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0px;
    background: transparent;
}

QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: transparent;
}
        """)
        

        container = QWidget()
        self.list_layout = QVBoxLayout(container)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setStyleSheet("""
            background-color: #1e1e1e;
        """)

        scroll.setWidget(container)

        main_layout.addWidget(scroll)

    def add_card(self, foil_data: AirFoil) -> AirfoilCard:


        card = AirfoilCard(foil_data)
        self.list_layout.addWidget(card)

        card.airfoil_updated.connect(self.airfoil_updated)

        card.airfoil_visibility_toggle.connect(self.airfoil_visibility_toggle)

        self.cards.append(card)

        return card



    def remove_card(self, card: AirfoilCard) -> None:

        self.list_layout.removeWidget(card)

        i = self.cards.index(card)

        self.cards.remove(card)

        self.airfoil_deleted.emit(i)

        card.deleteLater()




    
    def is_name_color_available(self, name: str, color: str, old_name: str, old_color: str) -> list[bool]:

        val = [True, True]

        for card in self.cards:

            if card.name == name and card.name != old_name:

                val[0] = False

            if card.color == color and (card.color != old_color):

                val[1] = False

        return val





class AnalysisWindow(QMainWindow):

    def __init__(self, import_data: tuple[list[AirFoil], list[bool]]|None = None):

        super().__init__()

        FoilUtils.clean()

        self.setWindowTitle("SAM - Airfoil Analysis")

        self.setStyleSheet("background-color: #20252B;")

        self.adding_airfoil = False

        self.airfoil_import_queue: deque = deque()

        self.airfoil_update_queue: deque = deque()

        self.windows: list[AnalysisWindow] = []

        self.save_location: Path | str = ""

        self.analysis_thread: QThread | None = None

        self.analysis_worker: Worker | None = None

        central_widget = QWidget()

        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        self.setWindowIcon(QtGui.QIcon(str((Path(__file__).parent / "../" / "resources" / "app_icon.png").resolve())))

        layout.setContentsMargins(15, 15, 15, 15)

        layout.setSpacing(15)

        menu_bar: QMenuBar = QMenuBar(self)
 
        file_menu: QMenu = cast(QMenu, menu_bar.addMenu("File"))

        view_menu: QMenu = cast(QMenu, menu_bar.addMenu("View"))

        plot_menu: QMenu = cast(QMenu, menu_bar.addMenu("Plot"))

        add_airfoil_menu: QMenu = cast(QMenu, file_menu.addMenu("Add New Airfoil"))

        add_naca_4_airfoil_action = cast(QMenu, add_airfoil_menu.addAction("Add Standard NACA 4-digit Airfoil"))

        add_naca_5_airfoil_action = cast(QMenu, add_airfoil_menu.addAction("Add Standard NACA 5-digit Airfoil"))

        add_custom_dat_airfoil_action = cast(QMenu, add_airfoil_menu.addAction("Add Custom .dat Airfoil"))

        add_naca_4_airfoil_action.triggered.connect(lambda: self.get_foil_dialog_and_add(standards.NACA_4_AIRFOIL))

        add_naca_5_airfoil_action.triggered.connect(lambda: self.get_foil_dialog_and_add(standards.NACA_5_AIRFOIL))

        add_custom_dat_airfoil_action.triggered.connect(self.get_foil_dialog_and_add)

        save_project_action: QAction = cast(QAction, file_menu.addAction("Save Project"))

        save_project_action.triggered.connect(self.save_project)

        load_project_action: QAction = cast(QAction, file_menu.addAction("Load Project"))

        load_project_action.triggered.connect(self.load_project)

        revert_all_plots_action: QAction = cast(QAction, view_menu.addAction("Revert All Plots To Original"))

        revert_all_plots_action.triggered.connect(self.revert_all_plots)

        show_all_plots_action: QAction = cast(QAction, view_menu.addAction("Show All Plots"))

        show_all_plots_action.triggered.connect(lambda: self.show_or_hide_all_plots(False))

        hide_all_plots_action: QAction = cast(QAction, view_menu.addAction("Hide All Plots"))

        hide_all_plots_action.triggered.connect(lambda: self.show_or_hide_all_plots(True))

        set_alpha_bounds: QAction = cast(QAction, plot_menu.addAction("Set Alpha Bounds"))

        set_alpha_bounds.triggered.connect(self.set_alpha_bounds)

        left_panel: QFrame = QFrame(self)

        left_panel.setStyleSheet("""
            QFrame {
            background-color: rgba(255, 255, 255, 0.12);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.25);
            }
        """)

        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: rgba(255, 255, 255, 0.06);
                color: white;
                padding: 4px;
            }

            QMenuBar::item {
                background: transparent;
                padding: 6px 12px;
                border-radius: 6px;
                color: white;
            }

            QMenuBar::item:selected {
                background-color: rgba(255, 255, 255, 0.14);
            }   

            QMenu {
                background-color: rgba(35, 40, 48, 0.95);
                color: white;
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 10px;
                padding: 4px;
            }

            QMenu::item {
                padding: 8px 20px;
                border-radius: 6px;
            }

            QMenu::item:selected {
                background-color: rgba(255,255,255,0.12);
            }
        """)

        left_layout = QVBoxLayout(left_panel)

        self.left_panel = LeftPanel()

        left_layout.addWidget(self.left_panel)

        self.left_panel.airfoil_updated.connect(self.update_airfoil)

        self.left_panel.airfoil_deleted.connect(self.delete_airfoil)

        self.left_panel.airfoil_visibility_toggle.connect(self.toggle_visibility_airfoil)

        right_panel = QFrame(self)

        self.cl_a_plot = PlotWidget("Cl vs. Alpha", "Alpha (°)", "Cl")

        self.cd_a_plot = PlotWidget("Cd vs. Alpha", "Alpha (°)", "Cd")

        self.cm_a_plot = PlotWidget("Cm vs. Alpha", "Alpha (°)", "Cm")

        self.cd_cl_plot = PlotWidget("Cd vs. Cl", "Cl", "Cd")

        self.foil_plot = PlotWidget("Airfoil Shape", "x/c", "y/c")

        right_panel_layout = QGridLayout(right_panel)

        right_panel_layout.addWidget(self.cl_a_plot, 0, 0)
        right_panel_layout.addWidget(self.cd_a_plot, 0, 1)
        right_panel_layout.addWidget(self.cm_a_plot, 0, 2)
        right_panel_layout.addWidget(self.cd_cl_plot, 1, 0)
        right_panel_layout.addWidget(self.foil_plot, 1, 2)
        right_panel.setStyleSheet("""
            QFrame {
            background-color: rgba(255, 255, 255, 0.12);
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.25);
            }
        """)

        layout.addWidget(left_panel, 2)

        layout.addWidget(right_panel, 8)

        layout.setMenuBar(menu_bar)

        if import_data != None:

            airfoils, visibility_data = import_data

            for i in range(len(airfoils)):

                self.airfoil_import_queue.append((airfoils[i], visibility_data[i]))

            self.airfoil_addition_queue_flush()





    def airfoil_addition_queue_flush(self) -> None:

        if self.adding_airfoil:

            return
        
        if not self.airfoil_import_queue:

            self.sync_card_plot_visibility()

            return
        
        airfoil, visibility = self.airfoil_import_queue.popleft()

        self.add_airfoil(airfoil, visibility)



    def run_thread_task(self, running_func: Callable[..., Any], update_func: Callable[..., None], finishing_func: Callable[..., None]) -> None:

        if self.analysis_thread == None and self.analysis_worker == None:

            self.analysis_thread = QThread()

            self.analysis_worker = Worker(running_func)

            self.analysis_worker.moveToThread(self.analysis_thread)

            self.analysis_thread.started.connect(self.analysis_worker.run)

            self.analysis_worker.finished.connect(finishing_func)

            self.analysis_worker.finished.connect(self.analysis_thread.quit)

            self.analysis_worker.progress.connect(update_func)

            self.analysis_worker.finished.connect(self.analysis_worker.deleteLater)

            self.analysis_thread.finished.connect(self.analysis_thread.deleteLater)

            self.analysis_thread.finished.connect(self.cleanup_thread_refs)

            self.analysis_worker.error.connect(self.task_error)

            self.analysis_thread.start()




               








    def get_foil_dialog_and_add(self, foil_type: str = standards.CUSTOM_AIRFOIL) -> None:

        match foil_type:

            case standards.NACA_4_AIRFOIL:


                dialog: AddNACA4StandardFoil | AddNACA5StandardFoil | AddCustomFoil = AddNACA4StandardFoil()

            case standards.NACA_5_AIRFOIL:

                dialog = AddNACA5StandardFoil()

            case _:

                dialog = AddCustomFoil()

        if dialog.exec():

            self.airfoil_import_queue.append((dialog.foil_data, False))

            self.airfoil_addition_queue_flush()




    def add_airfoil(self, foil_data: AirFoil, visibility_data: bool|None = None) -> None:

        self.adding_airfoil = True

        for card in self.left_panel.cards:

            if card.name == foil_data.name:

                msg = QMessageBox(self)

                msg.setIcon(QMessageBox.Icon.Critical)

                msg.setWindowTitle("Duplicate Airfoil")

                msg.setText("An airfoil with this name already exists. Please choose a different name.")

                msg.exec()

                return
                
            elif card.color == foil_data.color:

                res: QMessageBox.StandardButton = QMessageBox.question(self, "Duplicate Colour", "An airfoil with this color already exists and may be difficult to distinguish on the plots. Do you want to keep it like this?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                if res == QMessageBox.StandardButton.Yes:

                    break
                    
                else:

                    return



        card = self.left_panel.add_card(foil_data)

        if visibility_data != None:

            card.toggle_visibility(visibility_data)



        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        steps = int(((foil_data.reynolds_num_stop - foil_data.reynolds_num_start) / foil_data.reynolds_num_step) + 1)

        self.progress_dialog = ProgressDialog(steps)

        self.run_thread_task(foil_data.run_xfoil_model, self.progress_dialog.update_progress, self.add_task_done)

        self.progress_dialog.show()

        




            

    def update_airfoil(self, update_info: tuple[AirFoil, AirFoil]|tuple[AirFoil, AirFoil, int], passed_index: bool = False) -> None:

        i = 0

        old_data = update_info[1]

        if not passed_index:

            for card in self.left_panel.cards:

                if card.name == update_info[1].name:

                    self.left_panel.cards[i].name = update_info[0].name

                    self.left_panel.cards[i].color = update_info[0].color

                    self.left_panel.cards[i].foil_data = update_info[0]

                    break

                i += 1

        else:

            assert len(update_info) == 3

            i = update_info[2]

        self.left_panel.cards[i].foil_data = update_info[0]

        data = update_info[0]

        if data.is_almost_same(old_data):

            self.cl_a_plot.update_only_color(i, data.color)

            self.cd_a_plot.update_only_color(i, data.color)

            self.cm_a_plot.update_only_color(i, data.color)

            self.cd_cl_plot.update_only_color(i, data.color)

            self.foil_plot.update_only_color(i, data.color)

            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        steps = int(((data.reynolds_num_stop - data.reynolds_num_start) / data.reynolds_num_step) + 1)

        self.progress_dialog = ProgressDialog(steps)

        self.airfoil_update_queue.append(i)

        self.run_thread_task(data.run_xfoil_model, self.progress_dialog.update_progress, self.update_task_done)

        self.progress_dialog.show()





    def delete_airfoil(self, deleted_card_index: int) -> None:

        i = deleted_card_index

        self.cl_a_plot.remove_plot(i)

        self.cd_a_plot.remove_plot(i)

        self.cm_a_plot.remove_plot(i)

        self.cd_cl_plot.remove_plot(i)

        self.foil_plot.remove_plot(i)

    def closeEvent(self, event):

        if hasattr(self, "analysis_thread") and self.analysis_thread is not None:

            if self.analysis_thread.isRunning():

                QMessageBox.warning(
                    self,
                    "Analysis Running",
                    "Wait for the current analysis to finish."
                )

                event.ignore()
                return

        super().closeEvent(event)



    def toggle_visibility_airfoil(self, hidden_foil_data: AirFoil) -> None:

        i = 0

        for card in self.left_panel.cards:

            if card.name == hidden_foil_data.name:

                break

            i += 1

        self.cd_a_plot.toggle_visibility_plot(i)

        self.cl_a_plot.toggle_visibility_plot(i)

        self.cd_cl_plot.toggle_visibility_plot(i)

        self.cm_a_plot.toggle_visibility_plot(i)

        self.foil_plot.toggle_visibility_plot(i)



    def sync_card_plot_visibility(self) -> None:

        for i in range(len(self.left_panel.cards)):

            self.cd_a_plot.toggle_visibility_plot(i, self.left_panel.cards[i].hidden)

            self.cl_a_plot.toggle_visibility_plot(i, self.left_panel.cards[i].hidden)

            self.cd_cl_plot.toggle_visibility_plot(i, self.left_panel.cards[i].hidden)

            self.cm_a_plot.toggle_visibility_plot(i, self.left_panel.cards[i].hidden)

            self.foil_plot.toggle_visibility_plot(i, self.left_panel.cards[i].hidden)




    def show_or_hide_all_plots(self, value: bool):


        for i in range(len(self.left_panel.cards)):

            self.left_panel.cards[i].toggle_visibility(value)

            self.cd_a_plot.toggle_visibility_plot(i, value)

            self.cl_a_plot.toggle_visibility_plot(i, value)

            self.cd_cl_plot.toggle_visibility_plot(i, value)

            self.cm_a_plot.toggle_visibility_plot(i, value)

            self.foil_plot.toggle_visibility_plot(i, value)


    def get_json_data(self) -> dict[str, dict[str, str]]:

        data = {}

        for card in self.left_panel.cards:

            attrs = (
            "reynolds_num_start",
            "reynolds_num_stop",
            "reynolds_num_step",
            "alpha_num_start",
            "alpha_num_stop",
            "alpha_num_step",
            "type",
            "color"
            )

            card_data = {}

            for attr in attrs:

                card_data[attr] = getattr(card.foil_data, attr)

            if not card.foil_data.is_standard_foil():

                card_data["xu"] = card.foil_data.xu.tolist()

                card_data["yu"] = card.foil_data.yu.tolist()

                card_data["xl"] = card.foil_data.xl.tolist()

                card_data["yl"] = card.foil_data.yl.tolist()



            card_data["hidden"] = card.hidden

            data[card.name] = card_data

        return data



    def save_project(self, save_as: bool = False) -> None:

        data = self.get_json_data()

        if save_as:  # Future feature to implement "Save As" functionality, currently not used in the code

            if Path(self.save_location).exists():

                with open(self.save_location, "w") as file:

                    json.dump(data, file, indent=4)

                    file.close()

                    raise NotImplementedError("Save As functionality is not implemented yet.")
                
        dialog = SaveProject()

        if dialog.exec():

            file_path = Path(dialog.file_path) / f"{dialog.project_name}.json"

            if file_path.exists():

                res: QMessageBox.StandardButton = QMessageBox.question(self, "File Exists", "A file already exists with this name. Do you want to overwrite it?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                if res == QMessageBox.StandardButton.No:

                    return
                

            with open(file_path, "w") as file:

                json.dump(data, file, indent=4)

                file.close()

        self.save_location = file_path

        msg: QMessageBox = QMessageBox(self)

        msg.setIcon(QMessageBox.Icon.Information)

        msg.setWindowTitle("Project Saved Sucessfully")

        msg.setText(f"The project has been saved at {file_path} sucessfully")

        msg.exec()


    def load_project(self):

        failed_foils = []

        dialog = LoadProject()

        if dialog.exec():


            file_path = dialog.file_path

            data = {}

            foils = []

            visibility_data = []

            try:

                with open(file_path, "r") as file:

                    data = json.load(file)

            except json.JSONDecodeError:

                msg = QMessageBox(self)

                msg.setIcon(QMessageBox.Icon.Critical)

                msg.setWindowTitle("Corrupted File")

                msg.setText("Project file is corrupted or malformed")

                msg.exec()

                return
            
            except:

                msg = QMessageBox(self)

                msg.setIcon(QMessageBox.Icon.Critical)

                msg.setWindowTitle("Read Error")

                msg.setText("File could not be read. Check if the file has read permissions.")

                msg.exec()

                return
            
            required_standard_keys = {
                "type",
                "color"
            }

            required_custom_keys = {
                "type",
                "color",
                "xu",
                "yu",
                "xl",
                "yl"
            }

            for name, foil_data in data.items():

                if not required_standard_keys.issubset(foil_data):

                    failed_foils.append(name)

                    continue

                foil_type = foil_data["type"]

                if foil_type == standards.CUSTOM_AIRFOIL:

                    if not required_custom_keys.issubset(foil_data):

                        failed_foils.append(name)

                        continue
                
                foil_color = foil_data["color"]

                hidden = foil_data.get("hidden", True)

                re_start = foil_data.get("reynolds_num_start", standards.DEFAULT_RE_START)

                re_stop = foil_data.get("reynolds_num_stop", standards.DEFAULT_RE_STOP)
                
                re_step = foil_data.get("reynolds_num_step", standards.DEFAULT_RE_STEP)

                alpha_start = foil_data.get("alpha_num_start", standards.DEFAULT_START_ALPHA)

                alpha_stop = foil_data.get("alpha_num_stop", standards.DEFAULT_STOP_ALPHA)

                alpha_step = foil_data.get("alpha_num_step", standards.DEFAULT_STEP_ALPHA)

                airfoil = ""


                if foil_type == standards.NACA_4_AIRFOIL:

                    naca_num = name.split()[1]

                    airfoil = NACA_4_Standard_AirFoil(naca_num, re_start, re_stop, re_step, foil_color, alpha_start, alpha_stop, alpha_step)

                elif foil_type == standards.NACA_5_AIRFOIL:

                    naca_num = name.split()[1]

                    airfoil = NACA_5_Standard_Airfoil(naca_num, re_start, re_stop, re_step, foil_color, alpha_start, alpha_stop, alpha_step)

                elif foil_type == standards.CUSTOM_AIRFOIL:

                    airfoil = AirFoil(name, re_start, re_stop, re_step, foil_color, alpha_start, alpha_stop, alpha_step)

                    airfoil.set_coordinates(np.array(foil_data["xu"]), np.array(foil_data["yu"]), np.array(foil_data["xl"]), np.array(foil_data["yl"]))

                foils.append(airfoil)

                visibility_data.append(hidden)


            if failed_foils:

                msg = QMessageBox.question(self, "Some Foils Failed To Load", f"We couldn’t load some airfoils because essential data was missing:{failed_foils}. \nThe rest were loaded successfully, with default values filled in where needed. \nDo you want to continue?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                if msg == QMessageBox.StandardButton.No:

                    return
            
            else:

                msg = QMessageBox.question(self, "Foils Loaded", f"The airfoils were loaded successfully. \nAirfoils with non critical missing data were filled with default values wherever needed. \nDo you want to continue?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                if msg == QMessageBox.StandardButton.No:

                    return
            
            window = AnalysisWindow((foils, visibility_data))

            self.windows.append(window)

            window.showMaximized()
            
            
        
            
        

            


                

            




                    
        
            





    def revert_all_plots(self) -> None:

        self.cl_a_plot.toolbar.home()

        self.cd_a_plot.toolbar.home()

        self.cd_cl_plot.toolbar.home()

        self.cm_a_plot.toolbar.home()

        self.foil_plot.toolbar.home()


    def set_alpha_bounds(self, card: AirfoilCard | None) -> None:

        if len(self.left_panel.cards) == 0:

            msg = QMessageBox(self)

            msg.setIcon(QMessageBox.Icon.Critical)

            msg.setWindowTitle("No Airfoils")

            msg.setText("Add an airfoil to modify the alpha parameters")

            msg.exec()

            return



        if not isinstance(card, AirfoilCard):

            card = None

        dialog = UpdateAlphaBounds(self.left_panel.cards, card)

        if dialog.exec():

            update_info: tuple[int, tuple[float, float, float]] = dialog.update_info

            old_foil_data = self.left_panel.cards[update_info[0]].foil_data

            new_foil_data = copy.deepcopy(old_foil_data)

            new_foil_data.alpha_num_start = update_info[1][0]

            new_foil_data.alpha_num_stop = update_info[1][1]

            new_foil_data.alpha_num_step = update_info[1][2]

            self.update_airfoil((new_foil_data, old_foil_data, update_info[0]), True)




    def add_task_done(self, result: tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], str, AirFoil]) -> None:

        xu, yu, xl, yl, foil_data_path, data = result

        alpha, cl, cd, cm, failed_Re = [], [], [], [], []

        for re in range(int(data.reynolds_num_start), int(data.reynolds_num_stop + 1), int(data.reynolds_num_step)):

            file_path = (Path(__file__).parent / "../" / f"polar{re}.txt").resolve()

            alpha_i, cl_i, cd_i, cm_i = DataUtils.parse_file(str(file_path))

            alpha.append(alpha_i)

            cd.append(cd_i)

            cl.append(cl_i)

            cm.append(cm_i)

            file_path.unlink()

        
        QApplication.restoreOverrideCursor()


        with open("incomplete_runs.txt", "r") as file:

            lines = file.readlines()

            for line in lines:

                failed_Re.append(float(line))


            if failed_Re:

                msg = QMessageBox(self)

                msg.setIcon(QMessageBox.Icon.Critical)

                msg.setWindowTitle("Convergence Failure")

                msg.setText(f"Analysis at certain reynold's numbers exceeded the convergence limit. These values are plotted till their convergence. The following reynold's numbers caused convergence issues: {failed_Re}")

                msg.exec()

        file.close()

        (Path(__file__).parent / "../" / "incomplete_runs.txt").resolve().unlink()

        self.cl_a_plot.add_plot(PlotBlock(alpha, cl), data.color, data.name, "Alpha (°)", "Cl", "Cl vs. Alpha")
        self.cd_a_plot.add_plot(PlotBlock(alpha, cd), data.color, data.name, "Alpha (°)", "Cd", "Cd vs. Alpha")
        self.cm_a_plot.add_plot(PlotBlock(alpha, cm), data.color, data.name, "Alpha (°)", "Cm", "Cm vs. Alpha")
        self.cd_cl_plot.add_plot(PlotBlock(cd, cl), data.color, data.name, "Cd", "Cl", "Cl vs. Cd")

        x = np.concatenate((xu, xl[::-1]))

        y = np.concatenate((yu, yl[::-1]))

        self.foil_plot.add_plot(PlotBlock([x], [y]), data.color, title = "Foil shape", equal_aspect=True, name = data.name)

        self.progress_dialog.accept()

        if data.is_standard_foil():

            Path(foil_data_path).unlink()



    def task_error(self, data: AirFoil) -> None:

        print(data)



    def update_task_done(self, result: tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]) -> None:

        
        i = self.airfoil_update_queue.popleft()


        xu, yu, xl, yl, foil_data_path, data = result

        alpha, cl, cd, cm, failed_Re = [], [], [], [], []

        for re in range(int(data.reynolds_num_start), int(data.reynolds_num_stop + 1), int(data.reynolds_num_step)):

            file_path = (Path(__file__).parent / "../" / f"polar{re}.txt").resolve()

            alpha_i, cl_i, cd_i, cm_i = DataUtils.parse_file(str(file_path))

            alpha.append(alpha_i)

            cd.append(cd_i)

            cl.append(cl_i)

            cm.append(cm_i)

            file_path.unlink()

        
        QApplication.restoreOverrideCursor()


        with open("incomplete_runs.txt", "r") as file:

            lines = file.readlines()

            for line in lines:

                failed_Re.append(float(line))


            if failed_Re:

                msg = QMessageBox(self)

                msg.setIcon(QMessageBox.Icon.Critical)

                msg.setWindowTitle("Convergence Failure")

                msg.setText(f"Analysis at certain reynold's numbers exceeded the convergence limit. These values are plotted till their convergence. The following reynold's numbers caused convergence issues: {failed_Re}")

                msg.exec()

        file.close()

        (Path(__file__).parent / "../" / "incomplete_runs.txt").resolve().unlink()

        self.cl_a_plot.update_plot(i, PlotBlock(alpha, cl), data.color, data.name)
        self.cd_a_plot.update_plot(i, PlotBlock(alpha, cd), data.color, data.name)
        self.cm_a_plot.update_plot(i, PlotBlock(alpha, cm), data.color, data.name)
        self.cd_cl_plot.update_plot(i, PlotBlock(cd, cl), data.color, data.name)

        x = np.concatenate((xu, xl[::-1]))

        y = np.concatenate((yu, yl[::-1]))

        self.foil_plot.update_plot(i, PlotBlock([x], [y]), data.color, equal_aspect=True, name = data.name)

        self.progress_dialog.accept()


        if Path(foil_data_path).exists():

            Path(foil_data_path).unlink()

    def cleanup_thread_refs(self):

        self.adding_airfoil = False

        self.analysis_thread = None
        self.analysis_worker = None

        self.airfoil_addition_queue_flush()
    






            
        

 

    

if __name__ == "__main__":

    app = QApplication(sys.argv)

    app.setWindowIcon(QtGui.QIcon(str((Path(__file__).parent / "../" / "resources/app_icon.png").resolve())))

    window = AnalysisWindow()

    window.showMaximized()

    sys.exit(app.exec())



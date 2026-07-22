
# --- Imports for ploting ---
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from matplotlib.backends.backend_qt import NavigationToolbar2QT

from matplotlib.backend_bases import FigureManagerBase

from matplotlib.figure import Figure


# --- Imports for GUI ---
from PyQt6.QtWidgets import (
    QDialog, QMenu, QMessageBox, QProgressBar, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QPushButton, QLabel
)

from PyQt6.QtCore import QSize, Qt, pyqtSignal

from PyQt6.QtGui import QPainterPath, QRegion

from PyQt6.QtCore import QRectF

from PyQt6.QtGui import QPainter


# --- Imports for GUI (custom dialogs) ---
from foil_data import NACA_4_Standard_AirFoil, AirFoil, NACA_5_Standard_Airfoil

from update_ui import UpdateNACA4StandardFoil, UpdateCustomFoil, UpdateNACA5StandardFoil


# --- Imports for models ---
from support_models import PlotData, PlotBlock


# --- Imports for type annotations ---
from typing import cast, TYPE_CHECKING

if TYPE_CHECKING: # To prevent circular imports

    from app_ui import AnalysisWindow


# --- Import for copy ---
import copy


""" Project Widgets

This module has all the widgets used by the tool.

"""




class AirfoilCard(QFrame):

    """
    
    Represents an airfoil card,.

    Stores metadata and UI elements associated with an airfoil, such as its plotting color, visibility state, and controls for 
    editing its parameters.

    Attributes:
        foil_data (AirFoil): The information about the airfoil.
        name (str): The name of the airfoil.
        color (str): The hex code of the color used to plot the airfoil.
        hidden (bool): Whether the foil is hidden. It is False on initially.
        airfoil_updated (pyqtSignal): The signal emitted when the airfoil is updated.
        airfoil_visibility_toggle (pyqtSignal): The signal emitted when the visibility of the airfoil changes.
        color_preview (QFrame): The QFrame displaying the chosen color for plotting.
        label (QLabel): The QLabel displaying the name of the airfoil.
        edit_btn (QPushButton): The button allowing the user to edit the airfoil parameters.

    """

    airfoil_updated = pyqtSignal(object)

    airfoil_visibility_toggle = pyqtSignal(object)


    def __init__(self, foil_data: AirFoil):

        """
        
        Initializes an AirfoilCard.

        Args:
            foil_data (AirFoil): The imformation about the foil the card represents
        
        """

        super().__init__()

        self.foil_data: AirFoil = foil_data

        self.name: str = foil_data.name

        self.color: str = foil_data.color

        self.hidden: bool = False

        self.setFixedHeight(60)

        self.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 30, 0.55);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.10);
            }
        """)

        layout: QHBoxLayout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)


        self.color_preview: QFrame = QFrame()
        self.color_preview.setFixedSize(15, 15)
        self.color_preview.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border-radius: 7px;
            }}
        """)

        self.label: QLabel = QLabel(self.name)
        self.label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)

        self.edit_btn: QPushButton = QPushButton("EDIT")
        self.edit_btn.setFixedWidth(60)

        self.edit_btn.setFixedHeight(35)
        self.edit_btn.setStyleSheet("""

            QPushButton {


                border-radius: 10px;    
                font-weight: bold; 
                background-color: black;      
                               
                               
            }
                               

        """)

        self.edit_btn.clicked.connect(self.edit_airfoil)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.color_preview)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.edit_btn)



    def edit_airfoil(self) -> None:

        """
        
        The action triggered if the user clicks on the edit button. Displays a dialog depending on the airfoil and emits the
        airfoil_updated signal.

        Returns:
            None
        
        """

        foil_data = copy.deepcopy(self.foil_data)

        if isinstance(foil_data, NACA_4_Standard_AirFoil):

            dialog: UpdateNACA4StandardFoil | UpdateNACA5StandardFoil | UpdateCustomFoil = UpdateNACA4StandardFoil(foil_data)

        elif isinstance(foil_data, NACA_5_Standard_Airfoil):

            dialog = UpdateNACA5StandardFoil(foil_data)

        else:

            dialog = UpdateCustomFoil(foil_data)



        if dialog.exec():

                updated_data = dialog.foil_data

                name_available, color_available = cast("AnalysisWindow", self.window()).left_panel.is_name_color_available(updated_data.name, updated_data.color, self.name, self.color)

                if not name_available:

                    msg = QMessageBox(self)

                    msg.setIcon(QMessageBox.Icon.Critical)

                    msg.setWindowTitle("Duplicate Airfoil")

                    msg.setText("An airfoil with this name already exists. Please choose a different name.")

                    msg.exec()

                    return
        
                elif not color_available:
            
                    res: QMessageBox.StandardButton = QMessageBox.question(self, "Duplicate Colour", "An airfoil with this color already exists and may be difficult to distinguish on the plots. Do you want to keep it like this?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

                    if res == QMessageBox.StandardButton.Yes:

                        pass
            
                    else:

                        return

                self.color_preview.setStyleSheet(f"""
                    QFrame {{
                    background-color: {updated_data.color};
                    border-radius: 7px;
                }}
                """)

                self.label.setText(updated_data.name)

                # type: ignore[attr-defined]
                self.airfoil_updated.emit((updated_data, self.foil_data))


        





    def delete_card(self) -> None:

        """
        
        The mothod to remove a card. Calls the remove method in the left panel.

        Returns:
            None
        
        """

        cast("AnalysisWindow", self.window()).left_panel.remove_card(self)

    
    def toggle_visibility(self, value: bool|None = None) -> None:

        """
        
        Toggles the visibility of the airfoil. If value is passed, then the hidden attribute value is set to it, otherwise it 
        inverts the current visibility. Emits the airfoil_visibility_toggle signal if called without a passed value or if it 
        is None.

        Args:
            value (bool | None): The value for the hidden attribute. Inverts the attribute if None (default).

        Returns:
            None
        
        """

        if value == None:

            self.hidden = not self.hidden

        else:

            self.hidden = value


        if self.hidden:

            self.setStyleSheet("""

                QFrame {
                    background-color: rgba(15, 15, 15, 0.18);
                    border-radius: 12px;
                    font-weight: bold;
                    border: 1px solid rgba(255, 255, 255, 0.02);
                }
                               
            """)

            self.edit_btn.setStyleSheet("""

                QPushButton {
                    border-radius: 10px;
                    font-weight: bold;

                    background-color: rgba(15, 15, 15, 0.18);
                    color: rgba(255, 255, 255, 0.35);

                    border: 1px solid rgba(255, 255, 255, 0.03);
                }


            """)

            self.label.setStyleSheet("""

                QLabel {
                    color: rgba(255, 255, 255, 0.32);
                    background: transparent;

                    font-size: 14px;
                    font-weight: bold;
                }


            """)

            

        else:

            self.setStyleSheet("""
                               
                QFrame {
                    background-color: rgba(30, 30, 30, 0.55);
                    border-radius: 12px;
                    border: 1px solid rgba(255, 255, 255, 0.10);
                }
                               
            """)

            self.edit_btn.setStyleSheet("""

                QPushButton {


                    border-radius: 10px;    
                    font-weight: bold; 
                    background-color: black;      
                               
                               
                }
                               

            """)

            self.label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
            
        if value == None:

            self.airfoil_visibility_toggle.emit(copy.deepcopy(self.foil_data))


    def show_context_menu(self, pos) -> None:

        """
        
        Displays the context menu when right clicking an airfoil card.

        Returns:
            None

        
        """

        menu = QMenu(self)

        menu.setStyleSheet("""
    
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

        delete_action = menu.addAction("Delete")

        modify_alpha_action = menu.addAction("Modify Alpha Bounds")


        if self.hidden:

            toggle_visibility_action = menu.addAction("Show")

        else:

            toggle_visibility_action = menu.addAction("Hide")

        action = menu.exec(self.mapToGlobal(pos))
        

        if action == delete_action:

            self.delete_card()

        elif action == toggle_visibility_action:

            self.toggle_visibility()

        elif action == modify_alpha_action:

            cast("AnalysisWindow", self.window()).set_alpha_bounds(self)


class VerticalLabel(QLabel):

    """
    
    The label used to display text vertically. Used for the y axis of PlotWidget.
    
    """

    def paintEvent(self, event) -> None:

        painter = QPainter(self)

        painter.translate(0, self.height())

        painter.rotate(-90)

        painter.drawText(
            0,
            0,
            self.height(),
            self.width(),
            Qt.AlignmentFlag.AlignCenter,
            self.text()
        )

    def minimumSizeHint(self) -> QSize:

        size = super().minimumSizeHint()

        return size.transposed()

    def sizeHint(self) -> QSize:

        size = super().sizeHint()

        return size.transposed()
    




class RoundedCanvas(FigureCanvasQTAgg):

    """
    
    The rounded canvas used to display the plot.

    """

    def resizeEvent(self, event) -> None:

        super().resizeEvent(event)

        path = QPainterPath()

        path.addRoundedRect(QRectF(self.rect()), 14, 14)

        region = QRegion(path.toFillPolygon().toPolygon())

        self.setMask(region)


class PlotWidget(QWidget):

    """
    
    The widget that does all the plotting.
    
    """

    def __init__(self, title: str, xlabel: str, ylabel: str):
        super().__init__()

        main_layout = QVBoxLayout(self)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label_style: str = """
            QLabel {
                color: rgba(255, 255, 255, 0.88);
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.10);
                border-radius: 6px;

                font-size: 11px;
                font-weight: bold;

                padding: 2px 6px;

                margin: 1px;
            }
        """

        title_label.setStyleSheet(label_style)

        plot_layout = QHBoxLayout()

        ylabel_label = VerticalLabel(ylabel)

        ylabel_label.setStyleSheet(label_style)

        ylabel_label.setFixedWidth(20)

        self.figure = Figure(facecolor="none")

        canvas_container = QFrame()

        canvas_container.setStyleSheet("""
            QFrame {
                background-color: #20252B;
                border-radius: 14px;
                border: 1px solid rgba(255,255,255,0.08);
            }
        """)

        canvas_container_layout = QVBoxLayout(canvas_container)
        canvas_container_layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = RoundedCanvas(self.figure)

        canvas_container_layout.addWidget(self.canvas)

        canvas_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        plot_layout.addWidget(ylabel_label)

        plot_layout.addWidget(canvas_container)

        xlabel_label = QLabel(xlabel)

        xlabel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        xlabel_label.setStyleSheet(label_style)

        main_layout.addWidget(title_label)
        main_layout.addLayout(plot_layout)
        main_layout.addWidget(xlabel_label)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.customContextMenuRequested.connect(self.show_context_menu)

        self.plot_data = PlotData()

        self.ax = self.figure.add_subplot(111)

        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.toolbar.hide()

        self.figure.patch.set_facecolor("#20252B")

        self.figure.patch.set_alpha(0)

        self.ax.set_facecolor("#20252B")

        self.ax.tick_params(colors="white")

        self.has_data = False

    def clear_plot(self) -> None:

        """
        
        Clears the plot widget, removing all current plots.
        
        """

        self.ax.clear()

        self.ax.set_facecolor("#20252B")

        self.ax.tick_params(colors="white")


    def add_plot(self, plot_block: PlotBlock, color: str, name: str="", xtitle:str ="", ytitle: str="", title: str="", equal_aspect: bool =False) -> None:


        """
        
        Adds a plot to the plot widget.

        Args:
            plot_block (PlotBlock): The plotting data for the airfoil. If the airfoil plot has multiple reynold's numbers, then the plotting data for each reynold's number should be in this block.
            color (str): The color used to plot the airfoil.
            name (str): The name of the airfoil.
            xtitle (str): The title for the x axis.
            ytitle (str): The title for the y axis.
            title (str): The main title for the plot.
            equal_aspect (bool): Whether the plot should do equal scaling for both x and y axes.

        Returns:
            None
        
        """

        self.plot_data.colors.append(color)
        self.plot_data.legend.append(name)
        self.plot_data.xtitle = xtitle
        self.plot_data.ytitle = ytitle
        self.plot_data.title = title
        self.plot_data.equal_aspect = equal_aspect

        for i in range(len(plot_block.xplots)):

            line, = self.ax.plot(plot_block.xplots[i], plot_block.yplots[i], color = color)

            plot_block.lines.append(line)


        self.plot_data.plot_blocks.append(plot_block)

        self.ax.axhline(0, color="gray", linewidth=0.8)

        self.ax.axvline(0, color="gray", linewidth=0.8)

        self.ax.grid(True, alpha=0.2)

        if equal_aspect:

            self.ax.set_aspect('equal', adjustable='datalim')

        self.toolbar.home()

        self.ax.relim()
        self.ax.autoscale_view()

        self.toolbar.update()

        self.canvas.draw_idle()

        if not self.has_data:

            self.toolbar.pan()

            self.has_data = True


    def update_plot(self, pos: int, plot_block: PlotBlock, color: str, name: str="", equal_aspect: bool = False) -> None:

        """
        
        Updates the plot widget with the new plotting data. Do not use this to update only the color.

        Args:
            pos (int): The index of the plotting data to update.
            plot_block (PlotBlock): The new plotting data.
            color (str): The new color.
            name (str): The name of the airfoil.
            equal_aspect (bool): Whether to plot with equal scaling in x and y axes.
        
        Returns:
            None
        
        """

        old_lines = self.plot_data.plot_blocks[pos].lines

        old_is_hidden = self.plot_data.plot_blocks[pos].hidden

        plot_block.hidden = old_is_hidden

        self.plot_data.colors[pos] = color
        self.plot_data.legend[pos] = name

        self.plot_data.equal_aspect = equal_aspect

        for line in old_lines:

            line.remove()

        for i in range(len(plot_block.xplots)):

            line, = self.ax.plot(plot_block.xplots[i], plot_block.yplots[i], color = color)

            plot_block.lines.append(line)

            line.set_visible(not old_is_hidden)

        self.plot_data.plot_blocks[pos] = plot_block



        if equal_aspect:

            self.ax.set_aspect('equal', adjustable='datalim')

        self.toolbar.home()

        self.ax.relim()
        self.ax.autoscale_view()

        self.toolbar.update()

        self.canvas.draw_idle()


    def remove_plot(self, pos: int) -> None:

        """

        Removes the plot at the given index.

        Args:
            pos (int): The index of the plot to be removed.

        Returns:
            None
        
        """

        plot_block = self.plot_data.plot_blocks.pop(pos)

        self.plot_data.colors.pop(pos)

        self.plot_data.legend.pop(pos)

        old_lines = plot_block.lines

        for line in old_lines:

            line.remove()

        self.toolbar.home()

        self.ax.relim()
        self.ax.autoscale_view()

        self.toolbar.update()

        self.canvas.draw_idle()

    
    def toggle_visibility_plot(self, pos: int, value: bool|None = None) -> None:

        """
        
        Toggles the visibility of the plot at a given position.

        Args:
            pos (int): The index of the plot to be removed.
            value (bool | None): The visibility of the plot. True is visible and False is hidden. If None, inverts the current visibility.

        Returns:
            None
        
        """

        plot_block = self.plot_data.plot_blocks[pos]

        hidden = not value if value != None else plot_block.hidden

        lines = plot_block.lines

        for line in lines:

            line.set_visible(hidden)

        if value == None:

            self.plot_data.plot_blocks[pos].hidden = not hidden


        else:

            self.plot_data.plot_blocks[pos].hidden = value



        self.toolbar.home()


        self.canvas.draw_idle()



    def show_context_menu(self, pos) -> None:

        """
        
        The context menu displayed when the user right clicks the plot.

        Returns:
            None

        """

        menu = QMenu(self)

        menu.setStyleSheet("""
    
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

        view_action = menu.addAction("View")

        original_zoom_action = menu.addAction("Revert to original")

        action = menu.exec(self.mapToGlobal(pos))

        if action == view_action:

            self.open_full_plot()

        elif action == original_zoom_action:

            self.toolbar.home()



    def open_full_plot(self) -> None:

        """
        
        Opens a matplotlib dialog to view the plot on a larger window.

        Returns:
            None
        
        """

        if self.plot_data.plot_blocks == []:
            return

        plt.figure(figsize=(10, 6), facecolor="#20252B")


        for plot_blocks, color, legend in zip(self.plot_data.plot_blocks, self.plot_data.colors, self.plot_data.legend):


            for i in range(len(plot_blocks.xplots)):

                if i == 0:

                    plt.plot(
                    plot_blocks.xplots[i],
                    plot_blocks.yplots[i],
                    color=color,
                    linewidth=2,
                    label = legend
                    )

                else:


                    plt.plot(
                        plot_blocks.xplots[i],
                        plot_blocks.yplots[i],
                        color=color,
                        linewidth=2
                    )

        plt.xlabel(self.plot_data.xtitle, color="white")

        plt.ylabel(self.plot_data.ytitle, color="white")

        plt.title(self.plot_data.title, color="white")

        cast(FigureManagerBase, plt.gcf().canvas.manager).set_window_title(f"Expanded View - {self.plot_data.title}")

        if self.plot_data.equal_aspect:

            plt.gca().set_aspect('equal', adjustable='datalim')

        plt.axhline(0, color="gray", linewidth=0.8)

        plt.axvline(0, color="gray", linewidth=0.8)

        plt.tick_params(colors="white")

        plt.gca().set_facecolor("#20252B")

        plt.grid(True)

        plt.legend()

        plt.show()


    def update_only_color(self, pos: int, color: str) -> None:

        """
        
        Updates only the color of the plot at the given index and does not redraw all the lines.

        Args:
            pos (int): The index of the plot to change.
            color (str): The new color to use.

        Returns:
            None
        
        """

        old_lines = self.plot_data.plot_blocks[pos].lines

        old_is_hidden = self.plot_data.plot_blocks[pos].hidden

        self.plot_data.colors[pos] = color

        plot_block = self.plot_data.plot_blocks[pos]

        for line in old_lines:

            line.remove()

        plot_block.lines = []

        for i in range(len(plot_block.xplots)):

            line, = self.ax.plot(plot_block.xplots[i], plot_block.yplots[i], color = color)

            plot_block.lines.append(line)

            line.set_visible(not old_is_hidden)

        plot_block.hidden = old_is_hidden

        self.plot_data.plot_blocks[pos] = plot_block

        self.canvas.draw()

        


class ProgressDialog(QDialog):

    """
    
    The progress dialog displayed when the analysis tool is doing a heavy task on another thread.
    
    """
    
    def __init__(self, total: int):
        
        """
        
        Initializes the ProgressDialog with a given total.

        Args:
            total (int): The total used to display progress against.

        """

        super().__init__()

        self.total: int = total
        self.current: int = 0

        self.setWindowTitle("Processing...")
        self.setFixedSize(300, 120)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        layout = QVBoxLayout(self)

        self.label = QLabel(f"0/{self.total} completed")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.bar = QProgressBar()
        self.bar.setRange(0, self.total)
        self.bar.setValue(0)

        layout.addWidget(self.label)
        layout.addWidget(self.bar)

    def update_progress(self, value: int) -> None:
        self.bar.setValue(value)
        self.label.setText(f"{value}/{self.total} completed")


class MetaProgressDialog(QDialog):

    """
    
    This is used for imports, when tasks have multiple subtasks and the progress must be displayed. This hasn't been implemented
    yet.

    """
    
    def __init__(self, total: int, airfoil_total: int, curr_name: str):

        super().__init__()

        self.total: int = total
        self.current: int = 0

        self.airfoil_progress_total: int = airfoil_total

        self.setWindowTitle("Processing...")
        self.setFixedSize(300, 120)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        layout = QVBoxLayout(self)

        self.name_label = QLabel(f"Loading {curr_name}")

        self.airfoil_progress_label = QLabel(f"0/{self.airfoil_progress_total} airfoils loaded")

        self.label = QLabel(f"0/{self.total} completed")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.bar = QProgressBar()
        self.bar.setRange(0, self.total)
        self.bar.setValue(0)

        layout.addWidget(self.name_label)

        layout.addWidget(self.airfoil_progress_label)

        layout.addWidget(self.label)
        layout.addWidget(self.bar)

        raise NotImplementedError("MetaProgressDialog hasn't been implemented yet")

    def update_progress(self, value: int) -> None:
        self.bar.setValue(value)
        self.label.setText(f"{value}/{self.total} completed")
                
        raise NotImplementedError("MetaProgressDialog hasn't been implemented yet")

        

    def airfoil_done(self, airfoil_value: int, total: int, name: str) -> None:

        self.bar.setRange(0, self.total)

        self.bar.setValue(0)

        self.total = total

        self.name_label.setText(f"Loading {name}")

        self.label.setText(f"0/{self.total} completed")

        self.airfoil_progress_label.setText(f"{airfoil_value}/{self.airfoil_progress_total} airfoils loaded")

        raise NotImplementedError("MetaProgressDialog hasn't been implemented yet")

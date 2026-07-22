from PyQt6.QtCore import QObject, pyqtSignal
import numpy as np


from typing import Callable, Any

from numpy.typing import NDArray

from matplotlib.lines import Line2D

import math






class Worker(QObject):


    finished = pyqtSignal(object)

    error = pyqtSignal(str)

    progress = pyqtSignal(int)

    def __init__(self, func: Callable[..., Any], *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):

        try:

            result = self.func(*self.args, callback_func = self.progress.emit, **self.kwargs)

           

            self.finished.emit(result)



        except Exception as e:

            self.error.emit(str(e))

class PlotBlock:

    def __init__(self, xplots: list[NDArray[np.float64]], yplots: list[NDArray[np.float64]]):

        self.xplots: list[NDArray[np.float64]] = xplots

        self.yplots: list[NDArray[np.float64]] = yplots

        self.lines: list[Line2D] = []

        self.hidden: bool = False


class PlotData:

    def __init__(self):

        self.plot_blocks: list[PlotBlock] = []

        self.xtitle: str = ""

        self.ytitle: str = ""

        self.title: str = ""

        self.colors: list[str] = []

        self.legend: list[str] = []

        self.equal_aspect: bool = False



class Freestream:

    def __init__(self, velocity: float, alpha_deg: float):

        self.velocity = velocity

        self.alpha_rad = np.radians(alpha_deg)

        self.u = velocity * math.cos(self.alpha_rad)

        self.v = velocity * math.sin(self.alpha_rad)





class Panel:

    def __init__(self, p1: tuple[float, float], p2: tuple[float, float]):

        self.x1, self.y1 = p1

        self.x2, self.y2 = p2

        self.xc = (self.x1 + self.x2) / 2

        self.yc = (self.y1 + self.y2) / 2

        self.tx = self.x2 - self.x1

        self.ty = self.y2 - self.y1

        self.length = (self.tx**2 + self.ty**2) ** 0.5

        self.tx /= self.length

        self.ty /= self.length

        self.nx = (- self.ty)

        self.ny = self.tx

        self.angle = math.atan2(self.ty, self.tx)

        self.ds = ds = np.sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)


    def normal_velocity(self, freestream: Freestream) -> float:

        return (self.nx * freestream.u + self.ny * freestream.v)




        
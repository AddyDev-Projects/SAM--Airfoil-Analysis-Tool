import numpy as np

from numpy.typing import NDArray

import subprocess

from pathlib import Path

from typing import Callable, Any

import standards

class FoilUtils:

    @staticmethod
    def generate_naca_4_foil_data(naca_num: str) -> tuple[float, float, float]:

        if len(naca_num) != 4 or not naca_num.isdigit():

            raise ValueError("Invalid NACA number")
        
        m = int(naca_num[0]) / 100

        p = int(naca_num[1]) / 10

        t = int(naca_num[2:]) / 100

        return m, p, t
    


    @staticmethod
    def generate_naca_5_foil_data(naca_num: str) -> tuple[bool, float, float, float, float]:

        if len(naca_num) != 5 or not naca_num.isdigit():
            raise ValueError("Invalid NACA 5-digit number")

        p_digit = int(naca_num[1])

        reflex_digit = int(naca_num[2])

        t = int(naca_num[3:]) / 100

        is_reflex = reflex_digit == 1

        NACA5_NORMAL = {
        1: (0.0580, 361.4),
        2: (0.1260, 51.64),
        3: (0.2025, 15.957),
        4: (0.2900, 6.643),
        5: (0.3910, 3.230),
        }

        NACA5_REFLEX = {
        1: (0.1300, 51.99, 0.000764),
        2: (0.2170, 15.793, 0.00677),
        3: (0.3180, 6.520, 0.0303),
        4: (0.4410, 3.191, 0.1355),
        5: (0.5600, 1.939, 0.4370),
        }

        if is_reflex:

            if p_digit not in NACA5_REFLEX:
                raise ValueError("Unsupported reflex NACA 5 foil")

            m, k1, k2k1 = NACA5_REFLEX[p_digit]

        else:

            if p_digit not in NACA5_NORMAL:
                raise ValueError("Unsupported NACA 5 foil")

            m, k1 = NACA5_NORMAL[p_digit]

            k2k1 = 0.0

        return is_reflex, m, k1, k2k1, t


    


    @staticmethod
    def generate_x(num : int = 100) -> NDArray[np.float64]:

        b = np.linspace(0, np.pi, num)

        x = (1 - np.cos(b)) / 2

        return x
    

    @staticmethod
    def generate_thickness(x: NDArray[np.float64], t: float) -> NDArray[np.float64]:

        return 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
    

    @staticmethod
    def camber_line_naca_4(x: NDArray[np.float64], m: float, p: float) -> NDArray[np.float64]:

        zc = np.zeros_like(x)

        for i in range(len(x)):

            if x[i] < p:

                zc[i] = (m / p**2) * (2*p*x[i] - x[i]**2)

            else:

                zc[i] = (m / (1 - p)**2) * ((1 - 2*p) + 2*p*x[i] - x[i]**2)

        return zc
    


    @staticmethod
    def camber_slope_naca_4(x: NDArray[np.float64], m: float, p: float) -> NDArray[np.float64]:

        dzdx = np.zeros_like(x)

        for i in range(len(x)):

            if x[i] < p:

                dzdx[i] = (2*m / p**2) * (p - x[i])

            else:

                dzdx[i] = (2*m / (1 - p)**2) * (p - x[i])


        return dzdx
    

    @staticmethod
    def camber_line_naca_5(x: NDArray[np.float64], m: float, k1: float, reflex: bool = False, k2k1: float = 0.0) -> NDArray[np.float64]:

        zc = np.zeros_like(x)

        for i in range(len(x)):

            if not reflex:

                if x[i] < m:

                    zc[i] = (k1 / 6) * (
                        x[i]**3
                        - 3*m*x[i]**2
                        + m**2 * (3 - m) * x[i]
                    )

                else:

                    zc[i] = (k1 / 6) * m**3 * (1 - x[i])

            else:

                if x[i] < m:

                    zc[i] = (k1 / 6) * (
                        (x[i] - m)**3
                        - k2k1 * (1 - m)**3 * x[i]
                        - m**3 * x[i]
                        + m**3
                    )

                else:

                    zc[i] = (k1 / 6) * (
                        k2k1 * (x[i] - m)**3
                        - k2k1 * (1 - m)**3 * x[i]
                        - m**3 * x[i]
                        + m**3
                    )

        return zc
    

    @staticmethod
    def camber_slope_naca_5(x: NDArray[np.float64], m: float, k1: float, reflex: bool = False, k2k1: float = 0.0) -> NDArray[np.float64]:

        dzdx = np.zeros_like(x)

        for i in range(len(x)):

            if not reflex:

                if x[i] < m:

                    dzdx[i] = (k1 / 6) * (
                        3*x[i]**2
                        - 6*m*x[i]
                        + m**2 * (3 - m)
                    )

                else:

                    dzdx[i] = -(k1 / 6) * m**3

            else:

                if x[i] < m:

                    dzdx[i] = (k1 / 6) * (
                        3*(x[i] - m)**2
                        - k2k1 * (1 - m)**3
                        - m**3
                    )

                else:

                    dzdx[i] = (k1 / 6) * (
                        3*k2k1*(x[i] - m)**2
                        - k2k1 * (1 - m)**3
                        - m**3
                    )

        return dzdx


    
    @staticmethod
    def airfoil_coordinates(x: NDArray[np.float64], yt: NDArray[np.float64], zc: NDArray[np.float64], dzdx: NDArray[np.float64]) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:

        theta = np.arctan(dzdx)

        xu = x - yt * np.sin(theta)

        yu = zc + yt * np.cos(theta)

        xl = x + yt * np.sin(theta)

        yl = zc - yt * np.cos(theta)

        xu = np.clip(xu, 0, 1)

        xl = np.clip(xl, 0, 1)

        return xu, yu, xl, yl
    

    @staticmethod
    def load_airfoil_dat(file_path: str) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:

        coords_list = []

        with open(file_path, "r") as file:

            lines = file.readlines()[1:] 

            for line in lines:

                parts = line.strip().split()

                if len(parts) != 2:
                    continue

                x_1, y_1 = map(float, parts)

                coords_list.append((x_1, y_1))

        coords: NDArray[np.float64] = np.array(coords_list)

        x: NDArray[np.float64] = coords[:, 0]
        y: NDArray[np.float64] = coords[:, 1]

    
        le_index = np.argmin(x)

    
        xu: NDArray[np.float64] = x[:le_index + 1]
        yu: NDArray[np.float64] = y[:le_index + 1]

    
        xl: NDArray[np.float64] = x[le_index:]
        yl: NDArray[np.float64] = y[le_index:]

    
        xu = xu[::-1]
        yu = yu[::-1]

        return xu, yu, xl, yl
    
    @staticmethod
    def save_airfoil(filename: str, xu: NDArray[np.float64], yu: NDArray[np.float64], xl: NDArray[np.float64], yl: NDArray[np.float64]) -> Path:

        with open(filename, "w") as file:

            file.write(filename + "\n")

            for i in range(len(xu) - 1, -1, -1):

                file.write(f"{xu[i]:.6f} {yu[i]:.6f}\n")

            for i in range(1, len(xl)):

                file.write(f"{xl[i]:.6f} {yl[i]:.6f}\n")

        file.close()

        return (Path(__file__).parent / "../" / filename).resolve()


    @staticmethod
    def run_xfoil(dat_file: str, Re: int = 100000, start_alpha: int = -5, end_alpha: int = 15, step_alpha: int = 1) -> None|str:

        commands = f"""
LOAD {dat_file}
PANE
OPER
VISC {Re}
ITER 100
PACC
polar{Re}.txt

ASEQ {start_alpha} {end_alpha} {step_alpha}
QUIT
"""
    
        try:

            startupinfo = subprocess.STARTUPINFO()

            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        
            process = subprocess.Popen("xfoil", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, startupinfo=startupinfo)

            output, error = process.communicate(input=commands, timeout=10)

            return output
    
    
        except subprocess.TimeoutExpired:

            print(f"XFOIL failed for Reynolds number: {Re}")

            return None
        


    @staticmethod
    def clean() -> None:

        folder = (Path(__file__).parent / "../").resolve()

        for file in folder.glob("polar*.txt"):

            if file.exists():

                file.unlink()

        for file in folder.glob("naca*.dat"):

            if file.exists():

                file.unlink()

        file = (Path(__file__).parent / "../" / "incomplete_runs.txt").resolve()

        if file.exists():

            file.unlink()

    @staticmethod
    def check_naca_5(naca_num: str) -> bool:

        try:

            if int(naca_num[0]) != 2:
                 
                raise ValueError("Invalid first digit")
            
            if not (int(naca_num[1]) >= 1 and int(naca_num[1]) <= 5):
                 
                raise ValueError("Invalid second digit")

            if not (int(naca_num[2]) == 0 or int(naca_num[2]) == 1):
                 
                raise ValueError("Invalid third digit")

            if not (int(naca_num[3:]) >= 1 and int(naca_num[3:]) <= 40):
                 
                raise ValueError("Invalid last two digits")
            
            return True
        
        
        
        except:

            return False







    
class AirFoil:

    def __init__(self, name: str, reynolds_num_start: float, reynolds_num_stop: float, reynolds_num_step: float, color: str, alpha_num_start: int = -10, alpha_num_stop: int = 20, alpha_num_step: int = 1, file_path: str|None = None):

        self.name = name

        self.reynolds_num_start = reynolds_num_start

        self.reynolds_num_stop = reynolds_num_stop

        self.reynolds_num_step = reynolds_num_step

        self.alpha_num_start = alpha_num_start

        self.alpha_num_stop = alpha_num_stop

        self.alpha_num_step = alpha_num_step

        self.color = color

        self.type = standards.CUSTOM_AIRFOIL

        self.foil_data_path = file_path

        if file_path != None:

            xu, yu, xl, yl = FoilUtils.load_airfoil_dat(file_path)

            self.xu = xu

            self.yu = yu

            self.xl = xl
            
            self.yl = yl


    def set_coordinates(self, xu: NDArray[np.float64], yu: NDArray[np.float64], xl: NDArray[np.float64], yl: NDArray[np.float64]):

        self.xu = xu

        self.yu = yu

        self.xl = xl
            
        self.yl = yl




    def is_standard_foil(self) -> bool:

        return False
    
    def is_almost_same(self, other: "AirFoil"):

        attrs = (
            "name",
            "reynolds_num_start",
            "reynolds_num_stop",
            "reynolds_num_step",
            "alpha_num_start",
            "alpha_num_stop",
            "alpha_num_step"
        )

        return all(
            getattr(self, attr) == getattr(other, attr)
            for attr in attrs
        )
    
    def run_xfoil_model(self, callback_func: Callable[..., Any]) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], str, "AirFoil"]:

        print("Loading foil data into XFOIL....")

        i = 0

        with open("incomplete_runs.txt", "w") as file:

            for re in range(int(self.reynolds_num_start), int(self.reynolds_num_stop) + 1, int(self.reynolds_num_step)):

                print(f"Running XFOIL for Reynolds number: {re}")

                foil_data_path = FoilUtils.save_airfoil(f"{self.name}.dat", self.xu, self.yu, self.xl, self.yl)

                res = FoilUtils.run_xfoil(str(foil_data_path), start_alpha = self.alpha_num_start, end_alpha=self.alpha_num_stop, step_alpha=self.alpha_num_step, Re = re)

                if res == None:

                    file.write(f"{re}\n")

                i += 1

                callback_func(i)

            file.flush()

            file.close()


            Path(foil_data_path).unlink()

        return self.xu, self.yu, self.xl, self.yl, str(foil_data_path), self


class NACA_4_Standard_AirFoil(AirFoil):

    def __init__(self, num: str, reynolds_num_start: float, reynolds_num_stop: float, reynolds_num_step: float, color: str, alpha_num_start: int = -10, alpha_num_stop: int = 20, alpha_num_step: int = 1):

        super().__init__(f"NACA {num}", reynolds_num_start, reynolds_num_stop, reynolds_num_step, color, alpha_num_start, alpha_num_stop, alpha_num_step)

        self.naca_num: str = num

        self.type = standards.NACA_4_AIRFOIL

    def is_standard_foil(self) -> bool:

        return True


    
    def run_xfoil_model(self, callback_func: Callable[..., Any]) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], str, AirFoil]:

        m, p, t = FoilUtils.generate_naca_4_foil_data(self.name.split()[1])

        x = FoilUtils.generate_x()

        y = FoilUtils.generate_thickness(x, t)

        zc = FoilUtils.camber_line_naca_4(x, m, p)

        dzdx = FoilUtils.camber_slope_naca_4(x, m, p)

        xu, yu, xl, yl = FoilUtils.airfoil_coordinates(x, y, zc, dzdx)

        foil_data_path = FoilUtils.save_airfoil(f"{self.name.replace(' ', '').lower()}.dat", xu, yu, xl, yl)

        print("Loading foil data into XFOIL....")

        i = 0

        with open("incomplete_runs.txt", "w") as file:

            for re in range(int(self.reynolds_num_start), int(self.reynolds_num_stop) + 1, int(self.reynolds_num_step)):

                print(f"Running XFOIL for Reynolds number: {re}")

                res = FoilUtils.run_xfoil(str(foil_data_path), start_alpha = self.alpha_num_start, end_alpha=self.alpha_num_stop, step_alpha=self.alpha_num_step, Re = re)

                if res == None:

                    file.write(f"{re}\n")

                i += 1

                callback_func(i)

            file.flush()

            file.close()

        return xu, yu, xl, yl, str(foil_data_path), self
    


class NACA_5_Standard_Airfoil(AirFoil):

    def __init__(self, num: str , reynolds_num_start, reynolds_num_stop, reynolds_num_step, color, alpha_num_start = -10, alpha_num_stop = 20, alpha_num_step = 1):

        super().__init__(f"NACA {num}", reynolds_num_start, reynolds_num_stop, reynolds_num_step, color, alpha_num_start, alpha_num_stop, alpha_num_step)

        self.naca_num: str = num

        self.type = standards.NACA_5_AIRFOIL

    
    def is_standard_foil(self):

        return True
    
    
    def run_xfoil_model(self, callback_func: Callable[..., Any]) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], str, AirFoil]:


        is_reflex, m, k1, k2k1, t = FoilUtils.generate_naca_5_foil_data(self.naca_num)

        x = FoilUtils.generate_x()

        y = FoilUtils.generate_thickness(x, t)

        zc = FoilUtils.camber_line_naca_5(x, m, k1, is_reflex, k2k1)

        dzdx = FoilUtils.camber_slope_naca_5(x, m, k1, is_reflex, k2k1)

        xu, yu, xl, yl = FoilUtils.airfoil_coordinates(x, y, zc, dzdx)

        foil_data_path = FoilUtils.save_airfoil(f"{self.name.replace(' ', '').lower()}.dat", xu, yu, xl, yl)

        print("Loading foil data into XFOIL....")

        i = 0

        with open("incomplete_runs.txt", "w") as file:

            for re in range(int(self.reynolds_num_start), int(self.reynolds_num_stop) + 1, int(self.reynolds_num_step)):

                print(f"Running XFOIL for Reynolds number: {re}")

                res = FoilUtils.run_xfoil(str(foil_data_path), start_alpha = self.alpha_num_start, end_alpha=self.alpha_num_stop, step_alpha=self.alpha_num_step, Re = re)

                if res == None:

                    file.write(f"{re}\n")

                i += 1

                callback_func(i)

            file.flush()

            file.close()

        return xu, yu, xl, yl, str(foil_data_path), self






    
    
    



    


    



    


        

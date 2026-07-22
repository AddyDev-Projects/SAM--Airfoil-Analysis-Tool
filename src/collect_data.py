from pathlib import Path

import numpy as np

from numpy.typing import NDArray


class DataUtils:

    @staticmethod
    def parse_file(file_path: str) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:

        alpha = []

        cl = []

        cd = []

        cm = []

        alpha_idx = 0

        cl_idx = 1

        cd_idx = 2

        cm_idx = 3

        indexes_found = False

        if Path(file_path).exists():


            try:


                with open(file_path, "r") as file:

                    data = file.readlines()

                    for line in data:

                        try:

                            parts = line.lower().split()

                            if "alpha" in parts:

                                alpha_idx = parts.index("alpha")

                                cl_idx = parts.index("cl")

                                cd_idx = parts.index("cd")

                                cm_idx = parts.index("cm")

                                indexes_found = True

                                continue

                            if not indexes_found:

                                continue

                            if len(parts) < 3:

                                continue

                            a = float(parts[alpha_idx])

                            l = float(parts[cl_idx])

                            d = float(parts[cd_idx])

                            m = float(parts[cm_idx])

                            alpha.append(a)

                            cl.append(l)

                            cd.append(d)

                            cm.append(m)

                        except:

                            if not indexes_found:

                                raise ValueError("Alpha, Cl, Cd and Cm are required columns in the file")

                            continue

            except:

                raise ValueError("Invalid file path")
            

        return np.array(alpha), np.array(cl), np.array(cd), np.array(cm)




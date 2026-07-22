from foil_data import FoilUtils

import matplotlib.pyplot as plt

from pathlib import Path

import numpy as np

from collect_data import DataUtils

"""

Just to check the plotting function


"""

while True:

    naca_num = input("Enter NACA number:")

    m, p, t = FoilUtils.generate_naca_4_foil_data(naca_num)

    x = FoilUtils.generate_x()

    y = FoilUtils.generate_thickness(x, t)

    zc = FoilUtils.camber_line_naca_4(x, m, p)

    dzdx = FoilUtils.camber_slope_naca_5(x, m, p)

    xu, yu, xl, yl = FoilUtils.airfoil_coordinates(x, y, zc, dzdx)

    foil_data = FoilUtils.save_airfoil(f"naca{int(m*100)}{int(p*10)}{int(t*100)}.dat", xu, yu, xl, yl)

    print("Loading foil data into XFOIL....")

    FoilUtils.run_xfoil(foil_data, start_alpha = -10, end_alpha=20)

    file_path = (Path(__file__).parent / "../" / "polar.txt").resolve()

    alpha, cl, cd, cm = DataUtils.parse_file(str(file_path))


    plt.figure()
    plt.plot(alpha, cl)
    plt.xlabel("Angle of Attack (deg)")
    plt.ylabel("Cl")
    plt.title(f"Cl vs Alpha - NACA {int(m*100)}{int(p*10)}{int(t*100)}")

    plt.axhline(0, color='grey', linewidth=1)
    plt.axvline(0, color='grey', linewidth=1)

    plt.grid()

    plt.figure()

    x = np.concatenate((xu, xl[::-1]))

    y = np.concatenate((yu, yl[::-1]))

    plt.plot(x, y)

    plt.axis('equal')

    plt.show()

    file_path.unlink()

    Path(foil_data).unlink()
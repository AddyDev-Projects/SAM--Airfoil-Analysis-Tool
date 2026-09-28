# Aerofoil Analysis Tool

An interactive desktop application for generating and analyzing NACA airfoils. The application allows users to vary NACA parameters and visualize aerodynamic characteristics through an intuitive graphical interface.

The application uses **XFOIL** as the aerodynamic analysis backend.

> **Note:** Documentation is still a work in progress. While the core files have been documented, I am currently expanding the documentation to cover the entire project.

## Features

- Generate NACA airfoils
- Interactive GUI built with PyQt6
- Airfoil visualization
- Aerodynamic analysis for different Reynolds numbers
- Performance plots, including:
  - Lift Coefficient (Cl)
  - Drag Coefficient (Cd)
  - Lift-to-Drag Ratio (Cl/Cd)
  - Additional aerodynamic plots as the project evolves

## Technologies Used

- Python
- PyQt6
- NumPy
- Matplotlib
- XFOIL

## Installation

1. Clone the repository:

```bash
git clone https://github.com/AddyDev-Projects/SAM--Airfoil-Analysis-Tool.git
cd SAM--Airfoil-Analysis-Tool
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python src/app_ui.py
```

## Project Structure

```
.
├── resources/
├── src/
├── test/
├── pyplot.exe
├── pxplot.exe
├── xfoil.exe
├── requirements.txt
├── README.md
└── .gitignore
```

## Future Improvements

- Support for additional NACA series
- Improved visualization tools
- Better button interaction and UI responsiveness
- Standalone executable release

## Project Repository

GitHub: **https://github.com/AddyDev-Projects/SAM--Airfoil-Analysis-Tool**

## Acknowledgements

I would like to sincerely thank **[Maxon David Nazareth](https://www.linkedin.com/in/mdnazareth/)** and **Saianish** for their valuable help with the mathematical foundations and aerodynamic concepts used throughout this project.

## License

This project is licensed under the MIT License.

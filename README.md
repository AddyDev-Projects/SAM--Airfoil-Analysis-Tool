````markdown
# Aerofoil Analysis Tool

An interactive desktop application for generating and analyzing NACA airfoils. The application allows users to vary NACA parameters and visualize aerodynamic characteristics through an intuitive graphical interface. This program uses the standard sfoil analysis tool as the physics engine. I haven't documented the all the files properly (only some main files have documentation). I plan to document it properly soon.

## Features

- Generate NACA airfoils
- Interactive GUI built with PyQt6
- Airfoil visualization
- Aerodynamic analysis for different Reynolds numbers
- Performance plots, including:
  - Lift Coefficient (Cl)
  - Drag Coefficient (Cd)
  - Lift-to-Drag ratio (Cl/Cd)
  - Additional aerodynamic plots as the project evolves

## Technologies Used

- Python
- PyQt6
- NumPy
- Matplotlib

## Installation

1. Clone the repository:

```bash
git clone https://github.com/AddyDev-Projects/SAM--Airfoil-Analysis-Tool
cd SAM--Airfoil-Analysis-Tool
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python app_ui.py
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

- Additional series supports
- Improved visualization tools
- Better haptics on button clicks
- Conversion to .exe file

## Acknowledgements

I would like to sincerely thank **Maxon David Nazareth** (https://www.linkedin.com/in/mdnazareth/)and **Saianish** for their valuable help with the mathematical foundations and aerodynamic concepts used throughout this project.



## License

This project is licensed under the MIT License.
````

import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QComboBox
from sympy import *
import qwt
import pyqtgraph as pg

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.hbox = QHBoxLayout()

        self.plot = pg.PlotWidget()  # Use PlotWidget from pyqtgraph for the plot

        self.layout.addLayout(self.hbox)

        self.input_line = QTextEdit()
        self.input_line1 = QTextEdit()

        self.input_line.setPlaceholderText('Voeg formules toe')
        self.input_line1.setPlaceholderText('Voeg startwaarden toe')

        self.xvar_combo = QComboBox()
        self.xvar_combo.addItems([])

        self.yvar_combo = QComboBox()
        self.yvar_combo.addItems([])

        self.hbox.addWidget(self.input_line)
        self.hbox.addWidget(self.input_line1)
        self.hbox.addWidget(self.xvar_combo)
        self.hbox.addWidget(self.yvar_combo)

        self.exec_button = QPushButton('Voer model uit')
        self.plot_button = QPushButton('Maak plot')

        self.hbox.addWidget(self.exec_button)
        self.hbox.addWidget(self.plot_button)

        self.hbox.addWidget(self.plot)

        self.setLayout(self.layout)

        self.exec_button.clicked.connect(self.execute_model)
        self.plot_button.clicked.connect(self.create_plot)

    def read_lines(self, text):
        lines = text.split('\n')
        lines_list = [line.strip() for line in lines if line.strip()]  # Exclude empty lines

        self.variables_and_values = {}
        self.non_numeric_values = []
        self.formulas = []

        for line in lines_list:
            parts = line.split('=')
            if len(parts) == 2:
                variable_name = parts[0].strip()
                variable_value_str = parts[1].strip()
                try:
                    variable_value = float(variable_value_str)
                    if variable_name in self.variables_and_values:
                        self.variables_and_values[variable_name].append(variable_value)
                    else:
                        self.variables_and_values[variable_name] = [variable_value]
                except ValueError:
                    # Non-numeric value, add to non_numeric_values list as a tuple
                    self.non_numeric_values.append((variable_name, variable_value_str))

        for variable_tuple in self.non_numeric_values:
            variable_name, variable_value_str = variable_tuple
            y_value = symbols(variable_name)
            formula_expr = sympify(variable_value_str)

            self.formula = Eq(y_value, formula_expr)
            self.formulas.append(self.formula)

        # Substitute values for every occurrence of variables in the formulas
        substituted_formulas = [formula.subs(self.variables_and_values) for formula in self.formulas]

        # Create a dictionary with separate entries for each variable
        self.numeric_values_and_formulas = {variable: values for variable, values in self.variables_and_values.items()}

        print("Numeric Values and Substituted Formulas:", self.numeric_values_and_formulas)
        print("Non-Numeric Values:", self.non_numeric_values)

        return self.numeric_values_and_formulas, self.non_numeric_values, substituted_formulas

    def execute_model(self):
        self.numeric_values_and_formulas, non_numeric_values, substituted_formulas = self.read_lines(self.input_line1.toPlainText())

        for variable in self.numeric_values_and_formulas.keys():
            self.xvar_combo.addItem(str(variable))
            self.yvar_combo.addItem(str(variable))
       
            
         # Clear existing plot
        self.plot.clear()

        
        



    def create_plot(self):
        # Extract selected variables from combo-boxes
        y_variable = symbols(self.xvar_combo.currentText())
        x_variable = symbols(self.yvar_combo.currentText())

        if not x_variable or not y_variable:
            print("Please select variables from the combo-boxes.")
            return
        
        
        
        # Get corresponding values from the dictionary
        x_values = self.numeric_values_and_formulas.get(x_variable, [])
        y_values = self.numeric_values_and_formulas.get(y_variable, [])
        
        

        print(f"Creating plot for {x_variable}: {x_values}, {y_variable}: {y_values}")

        # Create a curve if it doesn't exist or update existing curve
        curve_name = f'{x_variable}-{y_variable}'
        existing_curve = None
        for item in self.plot.getPlotItem().listDataItems():
            if item.name() == curve_name:
                existing_curve = item
                break

        if existing_curve is not None:
            # Update the data of the existing curve
            print(f"Updating existing curve {curve_name}")
            existing_curve.setData(x=x_values, y=y_values)
        else:
            # Create a new curve and add it to the plot
            print(f"Creating new curve {curve_name}")
            curve = self.plot.plot(x=x_values, y=y_values, symbol='o', name=curve_name)

        self.plot.replot()

        

if __name__ == '__main__':
    app = QApplication([])
    window = MyApp()
    window.show()
    app.exec_()
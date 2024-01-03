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
        z = 0
        lines = text.split('\n')
        lines_list = [line.strip() for line in lines if line.strip()]  # Exclude empty lines

        self.variables_and_values = {}
        self.non_numeric_values = []
        self.formulas = []
        self.formulas_ = []
        self.numeric_values_and_formulas = {variable: values for variable, values in self.variables_and_values.items()}
        for line in lines_list:
            parts = line.split('=')
            if len(parts) == 2:
                variable_name = parts[0].strip()
                self.variable_value_str = parts[1].strip()
                try:
                    self.variable_value = float(self.variable_value_str)
                    if variable_name in self.variables_and_values:
                        self.variables_and_values[variable_name].append(self.variable_value)
                    else:
                        self.variables_and_values[variable_name] = [self.variable_value]
                except ValueError:
                    # Non-numeric value, add to non_numeric_values list as a tuple
                    self.non_numeric_values.append((variable_name, self.variable_value_str))
        # x is set to zero!!!
        for variable_tuple in self.non_numeric_values:
            variable_name, self.variable_value_str = variable_tuple
            self.y_value = symbols(variable_name)
            formula_expr = sympify(self.variable_value_str)


            self.variables_in_equation = [str(var) for var in formula_expr.free_symbols]
            if variable_name in self.variables_in_equation and '+' in self.variable_value_str:
                
                # Extract variable and step size
                variable1, stepsize_str = map(str.strip, self.variable_value_str.split('+'))
                # Get the start value for the variable from input_line1

                start_value = symbols(variable1)
                if start_value in self.variables_and_values:
                    start_value = self.variables_and_values[start_value][-1]
                else:
                    # Use 0 as the default start value if not specified
                    start_value = 0
                
                for i in range(11):
                    substituted_formulas = []

                # Create the updated equation with the start value
                    stepsize_expr = sympify(stepsize_str)
                    stepsize_expr_ = i*stepsize_expr
                    formula_expr = Eq(self.y_value, stepsize_expr_)
                    formula = formula_expr  
                    self.formulas.append(formula)
                for formula in self.formulas:

                    for variable_name, values in self.variables_and_values.items():

                        for value in values:
        
                            substituted_formula = formula.subs({variable_name: value})
                            substituted_formulas.append(substituted_formula)
                            self.formulas_.append(formula)                     
                self.variables_and_values[formula.lhs] = [formula.rhs for formula in substituted_formulas]
                self.numeric_values_and_formulas[formula.lhs] = [formula.rhs for formula in substituted_formulas]
            else:
                formula = Eq(self.y_value, formula_expr)
                self.formulas.append(formula)
        for formula in self.formulas:
            if formula not in self.formulas_:

                for variable_name_, values_ in self.variables_and_values.items():
                    
                    # substituted_formula_ = formula
                    for value_ in values_:
                        substituted_formula_ = formula.subs({variable_name_: value_})
                        
                        if substituted_formula_.lhs not in self.numeric_values_and_formulas:
                            self.numeric_values_and_formulas[substituted_formula_.lhs] = [substituted_formula_.rhs]
                        else:
                            self.numeric_values_and_formulas[substituted_formula_.lhs].append(substituted_formula_.rhs)

        print("Numeric Values and Substituted Formulas:", self.numeric_values_and_formulas)
        print("variable and values", self.variables_and_values)

        

        return self.numeric_values_and_formulas

    def execute_model(self):
        self.numeric_values_and_formulas = self.read_lines(self.input_line1.toPlainText())

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
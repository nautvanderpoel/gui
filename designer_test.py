import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QComboBox
from sympy import *
import qwt
import pyqtgraph as pg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.hbox = QHBoxLayout()

        # self.plot = pg.PlotWidget()  # Use PlotWidget from pyqtgraph for the plot

        self.layout.addLayout(self.hbox)

        self.input_line = QTextEdit()
        self.input_line1 = QTextEdit()

        self.input_line1.setPlaceholderText('Voeg formules toe')
        self.input_line.setPlaceholderText('Voeg startwaarden toe')

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

        # self.hbox.addWidget(self.plot)

        self.setLayout(self.layout)

        self.exec_button.clicked.connect(self.execute_model)
        self.plot_button.clicked.connect(self.create_plot)

    def read_lines(self, text):
        z = 0
        lines = text.split('\n')
        lines_list = [line.strip() for line in lines if line.strip()]  # Exclude empty lines

        variables_and_values = {}
        self.non_numeric_values = []
        self.formulas = []
        self.formulas_ = []
        self.numeric_values_and_formulas = {variable: values for variable, values in variables_and_values.items()}
        for line in lines_list:
            parts = line.split('=')
            if len(parts) == 2:
                variable_name = parts[0].strip()
                self.variable_value_str = parts[1].strip()
                try:
                    self.variable_value = float(self.variable_value_str)
                    if variable_name in variables_and_values:
                        variables_and_values[variable_name].append(self.variable_value)
                    else:
                        variables_and_values[variable_name] = [self.variable_value]
                except ValueError:
                    # Non-numeric value, add to non_numeric_values list as a tuple
                    self.non_numeric_values.append((variable_name, self.variable_value_str))
        # x is set to zero!!!
        for variable_tuple in self.non_numeric_values:
            variable_name, self.variable_value_str = variable_tuple
            y_value = symbols(variable_name)
            formula_expr = sympify(self.variable_value_str)


            self.variables_in_equation = [str(var) for var in formula_expr.free_symbols]
            if variable_name in self.variables_in_equation and '+' in self.variable_value_str:
                
                # Extract variable and step size
                variable1, stepsize_str = map(str.strip, self.variable_value_str.split('+'))
                # Get the start value for the variable from input_line1
                start_value = symbols(variable1)
                if start_value in variables_and_values:
                    start_value = variables_and_values[start_value][-1]
                else:
                    # Use 0 as the default start value if not specified
                    start_value = 6

                substituted_formulas = []
                for i in range(11):

                # Create the updated equation with the start value
                    stepsize_expr = sympify(stepsize_str)
                    stepsize_expr_ = i*stepsize_expr
                    formula_expr = Eq(y_value, stepsize_expr_)
                    formula = formula_expr  
                    self.formulas.append(formula)

                for formula in self.formulas:
                    for variable_name, values in variables_and_values.items():
                        for value in values:
        
                            substituted_formula = formula.subs({variable_name: value})
                    if substituted_formula != True and substituted_formula != False:
                        substituted_formulas.append(substituted_formula)
                        self.formulas_.append(formula)

                print(substituted_formulas) 
                variables_and_values[formula.lhs] = [formula.rhs for formula in substituted_formulas]
                self.numeric_values_and_formulas[formula.lhs] = [formula.rhs for formula in substituted_formulas]
            else:
                formula = Eq(y_value, formula_expr)
                self.formulas.append(formula)
        return variables_and_values
    
    def substitute(self):
        variables_and_values_start = self.read_lines(self.input_line.toPlainText())
        variables_and_values = self.read_lines(self.input_line1.toPlainText())
        

        for variable3 in variables_and_values_start.keys():
            start_value3 = variables_and_values_start.get(variable3)
            variable_name3 = symbols(variable3)
            if variable_name3 in variables_and_values:
                    variables_and_values[variable_name3] = [value3 for value3 in variables_and_values[variable_name3] if value3 >= start_value3[-1]]
                    self.numeric_values_and_formulas[variable_name3] = [value3 for value3 in self.numeric_values_and_formulas[variable_name3] if value3 >= start_value3[-1]]
            
                

        for formula in self.formulas:
            # if formula not in self.formulas_:
                
            for variable_name_, values_ in variables_and_values.items():
                for value_ in values_:
                    substituted_formula_ = formula.subs({variable_name_: value_})
                    if substituted_formula_ != True or False:
                        if type(substituted_formula_.rhs) is Float or substituted_formula_.rhs == 0:

                            if substituted_formula_.lhs not in self.numeric_values_and_formulas:
                                self.numeric_values_and_formulas[substituted_formula_.lhs] = [substituted_formula_.rhs]
                            else:
                                self.numeric_values_and_formulas[substituted_formula_.lhs].append(substituted_formula_.rhs)

        print("Numeric Values and Substituted Formulas:", self.numeric_values_and_formulas)
        # print("variable and values", variables_and_values)

        

        return self.numeric_values_and_formulas

    def execute_model(self):
        self.yvar_combo.clear()
        self.xvar_combo.clear()

        self.numeric_values_and_formulas = self.substitute()

        for variable in self.numeric_values_and_formulas.keys():
            self.xvar_combo.addItem(str(variable))
            self.yvar_combo.addItem(str(variable))
       
            
        # self.plot.clear()

        
    def create_plot(self):
        # Extract selected variables from combo-boxes
        self.y_variable = symbols(self.xvar_combo.currentText())
        self.x_variable = symbols(self.yvar_combo.currentText())

        if self.x_variable not in self.numeric_values_and_formulas or self.y_variable not in self.numeric_values_and_formulas:
            print("No data available for selected variables.")
            return

        # Get corresponding values from the dictionary
        x_values = self.numeric_values_and_formulas[self.x_variable]
        y_values = self.numeric_values_and_formulas[self.y_variable]
        print(x_values)
        # Ensure that x_values and y_values are numeric
        print(f"Creating plot for {self.x_variable}: {x_values}, {self.y_variable}: {y_values}")

        # If either x_values or y_values is empty, return without creating or updating the plot
        if not x_values or not y_values:
            print("No data to plot.")
            return

        # Create or update a Matplotlib plot
        if not hasattr(self, 'figure'):
            self.figure, self.ax = plt.subplots()
            self.ax.set_xlabel(str(self.x_variable))
            self.ax.set_ylabel(str(self.y_variable))
            self.ax.plot(x_values, y_values, 'o-', label=f'{self.x_variable}-{self.y_variable}')
            self.ax.legend()
            self.canvas = FigureCanvas(self.figure)
            self.layout.addWidget(self.canvas)
        else:
            self.ax.clear()
            self.ax.set_xlabel(str(self.x_variable))
            self.ax.set_ylabel(str(self.y_variable))
            self.ax.plot(x_values, y_values, 'o-', label=f'{self.x_variable}-{self.y_variable}')
            self.ax.legend()
            self.canvas.draw()


        

if __name__ == '__main__':
    app = QApplication([])
    window = MyApp()
    window.show()
    app.exec_()
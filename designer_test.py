from sympy import Eq, symbols, Matrix, sympify
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

                # Create the updated equation with the start value
                    stepsize_expr = sympify(stepsize_str)
                    stepsize_expr_ = i*stepsize_expr
                    formula_expr = Eq(self.y_value, stepsize_expr_)
                    formula = formula_expr  
                    self.formulas.append(formula)
                                     
                
            else:
                formula = Eq(self.y_value, formula_expr)
                self.formulas.append(formula)
                self.variables_and_values[formula.lhs] = [formula.rhs for formula in self.formulas]

        return self.variables_and_values
    
    def substitute(self):
        self.variables_and_values_start = self.read_lines(self.input_line.toPlainText())
        _ = self.read_lines(self.input_line1.toPlainText())
        substituted_formulas = []

        for formula in self.formulas:
            current_sub_formula = []
            for d in range(len(self.variables_and_values_start)):
                for variable_name, values in self.variables_and_values_start.items():
                    for value in values:
                        if d == 0:
                            substituted_formula = formula.subs({variable_name: value})
                            current_sub_formula.append(substituted_formula)
                        else:
                            current = current_sub_formula[-1].subs({variable_name: value}) 
                            current_sub_formula.append(current)
            substituted_formulas.append(current_sub_formula[-1])

        for substituted_formula in substituted_formulas:
            if isinstance(substituted_formula.rhs, Float) or substituted_formula.rhs == 0:
                if substituted_formula.lhs not in self.numeric_values_and_formulas:
                    self.numeric_values_and_formulas[substituted_formula.lhs] = [substituted_formula.rhs]
                    self.variables_and_values[substituted_formula.lhs] = [substituted_formula.rhs]
                else:
                    self.numeric_values_and_formulas[substituted_formula.lhs].append(substituted_formula.rhs)
                    self.variables_and_values[substituted_formula.lhs].append(substituted_formula.rhs)
        d = 0
        for k, substituted_formula in enumerate(substituted_formulas):    
            for variable_name_ in self.variables_and_values.keys():
                values = self.variables_and_values[variable_name_]
                try:
                    if str(variable_name_) in ([str(var) for var in substituted_formula.rhs.free_symbols]):
                        
                            substituted_formula_ = substituted_formula.subs({variable_name: values[k]})
                            if type(substituted_formula_.rhs) is Float or substituted_formula_.rhs == 0:
                                d += 1
                                if substituted_formula_.lhs not in self.numeric_values_and_formulas:
                                        self.numeric_values_and_formulas[substituted_formula_.lhs] = [substituted_formula_.rhs]
                                else:
                                        self.numeric_values_and_formulas[substituted_formula_.lhs].append(substituted_formula_.rhs)
                except AttributeError:
                    continue
            if all(isinstance(substituted_formula.rhs, (Float, int)) or substituted_formula.rhs == 0 for substituted_formula in substituted_formulas):
                break            
        self.variables_and_values[formula.lhs] = [formula.rhs for formula in substituted_formulas]
        self.numeric_values_and_formulas[formula.lhs] = [formula.rhs for formula in substituted_formulas]



        # for variable3 in self.variables_and_values_start.keys():
        #     start_value3 = self.variables_and_values_start.get(variable3)
        #     variable_name3 = symbols(variable3)
        #     if variable_name3 in self.variables_and_values:
        #             self.variables_and_values[variable_name3] = [value3 for value3 in self.variables_and_values[variable_name3] if value3 >= start_value3[-1]]
        #             self.numeric_values_and_formulas[variable_name3] = [value3 for value3 in self.numeric_values_and_formulas[variable_name3] if value3 >= start_value3[-1]]
        
                

        print("numeric values and formulas", self.numeric_values_and_formulas)
        print("variable and values", self.variables_and_values)

        

        return self.numeric_values_and_formulas

    def execute_model(self):
        self.yvar_combo.clear()
        self.xvar_combo.clear()

        self.numeric_values_and_formulas = self.substitute()

        for variable in self.numeric_values_and_formulas.keys():
            self.xvar_combo.addItem(str(variable))
            self.yvar_combo.addItem(str(variable))
       
            
         # Clear existing plot
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
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QComboBox
from sympy import *
import qwt
import pyqtgraph as pg
from sympy import symbols, Eq, sympify

# PyQtGraph global options
pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.hbox = QHBoxLayout()

        self.plot = qwt.QwtPlot()

        self.plot.replot()
        self.plot.show()

        self.layout.addLayout(self.hbox)

        self.input_line = QTextEdit()
        self.input_line1 = QTextEdit()

        self.input_line.setPlaceholderText('Voeg formules toe')
        self.input_line1.setPlaceholderText('Voeg startwaarden toe')

        self.xvar_combo = QComboBox()
        self.xvar_combo.addItems(['x', 'y', 'z'])

        self.yvar_combo = QComboBox()
        self.yvar_combo.addItems(['d', 'e', 'f'])

        self.hbox.addWidget(self.input_line)
        self.hbox.addWidget(self.input_line1)
        self.hbox.addWidget(self.xvar_combo)
        self.hbox.addWidget(self.yvar_combo)

        self.exec_button = QPushButton('Voer model uit')

        self.hbox.addWidget(self.exec_button)

        self.hbox.addWidget(self.plot)

        self.setLayout(self.layout)

   

        self.exec_button = QPushButton('Voer model uit', self)
        self.exec_button.clicked.connect(lambda: self.read_lines(self.input_line1.toPlainText()))
        self.exec_button.clicked.connect(lambda: self.read_lines(self.input_line.toPlainText()))

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
                    self.variables_and_values[variable_name] = []

                # converts the non_numeric_values into formula's
                for self.variable_tuple in self.non_numeric_values:
                    self.variable_name, self.variable_value_str = self.variable_tuple
                    self.y_value = symbols(variable_name)
                    self.formula_expr = sympify(variable_value_str)
                    self.formula = Eq(self.y_value, self.formula_expr)
                    self.formulas.append(self.formula)

        print("Formulas:", self.formulas)
        print("Numeric Values:", self.variables_and_values)
        print("Non-Numeric Values:", self.non_numeric_values)
  
        for self.variable_name, self.values in self.variables_and_values.items():
            for value in self.values:
                for self.formula in self.formulas:
                    # Substitute the value of the variable into the formula
                    self.substituted_formula = self.formula.subs(symbols(self.variable_name), value)
                    
                    # Convert the formula into a string and then use sympify to parse it
                    formula_str = str(self.substituted_formula)
                    self.substituted_formula = sympify(formula_str)
                    
                    # Evaluate the formula
                    self.substituted_formula_value = self.substituted_formula.rhs
                    
                    print(f"{self.substituted_formula_value}=")
                    self.variables_and_values[self.variable_name].append(self.substituted_formula_value)

        
   
        
        return self.variables_and_values, self.non_numeric_values, self.formulas    
    
    


    

        

if __name__ == '__main__':
    app = QApplication([])
    window = MyApp()
    window.show()
    app.exec_()
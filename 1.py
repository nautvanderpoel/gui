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

        self.exec_button.clicked.connect(self.execute_model)

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
            formula = Eq(y_value, formula_expr)
            self.formulas.append(formula)

        # Substitute values for every occurrence of variables in the formulas
        substituted_formulas = []
        for formula in self.formulas:
            substituted_formula = formula
            for variable_name, values in self.variables_and_values.items():
                for value in values:
                    substituted_formula = substituted_formula.subs(symbols(variable_name), value)
            substituted_formulas.append(substituted_formula)

        # Create a dictionary with separate entries for each variable
        numeric_values_and_formulas = {variable: values for variable, values in self.variables_and_values.items()}
        numeric_values_and_formulas[substituted_formula.lhs] = [formula.rhs for formula in substituted_formulas]

        print("Numeric Values and Substituted Formulas:", numeric_values_and_formulas)
        print("Non-Numeric Values:", self.non_numeric_values)

        return numeric_values_and_formulas, self.non_numeric_values, substituted_formulas

    def execute_model(self):
        numeric_values_and_formulas, non_numeric_values, substituted_formulas = self.read_lines(self.input_line1.toPlainText())

        # Perform further actions if needed using the numeric_values_and_formulas, substituted_formulas, and other data

if __name__ == '__main__':
    app = QApplication([])
    window = MyApp()
    window.show()
    app.exec_()

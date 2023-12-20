from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QLineEdit
from PyQt5.QtCore import QPointF
import qwt 
import numpy as np
import sys
import sympy as sp

def func(x):
    return x**2

def plot_formula(formula):

    plot = qwt.QwtPlot()
    curve = qwt.QwtPlotCurve()

    curve.setData(x, y)
    curve.attach(plot)

    plot.replot()
    plot.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    formula_str = QInputDialog.getText(None, "Input", "Enter a formula:")
    # start = float(QInputDialog.getText(None, "Input", "Enter start value:", QLineEdit.Normal, "0.0"))
    # end = float(QInputDialog.getText(None, "Input", "Enter end value:"))
    # step = float(QInputDialog.getText(None, "Input", "Enter step value:"))

    formula = sp.sympify(formula_str)
    plot_formula(formula)

    sys.exit(app.exec_())
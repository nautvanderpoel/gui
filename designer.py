import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QComboBox
from sympy import *
import qwt
import pyqtgraph as pg

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
        self.xvar_combo.addItems(['a', 'b', 'c'])

        self.yvar_combo = QComboBox()
        self.yvar_combo.addItems(['d', 'e', 'f'])

        self.hbox.addWidget(self.input_line)
        self.hbox.addWidget(self.input_line1)
        self.hbox.addWidget(self.xvar_combo)
        self.hbox.addWidget(self.yvar_combo)

        self.exec_button = QPushButton('Voer model uit')
        self.exec_button.clicked.connect(lambda: self.execute_model(self.xvar_combo.currentText(),self.yvar_combo.currentText()))

        self.hbox.addWidget(self.exec_button)
        
        self.hbox.addWidget(self.plot)
        
        self.setLayout(self.layout)
    
   
    def execute_model(self,x,y):
        formula = self.input_line.toPlainText()

        start_value = self.input_line1.toPlainText()
        
        # Here's how you can create a mathematical function from a string using SymPy
        func = lambdify(x, formula, 'numpy')

        x = np.linspace(0, 10, 1000)
        y = func(x)

    
        curve = qwt.QwtPlotCurve()
        curve.setData(x, y)
        curve.attach(self.plot)
        self.plot.replot()

       

if __name__ == '__main__':
    app = QApplication([])
    window = MyApp()
    window.show()
    app.exec_()


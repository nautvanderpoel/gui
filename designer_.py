from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
import sys
import threading
import webview
from flask import Flask

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        button = QPushButton('Click me')
        button.clicked.connect(self.on_button_click)

        layout.addWidget(button)
        self.setLayout(layout)

    def on_button_click(self):
        print('Button clicked')

def create_flask_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'Hello, this is the web app!'

    return app

def run_flask_app():
    app = create_flask_app()
    app.run()

def run_qt_app():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # Wait for Flask to start (you may need to adjust the sleep time)
    import time
    time.sleep(2)

    # Open a webview window to display the PyQt5 app
    webview.create_window('My PyQt5 App', 'http://127.0.0.1:5000')
    webview.start()

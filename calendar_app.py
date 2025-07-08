import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QCalendarWidget
from PyQt5.QtCore import QDate


class CalendarApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Calendar App")
        self.setGeometry(100, 100, 400, 300)

        # Layout
        layout = QVBoxLayout()

        # Calendar Widget
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_clicked)

        # Label to show selected date
        self.label = QLabel("Select a date...", self)

        # Add widgets to layout
        layout.addWidget(self.calendar)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def on_date_clicked(self, date: QDate):
        self.label.setText(f"You selected: {date.toString()}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalendarApp()
    window.show()
    sys.exit(app.exec_())

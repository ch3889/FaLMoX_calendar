import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QCalendarWidget, QDesktopWidget
from PyQt5.QtCore import QDate


class CalendarApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaLMoX calendar")
        self.resize(800, 600)  # window size
        self.center()          # make the frame center

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

    def center(self):
        # get window's frame geometry
        frame = self.frameGeometry()
        # get the center point of the screen
        screen_center = QDesktopWidget().availableGeometry().center()
        # move the frame's center to the screen center
        frame.moveCenter(screen_center)
        # match the top-left point of the window to the frame
        self.move(frame.topLeft())

    def on_date_clicked(self, date: QDate):
        # dddd: full day name, MMMM: full month name, d: day of month, yyyy: four degit year
        formatted_date = date.toString("dddd, MMMM d, yyyy")
        self.label.setText(f"{formatted_date} selected")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalendarApp()
    window.show()
    sys.exit(app.exec_())

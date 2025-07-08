import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QCalendarWidget, QDesktopWidget, QInputDialog, QStackedWidget, QPushButton
from PyQt5.QtCore import QDate
from app.event_dialog import EventInputDialog
from app.weekly_view import WeeklyView


class CalendarApp(QWidget):

    # initializing the calendar
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaLMoX calendar")
        self.resize(800, 600)  # window size
        self.center()          # make the frame center

        # create the two pages to swap around
        self.calendar_page = self._build_calendar_page()
        self.weekly_page = QWidget()    # placeholder page

        # stack widgets to hold both pages
        self.stack = QStackedWidget(self)
        self.stack.addWidget(self.calendar_page)
        self.stack.addWidget(self.weekly_page)

        # main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        # events
        # Dictionary: {QDate.toString(): ["event1", "event2", ...]}
        self.events = {}

    # calendar page
    def _build_calendar_page(self):
        label = QWidget()
        layout = QVBoxLayout(label)
        self.calendar = QCalendarWidget(label)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_clicked)
        self.cal_label = QLabel("Select a date...", label)

        layout.addWidget(self.calendar)
        layout.addWidget(self.cal_label)
        return label

    # make it appear in the center of the screen
    def center(self):
        # get window's frame geometry
        frame = self.frameGeometry()
        # get the center point of the screen
        screen_center = QDesktopWidget().availableGeometry().center()
        # move the frame's center to the screen center
        frame.moveCenter(screen_center)
        # match the top-left point of the window to the frame
        self.move(frame.topLeft())

    # when click on a date
    def on_date_clicked(self, date: QDate):

        # new WeeklyView for this date:
        week = WeeklyView(date, parent=self)
        # back button to go back to calendar
        week.confirm_btn.clicked.connect(self._back_to_calendar)
        week.back_button = QPushButton("← Back", week)
        week.layout().insertWidget(0, week.back_button)  # put it at top
        week.back_button.clicked.connect(self._back_to_calendar)

        # replace the placeholder page with this one:
        idx = self.stack.indexOf(self.weekly_page)
        self.stack.removeWidget(self.weekly_page)
        self.weekly_page = week
        self.stack.insertWidget(idx, self.weekly_page)

        # go to the weekly page:
        self.stack.setCurrentWidget(self.weekly_page)

    # back button to calendar page
    def _back_to_calendar(self):
        self.stack.setCurrentWidget(self.calendar_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CalendarApp()
    window.show()
    sys.exit(app.exec_())

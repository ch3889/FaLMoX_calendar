# app/calendar_app.py
import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QCalendarWidget, QLabel,
    QDesktopWidget, QStackedWidget, QPushButton, QToolTip, QTableView
)
from PyQt5.QtCore import QDate, Qt, QEvent, QTime
from PyQt5.QtGui import QCursor
from app.weekly_view import WeeklyView


class CalendarApp(QWidget):
    def __init__(self):
        super().__init__()
        # consistent window size
        self.setWindowTitle("FaLMoX Calendar")
        self.resize(1000, 650)
        self.center()
        # load events
        self.events_file = os.path.join(
            os.path.dirname(__file__), 'events.json')
        self.events = {}
        self._load_events()
        # calendar page
        self.calendar_page = self._build_calendar_page()
        self.weekly_page = None
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self._back_to_calendar)
        self.back_btn.hide()
        self.stack = QStackedWidget()
        self.stack.addWidget(self.calendar_page)
        layout = QVBoxLayout(self)
        layout.addWidget(self.back_btn, alignment=Qt.AlignLeft)
        layout.addWidget(self.stack)
        # tooltip setup
        cv = self.calendar.findChild(QTableView)
        cv.viewport().installEventFilter(self)
        cv.setMouseTracking(True)

    def _build_calendar_page(self):
        w = QWidget(self)
        l = QVBoxLayout(w)
        self.calendar = QCalendarWidget(w)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self._open_week)
        self.lbl = QLabel("Select a date...", w)
        l.addWidget(self.calendar)
        l.addWidget(self.lbl)
        return w

    def _open_week(self, date: QDate):
        week = WeeklyView(date, self.events, parent=self)
        self.stack.addWidget(week)
        self.weekly_page = week
        self.back_btn.show()
        self.stack.setCurrentWidget(week)

    def _back_to_calendar(self):
        self._save_events()
        self.back_btn.hide()
        self.stack.setCurrentIndex(0)

    def _load_events(self):
        if os.path.exists(self.events_file):
            with open(self.events_file) as f:
                d = json.load(f)
            for k, evs in d.items():
                self.events[k] = []
                for ev in evs:
                    self.events[k].append({
                        'name': ev['name'],
                        'start': QTime.fromString(ev['start'], 'HH:mm'),
                        'end': QTime.fromString(ev['end'], 'HH:mm'),
                        'notes': ev.get('notes', '')
                    })

    def _save_events(self):
        out = {}
        for k, evs in self.events.items():
            out[k] = [{'name': e['name'], 'start': e['start'].toString(
                'HH:mm'), 'end': e['end'].toString('HH:mm'), 'notes': e.get('notes', '')} for e in evs]
        with open(self.events_file, 'w') as f:
            json.dump(out, f, indent=2)

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.MouseMove:
            cv = self.calendar.findChild(QTableView)
            idx = cv.indexAt(ev.pos())
            if idx.isValid():
                v = idx.data()
                if isinstance(v, int):
                    v = str(v)
                if v and v.isdigit():
                    day = int(v)
                    m = self.calendar.monthShown()
                    y = self.calendar.yearShown()
                    key = QDate(y, m, day).toString('yyyy-MM-dd')
                    evs = self.events.get(key, [])
                    if evs:
                        txt = "\n".join(
                            f"{e['name']}: {e['start'].toString('HH:mm')}-{e['end'].toString('HH:mm')}" for e in evs)
                        QToolTip.showText(QCursor.pos(), txt, self)
                    else:
                        QToolTip.hideText()
        return super().eventFilter(obj, ev)

    def center(self):
        f = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        f.moveCenter(cp)
        self.move(f.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = CalendarApp()
    win.show()
    sys.exit(app.exec_())

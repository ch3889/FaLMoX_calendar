# app/calendar_app.py
import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QCalendarWidget, QLabel,
    QDesktopWidget, QStackedWidget, QPushButton, QToolTip, QTableView
)
from PyQt5.QtCore import QDate, Qt, QEvent
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import QTime
from app.weekly_view import WeeklyView


class CalendarApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaLMoX Calendar")
        self.resize(800, 600)
        self.center()
        # persistence
        self.events_file = os.path.join(
            os.path.dirname(__file__), 'events.json')
        self.events = {}
        self._load_events()
        # UI
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
        # tooltip filter
        cv = self.calendar.findChild(QTableView)
        cv.viewport().installEventFilter(self)
        cv.setMouseTracking(True)

    def _build_calendar_page(self):
        w = QWidget(self)
        lay = QVBoxLayout(w)
        self.calendar = QCalendarWidget(w)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self._open_weekly)
        self.label = QLabel("Select a date...", w)
        lay.addWidget(self.calendar)
        lay.addWidget(self.label)
        return w

    def _open_weekly(self, date: QDate):
        week = WeeklyView(date, self.events, parent=self)
        self.stack.addWidget(week)
        self.weekly_page = week
        self.back_btn.show()
        self.stack.setCurrentWidget(week)

    def _back_to_calendar(self):
        self._save_events()
        self.back_btn.hide()
        self.stack.setCurrentWidget(self.calendar_page)

    def _load_events(self):
        if os.path.exists(self.events_file):
            with open(self.events_file) as f:
                data = json.load(f)
            for k, evs in data.items():
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
            out[k] = []
            for ev in evs:
                out[k].append({
                    'name': ev['name'],
                    'start': ev['start'].toString('HH:mm'),
                    'end': ev['end'].toString('HH:mm'),
                    'notes': ev.get('notes', '')
                })
        with open(self.events_file, 'w') as f:
            json.dump(out, f, indent=2)

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.MouseMove:
            cv = self.calendar.findChild(QTableView)
            pos = ev.pos()
            idx = cv.indexAt(pos)
            if idx.isValid():
                v = idx.data()
                try:
                    day = int(v)
                except Exception:
                    return super().eventFilter(obj, ev)
                m = self.calendar.monthShown()
                y = self.calendar.yearShown()
                date = QDate(y, m, day)
                key = date.toString('yyyy-MM-dd')
                evs = self.events.get(key, [])
                if evs:
                    lines = [
                        f"{e['name']}: {e['start'].toString('HH:mm')}-{e['end'].toString('HH:mm')}" for e in evs]
                    QToolTip.showText(QCursor.pos(), "\n".join(lines), self)
                else:
                    QToolTip.hideText()
        return super().eventFilter(obj, ev)

    def center(self):
        frame = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(cp)
        self.move(frame.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalendarApp()
    window.show()
    sys.exit(app.exec_())

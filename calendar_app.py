# app/calendar_app.py
import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QCalendarWidget, QLabel,
    QDesktopWidget, QStackedWidget, QPushButton, QTableView
)
from PyQt5.QtCore import QDate, Qt, QEvent, QTime, QPoint
from PyQt5.QtGui import QCursor
from app.weekly_view import WeeklyView


class CalendarApp(QWidget):
    def __init__(self):
        super().__init__()
        # Consistent window size
        self.setWindowTitle("FaLMoX Calendar")
        self.resize(1000, 650)
        self.center()

        # Event persistence file
        self.events_file = os.path.join(
            os.path.dirname(__file__), 'events.json')
        self.events = {}
        self._load_events()

        # Build UI pages
        self.calendar_page = self._build_calendar_page()
        self.weekly_page = None

        # Back button
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self._back_to_calendar)
        self.back_btn.hide()

        # Stacked widget for page switching
        self.stack = QStackedWidget()
        self.stack.addWidget(self.calendar_page)

        # Hover popup for date events
        self.hover_popup = QLabel(self)
        self.hover_popup.setWindowFlags(Qt.ToolTip)
        self.hover_popup.setStyleSheet(
            "background-color: #FFFFE0; border: 1px solid black; padding: 4px;"
        )
        self.hover_popup.hide()

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.back_btn, alignment=Qt.AlignLeft)
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        # Install event filter on calendar viewport
        cal_view = self.calendar.findChild(QTableView)
        cal_view.viewport().installEventFilter(self)
        cal_view.setMouseTracking(True)

    def _build_calendar_page(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)

        self.calendar = QCalendarWidget(page)
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self._open_weekly)

        self.cal_label = QLabel("Select a date...", page)
        layout.addWidget(self.calendar)
        layout.addWidget(self.cal_label)

        return page

    def _open_weekly(self, date: QDate):
        # Hide hover popup when entering weekly view
        self.hover_popup.hide()
        # Create or update weekly view
        week = WeeklyView(date, self.events, parent=self)
        if self.weekly_page:
            self.stack.removeWidget(self.weekly_page)
        self.weekly_page = week
        self.stack.addWidget(self.weekly_page)
        self.back_btn.show()
        self.stack.setCurrentWidget(self.weekly_page)

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
        # Persistent hover as long as mouse inside a date cell
        if ev.type() == QEvent.MouseMove:
            cal_view = self.calendar.findChild(QTableView)
            idx = cal_view.indexAt(ev.pos())
            if idx.isValid():
                val = idx.data(Qt.DisplayRole)
                day_str = str(val)
                if day_str.isdigit():
                    d = int(day_str)
                    m = self.calendar.monthShown()
                    y = self.calendar.yearShown()
                    date = QDate(y, m, d)
                    key = date.toString('yyyy-MM-dd')
                    evs = self.events.get(key, [])
                    if evs:
                        lines = [
                            f"{e['name']}: {e['start'].toString('HH:mm')}-{e['end'].toString('HH:mm')}"
                            for e in evs
                        ]
                        text = "\n".join(lines)
                        self.hover_popup.setText(text)
                        self.hover_popup.adjustSize()
                        global_pos = cal_view.viewport().mapToGlobal(ev.pos())
                        self.hover_popup.move(global_pos + QPoint(10, 10))
                        self.hover_popup.show()
                        return True
            # hide if not valid or no events
            self.hover_popup.hide()
        return super().eventFilter(obj, ev)

    def center(self):
        frame = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(cp)
        self.move(frame.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = CalendarApp()
    win.show()
    sys.exit(app.exec_())

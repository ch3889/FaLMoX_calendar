# app/weekly_view.py
from PyQt5.QtWidgets import (
    QWidget, QScrollArea, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QTimeEdit, QPushButton
)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

CELL_HEIGHT = 30


class ScheduleWidget(QWidget):
    def __init__(self, days, events, parent=None):
        super().__init__(parent)
        self.days = days
        self.events = events
        self.hour_height = CELL_HEIGHT
        self.minute_height = self.hour_height / 60.0
        self.day_width = 0

    def resizeEvent(self, event):
        total_width = self.width()
        self.day_width = total_width / 7.0
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        w = int(self.width())
        h = int(self.height())
        pen = QPen(Qt.gray)
        painter.setPen(pen)
        # horizontal grid lines
        for hour in range(25):
            y = int(hour * self.hour_height)
            painter.drawLine(0, y, w, y)
        # vertical grid lines
        for col in range(8):
            x = int(col * self.day_width)
            painter.drawLine(x, 0, x, h)
        # draw events with 10-min precision
        for col, day in enumerate(self.days):
            key = day.toString('yyyy-MM-dd')
            for ev in self.events.get(key, []):
                start = ev['start']
                end = ev['end']
                y1 = int((start.hour()*60 + start.minute())
                         * self.minute_height)
                y2 = int((end.hour()*60 + end.minute()) * self.minute_height)
                height = max(y2 - y1, int(self.minute_height))
                x1 = int(col * self.day_width)
                # assign color if not exists
                if '_color' not in ev:
                    ev['_color'] = QColor.fromHsvF(
                        (hash(ev['name']) % 360)/360.0, 0.5, 0.9)
                color = ev['_color']
                color.setAlpha(160)
                painter.fillRect(
                    x1+1, y1+1, int(self.day_width)-2, height-2, color)
                # border
                painter.setPen(QPen(Qt.black))
                painter.drawRect(x1+1, y1+1, int(self.day_width)-2, height-2)
                # text
                painter.setFont(QFont('Sans', 8))
                painter.drawText(
                    x1+3, y1+12,
                    int(self.day_width)-6, height-6,
                    Qt.TextWordWrap,
                    ev['name']
                )


class WeeklyView(QWidget):
    def __init__(self, selected_date: QDate, events: dict, parent=None):
        super().__init__(parent)
        self.selected_date = selected_date
        self.events = events
        # compute Sunday-Saturday
        dow = selected_date.dayOfWeek()
        sunday = selected_date.addDays(- (dow % 7))
        self.days = [sunday.addDays(i) for i in range(7)]
        self._build_ui()

    def _build_ui(self):
        main = QHBoxLayout(self)
        # time labels
        time_col = QWidget(self)
        tl = QVBoxLayout(time_col)
        tl.setSpacing(0)
        tl.setContentsMargins(0, 0, 0, 0)
        for hour in range(24):
            lbl = QLabel(f"{hour:02d}:00", time_col)
            lbl.setFixedHeight(CELL_HEIGHT)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)
            tl.addWidget(lbl)
        main.addWidget(time_col)
        # schedule
        scroll = QScrollArea(self)
        self.schedule = ScheduleWidget(self.days, self.events, self)
        scroll.setWidget(self.schedule)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        main.addWidget(scroll, 3)
        # input panel
        panel = QWidget(self)
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(10, 10, 10, 10)
        pl.setSpacing(8)
        pl.addWidget(QLabel("Event Name:"))
        self.name_input = QLineEdit()
        pl.addWidget(self.name_input)
        tl2 = QHBoxLayout()
        tl2.addWidget(QLabel("Start Time:"))
        self.st = QTimeEdit()
        self.st.setDisplayFormat("HH:mm")
        tl2.addWidget(self.st)
        tl2.addWidget(QLabel("End Time:"))
        self.et = QTimeEdit()
        self.et.setDisplayFormat("HH:mm")
        tl2.addWidget(self.et)
        pl.addLayout(tl2)
        pl.addWidget(QLabel("Notes:"))
        self.nt = QTextEdit()
        pl.addWidget(self.nt)
        self.confirm = QPushButton("Confirm")
        pl.addWidget(self.confirm)
        pl.addStretch(1)
        main.addWidget(panel, 1)
        self.confirm.clicked.connect(self._on_confirm)
        # initial render
        self.schedule.update()

    def _on_confirm(self):
        name = self.name_input.text().strip()
        if not name:
            return
        start = self.st.time()
        end = self.et.time()
        notes = self.nt.toPlainText().strip()
        key = self.selected_date.toString('yyyy-MM-dd')
        self.events.setdefault(key, []).append(
            {'name': name, 'start': start, 'end': end, 'notes': notes})
        self.schedule.update()
        # clear
        self.name_input.clear()
        self.nt.clear()
        self.st.setTime(QTime(0, 0))
        self.et.setTime(QTime(0, 0))

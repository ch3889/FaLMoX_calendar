# app/weekly_view.py
from PyQt5.QtWidgets import (
    QWidget, QScrollArea, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QTimeEdit, QPushButton
)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

CELL_HEIGHT = 30          # height of each hour row in pixels
HEADER_HEIGHT = 30        # height of the day/date header row


class ScheduleWidget(QWidget):
    def __init__(self, days, events, parent=None):
        super().__init__(parent)
        self.days = days        # list of QDate for Sunday→Saturday
        self.events = events    # shared dict from CalendarApp
        self.hour_height = CELL_HEIGHT
        self.minute_height = self.hour_height / 60.0
        self.day_width = 0

    def resizeEvent(self, event):
        # Recompute width per day on resize
        self.day_width = self.width() / 7.0
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        total_width = int(self.width())
        total_height = int(self.hour_height * 24)

        # Draw grid lines
        pen = QPen(Qt.gray)
        painter.setPen(pen)
        # horizontal hour lines
        for h in range(25):
            y = int(h * self.hour_height)
            painter.drawLine(0, y, total_width, y)
        # vertical day lines (8 lines to close grid)
        for c in range(8):
            x = int(c * self.day_width)
            painter.drawLine(x, 0, x, total_height)

        # Draw events
        for col, day in enumerate(self.days):
            key = day.toString('yyyy-MM-dd')
            for ev in self.events.get(key, []):
                start = ev['start']
                end = ev['end']
                name = ev['name']
                # compute y positions with 10-min precision
                y1 = int((start.hour()*60 + start.minute())
                         * self.minute_height)
                y2 = int((end.hour()*60 + end.minute()) * self.minute_height)
                height = max(y2 - y1, int(self.minute_height))
                x1 = int(col * self.day_width)
                # assign stable pastel color if not set
                if '_color' not in ev:
                    hue = (abs(hash(name)) % 360)
                    ev['_color'] = QColor.fromHsv(hue, 127, 229, 160)
                color = ev['_color']
                # fill
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
                    name
                )


class WeeklyView(QWidget):
    def __init__(self, selected_date: QDate, events: dict, parent=None):
        super().__init__(parent)
        self.selected_date = selected_date
        self.events = events
        # determine Sunday→Saturday for this date's week
        dow = selected_date.dayOfWeek()  # Monday=1…Sunday=7
        sunday = selected_date.addDays(- (dow % 7))
        self.days = [sunday.addDays(i) for i in range(7)]
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout(self)

        # ── Time labels column ──
        time_col = QWidget(self)
        tl = QVBoxLayout(time_col)
        tl.setSpacing(0)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.addSpacing(HEADER_HEIGHT)
        for h in range(24):
            lbl = QLabel(f"{h:02d}:00", time_col)
            lbl.setFixedHeight(CELL_HEIGHT)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)
            tl.addWidget(lbl)
        root.addWidget(time_col)

        # ── Schedule grid with header ──
        sched_cont = QWidget(self)
        sc = QVBoxLayout(sched_cont)
        sc.setSpacing(0)
        sc.setContentsMargins(0, 0, 0, 0)

        # header row: day and date
        header = QWidget(sched_cont)
        hl = QHBoxLayout(header)
        hl.setSpacing(0)
        hl.setContentsMargins(0, 0, 0, 0)
        for day in self.days:
            lbl = QLabel(day.toString('ddd M/d'), header)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedHeight(HEADER_HEIGHT)
            hl.addWidget(lbl)
        sc.addWidget(header)

        # scrollable schedule area
        scroll = QScrollArea(self)
        self.schedule = ScheduleWidget(self.days, self.events, self)
        scroll.setWidget(self.schedule)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sc.addWidget(scroll)

        root.addWidget(sched_cont, 3)

        # ── Input panel ──
        panel = QWidget(self)
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(10, 10, 10, 10)
        pl.setSpacing(8)

        pl.addWidget(QLabel("Event Name:"))
        self.name_input = QLineEdit()
        pl.addWidget(self.name_input)

        tl2 = QHBoxLayout()
        tl2.addWidget(QLabel("Start Time:"))
        self.start_input = QTimeEdit()
        self.start_input.setDisplayFormat("HH:mm")
        tl2.addWidget(self.start_input)
        tl2.addWidget(QLabel("End Time:"))
        self.end_input = QTimeEdit()
        self.end_input.setDisplayFormat("HH:mm")
        tl2.addWidget(self.end_input)
        pl.addLayout(tl2)

        pl.addWidget(QLabel("Notes:"))
        self.notes_input = QTextEdit()
        pl.addWidget(self.notes_input)

        self.confirm_btn = QPushButton("Confirm")
        pl.addWidget(self.confirm_btn)
        pl.addStretch(1)
        root.addWidget(panel, 1)

        # wire up
        self.confirm_btn.clicked.connect(self._add_event)
        # initial render
        self.schedule.update()

    def _add_event(self):
        name = self.name_input.text().strip()
        if not name:
            return
        start = self.start_input.time()
        end = self.end_input.time()
        key = self.selected_date.toString('yyyy-MM-dd')
        self.events.setdefault(key, []).append({
            'name': name,
            'start': start,
            'end': end,
            'notes': self.notes_input.toPlainText().strip()
        })
        # refresh
        self.schedule.update()
        # clear inputs
        self.name_input.clear()
        self.notes_input.clear()
        self.start_input.setTime(QTime(0, 0))
        self.end_input.setTime(QTime(0, 0))

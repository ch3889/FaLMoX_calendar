# app/weekly_view.py
from PyQt5.QtWidgets import (
    QWidget, QScrollArea, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QTimeEdit, QPushButton, QDialog, QToolTip
)
from PyQt5.QtCore import Qt, QDate, QTime, QRect, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

CELL_HEIGHT = 30          # height per hour row
HEADER_HEIGHT = 30        # height for header row


class EventEditDialog(QDialog):
    def __init__(self, event, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Event")
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint |
                            Qt.WindowCloseButtonHint)
        layout = QVBoxLayout(self)
        # Name
        layout.addWidget(QLabel("Event Name:"))
        self.name_edit = QLineEdit(event['name'], self)
        layout.addWidget(self.name_edit)
        # Times
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Start Time:"))
        self.start_edit = QTimeEdit(event['start'], self)
        self.start_edit.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.start_edit)
        time_layout.addWidget(QLabel("End Time:"))
        self.end_edit = QTimeEdit(event['end'], self)
        self.end_edit.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.end_edit)
        layout.addLayout(time_layout)
        # Notes
        layout.addWidget(QLabel("Notes:"))
        self.notes_edit = QTextEdit(event.get('notes', ''), self)
        layout.addWidget(self.notes_edit)
        # Buttons
        btn_layout = QHBoxLayout()
        update_btn = QPushButton("Update", self)
        cancel_btn = QPushButton("Cancel", self)
        btn_layout.addWidget(update_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        update_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'start': self.start_edit.time(),
            'end': self.end_edit.time(),
            'notes': self.notes_edit.toPlainText().strip()
        }


class ScheduleWidget(QWidget):
    def __init__(self, days, events, parent=None):
        super().__init__(parent)
        self.days = days
        self.events = events
        self.hour_height = CELL_HEIGHT
        self.minute_height = self.hour_height / 60.0
        self.day_width = 0
        self._rects = []    # (QRect, key, idx, name)
        self.setMouseTracking(True)

    def resizeEvent(self, e):
        self.day_width = self.width() / 7.0
        super().resizeEvent(e)

    def paintEvent(self, e):
        painter = QPainter(self)
        w = int(self.width())
        h = int(self.hour_height * 24)
        painter.setPen(QPen(Qt.gray))
        # grid
        for i in range(25):
            painter.drawLine(0, int(i*self.hour_height),
                             w, int(i*self.hour_height))
        for c in range(8):
            painter.drawLine(int(c*self.day_width), 0,
                             int(c*self.day_width), h)
        # events
        self._rects.clear()
        for col, day in enumerate(self.days):
            key = day.toString('yyyy-MM-dd')
            for idx, ev in enumerate(self.events.get(key, [])):
                start = ev['start']
                end = ev['end']
                name = ev['name']
                y1 = int((start.hour()*60 + start.minute())
                         * self.minute_height)
                y2 = int((end.hour()*60 + end.minute()) * self.minute_height)
                height = max(y2-y1, int(self.minute_height))
                x1 = int(col * self.day_width)
                if '_color' not in ev:
                    hue = abs(hash(name)) % 360
                    ev['_color'] = QColor.fromHsv(hue, 127, 229, 160)
                rect = QRect(x1+1, y1+1, int(self.day_width)-2, height-2)
                self._rects.append((rect, key, idx, name))
                painter.fillRect(rect, ev['_color'])
                painter.setPen(QPen(Qt.black))
                painter.drawRect(rect)
                painter.setFont(QFont('Sans', 8))
                painter.drawText(rect.adjusted(2, 2, -2, -2),
                                 Qt.TextWordWrap, name)

    def mouseMoveEvent(self, e):
        pos = e.pos()
        for rect, key, idx, name in self._rects:
            if rect.contains(pos):
                global_pos = self.mapToGlobal(pos + QPoint(10, 10))
                QToolTip.showText(global_pos, name, self)
                return
        QToolTip.hideText()
        super().mouseMoveEvent(e)

    def mousePressEvent(self, e):
        pos = e.pos()
        hits = [(key, idx)
                for rect, key, idx, name in self._rects if rect.contains(pos)]
        if hits:
            key, idx = hits[-1]
            parent = self.parent()
            dlg = EventEditDialog(self.events[key][idx], parent)
            # center dialog
            dlg.move(parent.mapToGlobal(
                parent.rect().center()) - dlg.rect().center())
            if dlg.exec_():
                data = dlg.get_data()
                ev = self.events[key][idx]
                ev.update(data)
                self.update()
            return
        super().mousePressEvent(e)


class WeeklyView(QWidget):
    def __init__(self, selected_date: QDate, events: dict, parent=None):
        super().__init__(parent)
        self.selected_date = selected_date
        self.events = events
        dow = selected_date.dayOfWeek()
        sunday = selected_date.addDays(- (dow % 7))
        self.days = [sunday.addDays(i) for i in range(7)]
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        # time column
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
        layout.addWidget(time_col)
        # schedule
        cont = QWidget(self)
        sc = QVBoxLayout(cont)
        sc.setSpacing(0)
        sc.setContentsMargins(0, 0, 0, 0)
        # header
        hdr = QWidget(cont)
        hl = QHBoxLayout(hdr)
        hl.setSpacing(0)
        hl.setContentsMargins(0, 0, 0, 0)
        for day in self.days:
            lbl = QLabel(day.toString('ddd M/d'), hdr)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFixedHeight(HEADER_HEIGHT)
            hl.addWidget(lbl)
        sc.addWidget(hdr)
        scroll = QScrollArea(self)
        self.schedule = ScheduleWidget(self.days, self.events, self)
        scroll.setWidget(self.schedule)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sc.addWidget(scroll)
        layout.addWidget(cont, 3)
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
        layout.addWidget(panel, 1)
        self.confirm_btn.clicked.connect(self._add_event)

    def _add_event(self):
        name = self.name_input.text().strip()
        if not name:
            return
        key = self.selected_date.toString('yyyy-MM-dd')
        self.events.setdefault(key, []).append({
            'name': name,
            'start': self.start_input.time(),
            'end': self.end_input.time(),
            'notes': self.notes_input.toPlainText().strip()
        })
        self.schedule.update()
        self.name_input.clear()
        self.notes_input.clear()

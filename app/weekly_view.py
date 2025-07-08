from PyQt5.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QTimeEdit, QPushButton, QSizePolicy, QApplication, QScrollArea
)
from PyQt5.QtCore import Qt, QDate, QTime


class WeeklyView(QWidget):
    def __init__(self, selected_date: QDate, parent=None):
        super().__init__(parent)
        self.selected_date = selected_date
        self.setWindowTitle(
            f"Week View ({selected_date.toString('yyyy-MM-dd')})")
        self.resize(1000, 600)

        # Compute week days starting Sunday
        dow = selected_date.dayOfWeek()  # Monday=1...Sunday=7
        # Determine the Sunday of this week
        sunday = selected_date.addDays(- (dow % 7))
        self.days = [sunday.addDays(i) for i in range(7)]

        # Event storage for this week
        self.events = {day.toString('yyyy-MM-dd'): [] for day in self.days}

        self._build_ui()

    def _build_ui(self):
        main_layout = QHBoxLayout(self)

        # ===== Schedule Table =====
        self.table = QTableWidget(24, 7, self)
        # Row headers: hours
        hours = [f"{h:02d}:00" for h in range(24)]
        self.table.setVerticalHeaderLabels(hours)
        # Column headers: day names and dates
        col_labels = [day.toString('ddd\nM/d') for day in self.days]
        self.table.setHorizontalHeaderLabels(col_labels)
        # Stretch columns, fix row height
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Wrap in a scroll area for vertical scroll
        scroll = QScrollArea(self)
        scroll.setWidget(self.table)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(scroll, 3)

        # ===== Input Panel =====
        panel = QWidget(self)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(8)

        panel_layout.addWidget(QLabel("Event Name:"))
        self.name_input = QLineEdit()
        panel_layout.addWidget(self.name_input)

        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Start Time:"))
        self.start_input = QTimeEdit()
        self.start_input.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.start_input)

        time_layout.addWidget(QLabel("End Time:"))
        self.end_input = QTimeEdit()
        self.end_input.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.end_input)

        panel_layout.addLayout(time_layout)

        panel_layout.addWidget(QLabel("Notes:"))
        self.notes_input = QTextEdit()
        panel_layout.addWidget(self.notes_input)

        self.confirm_btn = QPushButton("Confirm")
        panel_layout.addWidget(self.confirm_btn)
        panel_layout.addStretch(1)

        main_layout.addWidget(panel, 1)

        # Connect confirm
        self.confirm_btn.clicked.connect(self._on_confirm)

    def _on_confirm(self):
        name = self.name_input.text().strip()
        if not name:
            return
        start = self.start_input.time()
        end = self.end_input.time()
        date_key = self.selected_date.toString('yyyy-MM-dd')
        # Store event data
        event = {'name': name, 'start': start, 'end': end,
                 'notes': self.notes_input.toPlainText().strip()}
        self.events[date_key].append(event)
        # Render event in table
        col = self.days.index(self.selected_date)
        # Compute start/end rows based on hour
        start_row = start.hour()
        end_row = end.hour()
        for row in range(start_row, end_row + 1):
            item = QTableWidgetItem(name)
            item.setBackground(Qt.yellow)
            self.table.setItem(row, col, item)
        # Clear inputs for next entry
        self.name_input.clear()
        self.notes_input.clear()

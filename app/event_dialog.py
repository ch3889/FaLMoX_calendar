from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QTextEdit, QTimeEdit,
    QVBoxLayout, QHBoxLayout, QPushButton, QApplication
)
from PyQt5.QtCore import Qt, QTime, QEvent


class EventInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # window flags
        flags = (
            Qt.Window
            | Qt.WindowTitleHint
            | Qt.WindowSystemMenuHint
            | Qt.WindowCloseButtonHint
            | Qt.WindowStaysOnTopHint
        )
        self.setWindowFlags(flags)
        self.setWindowTitle("Add Event")

        # dialog paints its own background
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_StyledBackground, True)

        # visibility
        self.setStyleSheet("""
            QDialog {
                background-color: cyan;
            }
            QLineEdit, QTextEdit, QTimeEdit {
                background: white;
                padding: 4px;
                border: 1px solid #aaa;
            }
            QPushButton {
                background-color: #FF8C00;
                color: white;
                border: none;
                padding: 6px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #FFA500;
            }
        """)

        # input UI
        self.event_name_input = QLineEdit(self)
        self.start_time_input = QTimeEdit(self)
        self.start_time_input.setDisplayFormat("HH:mm")
        self.start_time_input.setTime(QTime.currentTime())

        self.end_time_input = QTimeEdit(self)
        self.end_time_input.setDisplayFormat("HH:mm")
        self.end_time_input.setMinimumTime(QTime(0, 0))
        self.end_time_input.setDisplayFormat("HH:mm")
        self.end_time_input.setTime(QTime(0, 0))  # default shows "(optional)"

        self.notes_input = QTextEdit(self)
        self.confirm_button = QPushButton("Confirm", self)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Event Name:"))
        layout.addWidget(self.event_name_input)

        tlay = QHBoxLayout()
        tlay.addWidget(QLabel("Start Time:"))
        tlay.addWidget(self.start_time_input)
        tlay.addWidget(QLabel("End Time (optional):"))
        tlay.addWidget(self.end_time_input)
        layout.addLayout(tlay)

        layout.addWidget(QLabel("Notes:"))
        layout.addWidget(self.notes_input)
        layout.addWidget(self.confirm_button)

        # collect results
        self.result_data = None
        self.confirm_button.clicked.connect(self._on_confirm)

        # the filter to catch outside clicks
        QApplication.instance().installEventFilter(self)

    # save events by confirm button
    def _on_confirm(self):
        name = self.event_name_input.text().strip()
        if not name:
            return
        start = self.start_time_input.time().toString("HH:mm")
        etime = self.end_time_input.time()
        end = etime.toString("HH:mm") if etime != QTime(0, 0) else None
        notes = self.notes_input.toPlainText().strip()
        self.result_data = {
            'name': name,
            'start_time': start,
            'end_time': end,
            'notes': notes
        }
        self.accept()

    # when press outside of box will return back to calendar
    def eventFilter(self, obj, ev):
        # close when clicking outside this dialog
        if ev.type() == QEvent.MouseButtonPress and self.isVisible():
            # reject everything outside the popup window
            global_pos = ev.globalPos()
            if not self.geometry().contains(global_pos):
                self.reject()
        return super().eventFilter(obj, ev)

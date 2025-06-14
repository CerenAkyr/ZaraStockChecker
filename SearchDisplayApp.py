from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
)
from PySide6.QtCore import Qt, Signal

class SearchDisplayApp(QWidget):
    search_state_changed = Signal(bool)
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Search Display App")

        # Layouts
        main_layout = QVBoxLayout()

        # Title
        title_label = QLabel("Arama Sonuçları")
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("font-size: 24px; font-weight: 500; margin-bottom: 10px")
        main_layout.addWidget(title_label)

        # Scrollable status area
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setPlaceholderText("Arama sonuçları burada çıkacak...")
        self.status_display.setMinimumSize(500, 200)
        main_layout.addWidget(self.status_display)

        # Button to start/stop search
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.search_button = QPushButton("Aramayı Başlat")
        self.search_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px 12px;
                border-radius: 6px;
                border: 1px solid white;
                background-color: #141414;
                color: white;
                transition: 0.3s;
            }
            QPushButton:hover {
                background-color: white;
                color: #141414;
            }
        """)
        self.search_button.setFixedWidth(160)
        button_layout.addWidget(self.search_button)
        main_layout.addLayout(button_layout)
        self.search_button.clicked.connect(self.toggle_search)
        main_layout.addWidget(self.search_button)

        # Set main layout
        self.setLayout(main_layout)
        self.is_searching = False
    
    def update_status(self, message):
        self.status_display.append(message)

    def toggle_search(self):
        """Toggles the search state and updates the button and status display."""
        self.is_searching = not self.is_searching
        self.search_state_changed.emit(self.is_searching)  # Emit the signal with the current state
        if self.is_searching:
            self.search_button.setText("Aramayı Durdur")
            self.status_display.append("Arama başladı...")
        else:
            self.search_button.setText("Aramayı Başlat ")
            self.status_display.append("Arama durdu.")

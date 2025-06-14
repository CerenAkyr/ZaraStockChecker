from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QListWidget, QScrollArea, QListWidgetItem, QFrame
)
from PySide6.QtCore import Qt

class SearchItemsApp(QWidget):
    def __init__(self, items):
        super().__init__()
        self.setWindowTitle("Stock Checker")
        self.items = items  # Reference to the shared items list
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Title
        title_label = QLabel("Aranacak Ürünler")
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("font-size: 24px; font-weight: 500;")
        main_layout.addWidget(title_label)

        # Scrollable view
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.item_list_widget = QListWidget()
        self.scroll_area.setWidget(self.item_list_widget)
        self.scroll_area.setFixedHeight(200)  # Fixed height for the scrollable area
        main_layout.addWidget(self.scroll_area)

        # Horizontal input area
        input_layout = QHBoxLayout()

        self.item_link_input = QLineEdit()
        self.item_link_input.setPlaceholderText("Ürün linki girin")
        self.item_link_input.setStyleSheet("""
            QLineEdit {
        font-size: 16px;
        padding: 8px 12px;
        border-radius: 6px;
        }""")
        input_layout.addWidget(self.item_link_input)


        self.brand_combo = QComboBox()
        self.brand_combo.addItems(["Zara"])
        self.brand_combo.setStyleSheet("""
            QComboBox {
                font-size: 16px;
                padding: 8px 12px;
                border-radius: 6px;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
        """)
        input_layout.addWidget(self.brand_combo)

        self.size_combo = QComboBox()
        self.size_combo.addItems(["XS", "S", "M", "L", "XL"])
        self.size_combo.setStyleSheet("""
            QComboBox {
                font-size: 16px;
                padding: 8px 12px;
                border-radius: 6px;
                min-width: 80px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
        """)
        input_layout.addWidget(self.size_combo)

        main_layout.addLayout(input_layout)

        # Add item button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.add_item_button = QPushButton("Ürünü Ekle")
        self.add_item_button.setStyleSheet("""
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
        self.add_item_button.setFixedWidth(120)

        self.add_item_button.clicked.connect(self.add_item)
        button_layout.addWidget(self.add_item_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
    
    def set_add_item_button_state(self, state: bool):
        """Enable or disable the Add Item button."""
        self.add_item_button.setEnabled(state)

    def add_item(self):
        item_link = self.item_link_input.text().strip()
        brand = self.brand_combo.currentText()
        size = self.size_combo.currentText()

        if item_link:
            list_item = QListWidgetItem()
            self.item_list_widget.addItem(list_item)

            # Add item to the shared list
            item_data = {"brand": brand, "size": size, "link": item_link}
            self.items.append(item_data)
            print("Added item:", item_data)  # Print added item
            print("Updated shared items list:", self.items)

            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    border-radius: 6px;
                    padding: 8px;
                    margin: 2px;
                }
            """)
            
            frame_layout = QHBoxLayout()
            frame_layout.setContentsMargins(8, 4, 8, 4)

            # Display info labels to show:
            brand_label = QLabel(f"Marka: {brand}")
            size_label = QLabel(f"Beden: {size}")
            link_label = QLabel(f"Link: {item_link}")
            
            # Spacingg: 
            frame_layout.addWidget(brand_label)
            frame_layout.addWidget(size_label)
            frame_layout.addWidget(link_label)
            frame_layout.addStretch()

            delete_button = QPushButton("Sil")
            delete_button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    padding: 4px 12px;
                    border-radius: 4px;
                    border: 1px solid #e74c3c;
                    background-color: white;
                    color: #e74c3c;
                }
                QPushButton:disabled {
                    background-color: #bdc3c7;
                    color: #ecf0f1;
                    border: none;
                }
                QPushButton:hover:!disabled {
                    background-color: #2980b9;
                }
            """)
            delete_button.clicked.connect(lambda: self.remove_item(list_item))
            frame_layout.addWidget(delete_button)

            frame.setLayout(frame_layout)
            
            # Set a fixed height for the list item to accommodate the content
            list_item.setSizeHint(frame.sizeHint())
            self.item_list_widget.setItemWidget(list_item, frame)

            # Clear the input field
            self.item_link_input.clear()

    def remove_item(self, list_item):
        row = self.item_list_widget.row(list_item)
        self.item_list_widget.takeItem(row)

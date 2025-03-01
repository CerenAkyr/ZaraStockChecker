from SearchItemsApp import SearchItemsApp
from SearchDisplayApp import SearchDisplayApp
from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout
)
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout
from threading import Thread
from threading import Event
from scraperHelpers import stock_checker

stock_check_event = Event() # to stop-start searching

if __name__ == "__main__":
    app = QApplication([])

    # Shared items list (has size, link, brand)
    shared_items = []

    # Creating instances of both apps
    search_items_app = SearchItemsApp(shared_items)
    search_display_app = SearchDisplayApp()

    # Connect the signal to the slot
    search_display_app.search_state_changed.connect(
        lambda is_searching: stock_check_event.set() if is_searching else stock_check_event.clear()
    )

    # Main window layout to display both apps side by side
    main_window = QWidget()
    main_layout = QHBoxLayout()
    main_layout.addWidget(search_items_app)
    main_layout.addWidget(search_display_app)
    main_window.setLayout(main_layout)
    main_window.setWindowTitle("Stock Checker")
    main_window.show()
    print("Shared items list:", shared_items)

    stock_check_thread = Thread(target=stock_checker, args=(shared_items, stock_check_event, search_display_app), daemon=True)
    stock_check_thread.start()
    #app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, 'hand.ico')))
    app.exec()

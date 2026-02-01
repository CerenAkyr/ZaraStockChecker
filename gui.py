import queue
import threading
import tkinter as tk
from tkinter import ttk

from checker import run_checker


class ZaraStockCheckerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stock Checker")
        self.geometry("1020x900")
        self.minsize(980, 740)
        self.resizable(True, True)
        self._colors = {
            "bg": "#fbe1e8",
            "card": "#ffffff",
            "primary": "#a93d3d",
            "primary_hover": "#c45151",
            "text": "#2b1a1a",
            "muted": "#6a4b4b",
            "input_bg": "#fff7f9",
            "border": "#f2b5c4",
        }
        self.configure(bg=self._colors["bg"])

        self._log_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._worker_thread = None
        self._brands = ["mango", "bershka", "zara"]
        self._items = []
        self._sizes = ["XS", "S", "M", "L", "XL"]
        self._sleep_min_seconds = 12
        self._sleep_max_seconds = 22
        self._sleep_min_var = tk.IntVar(value=self._sleep_min_seconds)
        self._sleep_max_var = tk.IntVar(value=self._sleep_max_seconds)
        self._bot_api_var = tk.StringVar()
        self._chat_id_var = tk.StringVar()
        self._play_sound_var = tk.BooleanVar(value=True)
        self._bot_api_show = False
        self._chat_id_show = False

        self._build_styles()
        self._build_ui()
        self.after(100, self._drain_queue)

    def _build_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("App.TFrame", background=self._colors["bg"])
        style.configure(
            "App.TLabel",
            background=self._colors["bg"],
            foreground=self._colors["text"],
            font=("Avenir Next", 11),
        )
        style.configure("Card.TFrame", background=self._colors["card"])
        style.configure(
            "Card.TLabel",
            background=self._colors["card"],
            foreground=self._colors["text"],
            font=("Avenir Next", 11),
        )
        style.configure(
            "Title.TLabel",
            background=self._colors["bg"],
            foreground=self._colors["text"],
            font=("Avenir Next", 22, "bold"),
        )
        style.configure(
            "Primary.TButton",
            background=self._colors["primary"],
            foreground="white",
            padding=(14, 8),
            borderwidth=0,
        )
        style.map(
            "Primary.TButton",
            background=[("active", self._colors["primary_hover"])],
            foreground=[("active", "white")],
        )
        style.configure(
            "Secondary.TButton",
            background=self._colors["card"],
            foreground=self._colors["text"],
            padding=(14, 8),
            borderwidth=1,
        )
        style.map(
            "Secondary.TButton",
            background=[("active", self._colors["input_bg"])],
            foreground=[("active", self._colors["text"])],
        )
        style.configure(
            "App.TEntry",
            fieldbackground=self._colors["input_bg"],
            foreground=self._colors["text"],
        )
        style.configure(
            "App.TCombobox",
            fieldbackground=self._colors["input_bg"],
            foreground=self._colors["text"],
        )
        style.configure(
            "App.TLabelframe",
            background=self._colors["bg"],
            foreground=self._colors["muted"],
            font=("Avenir Next", 11, "bold"),
        )
        style.configure(
            "App.TLabelframe.Label",
            background=self._colors["bg"],
            foreground=self._colors["muted"],
            font=("Avenir Next", 11, "bold"),
        )
        style.configure(
            "Card.TLabelframe",
            background=self._colors["card"],
            foreground=self._colors["muted"],
            font=("Avenir Next", 11, "bold"),
        )
        style.configure(
            "Card.TLabelframe.Label",
            background=self._colors["card"],
            foreground=self._colors["muted"],
            font=("Avenir Next", 11, "bold"),
        )

    def _build_ui(self):
        header = ttk.Frame(self, style="App.TFrame")
        header.pack(fill="x", padx=26, pady=(20, 12))

        title = ttk.Label(header, text="Stock Checker", style="Title.TLabel")
        title.pack(side="left")

        self._status_var = tk.StringVar(value="Idle")
        self._status_badge = tk.Label(
            header,
            textvariable=self._status_var,
            bg=self._colors["muted"],
            fg="#1c0f0f",
            padx=12,
            pady=6,
            font=("Avenir Next", 10, "bold"),
        )
        self._status_badge.pack(side="right")

        top_row = ttk.Frame(self, style="App.TFrame")
        top_row.pack(fill="both", padx=26, pady=(0, 16), expand=True)
        top_row.columnconfigure(0, weight=1, uniform="two_col")
        top_row.columnconfigure(1, weight=2, uniform="two_col")
        top_row.rowconfigure(0, weight=1)

        sizes_frame = tk.Frame(
            top_row,
            bg=self._colors["card"],
            highlightbackground=self._colors["border"],
            highlightthickness=1,
        )
        sizes_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        sizes_section = ttk.Frame(sizes_frame, style="Card.TFrame")
        sizes_section.pack(fill="both", expand=True, padx=16, pady=12)
        sizes_section.columnconfigure(0, weight=1)
        ttk.Label(sizes_section, text="Size options", style="Card.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )

        ttk.Label(sizes_section, text="Custom size", style="Card.TLabel").grid(
            row=1, column=0, sticky="w"
        )
        custom_size_row = ttk.Frame(sizes_section, style="Card.TFrame")
        custom_size_row.grid(row=2, column=0, sticky="ew", pady=(4, 12))
        custom_size_row.columnconfigure(0, weight=1)
        self._custom_size_var = tk.StringVar()
        self._custom_size_entry = ttk.Entry(
            custom_size_row, textvariable=self._custom_size_var, width=14, style="App.TEntry"
        )
        self._custom_size_entry.grid(row=0, column=0, sticky="ew")
        self._add_size_button = ttk.Button(
            custom_size_row, text="Add", style="Secondary.TButton", command=self._add_custom_size
        )
        self._add_size_button.grid(row=0, column=1, padx=(8, 0))

        ttk.Label(sizes_section, text="Available sizes", style="Card.TLabel").grid(
            row=3, column=0, sticky="w"
        )
        self._sizes_list = tk.Listbox(
            sizes_section,
            height=6,
            bg=self._colors["input_bg"],
            fg=self._colors["text"],
            selectbackground=self._colors["primary"],
            selectforeground="white",
            highlightthickness=1,
            highlightbackground=self._colors["border"],
            relief="flat",
        )
        self._sizes_list.grid(row=4, column=0, sticky="ew")

        item_frame = tk.Frame(
            top_row,
            bg=self._colors["card"],
            highlightbackground=self._colors["border"],
            highlightthickness=1,
        )
        item_frame.grid(row=0, column=1, sticky="nsew")
        item_section = ttk.Frame(item_frame, style="Card.TFrame")
        item_section.pack(fill="both", expand=True, padx=16, pady=12)
        item_section.columnconfigure(2, weight=1)
        ttk.Label(item_section, text="Item to search", style="Card.TLabel").grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8)
        )

        ttk.Label(item_section, text="Brand", style="Card.TLabel").grid(row=1, column=0, sticky="w")
        self._brand_var = tk.StringVar(value=self._brands[0])
        self._brand_combo = ttk.Combobox(
            item_section,
            textvariable=self._brand_var,
            values=self._brands,
            width=12,
            state="readonly",
            style="App.TCombobox",
        )
        self._brand_combo.grid(row=2, column=0, padx=(0, 16), pady=(4, 12), sticky="w")

        ttk.Label(item_section, text="Size", style="Card.TLabel").grid(row=1, column=1, sticky="w")
        self._size_var = tk.StringVar()
        self._size_combo = ttk.Combobox(
            item_section,
            textvariable=self._size_var,
            values=self._sizes,
            width=12,
            state="readonly",
            style="App.TCombobox",
        )
        self._size_combo.grid(row=2, column=1, padx=(0, 12), pady=(4, 12), sticky="w")

        ttk.Label(item_section, text="Item link", style="Card.TLabel").grid(
            row=3, column=0, sticky="w", pady=(6, 0)
        )
        self._url_var = tk.StringVar()
        self._url_entry = ttk.Entry(item_section, textvariable=self._url_var, style="App.TEntry")
        self._url_entry.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(4, 0))

        self._add_item_button = ttk.Button(
            item_section, text="Add item to search", style="Primary.TButton", command=self._add_item
        )
        self._add_item_button.grid(row=5, column=2, pady=(10, 0), sticky="e")

        items_row = ttk.Frame(self, style="App.TFrame")
        items_row.pack(fill="both", padx=26, pady=(0, 16), expand=True)
        items_row.columnconfigure(0, weight=1, uniform="two_col")
        items_row.columnconfigure(1, weight=2, uniform="two_col")
        items_row.rowconfigure(0, weight=1)

        timing_frame = tk.Frame(
            items_row,
            bg=self._colors["card"],
            highlightbackground=self._colors["border"],
            highlightthickness=1,
        )
        timing_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        timing_inner = ttk.Frame(timing_frame, style="Card.TFrame")
        timing_inner.pack(fill="both", expand=True, padx=16, pady=12)
        timing_inner.columnconfigure(1, weight=1)

        ttk.Label(timing_inner, text="Check interval (seconds)", style="Card.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
        )
        ttk.Label(timing_inner, text="Min", style="Card.TLabel").grid(row=1, column=0, sticky="w")
        self._sleep_min_entry = ttk.Entry(
            timing_inner, textvariable=self._sleep_min_var, width=10, style="App.TEntry"
        )
        self._sleep_min_entry.grid(row=2, column=0, sticky="w", pady=(4, 16), padx=(0, 12))

        ttk.Label(timing_inner, text="Max", style="Card.TLabel").grid(row=1, column=1, sticky="w")
        self._sleep_max_entry = ttk.Entry(
            timing_inner, textvariable=self._sleep_max_var, width=10, style="App.TEntry"
        )
        self._sleep_max_entry.grid(row=2, column=1, sticky="w", pady=(4, 16))

        list_frame = tk.Frame(
            items_row,
            bg=self._colors["card"],
            highlightbackground=self._colors["border"],
            highlightthickness=1,
        )
        list_frame.grid(row=0, column=1, sticky="nsew")
        list_inner = ttk.Frame(list_frame, style="Card.TFrame")
        list_inner.pack(fill="both", expand=True, padx=16, pady=12)

        title_row = ttk.Frame(list_inner, style="Card.TFrame")
        title_row.pack(fill="x", pady=(0, 8))
        ttk.Label(title_row, text="Items", style="Card.TLabel").pack(side="left")

        self._items_list = tk.Listbox(
            list_inner,
            height=6,
            bg=self._colors["input_bg"],
            fg=self._colors["text"],
            selectbackground=self._colors["primary"],
            selectforeground="white",
            highlightthickness=1,
            highlightbackground=self._colors["border"],
            relief="flat",
        )
        self._items_list.pack(side="left", fill="both", expand=True)

        list_scroll = ttk.Scrollbar(list_inner, orient="vertical", command=self._items_list.yview)
        list_scroll.pack(side="left", fill="y", padx=(6, 0))
        self._items_list.configure(yscrollcommand=list_scroll.set)

        list_controls = ttk.Frame(list_inner, style="Card.TFrame")
        list_controls.pack(side="left", fill="y", padx=(12, 0))

        self._remove_item_button = ttk.Button(
            list_controls, text="Remove", style="Secondary.TButton", command=self._remove_item
        )
        self._remove_item_button.pack(anchor="n", pady=(28, 0))

        config_row = ttk.Frame(self, style="App.TFrame")
        config_row.pack(fill="both", padx=26, pady=(0, 16), expand=True)
        config_row.columnconfigure(0, weight=1, uniform="two_col")
        config_row.columnconfigure(1, weight=2, uniform="two_col")
        config_row.rowconfigure(0, weight=1)

        bot_frame = tk.Frame(
            config_row,
            bg=self._colors["card"],
            highlightbackground=self._colors["border"],
            highlightthickness=1,
        )
        bot_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        bot_inner = ttk.Frame(bot_frame, style="Card.TFrame")
        bot_inner.pack(fill="both", expand=True, padx=16, pady=12)
        bot_inner.columnconfigure(2, weight=1)

        ttk.Label(bot_inner, text="Bot configuration (optional)", style="Card.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 8), columnspan=2
        )

        ttk.Label(bot_inner, text="BOT API", style="Card.TLabel").grid(
            row=1, column=0, sticky="w", pady=(0, 2)
        )
        bot_api_row = ttk.Frame(bot_inner, style="Card.TFrame")
        bot_api_row.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(4, 12))
        bot_api_row.columnconfigure(0, weight=1)
        self._bot_api_entry = ttk.Entry(
            bot_api_row, textvariable=self._bot_api_var, show="*", style="App.TEntry"
        )
        self._bot_api_entry.grid(row=0, column=0, sticky="ew")
        self._bot_api_toggle = ttk.Button(
            bot_api_row, text="Show", style="Secondary.TButton", command=self._toggle_bot_api
        )
        self._bot_api_toggle.grid(row=0, column=1, padx=(8, 0), sticky="e")

        ttk.Label(bot_inner, text="Chat ID", style="Card.TLabel").grid(
            row=3, column=0, sticky="w", pady=(0, 2)
        )
        chat_id_row = ttk.Frame(bot_inner, style="Card.TFrame")
        chat_id_row.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(4, 12))
        chat_id_row.columnconfigure(0, weight=1)
        self._chat_id_entry = ttk.Entry(
            chat_id_row, textvariable=self._chat_id_var, show="*", style="App.TEntry"
        )
        self._chat_id_entry.grid(row=0, column=0, sticky="ew")
        self._chat_id_toggle = ttk.Button(
            chat_id_row, text="Show", style="Secondary.TButton", command=self._toggle_chat_id
        )
        self._chat_id_toggle.grid(row=0, column=1, padx=(8, 0), sticky="e")

        self._sound_check = ttk.Checkbutton(
            bot_inner, text="Notification sound", variable=self._play_sound_var
        )
        self._sound_check.grid(row=5, column=0, sticky="w", pady=(6, 0))

        log_frame = tk.Frame(
            config_row,
            bg=self._colors["card"],
            highlightbackground=self._colors["border"],
            highlightthickness=1,
        )
        log_frame.grid(row=0, column=1, sticky="nsew")
        log_inner = ttk.Frame(log_frame, style="Card.TFrame")
        log_inner.pack(fill="both", expand=True, padx=16, pady=12)

        ttk.Label(log_inner, text="Terminal", style="Card.TLabel").pack(anchor="w", pady=(0, 8))

        self._log_text = tk.Text(
            log_inner,
            height=12,
            wrap="word",
            state="disabled",
            bg=self._colors["input_bg"],
            fg=self._colors["text"],
            highlightthickness=1,
            highlightbackground=self._colors["border"],
            relief="flat",
        )
        self._log_text.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(log_inner, orient="vertical", command=self._log_text.yview)
        scrollbar.pack(side="left", fill="y", padx=(6, 0))
        self._log_text.configure(yscrollcommand=scrollbar.set)

        controls = ttk.Frame(self, style="App.TFrame")
        controls.pack(fill="x", padx=26, pady=(0, 20))

        self._start_button = ttk.Button(
            controls, text="Start", style="Primary.TButton", command=self._start
        )
        self._start_button.pack(side="left")

        self._stop_button = ttk.Button(
            controls, text="Stop", style="Secondary.TButton", command=self._stop, state="disabled"
        )
        self._stop_button.pack(side="left", padx=8)

        self._refresh_items_list()
        self._refresh_sizes_list()

    def _add_custom_size(self):
        size = self._custom_size_var.get().strip()
        if not size:
            return
        if size not in self._sizes:
            self._sizes.append(size)
            self._size_combo["values"] = self._sizes
            self._refresh_sizes_list()
        self._size_var.set(size)
        self._log(f"Added size: {size}")
        self._custom_size_var.set("")

    def _refresh_sizes_list(self):
        self._sizes_list.delete(0, "end")
        for size in self._sizes:
            self._sizes_list.insert("end", size)

    def _add_item(self):
        url = self._url_var.get().strip()
        if not url:
            self._log("Please enter a product link.")
            return
        size = self._size_var.get().strip()
        if not size:
            self._log("Please select a size for this item.")
            return

        item = {"store": self._brand_var.get(), "url": url, "sizes": [size]}
        self._items.append(item)
        self._refresh_items_list()
        self._url_var.set("")
        self._log(f"Added item: {item['store']} | {size} | {url}")

    def _remove_item(self):
        selection = self._items_list.curselection()
        if not selection:
            return
        index = selection[0]
        if index >= len(self._items):
            return
        removed = self._items.pop(index)
        self._refresh_items_list()
        self._log(f"Removed item: {removed.get('store')} | {removed.get('url')}")

    def _refresh_items_list(self):
        self._items_list.delete(0, "end")
        for item in self._items:
            sizes = item.get("sizes") or []
            size_label = ", ".join(sizes) if sizes else "any size"
            self._items_list.insert("end", f"{item.get('store')} | {size_label} | {item.get('url')}")

    def _toggle_bot_api(self):
        self._bot_api_show = not self._bot_api_show
        self._bot_api_entry.config(show="" if self._bot_api_show else "*")
        self._bot_api_toggle.config(text="Hide" if self._bot_api_show else "Show")

    def _toggle_chat_id(self):
        self._chat_id_show = not self._chat_id_show
        self._chat_id_entry.config(show="" if self._chat_id_show else "*")
        self._chat_id_toggle.config(text="Hide" if self._chat_id_show else "Show")

    def _start(self):
        if self._worker_thread and self._worker_thread.is_alive():
            return
        try:
            sleep_min = int(self._sleep_min_var.get())
            sleep_max = int(self._sleep_max_var.get())
        except (TypeError, ValueError):
            self._log("Please enter valid numbers for min/max seconds.")
            return
        if sleep_min <= 0 or sleep_max <= 0 or sleep_min > sleep_max:
            self._log("Min seconds must be > 0 and <= Max seconds.")
            return
        self._sleep_min_seconds = sleep_min
        self._sleep_max_seconds = sleep_max
        self._stop_event.clear()
        self._queue_status("Running")
        self._start_button.config(state="disabled")
        self._stop_button.config(state="normal")

        self._worker_thread = threading.Thread(
            target=self._run_checker, name="checker-thread", daemon=True
        )
        self._worker_thread.start()

    def _stop(self):
        if not self._worker_thread:
            return
        self._stop_event.set()
        self._queue_status("Stopping...")
        self._stop_button.config(state="disabled")

    def _run_checker(self):
        run_checker(
            stop_event=self._stop_event,
            log=self._log,
            items=list(self._items),
            sizes=list(self._sizes),
            sleep_min_seconds=self._sleep_min_seconds,
            sleep_max_seconds=self._sleep_max_seconds,
            bot_api=self._bot_api_var.get().strip() or None,
            chat_id=self._chat_id_var.get().strip() or None,
            play_sound_on_found=self._play_sound_var.get(),
        )
        self._queue_status("Idle")
        self._log_queue.put(("controls", "reset"))

    def _log(self, message):
        self._log_queue.put(("log", message))

    def _queue_status(self, message):
        self._log_queue.put(("status", message))

    def _drain_queue(self):
        while True:
            try:
                item_type, message = self._log_queue.get_nowait()
            except queue.Empty:
                break

            if item_type == "log":
                self._log_text.config(state="normal")
                self._log_text.insert("end", message + "\n")
                self._log_text.see("end")
                self._log_text.config(state="disabled")
            elif item_type == "status":
                self._status_var.set(message)
                status_color = self._colors["primary"]
                if message.lower().startswith("idle"):
                    status_color = self._colors["muted"]
                elif message.lower().startswith("stopping"):
                    status_color = self._colors["primary_hover"]
                self._status_badge.config(bg=status_color)
            elif item_type == "controls" and message == "reset":
                self._start_button.config(state="normal")
                self._stop_button.config(state="disabled")

        self.after(100, self._drain_queue)


if __name__ == "__main__":
    app = ZaraStockCheckerApp()
    app.mainloop()

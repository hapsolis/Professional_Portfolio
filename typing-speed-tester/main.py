# Day 86 – Typing Speed Test
# 100 Days of Code – Dr. Angela Yu Python Bootcamp
# ------------------------------------------------------------
# Goal:
# Build a desktop GUI app that measures typing speed (WPM – words per minute).
# - Show a paragraph of sample text
# - User types in a text box
# - Timer starts when user begins typing (60 seconds)
# - At the end: calculate WPM + basic accuracy
# - Show results + restart option
#
# Design choices (inspired by common typing tests like typing-speed-test.aoeu.eu):
# • 60-second countdown test
# • Timer starts on first keystroke
# • User types the whole paragraph (space-separated words)
# • Highlight current expected word
# • Show live WPM / timer / accuracy during typing (optional stretch)
# • Simple, clean UI similar to Day 85 watermark app style
#
# Libraries used:
# • tkinter     → GUI
# • threading   → run countdown timer without freezing GUI
# • random      → pick random paragraph (future extension)

# ----------------------------
# IMPORTS
# ----------------------------
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random


# ----------------------------
# GLOBAL VARIABLES / STATE
# ----------------------------
class TypingTest:
    """
    • Creates and manages all GUI elements
    • Holds test state (current text, word index, timer, typed words...)
    • Coordinates flow between display, input, timer, and result calculation
    • Responds to user actions (keystrokes, buttons)

    Important attributes (state):
        current_text        str         full paragraph being typed
        words               list[str]   split version of current_text
        current_word_index  int         which word the user should type next
        typed_words         list[str]   words the user has completed (space-separated)
        timer_running       bool
        time_left           int         seconds remaining
        start_time          float       time.time() when typing began

    Main flow / lifecycle:
        1. __init__ → setup_ui() → start_new_test()
        2. User presses first key → on_key_release() starts timer thread
        3. Every keystroke → on_key_release() checks progress
        4. Space/Enter → word completed → advance index, update highlight
        5. Timer reaches 0 or all words typed → finish_test()
        6. User clicks "New Test" → start_new_test() resets everything
    """

    def __init__(self, master):
        """Initialize the application and create the GUI."""
        self.master = master
        self.master.title("Typing Speed Test – Day 86")
        self.master.geometry("900x650+320+80")  # would place it 320 pixels from the left edge and 80 pixels from the top edge of the screen
        self.master.resizable(False, False)     # Blocks the maximize button and prevents the user from manually resizing the window.

        # ── State initialization ──
        self.current_text = ""
        self.words = []
        self.current_word_index = 0
        self.typed_words = []
        self.timer_running = False
        self.time_left = 60
        self.start_time = 0
        self.timer_thread = None

        self.sample_texts = self._load_paragraphs()

        self.setup_ui()           # Create all widgets
        self.start_new_test()     # Load first text & prepare test



    # ──────────────────────────────────────────────────────────────────────────
    #                           GUI CONSTRUCTION
    # ──────────────────────────────────────────────────────────────────────────

    def setup_ui(self):
        """
        Creates and lays out all visual elements.
        Called once during __init__.

        Widgets created (and stored as attributes when needed):
        • title_label
        • text_display     (tk.Text – shows paragraph, read-only)
        • entry            (ttk.Entry – where user types)
        • timer_label, wpm_label, accuracy_label
        • restart_button

        Bindings:
        • <KeyRelease> on entry → self.on_key_release
        """
        # main_frame  ---------------------------------------------------------------------

        main_frame = ttk.Frame(self.master, padding="20 20 20 20") #Left, Top, Right, and Bottom
        main_frame.pack(fill=tk.BOTH, expand=True)  #It stretches in both directions (width and height).

                                            # Title
        ttk.Label(
            main_frame,
            text="Typing Speed Test",
            font=("Helvetica", 24, "bold")
        ).pack(pady=(0, 20)) # 0 pixels of extra space above, and  20 pixels of space below the text,

                                            # Instructions
        ttk.Label(
            main_frame,
            text="Type the text below as fast and accurately as possible.\nTimer starts on first keystroke.",
            justify="center",
            font=("Helvetica", 11)
        ).pack(pady=(0, 15))

                                # Text to type (read-only) Displays paragraphs or documents.
        self.text_display = tk.Text(
            main_frame,
            height=8,
            width=80,
            wrap=tk.WORD, #Ensures that lines break at whole words
            font=("Consolas", 13),
            spacing1=6,
            spacing3=6,
            padx=10,
            pady=10,
            state=tk.DISABLED   # makes it a read-only display
        )
        self.text_display.pack(pady=10)

                                                        # Typing input label
        ttk.Label(
            main_frame,
            text="Start typing here:",
            font=("Helvetica", 12)
        ).pack(anchor="w", pady=(15, 5))

                                                     # Entry field
        self.entry = ttk.Entry(
            main_frame,
            font=("Consolas", 14),
            width=80
        )

        self.entry.pack(pady=5)

        # Tkinter automatically calls self.on_key_release and passes it an object called event
        # (which contains information such as which key was pressed).
        self.entry.bind("<KeyRelease>", self.on_key_release)
        self.entry.focus_set()

        # Status bar---------------------------------------------------------------------
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=0) # It only stretches horizontally


                    # Dynamic labels that will be updated during the test to show real-time stats
        self.timer_label = ttk.Label(status_frame, text="Time: 60 s", font=("Helvetica", 12))
        self.timer_label.pack(side=tk.LEFT, padx=30, expand=True)

        self.wpm_label = ttk.Label(status_frame, text="WPM: —", font=("Helvetica", 12))
        self.wpm_label.pack(side=tk.LEFT, padx=60, expand=True)  # wider spacing for balance

        self.accuracy_label = ttk.Label(status_frame, text="Accuracy: —", font=("Helvetica", 12))
        self.accuracy_label.pack(side=tk.LEFT, padx=30, expand=True)

        # Buttons---------------------------------------------------------------------
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)

        self.restart_button = ttk.Button(
            btn_frame,
            text="New Test",
            command=self.start_new_test,
            width=15
        )
        self.restart_button.pack(side=tk.LEFT, padx=15)

        ttk.Button(
            btn_frame,
            text="Quit",
            command=self.master.quit,
            width=15
        ).pack(side=tk.LEFT, padx=15)

    # ──────────────────────────────────────────────────────────────────────────
    #                         TEST LIFECYCLE METHODS
    # ──────────────────────────────────────────────────────────────────────────
    def _load_paragraphs(self, file_path="paragraphs.txt"):
        """Loads paragraphs when the app starts"""
        try:
            with open(file_path, encoding="utf-8") as file:
                content = file.read()
            raw_blocks = content.split("\n\n")
            paragraphs = [block.strip() for block in raw_blocks if block.strip()]
            if not paragraphs:
                raise ValueError("No valid paragraphs found")
            print(f"Loaded {len(paragraphs)} paragraphs")
            return paragraphs
        except Exception as e:
            print(f"Could not load paragraphs: {e}. Using fallback.")
            return ["The quick brown fox jumps over the lazy dog."]


    def start_new_test(self):
        """
        Reset state and prepare a new test.
        Called when:
        • Application starts (__init__)
        • User clicks "New Test" button

        Actions:
        1. Clear input & state variables
        2. Pick random paragraph
        3. Split into words
        4. Show text in display widget
        5. Highlight first word
        6. Reset labels & timer display
        """
        self.entry.delete(0, tk.END)
        # tk.NORMAL  Re-enables the widget so the user can click on it and type.
        self.entry.config(state=tk.NORMAL, foreground="black")
        self.timer_running = False
        self.time_left = 60
        self.current_word_index = 0
        self.typed_words = []
        self.start_time = 0

                                            # Select new text
        self.current_text = random.choice(self.sample_texts)
        self.words = self.current_text.split() #Splits on any whitespace to  get a clean list of the actual words

                                            # Update display
        self.text_display.config(state=tk.NORMAL)
        self.text_display.delete("1.0", tk.END) # line 1, column 0
        self.text_display.insert(tk.END, self.current_text)

        self.highlight_current_word()           # <==== Highlighted word

        # tk.DISABLED  Blocks the widget so the user can't click on it and type.
        self.text_display.config(state=tk.DISABLED)

                                         # Reset status labels
        self.timer_label.config(text="Time: 60 s")
        self.wpm_label.config(text="WPM: __")
        self.accuracy_label.config(text="Accuracy: __")

        self.entry.focus_set()

    def highlight_current_word(self):
        """
        Visually mark the word the user is expected to type next.
        Called from:
        • start_new_test()          → to highlight the first word
        • on_key_release()          → after a word is completed (space/enter)

        Uses Text widget tags to apply yellow background.
        """
        self.text_display.tag_remove("current", "1.0", tk.END) # Clean the whole box from highlighted words

        if self.current_word_index >= len(self.words):
            return

        # Calculate character position of current word
        # Tkinter uses "line.column" strings, and YOU CAN DO MATH inside them.
        text_before = " ".join(self.words[:self.current_word_index])
        offset = len(text_before)       # fills the gap between “the block of previous words” and “the current word.”
        if self.current_word_index > 0:
            offset += 1  # space

        start = f"1.0 + {offset} chars"
        end   = f"{start} + {len(self.words[self.current_word_index])} chars"

        self.text_display.tag_add("current", start, end)
        self.text_display.tag_config("current", background="yellow", foreground="black")

    # ──────────────────────────────────────────────────────────────────────────
    #                         TYPING & TIMER LOGIC
    # ──────────────────────────────────────────────────────────────────────────

    def on_key_release(self, event):
        """
        Called from:
        • setup_ui()

        Core typing handler – called on EVERY keystroke in the entry field.

        Responsibilities:
        1. Start timer on first keystroke
        2. Detect completed words (space or enter)
        3. Advance current_word_index when word is finished
        4. Provide live visual feedback (red text = mismatch)
        5. Check for early finish (all words typed)
        """

        typed_so_far = self.entry.get().strip()

        # ── Start timer on first real input ──
        if not self.timer_running and typed_so_far:
            self.timer_running = True
            self.start_time = time.time()

            # Launch the countdown timer in a separate background thread. This prevents the GUI from freezing while the
            # clock counts down.
            # 'daemon=True' ensures the timer stops automatically if the window is closed.           #
            self.timer_thread = threading.Thread(target=self.countdown, daemon=True)
            self.timer_thread.start()

        # ── Word completion (space or enter) ──
        if event.keysym in ("space", "Return") and typed_so_far: # empty string ("") counts as False
            self.typed_words.append(typed_so_far)   # calculate WPM or accuracy.
            self.current_word_index += 1    # only place where actually grows during a test
            self.highlight_current_word()
            self.entry.delete(0, tk.END)    # Clears the entry box
            self.update_live_stats()

            # Early finish: user typed everything before timer ended
            if self.current_word_index >= len(self.words):
                self.finish_test()   # <--- This triggers the end of the test

        # ── Live mismatch feedback ──
        else:
            current_word = self.words[self.current_word_index]
            expected = current_word[:len(typed_so_far)]
            if typed_so_far != expected:
                self.entry.config(foreground="red")
            else:
                self.entry.config(foreground="black")

    def countdown(self):
        """
        Background timer – runs in separate thread.
        - Tkinter isn’t thread-safe: only the main thread that created the widgets should touch them -
        Decrements time_left every second and updates GUI via after().
        Stops when time_left == 0 → triggers finish_test().
        """
        while self.time_left > 0 and self.timer_running:
            time.sleep(1)
            self.time_left -= 1
            self.master.after(ms= 0, func= self.update_timer_display)

        if self.timer_running:
            self.master.after(ms= 0, func= self.finish_test)

    def update_timer_display(self):
        """Refresh timer label (called from countdown thread via after)."""
        self.timer_label.config(text=f"Time: {self.time_left} s")

    def update_live_stats(self):
        """
        Optional live WPM & accuracy display.
        Called after each completed word.
        """
        if not self.start_time:
            return
        elapsed = time.time() - self.start_time
        if elapsed < 1: #  # avoid divide-by-zero in the first second
            return

        correct = sum(1 for a, b in zip(self.typed_words, self.words) if a == b)
        wpm = (len(self.typed_words) / elapsed) * 60
        acc = (correct / len(self.typed_words)) * 100 if self.typed_words else 100

        self.wpm_label.config(text=f"WPM: {int(wpm)}")
        self.accuracy_label.config(text=f"Accuracy: {int(acc)}%")

    def finish_test(self):
        """
        End of test – calculate final stats and show results popup.
        Called when:
        • Timer reaches 0 (from countdown)
        • User typed all words early (from on_key_release)
        """
        self.timer_running = False
        self.entry.config(state=tk.DISABLED)

        elapsed = 60 if self.time_left <= 0 else (time.time() - self.start_time)
        typed_count = len(self.typed_words)
        correct = sum(1 for a, b in zip(self.typed_words, self.words) if a == b)

        wpm = (typed_count / elapsed) * 60 if elapsed > 0 else 0
        accuracy = (correct / typed_count * 100) if typed_count > 0 else 100

        message = (
            f"Test finished!\n\n"
            f"Words typed: {typed_count}\n"
            f"Correct: {correct}\n"
            f"Time: {elapsed:.1f} s\n"
            f"WPM: {int(wpm)}\n"
            f"Accuracy: {int(accuracy)}%\n\n"
            f"Average: ~40 WPM    Excellent: 100+ WPM"
        )

        messagebox.showinfo("Results", message)
        # Entry is re-enabled when user clicks New Test

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = TypingTest(root)
    root.mainloop()
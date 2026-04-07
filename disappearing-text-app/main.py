# ---------------------------- DISAPPEARING TEXT WRITING APP ------------------------------- #
# Day 90 of 100 Days of Code - Dr. Angela Yu's Python Bootcamp
# Project: A modern desktop version of "The Most Dangerous Writing App"
# Features:
#   - Large, distraction-free text editor
#   - Inactivity timer (5/10/15 seconds) – text disappears if you stop typing
#   - Real-time warning + countdown when inactivity is detected
#   - Manual "Save" button to export current text as .txt
#   - Timer selector, motivational header, clean dark modern UI
#   - Optional Hardcore Mode (hides text while typing + disables backspace/delete)

import tkinter as tk
from tkinter import messagebox, filedialog
import os
from datetime import datetime


# ──────────────────────────────────────────────────────────────────────────
#                         CONSTANTS
# ──────────────────────────────────────────────────────────────────────────

DEFAULT_INACTIVITY_SECONDS = 5
INACTIVITY_OPTIONS = [5, 10, 15]
BG_COLOR = "#6367FF"          # Deep Blue/Purple (Main Background)
TEXT_BG = "#8494FF"           # Medium Blue (Editor Area)
ACCENT_COLOR = "#FFDBFD"      # Soft Pink (Titles and Save Button)
TEXT_COLOR = "#ffffff"        # White (Main Text)
FONT_FAMILY = "Helvetica"
TITLE_FONT = (FONT_FAMILY, 28, "bold")
HEADER_FONT = (FONT_FAMILY, 16, "bold")
BODY_FONT = (FONT_FAMILY, 14)



# ──────────────────────────────────────────────────────────────────────────
#                         MAIN APPLICATION CLASS
# ──────────────────────────────────────────────────────────────────────────

class DisappearingTextApp:
    """
    ENTRY POINT: Initializes the application state and UI.

    Logic Scope:
    - Sets up the root window and global state variables (timers, hardcore mode).
    - Orchestrates the initial build by calling setup_ui().
    - Starts the primary app heartbeat by calling start_inactivity_timer().
    - Establishes the link between the OS and the app via <KeyRelease> binding.
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Disappearing Text • Write or Lose It")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("1000x700+280+50")
        self.root.minsize(800, 600)
        self.root.resizable(False, False)  # Blocks the maximize button and prevents the user from manually resizing the window.

        # ── State variables ──
        self.inactivity_time = DEFAULT_INACTIVITY_SECONDS
        self.timer_id = None
        self.countdown_id = None
        self.countdown_remaining = 0
        self.hardcore_mode = tk.BooleanVar(value=False)
        self.is_warning_active = False

        # ── Interface ──
        self.setup_ui()
        self.start_inactivity_timer()

        # Bind key release globally on the text widget to reset timer and passes it the event object
        self.text_widget.bind(sequence="<KeyPress>", func= self.on_key_press)

        # method that intercepts OS signals, and links it with the on_closing method
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ──────────────────────────────────────────────────────────────────────────
    #                         UI SETUP
    # ──────────────────────────────────────────────────────────────────────────

    def setup_ui(self):
        """
        Constructs the visual environment and maps UI events to logic.

        Logic Scope:
        - Called exclusively by __init__ during startup.
        - Defines the geometry and styling of widgets.
        - Hooks the 'Save' button to manual_save() and the dropdown to change_inactivity_time().
        - Creates the 'warning_label' which acts as the visual bridge during the danger phase.
        """
        # ------------------------------------- Main container with padding -------------------------------------
        main_frame = tk.Frame(self.root, bg=BG_COLOR, padx=40, pady=30)
        main_frame.pack(fill="both", expand=True)

        # ----------------------------  Title / Motivational Header ----------------------------
        title_label = tk.Label(
            main_frame,
            text="WRITE OR IT DISAPPEARS",
            font=TITLE_FONT,
            fg=ACCENT_COLOR,
            bg=BG_COLOR
        )
        title_label.pack(pady=(0, 10))

        subtitle = tk.Label(
            main_frame,
            text="Don't stop typing. Every pause has consequences.",
            font=(FONT_FAMILY, 12),
            fg="#C9BEFF", # Soft light purple for contrast
            bg=BG_COLOR
        )
        subtitle.pack(pady=(0, 30))

        # ---------------------------- Controls Frame (Timer selector + Hardcore + Save) -------------------------------------

        controls_frame = tk.Frame(main_frame, bg=BG_COLOR)
        controls_frame.pack(fill="x", pady=(0, 20)) # fill="x" ensures that this bar occupies the entire available width.

                                                    # Inactivity Timer LABEL
        tk.Label(
            controls_frame,
            text="Inactivity Limit:",
            font=HEADER_FONT,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        ).pack(side="left")


        self.timer_var = tk.StringVar(value=str(DEFAULT_INACTIVITY_SECONDS))  # Tkinter ControlVariable (communication protocol) for selected position,treats everything as text

                                                # Inactivity Timer Selector

        timer_menu = tk.OptionMenu(
            controls_frame,
            self.timer_var,
            *[str(opt) for opt in INACTIVITY_OPTIONS],  # The * Unpacks the list into individual arguments for the menu
            command=self.change_inactivity_time         #  <======= Helper function
        )

        timer_menu.config(
            font=BODY_FONT,
            bg=TEXT_BG,
            fg=TEXT_COLOR,
            highlightthickness=0
        )
        timer_menu["menu"].config(bg="white", fg=BG_COLOR)
        timer_menu.pack(side="left", padx=(10, 30))

                                                # Hardcore Mode Checkbox

        hardcore_check = tk.Checkbutton(
            controls_frame,
            text="Hardcore Mode (hide text + no backspace)",
            variable=self.hardcore_mode,
            font=BODY_FONT,
            fg="yellow",
            bg=BG_COLOR,
            selectcolor=TEXT_BG,
            command=self.toggle_hardcore_mode  #  <======= Helper function
        )
        hardcore_check.pack(side="left")

                                                         # Save Button

        save_btn = tk.Button(
            controls_frame,
            text="💾 Save Now",
            font=HEADER_FONT,
            bg=ACCENT_COLOR,
            fg=BG_COLOR,
            padx=20,
            pady=8,
            relief="flat",
            command=self.manual_save            #  <======= Helper function
        )
        save_btn.pack(side="right")

        # ------------------------------------- Text Editor Area -------------------------------------
        # Warning / Countdown Label (initially hidden)
        self.warning_label = tk.Label(
            main_frame,
            text="",
            font=(FONT_FAMILY, 18, "bold"),
            fg="yellow",
            bg=BG_COLOR,
            pady=10
        )
        self.warning_label.pack(side="bottom", pady=(10, 2))


        editor_frame = tk.Frame(main_frame, bg=TEXT_BG, padx=20, pady=20)
        editor_frame.pack(fill="both", expand=True)

        self.text_widget = tk.Text(
            editor_frame,
            font=(FONT_FAMILY, 16),
            bg=TEXT_BG,
            fg=TEXT_COLOR,
            insertbackground=ACCENT_COLOR,
            wrap="word",        # Ensures that lines break at whole words
            undo=True,          # Enable basic Undo/Redo (but hardcore will limit it)
            padx=15,
            pady=15,
            relief="flat",
            highlightthickness=2,
            highlightbackground=BG_COLOR,
            highlightcolor=ACCENT_COLOR
        )
        self.text_widget.pack(fill="both", expand=True)

    # ──────────────────────────────────────────────────────────────────────────
    #                         TIMER LOGIC
    # ──────────────────────────────────────────────────────────────────────────


    def start_inactivity_timer(self):
        """
        Manages the primary 'inactivity' countdown.

        Logic:
        - Called by __init__ (startup), on_key_release (reset), and change_inactivity_time (update).
        - Crucial Step: Cancels any existing 'timer_id' to prevent multiple clocks from overlapping.
        - Schedules the execution of trigger_disappear() after the user-defined delay.
        """
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)

        # .after() returns a unique ID string to interact with the program
        self.timer_id = self.root.after(
                                            ms= self.inactivity_time * 1000,
                                            func = self.trigger_disappear
                                        )

    def on_key_press(self, event=None):
        """
        Responds to user keyboard input to keep the text alive.

        Logic Scope:
        - Triggered by the OS every time a key is released while the text widget is focused.
        - Resets the UI (clears warnings and stops the countdown_id).
        - Re-ignites the inactivity timer by calling start_inactivity_timer().
        - Serves as the primary 'safety' mechanism that prevents text deletion.
        """
        # In hardcore mode, the program still allow typing but hide the text and block certain keys
        if self.hardcore_mode.get():
            result = self.apply_hardcore_restrictions(event)
            if result == "break":
                return "break"

        # Variables used to trigger the text deletion
        self.is_warning_active = False
        self.warning_label.config(text="")

        # It fetches the ID to canceled it and turn it to none again
        if self.countdown_id is not None:
            self.root.after_cancel(self.countdown_id)
            self.countdown_id = None

        # Starts a new timer
        self.start_inactivity_timer()

    def change_inactivity_time(self, selected_value):
        """
        Synchronizes the internal timer logic with the user's UI selection.

        Logic Scope:
        - Triggered automatically by the OptionMenu widget when a new selection is made.
        - Receives the 'selected_value' string directly from the widget's internal callback.
        - Casts the string to an integer to update 'self.inactivity_time'.
        - Calls start_inactivity_timer() to override the current countdown
          with the new duration, ensuring the change is felt instantly.
        """
        self.inactivity_time = int(selected_value)
        self.start_inactivity_timer()   # Restart with new value
        self.warning_label.config(text=f"Timer updated to {self.inactivity_time}s")



    # ──────────────────────────────────────────────────────────────────────────
    #                         WARNING & DISAPPEAR LOGIC
    # ──────────────────────────────────────────────────────────────────────────


    def trigger_disappear(self):
        """
        PHASE 1: Initiates the transition from 'writing mode' to 'warning mode'.

        Logic Scope:
        - Triggered automatically by the inactivity timer when the after() time runs out.
        - Validates if the editor is empty (to avoid deleting nothing).
        - Hands off control to the recursive show_countdown_warning() method.
        """
        if not self.text_widget.get("1.0", tk.END).strip(): # Line 1, Character 0
            self.start_inactivity_timer()  # Nothing to delete
            return

        self.is_warning_active = True
        self.countdown_remaining = 5   #  <========== 5-second warning before total deletion

        self.show_countdown_warning()

    def show_countdown_warning(self):
        """
        PHASE 2: A recursive countdown.

        Logic Scope:
        - Called by trigger_disappear() and then calls itself every 1000ms.
        - Updates the UI warning label each recursive call.
        - If 'countdown_remaining' reaches zero, it executes the final deletion.
        - If interrupted by the is_warning_active flag from on_key_release(), this loop is killed via after_cancel tk method.
        """
        if not self.is_warning_active:
            return

        if self.countdown_remaining > 0:
            self.warning_label.config(
                text=f"⚠️  TEXT WILL DISAPPEAR IN {self.countdown_remaining}..."
            )
            self.countdown_remaining -= 1
            self.countdown_id = self.root.after(1000, self.show_countdown_warning)  # Recursive Functionality
        else:
            # Final deletion
            self.text_widget.delete("1.0", tk.END)
            self.warning_label.config(
                text="💥 EVERYTHING DISAPPEARED! Keep writing next time.",
                fg=ACCENT_COLOR
            )
            self.is_warning_active = False
            self.start_inactivity_timer()



    # ──────────────────────────────────────────────────────────────────────────
    #                         HARDCODE MODE
    # ──────────────────────────────────────────────────────────────────────────


    def toggle_hardcore_mode(self):
        """
        VISUAL BLINDFOLD: Toggles the visibility of the text to increase difficulty.

        Logic Scope:
        - Triggered by the BooleanVar change in the Hardcore Checkbutton.
        - Since tk.Text doesn't support 'show="•"', we simulate a mask by matching
          the foreground (text) color to the background color.
        - Updates the UI to provide clear feedback that 'Blind Mode' is active.
        - This is purely a visual layer; the internal text data remains intact for saving.
        """
        if self.hardcore_mode.get():
            self.text_widget.config(fg=TEXT_BG, insertbackground=ACCENT_COLOR)  # Hide characters
            self.warning_label.config(text="🔒 Hardcore Mode Active – No looking back!")
        else:
            self.text_widget.config(fg=TEXT_COLOR, insertbackground=ACCENT_COLOR)   # Show normal text
            self.warning_label.config(text="")

    @staticmethod
    def apply_hardcore_restrictions(event):
        """
        THE ENFORCER: A standalone helper to identify 'illegal' keys.
        """
        if event.keysym in ("BackSpace", "Delete", "Left", "Right", "Up", "Down"):
            # Returning "break" tells the OS: "Ignore this keypress. Do NOT delete the letter."
            return "break"
        return None


    # ──────────────────────────────────────────────────────────────────────────
    #                         SAVE FUNCTIONALITY
    # ──────────────────────────────────────────────────────────────────────────

    def manual_save(self):
        """
        THE SAFETY NET: Exports the current editor state to a physical file.

        Logic Scope:
        - Triggered manually by the user.
        - Operates independently of the timer logic.
        - Extracts raw string data from the Text widget and handles file I/O.
        """
        text_content = self.text_widget.get("1.0", tk.END).strip()

        if not text_content:
            messagebox.showwarning("Nothing to Save", "Write something first!")
            return

        default_name = f"writing_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text_content)
                messagebox.showinfo("Saved!", f"Session saved successfully:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save file:\n{str(e)}")



    # ──────────────────────────────────────────────────────────────────────────
    #                         WINDOW CLOSING
    # ──────────────────────────────────────────────────────────────────────────


    def on_closing(self):
        """
        EXIT GUARD: Manages the teardown of the application.

        Logic Scope:
        - Triggered by the OS when the user clicks the 'X' or closes the window.
        - Acts as a final interrupt to the mainloop to prevent accidental loss of work.
        - If the user cancels, the app's state (and timers) continues as if nothing happened.
        """
        if messagebox.askokcancel("Quit", "Are you sure you want to exit?\nUnsaved text will be lost."):
            self.root.destroy()



    # ──────────────────────────────────────────────────────────────────────────
    #                         RUN THE APP
    # ──────────────────────────────────────────────────────────────────────────

    def run(self):
        """
        Starts the infinite event loop of the application.

        Logic Scope:
        - Called by the entry point script (if __name__ == "__main__":).
        - Executes self.root.mainloop(), which allows Tkinter to begin listening for the
          keystrokes and timers defined in the other methods.
        - The app stays in this 'listening' state until on_closing() destroys the root.
        """
        self.root.mainloop()



# ──────────────────────────────────────────────────────────────────────────
#                         PROGRAM ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = DisappearingTextApp()
    app.run()
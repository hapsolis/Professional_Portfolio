# ---------------------------- PDF TO AUDIOBOOK CONVERTER ------------------------------- #
# Day 91 of 100 Days of Code - Dr. Angela Yu's Python Bootcamp
# Project: Convert PDF files to high-quality MP3 audiobooks

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import PyPDF2
import edge_tts
import asyncio
import threading
import os
from pathlib import Path
from datetime import datetime

# ---------------------------- CONSTANTS ------------------------------- #
# Custom palette from user design
PRIMARY_RED = "#D96868"     # Accents, header, buttons
LIGHT_BG = "#FBFBF6"        # Main background
MEDIUM_GREEN = "#6A7E3F"    # Success & highlights
DARK_GREEN = "#4C5C2D"      # Text and strong contrast
OFF_WHITE = "#FFFFFF"

# TTS defaults
DEFAULT_VOICE = "en-US-ChristopherNeural"
DEFAULT_RATE = 0
CHUNK_SIZE = 3000


# ──────────────────────────────────────────────────────────────────────────
#                           Data Prepare Construction
# ──────────────────────────────────────────────────────────────────────────

# ---------------------------- HELPER FUNCTIONS ------------------------------- #
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file using PyPDF2.

    Args:
        pdf_path (str): Full path to the PDF file.

    Returns:
        str: Extracted plain text.
    """
    text = ""
    try:
        # mode: r = read, b = binary
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)  # PdfReader reads the raw bytes and parses the PDF structure
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def split_text_into_chunks(text: str, chunk_size: int = CHUNK_SIZE) -> list:
    """
    Split long text into smaller chunks for reliable TTS processing.

    Args:
        text (str): Full extracted text.
        chunk_size (int): Max characters per chunk.

    Returns:
        list[str]: List of text chunks.
    """
    words = text.split()
    chunks = []
    current_chunk = []

    # for loop appends a chunk to the chunks list when it hits the limit
    for word in words:
        # If the new word overpasses the chunk_size limit and there is more than one item on current_chunk
        # it seals the packege and starts a new current_chunk list with that word as the only one on it
        if len(" ".join(current_chunk) + " " + word) > chunk_size and current_chunk: # " ".join add a space between elements
            chunks.append(" ".join(current_chunk)) # Save all the items as a "paragraph" into the chunks list
            current_chunk = [word]  # Resets and starts a new list with just the current word item

        # triggers when the word fits or in the case of a very long first word
        else:
            current_chunk.append(word)

    # It's execute on the final chunk if this didn't get to the 3k limit characters and is left over
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# ──────────────────────────────────────────────────────────────────────────
#                           Convertion Functions
# ──────────────────────────────────────────────────────────────────────────

# Async keyword tells the program that this is and asynchronous function
async def text_to_speech_async(text: str, output_path: str, voice: str, rate: int):
    """Convert text to speech using edge-tts."""
    # 'communicate' is the object that talks to the Microsoft Server
    communicate = edge_tts.Communicate(text, voice=voice, rate=f"{rate:+d}%")
    # await can only be used inside an async function, and it waits for it's code to return a response
    await communicate.save(output_path)


def convert_pdf_to_audiobook(pdf_path: str, output_dir: str, voice: str, rate: int, progress_callback, status_callback):
    """Main conversion logic running in background thread."""
    try:
        status_callback("Extracting text from PDF...")          # <========= CALLBACK STATUS
        progress_callback(10)                       # <========= callback

        text = extract_text_from_pdf(pdf_path)      # Helper function
        if not text:
            raise ValueError("No text could be extracted from the PDF.")

        status_callback("Preparing text chunks...")    # <========= CALLBACK STATUS
        progress_callback(20)   # <========= callback

        chunks = split_text_into_chunks(text)       # Helper function
        total_chunks = len(chunks)

        # Automatic unique name generation
        pdf_name = Path(pdf_path).stem
        timestamp = datetime.now().strftime("%b-%d-%Y_%I%p")
        output_file = os.path.join(output_dir, f"{pdf_name}_audiobook_{timestamp}.mp3")


        temp_files = []

        for i, chunk in enumerate(chunks):
            # Progress bar progression logic
            status_callback(f"Converting part {i+1} of {total_chunks}...")  # <========= CALLBACK STATUS
            progress = 20 + int(70 * ((i + 1) / total_chunks))

            temp_path = os.path.join(output_dir, f"temp_chunk_{i}.mp3")  #  returns the full path name for each chunk

            # asyncio.run lets the normal convert_pdf function trigger the async logic of text_to_speech_async.
            # binary Data convertion
            asyncio.run(text_to_speech_async(chunk, temp_path, voice, rate))

            temp_files.append(temp_path)

            progress_callback(progress)             # <========= callback



        status_callback("Finalizing audiobook file...")     # <========= CALLBACK STATUS

        with open(output_file, "wb") as outfile:  # "wb" (Write Binary) mode
            for temp_file in temp_files:
                with open(temp_file, "rb") as infile:   # "rb" (read Binary) mode
                    outfile.write(infile.read())

        # Cleanup section of the generated chunks
        for temp in temp_files:
            if os.path.exists(temp):
                os.remove(temp)

        progress_callback(100)  # <========= callback

        status_callback(f"✅ Audiobook created successfully!\n{output_file}")    # <========= CALLBACK STATUS




    except Exception as e:
        status_callback(f"❌ Error: {str(e)}")       # <========= CALLBACK STATUS
        progress_callback(0)    # <========= callback



# ──────────────────────────────────────────────────────────────────────────
#                           MAIN APPLICATION CLASS
# ──────────────────────────────────────────────────────────────────────────

class PdfToAudiobookApp:
    """Professional PDF to Audiobook Converter using the custom color palette."""

    def __init__(self):
        self.root = TkinterDnD.Tk() # Drag & Drop functionality
        self.root.title("PDF to Audiobook Converter")
        self.root.geometry("740x700+400+40")
        self.root.configure(bg=LIGHT_BG)
        self.root.resizable(True, True)

        # ..................... Tkinter Control Variables .....................
        self.pdf_path_var = tk.StringVar()
        self.voice_var = tk.StringVar(value=DEFAULT_VOICE)
        self.rate_var = tk.IntVar(value=DEFAULT_RATE)
        self.status_var = tk.StringVar(value="Ready — Drag & drop a PDF or click Browse")

        # ..................... Helper functions .....................
        self.setup_ui()
        # TkinterDnD object instance method that enables the Drag N' Drop functionality
        self.root.drop_target_register(DND_FILES)
        # dnd_bind connects the physical action of dropping to the program.
        self.root.dnd_bind('<<Drop>>', self.on_drop)



    # ──────────────────────────────────────────────────────────────────────────
    #                         UI SETUP
    # ──────────────────────────────────────────────────────────────────────────
    def setup_ui(self):
        """Build the UI with the new color palette distributed across all elements."""

        # ------------------------------Header ---------------------------------------

        header = tk.Frame(self.root,
                          bg=PRIMARY_RED,
                          height=90
                          )  # <==== UI parenting object section

        header.pack(fill="x")
        header.pack_propagate(False)

        title_label = tk.Label(header,
                               text="📘 PDF to Audiobook",
                               font=("Helvetica", 24, "bold"),
                               bg=PRIMARY_RED,
                               fg="white"
                               )

        title_label.pack(pady=(18, 0))

        subtitle = tk.Label(header,
                            text="Convert PDFs into natural-sounding audiobooks",
                            font=("Helvetica", 11),
                            bg=PRIMARY_RED,
                            fg="#f0f0f0"
                            )
        subtitle.pack()

        # ------------------------------Main content------------------------------------------------

        content = tk.Frame(self.root,
                           bg=LIGHT_BG
                           )      # <==== UI parenting object section

        content.pack(fill="both", expand=True, padx=40, pady=25)

        # ------------------------------Drag & Drop area ----------------------

        self.drop_frame = tk.Frame(content,
                                   bg=OFF_WHITE,
                                   height=150,
                                   relief="flat",
                                   highlightthickness=2,
                                   highlightbackground=DARK_GREEN
                                   )

        self.drop_frame.pack(fill="x", pady=(0, 20))

        self.drop_frame.pack_propagate(False)

        drop_label = tk.Label(self.drop_frame,
                              text="Drag & Drop PDF Here\nor",
                              font=("Helvetica", 14),
                              bg=OFF_WHITE,
                              fg=DARK_GREEN
                              )

        drop_label.pack(expand=True, pady=(30, 8))

        browse_btn = ttk.Button(self.drop_frame,
                                text="📂 Browse PDF File",
                                command=self.browse_pdf,
                                )

        browse_btn.pack(pady=10)

        # ------------------------------Selected file label------------------------------------------

        self.file_label = tk.Label(content,
                                   textvariable=self.pdf_path_var,
                                   wraplength=650,
                                   bg=LIGHT_BG,
                                   fg=DARK_GREEN,
                                   font=("Helvetica", 10, "underline")
                                   )

        self.file_label.pack(pady=8)

        # ------------------------------Controls frame------------------------------

        controls = tk.Frame(content,
                            bg=LIGHT_BG
                            )   # <==== UI parenting object section

        controls.pack(fill="x", pady=15)

        # ------------------------------Voice selection -----------------------------------------------

        tk.Label(controls,
                 text="Voice",
                 bg=LIGHT_BG,
                 fg=DARK_GREEN,
                 font=("Helvetica", 12, "bold")
                 ).pack(anchor="w")

        voices = ["en-US-ChristopherNeural", "en-US-EmmaNeural", "en-GB-RyanNeural",
                  "en-GB-SoniaNeural", "en-AU-WilliamNeural", "en-AU-NatashaNeural"]

        voice_combo = ttk.Combobox(controls,
                                   textvariable=self.voice_var,
                                   values=voices,
                                   state="readonly",
                                   width=50
                                   )

        voice_combo.pack(fill="x", pady=(5, 15))

        # ------------------------------Speed control---------------------------------------

        tk.Label(controls,
                 text="Speed",
                 bg=LIGHT_BG,
                 fg=DARK_GREEN,
                 font=("Helvetica", 12, "bold")
                 ).pack(anchor="w")

        speed_frame = tk.Frame(controls,
                               bg=LIGHT_BG
                               )

        speed_frame.pack(fill="x")

        speed_slider = ttk.Scale(speed_frame,
                                 from_=-50,
                                 to=50,
                                 variable=self.rate_var,
                                 orient="horizontal",
                                 command=self.update_speed_label
                                 )

        speed_slider.pack(side="left", fill="x", expand=True, pady=5)

        self.speed_value_label = tk.Label(speed_frame,
                                          text=f"{self.rate_var.get()}%",
                                          bg=LIGHT_BG,
                                          fg=DARK_GREEN,
                                          font=("Helvetica", 11, "bold")
                                          )

        self.speed_value_label.pack(side="right", padx=10)

        # ------------------------------Convert button -------------------------------------

        style = ttk.Style()
        style.configure("Accent.TButton",           # Custom Class
                        font=("Helvetica", 13, "bold"),
                        foreground= PRIMARY_RED
                        )

        self.convert_btn = ttk.Button(content,
                                      text="🚀 Convert to Audiobook",
                                      command=self.start_conversion,
                                      style="Accent.TButton"
                                      )

        self.convert_btn.pack(pady=(8, 8), ipadx=40, ipady=12)

        # ------------------------------ Progress bar --------------------------------------------

        self.progress = ttk.Progressbar(content,
                                        orient="horizontal",
                                        length=650,
                                        mode="determinate" # indeterminate: It shows a block bouncing back and forth .
                                        )

        self.progress.pack(pady=(10, 0))

        # ------------------------------Status label---------------------------------------------------------

        self.status_label = tk.Label(content,
                                     textvariable=self.status_var,
                                     bg=LIGHT_BG,
                                     fg=DARK_GREEN,
                                     font=("Helvetica", 10),
                                     justify="left",
                                     wraplength=650
                                     )

        self.status_label.pack(pady=(10, 0), ipady=5)

        # ------------------------------Footer------------------------------------------------------------

        footer = tk.Label(self.root,
                          text="Built with edge-tts • Custom palette • Day 91",
                          bg=LIGHT_BG,
                          fg=MEDIUM_GREEN,
                          font=("Helvetica", 9)
                          )

        footer.pack(side="bottom", pady=15, ipady=5)



    # ──────────────────────────────────────────────────────────────────────────
    #                         App Configuration functions
    # ──────────────────────────────────────────────────────────────────────────


    def update_speed_label(self, *args):
        """
        This method acts as a callback for the speed Scale widget. It retrieves
        the current integer value from self.rate_var and formats it as a
        percentage string for display.

        Args:
            *args: Catch-all for positional arguments passed by the Tkinter
                   event caller (e.g., the new scale value or trace metadata).
        """
        self.speed_value_label.config(text=f"{self.rate_var.get()}%")



    def on_drop(self, event):
        """
        Handles the Drag & Drop event when a file is released over the application.

        This method captures the dropped file path, if valid, it updates the application state;
        otherwise, it alerts the user.

        Args:
            event: The TkinterDnD event object containing the dropped data
                   in its .data attribute.
        """
        file_path = event.data
        # Because of how Windows Operating Systemhandle file paths with spaces.
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]

        if file_path.lower().endswith('.pdf'):
            self.pdf_path_var.set(file_path)
            self.status_var.set("PDF loaded successfully. Choose options and click Convert.")

        else:
            messagebox.showwarning("Invalid File", "Please drop a PDF file.")



    def browse_pdf(self):
        """
        Opens a native file explorer to allow the user to select a PDF.

        Uses the tkinter filedialog to filter for PDF files. If a file is selected,
        it updates the internal path variable and provides feedback via the
        status label. If the selection is cancelled, the state remains unchanged.
        """
        file = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])

        if file:

            self.pdf_path_var.set(file)
            self.status_var.set("PDF loaded successfully. Choose options and click Convert.")



    # ──────────────────────────────────────────────────────────────────────────
    #                Function helper's callbacks for convertion
    # ──────────────────────────────────────────────────────────────────────────

    def start_conversion(self):
        """
        Transitions to background processing.

        Validates the selected file and output directory, disables the UI
        to prevent multiple concurrent requests, and launches the
        heavy-lifting conversion logic in a separate daemon thread to
        keep the interface responsive.
        """
        pdf_path = self.pdf_path_var.get()

        if not pdf_path or not os.path.exists(pdf_path):
            messagebox.showerror("Error", "Please select a valid PDF file first.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Folder for Audiobook")
        if not output_dir:
            return

        self.convert_btn.config(state="disabled")
        self.status_var.set("Starting conversion...")

        thread = threading.Thread(
            target=convert_pdf_to_audiobook,
            args=(pdf_path,
                  output_dir,
                  self.voice_var.get(),
                  self.rate_var.get(),
                  self.update_progress, # Callback function
                  self.update_status),  # Callback function
            daemon=True   # Avoids that the program keeps running after closing the app
        )
        thread.start()




    def update_progress(self, value: int):
        """
        Updates the Progressbar widget and forces an immediate visual refresh.

        This method acts as the receiver for the progress_callback used in
        the conversion helper (convert_pdf_to_audiobook). It sets the widget's internal 'value' and
        calls update_idletasks to prevent the UI from appearing frozen
        during intensive background processing.

        Args:
            value (int): An integer from 0 to 100 representing completion.
        """
        # ttk.Progressbar property set to 0 by default.
        self.progress["value"] = value
        self.root.update_idletasks() # Runs every time the progress_callback() is called.



    def update_status(self, message: str):
        """
        Receives status updates from the convert_pdf_to_audiobook helper function.

        This method acts as the 'status_callback' listener. It updates the
        UI's StringVar to inform the user of current background tasks.
        When the helper signals completion (via ✅ or ❌ emojis), this method
        manages the 'reset' of the UI by re-enabling buttons and
        triggering final user notifications.

        Args:
            message (str): The current status text or final result string
                           delivered by the background thread (convert_pdf_to_audiobook).
        """
        self.status_var.set(message)
        if "✅" in message or "❌" in message:
            self.convert_btn.config(state="normal")
            if "✅" in message:
                messagebox.showinfo("Success", "Your audiobook has been created successfully!")
            else:  # This handles the ❌ case!
                messagebox.showerror("Conversion Failed", "Something went wrong. Check the status label for details.")
        self.root.update_idletasks()



    def run(self):
        self.root.mainloop()




# ──────────────────────────────────────────────────────────────────────────
#                         Main Loop
# ──────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = PdfToAudiobookApp()
    app.run()
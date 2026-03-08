import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageFont, ImageTk


# ---------------------------- CONSTANTS & GLOBAL STYLE ------------------------------- #
# ------------------------------------------------------------------------------------ #
APP_TITLE       = "Image Watermarker - Add Text or Logo Automatically"
BG_COLOR        = "#f0f0f0"
DEFAULT_OPACITY = 55
DEFAULT_FONT    = ("Arial", 10)


class WatermarkApp(tk.Tk):
    """
    Main application class for the Image Watermarker.
    Allows adding text or logo watermark to images with preview and save.
    This version uses grid() instead of pack() for layout management.
    """

    def __init__(self):
        """
        Initialize the main window, set title/geometry, create state variables
        and build the complete UI by calling create_widgets().
        """
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1150x780+200+0")    #would place it 200 pixels from the left edge and 0 pixels from the top edge of the screen
        self.minsize(900, 650)
        self.configure(bg=BG_COLOR)

        # State variables (model)
        self.original_image     = None                # PIL Image (RGB)
        self.watermarked_image  = None                # PIL Image (RGBA) — final result
        self.logo_path          = None                # str — path to logo file
        self.watermark_color    = (255, 255, 255)     # RGB tuple — default white

        self.create_widgets()                         # build UI    <=====








    # ---------------------------- UI SETUP (MAIN LAYOUT) ------------------------------- #
    # ------------------------------------------------------------------------------------ #
    def create_widgets(self):
        """
        Build and arrange all GUI elements using grid layout:
        - top action bar
        - side-by-side image display (original + preview)
        - bottom settings panel with type selector and dynamic controls
        """
                                    # 1. Main Window Grid Configuration

        # ----------------------------------------------------------------------
        # - self.columnconfigure(0, weight=1): Tells the main window's grid to make its first (and only)
        # column expandable. If the window gets wider, this column will take up the extra space.
        self.columnconfigure(0, weight=1)
        # - self.rowconfigure(1, weight=1): Makes the second row (where the images are displayed) expandable.
        self.rowconfigure(1, weight=1) # images expand
        # - self.rowconfigure(2, weight=0): Makes the third row (where the controls are) non-expandable.
        self.rowconfigure(2, weight=0) # controls fixed height



                                # 2. Top Action Bar (Upload and Save Buttons)

        # ----------------------------------------------------------------------
        # - Creates a ttk.Frame to hold the "Upload Main Image" and "Save Watermarked Image" buttons.
        # - 'self' is the parent, meaning this frame is directly inside the main window.
        top_frame = ttk.Frame(self)

        top_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))

        top_frame.columnconfigure(1, weight=1)
        # - Configures the grid *within* top_frame. Makes the second column of this frame expandable.

        ttk.Button(top_frame, text="📤 Upload Main Image", command=self.upload_main_image).grid(
            row=0, column=0, padx=5, sticky="w")

        ttk.Button(top_frame, text="💾 Save Watermarked Image", command=self.save_image).grid(
            row=0, column=1, padx=5, sticky="w")


                             # 3. Side-by-Side Image Display Area (Original + Preview)

        # ----------------------------------------------------------------------
        # - 'self' is the parent, meaning this frame is directly inside the main window.
        images_frame = ttk.Frame(self)

        # - sticky="nsew": Makes it stretch in all directions, allowing it to expand with the main window.
        images_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)

        images_frame.columnconfigure(0, weight=1)   #	Makes the left image panel expand horizontally.
        images_frame.columnconfigure(1, weight=1)   #	Makes the right image panel expand horizontally.
        images_frame.rowconfigure(0, weight=1)      # Makes both image panels expand vertically.


                                            # 3a. Original Image Panel

        original_panel = ttk.LabelFrame(images_frame, text=" Original Image ", padding=10)

        # - padx=(0, 10): Adds padding only to the right, creating a gap between it and the preview panel.
        original_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        # Important: Stop this LabelFrame from shrinking to fit its content,
        # ensuring it always takes its allocated space in the grid.
        original_panel.grid_propagate(False)

        # - Creates a standard tk.Label inside `original_panel`. This label will display the actual image.
        self.original_label = tk.Label(original_panel, text="No image loaded yet...\n",
                                       bg="white", relief="sunken", font=DEFAULT_FONT)

        self.original_label.grid(row=0, column=0, sticky="nsew")

        # - Makes the internal grid of `original_panel` expandable, so the `original_label` grows with it.
        original_panel.rowconfigure(0, weight=1)
        original_panel.columnconfigure(0, weight=1)



                                         # 3b. Preview Panel

        preview_panel = ttk.LabelFrame(images_frame, text=" Watermarked Preview ", padding=10)

        # - Placed in the second column of `images_frame`'s grid, with padding only on the left.
        preview_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        # Important: Stop this LabelFrame from shrinking to fit its content,
        # ensuring it always takes its allocated space in the grid.
        preview_panel.grid_propagate(False)

        self.preview_label = tk.Label(preview_panel, text="Preview appears here...\n",
                                      bg="white", relief="sunken", font=DEFAULT_FONT)
        # - Creates the tk.Label to display the preview image, similar to `original_label`.
        self.preview_label.grid(row=0, column=0, sticky="nsew")
        preview_panel.rowconfigure(0, weight=1)
        preview_panel.columnconfigure(0, weight=1)




                        # 4. Settings Control Panel (Watermark Type Selector, Text/Logo Controls, Apply Button)

        # ----------------------------------------------------------------------
        # - 'self' is the parent, meaning this frame is directly inside the main window.
        control_frame = ttk.LabelFrame(self, text=" Watermark Settings ", padding=5)

        # - sticky="ew": Stretches horizontally. Row 2 has weight=0, so it won't expand vertically.
        control_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(5, 10))

        # - Makes the first column *within* control_frame expandable.
        control_frame.columnconfigure(0, weight=1)



                                    # 4a. Watermark Type Selector (Radio Buttons)

        type_frame = ttk.Frame(control_frame)

        type_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        # - Label indicating "Watermark Type".
        ttk.Label(type_frame, text="Watermark Type:", font=(DEFAULT_FONT[0], 10, "bold")).grid(
            row=0, column=0, padx=5, sticky="w")

        # - A special Tkinter variable that holds the currently selected radio button's value.
        self.watermark_type = tk.StringVar(value="Logo")

        ttk.Radiobutton(type_frame, text="Text", variable=self.watermark_type,
                        value="Text", command=self.switch_controls).grid(row=0, column=1, padx=20, sticky="w")
        # - Creates the "Text" radio button.
        # - variable=self.watermark_type: Links it to the StringVar.
        # - value="Text": This is the string value that self.watermark_type will hold if this button is selected.
        # - command=self.switch_controls: When clicked, it calls the `switch_controls` method.
        ttk.Radiobutton(type_frame, text="Logo / Image", variable=self.watermark_type,
                        value="Logo", command=self.switch_controls).grid(row=0, column=2, padx=10, sticky="w")
        # - Creates the "Logo / Image" radio button, similar to "Text".



                            # 4b. Container for Dynamic Settings (Text vs. Logo)

        # - This frame acts as a placeholder. Either `self.text_frame` or `self.logo_frame` will be
        # packed into this container, depending on which radio button is selected.
        self.control_container = ttk.Frame(control_frame)

        # - Configures `control_container`'s grid to be expandable.
        self.control_container.grid(row=1, column=0, sticky="nsew", pady=5)
        self.control_container.columnconfigure(0, weight=1)
        self.control_container.rowconfigure(0, weight=1)

        # - Creates an empty ttk.Frame for text controls, then calls `create_text_controls` to populate it.
        # At this point, it's just created, not displayed. That depends on switch_controls()
        self.text_frame = ttk.Frame(self.control_container)
        self.create_text_controls()

        # - Creates an empty ttk.Frame for logo controls, then calls `create_logo_controls` to populate it.
        # Also just created, not displayed.
        self.logo_frame = ttk.Frame(self.control_container)
        self.create_logo_controls()

        # It immediately calls `switch_controls`. Based on the initial value of `self.watermark_type` ("Text"),
        # this will display `self.logo_frame` and hide `self.text_frame`.
        self.switch_controls()




                                        # 4c. Big "Apply Watermark" Button

        # - Creates the large "Apply Watermark" button at the bottom of the `control_frame`.
        ttk.Button(control_frame, text="🚀 Apply Watermark", command=self.apply_watermark).grid(
            row=2, column=0, pady=12, ipady=10, sticky="ew")





    # ---------------------------- TEXT WATERMARK CONTROLS ------------------------------- #
    # ------------------------------------------------------------------------------------ #

    def create_text_controls(self):
        """
        Create and grid all widgets specific to text watermark mode:
        text entry, size, color chooser, opacity slider, position selector
        """
        frame = self.text_frame # This 'frame' is the container for all text watermark widgets
        frame.columnconfigure(1, weight=1) # Makes the second column (index 1) expandable

        r = 0  #       <===========================     Initialize row counter for easy placement

        # 1. Watermark Text Entry
        ttk.Label(frame, text="Watermark Text:").grid(row=r, column=0, sticky="w", pady=6, padx=(5, 10))
        self.text_entry = ttk.Entry(frame, width=45) # Creates the input field
        self.text_entry.grid(row=r, column=1, sticky="ew", pady=6) # Places it, making it stretch horizontally
        self.text_entry.insert(0, "yourwebsite.com") # Sets a default value in the entry box

        r += 1          #       <===========================      Move to the next row

        # 2. Font Size Spinbox
        ttk.Label(frame, text="Font Size:").grid(row=r, column=0, sticky="w", pady=6, padx=(5, 10))
        self.font_size_var = tk.IntVar(value=48) # Tkinter variable detects the font size change instantly and  update the text on screen
        ttk.Spinbox(frame, from_=12, to=300, textvariable=self.font_size_var, width=10).grid(
            row=r, column=1, sticky="w", pady=6) # Creates a spinbox (number input with up/down arrows)

        r += 1          #       <===========================      Move to the next row

        # 3. Color Chooser Button and Swatch
        ttk.Label(frame, text="Color:").grid(row=r, column=0, sticky="w", pady=6, padx=(5, 10))
        ttk.Button(frame, text="🎨 Choose Color", command=self.choose_color).grid(
            row=r, column=1, sticky="w", pady=6) # Button to open the color picker dialog
        self.color_swatch = tk.Label(frame, bg="#ffffff", width=6, height=2, relief="ridge") # Small label to show chosen color, frame is the Parent Container
        self.color_swatch.grid(row=r, column=2, padx=12, pady=6) # Places the color swatch

        r += 1          #       <===========================      Move to the next row

        # 4. Opacity Slider
        ttk.Label(frame, text="Opacity (%):").grid(row=r, column=0, sticky="w", pady=6, padx=(5, 10))
        self.opacity_var = tk.IntVar(value=DEFAULT_OPACITY) # DoubleVar Tkinter ControlVariable (communication protocol) for opacity (0.0 to 100.0) floating-point numbers
        ttk.Scale(frame, from_=0, to=100, variable=self.opacity_var, orient="horizontal").grid(
            row=r, column=1, sticky="ew", pady=6) # Horizontal slider for opacity
        ttk.Label(frame, textvariable=self.opacity_var, width=3).grid(row=r, column=2, padx=10) # Label to display current opacity value

        r += 1          #       <===========================      Move to the next row

        # 5. Position Combobox (Dropdown)
        ttk.Label(frame, text="Position:").grid(row=r, column=0, sticky="w", pady=6, padx=(5, 10))
        self.position_var = tk.StringVar(value="Bottom Right") # Tkinter ControlVariable (communication protocol) for selected position,treats everything as text
        positions = ["Top Left", "Top Right", "Bottom Left", "Bottom Right", "Center"] # List of possible positions
        ttk.Combobox(frame, textvariable=self.position_var, values=positions,
                     state="readonly", width=22).grid(row=r, column=1, sticky="w", pady=6) # Dropdown menu for position

        r += 1          #       <===========================      Move to the next row



    # ---------------------------- LOGO WATERMARK CONTROLS ------------------------------- #
    # ------------------------------------------------------------------------------------ #

    def create_logo_controls(self):
        """
        Create and grid all widgets specific to logo watermark mode:
        logo upload, scale, opacity, position, small logo preview
        """
        frame = self.logo_frame # This 'frame' is the container for all logo watermark widgets
        frame.columnconfigure(1, weight=1) # Makes the second column (index 1) expandable

        r = 0 # Initialize row counter for easy placement

                                    # 1. Logo File Upload Button and Display
        # Label "Logo File:"
        ttk.Label(frame, text="Logo File:").grid(row=r, column=0, sticky="w", pady=6, padx=(5, 10))

        # Button to trigger the logo file dialog. When clicked, it calls self.upload_logo().
        ttk.Button(frame, text="📤 Upload Logo", command=self.upload_logo).grid(
            row=r, column=1, sticky="w", pady=6)

        # Label to display the name of the selected logo file. Initially "No logo selected".
        self.logo_name_label = ttk.Label(frame, text="No logo selected", foreground="gray")
        self.logo_name_label.grid(row=r, column=2, sticky="w", padx=12)

        r += 1 # Move to the next row for the next set of controls

                                            # 2. Logo Scale Spinbox
        # Label "Scale (% of original):"
        ttk.Label(frame, text="Scale (% of original):").grid(row=r, column=0, sticky="w", pady=6, padx=(5, 10))
        # Tkinter integer variable to hold the logo's scale percentage. Default value is 28%.
        self.logo_scale_var = tk.IntVar(value=28)
        # Spinbox (numerical input with up/down arrows) allowing users to select a scale from 5% to 80%.
        ttk.Spinbox(frame, from_=5, to=80, textvariable=self.logo_scale_var, width=10).grid(
            row=r, column=1, sticky="w", pady=6)

        r += 1

                                                # 3. Opacity Slider
        # Label "Opacity (%):"
        ttk.Label(frame, text="Opacity (%):").grid(row=r, column=0, sticky="w", pady=6, padx=(5, 10))
        # Tkinter double variable for the opacity. Note: it reuses self.opacity_var from text controls,
        # ensuring consistency between text and logo opacity settings if you switch between them.
        ttk.Scale(frame, from_=0, to=100, variable=self.opacity_var, orient="horizontal").grid(
            row=r, column=1, sticky="ew", pady=6) # Horizontal slider for opacity. It stretches ("ew").
        # Label to dynamically display the current opacity value from the slider.
        ttk.Label(frame, textvariable=self.opacity_var, width=4).grid(row=r, column=2, padx=10)

        r += 1

                                            # 4. Position Combobox (Dropdown)
        # Label "Position:"
        ttk.Label(frame, text="Position:").grid(row=r, column=0, sticky="w", pady=6, padx=(5, 10))
        # Tkinter string variable for the selected position. It reuses self.position_var from text controls.
        positions = ["Top Left", "Top Right", "Bottom Left", "Bottom Right", "Center"] # List of available positions
        ttk.Combobox(frame, textvariable=self.position_var, values=positions,
                     state="readonly", width=22).grid(row=r, column=1, sticky="w", pady=6) # Dropdown menu for position

        r += 1

                                                    # 5. Logo Preview Area
        # Label "Logo Preview:"
        ttk.Label(frame, text="Logo Preview:").grid(row=r, column=0, sticky="nw", pady=8, padx=(5, 10))
        # A Tkinter Label specifically for displaying a small preview of the uploaded logo.
        # It has a default background, fixed size, and a sunken relief to make it stand out.
        self.logo_preview_label = tk.Label(frame, bg="#eeeeee", width=18, height=2, relief="sunken")
        # Placed in the grid, spanning two columns (`columnspan=2`) and sticking to the northwest corner.
        self.logo_preview_label.grid(row=r, column=1, columnspan=2, sticky="w", pady=8)





    # ---------------------------- SWITCH BETWEEN TEXT / LOGO SETTINGS ------------------------------- #
    # ------------------------------------------------------------------------------------ #
    def switch_controls(self):
        """
        Hide both setting frames and show only the one matching the current watermark type.
        Called when radio buttons change and at startup.
        """
        self.text_frame.grid_remove()
        self.logo_frame.grid_remove()

        if self.watermark_type.get() == "Logo":
            self.logo_frame.grid(sticky="nsew")  # show logo controls
        else:
            self.text_frame.grid(sticky="nsew")           # show text controls

    # ---------------------------- IMAGE LOADING ------------------------------- #
    # ------------------------------------------------------------------------------------ #
    def upload_main_image(self):
        """
        Open file dialog to select main image, load with PIL, display it,
        and reset any previous watermark preview/result.
        """
        # 1. Open a Tkinter's file dialog to let the user choose an image file.
        # Returns a string containing the full, absolute path to the chosen file (e.g., C:/Users/YourName/Pictures/my_photo.jpg)
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff")]
        )

        # 2. Check if the user selected a file or cancelled the dialog.
        if not path:
            return  # If no file was selected, simply exit the function.

        # 3. Attempt to process the selected image.
        try:
            # 4. Open the image using Pillow (PIL) and convert it to RGB.           <========
            #    - Image.open(path): Loads the image from the specified file path (str), and
            #               returns an instance of the Image.Image class (often just referred to as a "Pillow Image object".
            #    - .convert("RGB"): Ensures the image is in RGB format (Red, Green, Blue).
            #      This is important because some image formats (like PNG) might have an alpha channel (RGBA),
            #      and working with a consistent format simplifies subsequent processing.
            self.original_image = Image.open(path).convert("RGB")

            # 5. Display the newly loaded image in the 'Original Image' panel.
            #    - self.display_image() is a helper function that takes a Pillow image and
            #      a Tkinter Label widget, resizes the image appropriately, and updates the label to show it.
            #    - self.original_label is the Tkinter Label widget where the original image should be shown on the Create_Widget Function.
            self.display_image(self.original_image, self.original_label)

            # 6. Clear the preview panel to indicate a fresh start.
            #    - self.preview_label.config(image="", text="..."): This updates the preview label.
            #      Setting 'image=""' removes any previously displayed image, and the text
            #      reappears, prompting the user to apply a watermark.
            self.preview_label.config(image="", text="Preview appears here\nafter you click 'Apply Watermark'")

            # 7. Reset the watermarked_image variable.
            #    - This ensures that if a user loads a new original image, any previous
            #      watermarked result is cleared from the application's memory until a new watermark is applied.
            self.watermarked_image = None

        # 8. Handle any errors that might occur during image loading or processing.
        except Exception as e:
            #    - If an error occurs (e.g., corrupted file, unsupported format),
            #      messagebox.showerror() displays an error pop-up to the user.
            messagebox.showerror("Error", f"Cannot open image:\n{e}")






    def upload_logo(self):
        """
        Open file dialog to select logo, store path, update status label,
        and show small preview in the controls.
        """
        # 1. Open a file dialog for the user to select a logo image.
        #    - filedialog.askopenfilename(): Presents a standard "Open File" window.
        #    - filetypes=[...]: Filters the file types to common image formats that support transparency
        #      (like PNG and GIF) or common non-transparent formats (JPG, BMP).
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )

        # 2. Check if the user cancelled the file dialog.
        #    - If 'path' is an empty string (meaning no file was selected), the function stops here.
        if not path:
            return

        # 3. Store the path to the selected logo.
        #    - self.logo_path is an instance variable that will hold the full file path.
        #      This path will be used later when the 'Apply Watermark' button is clicked
        #      to actually load and apply the logo to the main image.
        self.logo_path = path

        # 4. Update the UI to show the selected logo's filename.
        #    - self.logo_name_label: This is the Tkinter Label widget that says "No logo selected" initially.
        #    - .config(text=f"✓ {path.split('/')[-1]}", foreground="green"):
        #      - `path.split('/')[-1]` extracts just the filename (e.g., "my_logo.png") from the full path.
        #      - The text is updated with a checkmark and the filename.
        #      - The `foreground="green"` changes the text color to green, giving visual feedback that a logo was successfully selected.
        self.logo_name_label.config(text=f"✓ {path.split('/')[-1]}", foreground="green")

        # 5. Attempt to create a small preview of the logo.
        try:
            #    - Image.open(path): Loads the selected logo file into a Pillow Image object.
            logo = Image.open(path)
            #    - self.display_small_logo(logo): Calls a helper function to resize and
            #      display this `logo` image within the `self.logo_preview_label` widget in the UI.
            self.display_small_logo(logo)
        except:
            # 6. Gracefully handle any errors during logo loading.
            #    - This 'except' block catches any Exception that might occur during `Image.open()`
            #      or `display_small_logo()`.
            #    - `pass` means to do nothing if an error occurs. In a more robust app, you might want
            #      to show a messagebox.showerror() here, similar to `upload_main_image`, to inform the user.
            pass




    # ---------------------------- IMAGE DISPLAY HELPERS ------------------------------- #
    # ------------------------------------------------------------------------------------ #
    def display_image(self, pil_img, label_widget, max_dim=480):
        """
        Resize PIL image to fit label (max dimension), convert to PhotoImage
        and update the label. Used for both original and preview.
        """
        # 1. Create a copy of the original Pillow image.
        copy = pil_img.copy()

        # 2. Resize the image for display.
        #    - copy.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS):
        #      - `thumbnail()` is a Pillow method that resizes the image *in place* to fit within
        #        the given dimensions while maintaining its aspect ratio. It won't distort the image.
        #      - `(max_dim, max_dim)`: The image will be scaled down so that its largest dimension
        #        (either width or height) is no more than `max_dim` (defaulting to 480 pixels in this case),
        #        and the other dimension is scaled proportionally.
        #      - `Image.Resampling.LANCZOS`: This specifies the resampling filter to use during resizing.
        #        LANCZOS (also known as sinc interpolation) is a high-quality filter often used for
        #        downsampling, producing sharp-looking scaled images.
        copy.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

        # 3. Convert the Pillow image to a Tkinter PhotoImage.
        #    - Tkinter's `tk.Label` widgets (and other display widgets) cannot directly display
        #      Pillow Image objects. They require their own specific image format, `PhotoImage`.
        #    - ImageTk.PhotoImage(copy): This function from the `PIL.ImageTk` module performs
        #      that conversion, creating a `PhotoImage` object from the (now resized) Pillow image.
        photo = ImageTk.PhotoImage(copy)

        # 4. Update the target Tkinter Label widget.
        #    - label_widget.config(image=photo, text=""):
        #      - `label_widget` is the specific `tk.Label` (either `self.original_label` or `self.preview_label`)
        #        that you want to update.
        #      - `config()` is used to change the widget's properties.
        #      - `image=photo`: This tells the label to display the `PhotoImage` we just created.
        #      - `text=""`: This clears any text that might have been on the label (like "No image loaded yet"
        #        or "Preview appears here..."), ensuring only the image is shown.
        label_widget.config(image=photo, text="")

        # 5. Prevent the PhotoImage from being garbage collected.
        #    - label_widget.image = photo: This is a crucial line in Tkinter when displaying images.
        #      If you don't keep a strong reference to the `PhotoImage` object (like by attaching it
        #      as an attribute directly to the widget that displays it), Python's garbage collector
        #      might delete the `PhotoImage` object because it thinks it's no longer used. If that happens,
        #      your image will mysteriously disappear from the GUI!
        label_widget.image = photo




    def display_small_logo(self, pil_img):
        """
        Create small (140×140 max) thumbnail of logo and display in controls.
        """
        # 1. Create a copy of the incoming Pillow image object (pil_img).
        #    - This ensures that you're working with a separate version of the image data,
        #      leaving the original `pil_img` (which might be `self.original_image` or the full logo)
        #      untouched for other operations.
        copy = pil_img.copy()

        # 2. Resize the image to a small thumbnail size for preview.
        #    - copy.thumbnail((140, 140), Image.Resampling.LANCZOS):
        #      - Similar to `display_image`, `thumbnail()` resizes the `copy` image *in place*.
        #      - The image will be scaled down so that its largest dimension (width or height)
        #        is no more than 140 pixels, while maintaining its original aspect ratio.
        #      - `Image.Resampling.LANCZOS`: High-quality resampling filter
        #        used to ensure the scaled-down logo preview looks sharp and clear.
        copy.thumbnail((140, 140), Image.Resampling.LANCZOS)

        # 3. Convert the resized Pillow image into a Tkinter PhotoImage object.
        #    - Tkinter widgets can't display Pillow images directly. `ImageTk.PhotoImage()`
        #      converts the `copy` (which is a Pillow Image object) into a `PhotoImage`
        #      format that Tkinter can use.
        photo = ImageTk.PhotoImage(copy)

        # 4. Update the specific Tkinter Label widget designated for the logo preview.
        #    - self.logo_preview_label.config(image=photo, text=""):
        #      - `self.logo_preview_label` is the `tk.Label` widget created in `create_logo_controls`
        #        that serves as the dedicated preview area for the logo.
        #      - `config(image=photo)` sets the `PhotoImage` we just created as the image to be displayed
        #        by this label.
        #      - `text=""` clears any previous text (like "No logo selected" or any default text)
        #        from the label, ensuring only the image is visible.
        self.logo_preview_label.config(image=photo, text="")

        # 5. Prevent the PhotoImage object from being garbage collected by Python.
        #    - self.logo_preview_label.image = photo:  By assigning the `photo` object directly to an attribute of
        #                                   the `logo_preview_label` widget,it create a strong reference.
        #                                   This prevents Python's garbage collector from deleting
        #                                   the `PhotoImage` once the `display_small_logo` function finishes, which would otherwise
        #                                   cause the image to disappear from your GUI.
        self.logo_preview_label.image = photo



    # ---------------------------- COLOR CHOOSER ------------------------------- #
    # ------------------------------------------------------------------------------------ #

    def choose_color(self):
        """
        Open system color chooser, update selected color and swatch preview
        if user confirms a selection.
        """
        # 1. Open the system color chooser dialog.
        #      - colorchooser.askcolor(): Tkinter's colorchooser module opens a native color selection dialog
        #      - initialcolor=self.watermark_color: This parameter sets the color that the dialog will initially show.
        #
        #      - Return Value: `askcolor()` returns a tuple:
        #      `( (r, g, b), '#hexcode' )` if the user selects a color and clicks OK.
        #      Example: `( (255, 0, 0), '#ff0000' )` for red.
        #      `( None, None )` if the user clicks "Cancel" or closes the dialog.
        color = colorchooser.askcolor(initialcolor=self.watermark_color)

        # 2. Check if the user actually selected a color (i.e., didn't cancel).
        #       - if color[1]: This checks the second element of the returned tuple, which is the
        #       hexadecimal color string (e.g., '#ff0000').
        #       - If a color was chosen, `color[1]` will be a non-empty string, which evaluates to `True`.
        #       - If the user cancelled, `color[1]` will be `None`, which evaluates to `False`.
        if color[1]:
            # 3. Update the application's stored watermark color.
            # - self.watermark_color = color[0]: The first element of the returned tuple, `color[0]`,is the RGB tuple `(r, g, b)`.
            self.watermark_color = color[0]

            # 4. Update the visual color swatch in the UI.
            #       - self.color_swatch.config(bg=color[1]): `self.color_swatch` is the `tk.Label`
            #       defined in `create_text_controls` with a `relief="ridge"`.
            #       - `config(bg=color[1])` sets the background color of this `Label` to the new selected color.
            #       It uses `color[1]` (the hex string) because Tkinter's `bg` option typically accepts hex codes
            #       or standard color names.
            self.color_swatch.config(bg=color[1])










    # ---------------------------- POSITION CALCULATION (shared by text & logo) ------------------------------- #
    # ------------------------------------------------------------------------------------ #

    def get_position(self, img_w, img_h, wm_w, wm_h, pos_name):
        """
        Return (x, y) coordinates for placing watermark based on chosen position name.
        Used by both text and logo watermark application.

        Parameters:
        img_w: width of the main (original) image
        img_h: height of the main (original) image
        wm_w: width of the watermark (either text or logo)
        wm_h: height of the watermark (either text or logo)
        pos_name: the name of the desired position (e.g., "Top Left", "Center")
        """


        # 1. Define a margin for spacing.
        #    - `margin = 35`: This constant determines how far the watermark will be placed
        #      from the edges of the main image. A value of 35 pixels is chosen here for visual spacing.
        margin = 35

        # 2. Calculate (x, y) coordinates based on the requested position (`pos_name`).
        #    - Tkinter and Pillow's coordinate systems typically start with (0,0) at the top-left corner.
        #    - `x` increases to the right, `y` increases downwards.

        if pos_name == "Top Left":
            # The top-left corner of the watermark is placed `margin` pixels from the
            # top and `margin` pixels from the left edge of the main image.
            return margin, margin

        elif pos_name == "Top Right":
            # x-coordinate: `img_w` (total width) - `wm_w` (watermark width) - `margin`
            # This places the right edge of the watermark `margin` pixels from the right edge of the image.
            # y-coordinate: `margin` (from the top).
            return img_w - wm_w - margin, margin

        elif pos_name == "Bottom Left":
            # x-coordinate: `margin` (from the left).
            # y-coordinate: `img_h` (total height) - `wm_h` (watermark height) - `margin`
            # This places the bottom edge of the watermark `margin` pixels from the bottom edge of the image.
            return margin, img_h - wm_h - margin

        elif pos_name == "Bottom Right":
            # x-coordinate: `img_w` - `wm_w` - `margin` (from the right).
            # y-coordinate: `img_h` - `wm_h` - `margin` (from the bottom).
            return img_w - wm_w - margin, img_h - wm_h - margin

        else:  # Center
            # x-coordinate: `(img_w - wm_w) // 2`
            # This calculates the horizontal center by taking the total remaining space
            # (`img_w - wm_w`) and dividing it by 2. The `//` ensures integer division for pixel coordinates.
            # y-coordinate: `(img_h - wm_h) // 2`
            # This calculates the vertical center similarly.
            return (img_w - wm_w) // 2, (img_h - wm_h) // 2



    # ---------------------------- MAIN WATERMARK PROCESSING LOGIC ------------------------------- #
    # ------------------------------------------------------------------------------------ #

    def apply_watermark(self):
        """
        Main processing method: composites text or logo watermark onto copy of original image.
        Stores result and updates preview. Handles both modes with proper alpha blending.
         **Process Flow:**
        1. **Initial Checks**: Verifies that a main image has been uploaded. If not, it warns the user and returns.
        2. **Working Copy**: Creates a full-resolution RGBA copy of the `self.original_image`. This copy serves as the canvas for the watermark, ensuring transparency can be handled correctly and the original image remains untouched.
        3. **Watermark Type Branching**:
            * **If "Text" Watermark is selected**:
                * Retrieves text, font size, color, opacity, and position settings from the UI.
                * Loads the chosen font (with fallbacks if a specific font isn't found).
                * Creates a separate, transparent RGBA layer of the same size as the main image.
                * Draws the text onto this transparent layer, applying the specified color and opacity.
                * Calculates the (x, y) placement coordinates for the text using `self.get_position()`.
                * Blends this text layer onto the working image copy using `Image.alpha_composite()`.
            * **If "Logo" Watermark is selected**:
                * Verifies that a logo file has been uploaded.
                * Opens the logo file and converts it to RGBA.
                * Scales the logo based on user input, maintaining aspect ratio.
                * Adjusts the logo's overall opacity by modifying its alpha channel.
                * Calculates the (x, y) placement coordinates for the logo using `self.get_position()`.
                * Pastes the modified logo onto the working image copy, using the logo's own alpha channel for proper blending (`result.paste(logo,..., logo)`).
        4. **Finalization**: Stores the fully watermarked image in `self.watermarked_image` and updates the UI by calling `self.display_image()` to show the result in the preview panel.
        """
        # 1. Initial Checks & Setup
        # ----------------------------------------------------------------------
        # Ensure a main image has been uploaded before trying to apply a watermark.
        if self.original_image is None:
            messagebox.showwarning("No Image", "Please upload a main image first!")
            return

        # Create a working copy of the original image, converting it to RGBA.
        # RGBA (Red, Green, Blue, Alpha) is essential because the alpha channel allows for TRANSPARENCY.
        result = self.original_image.copy().convert("RGBA")

        # 2. Text Watermark Mode
        # ----------------------------------------------------------------------
        if self.watermark_type.get() == "Text":
            # Get the text the user entered and remove leading/trailing whitespace.
            text = self.text_entry.get().strip()
            # If no text was entered, show a warning and stop.
            if not text:
                messagebox.showwarning("Missing Text", "Please enter watermark text!")
                return

            # Retrieve text watermark settings from UI variables.
            font_size = self.font_size_var.get()
            opacity = self.opacity_var.get() / 100.0 # Convert percentage to a 0.0-1.0 scale
            alpha = int(255 * opacity) # Convert opacity to an 8-bit alpha value (0-255)
            # Combine the chosen color (RGB tuple) with the calculated alpha to get RGBA.
            fill_color = self.watermark_color + (alpha,) # e.g., (255, 255, 255) + (140,) -> (255, 255, 255, 140)

            # Load the font.
            # It tries to load "arial.ttf" directly, then from a common Windows font path,
            # and finally falls back to Pillow's default font if neither is found.
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()

            # Create a transparent layer to draw the text on.
            # Image.new(), Pillow creates a rectangular block of memory, in this case a temporary,
            #   transparent image of the same size as the main image.
            layer = Image.new("RGBA", result.size, (0,0,0,0))
            # Get a drawing context for this transparent layer with the ImageDraw Class module from Pillow.
            draw = ImageDraw.Draw(layer)

            # Measure the size of the text *before* drawing it.
            # This is needed to calculate its position accurately because some fonts have extra space or "tails" that hang below the line.
            # draw.textbbox() returns four numbers in this specific order:
            #               [0] Left, [1] Top, [2] Right, [3] Bottom.
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0] # Width of the text
            text_h = bbox[3] - bbox[1] # Height of the text

            # Calculate the (x, y) position for the text watermark using the helper function previously created.
            x, y = self.get_position(img_w= result.width, img_h=result.height, wm_w= text_w, wm_h= text_h, pos_name= self.position_var.get())
            # Actually Draw-ing the text onto the transparent layer with the calculated position, text, font, and RGBA color.
            draw.text((x, y), text, fill=fill_color, font=font)

            # Composite (overlay) the transparent text ("stencil") layer onto the main image.
            # Image.alpha_composite() blends the two RGBA images based on their alpha channels.
            result = Image.alpha_composite(result, layer)

        # 3. Logo Watermark Mode
        # ----------------------------------------------------------------------
        else: # Logo mode
            # Ensure a logo file has been selected.
            if not self.logo_path:
                messagebox.showwarning("No Logo", "Please upload a logo first!")
                return

            try:
                # Open the selected logo image, converting it to RGBA to ensure transparency support.
                logo = Image.open(self.logo_path).convert("RGBA")

                # Scale the logo based on user input on tk.IntVar field.
                scale = self.logo_scale_var.get() / 100.0
                # Calculate new width and height, ensuring a minimum size of 20 pixels to avoid errors with tiny images.
                new_w = max(20, int(logo.width * scale))
                new_h = max(20, int(logo.height * scale))
                # Resize the logo using LANCZOS for high quality.
                logo = logo.resize((new_w, new_h), Image.Resampling.LANCZOS)

                # Adjust the logo's opacity.
                opacity = self.opacity_var.get() / 100.0
                # Get the alpha channel or a grayscale image where 255 is fully visible and 0 is fully transparent of the resized logo.
                alpha = logo.getchannel("A")
                # Apply the user-defined opacity to the logo's alpha channel.
                # `point()` applies a function to each pixel in the channel.
                alpha = alpha.point(lambda p: int(p * opacity))
                # Put the modified alpha channel back into the logo image.
                logo.putalpha(alpha)

                # Calculate the (x, y) position for the logo watermark.
                x, y = self.get_position(img_w= result.width, img_h= result.height, wm_w= new_w, wm_h= new_h, pos_name= self.position_var.get())
                # Paste the logo onto the main image.
                # The last `logo` argument acts as a mask, ensuring correct blending using the logo's alpha channel.
                # And the first "logo" provides the RGB color
                result.paste(logo, (x, y), logo)

            except Exception as e:
                # Handle any errors during logo processing (e.g., corrupted logo file).
                messagebox.showerror("Logo Error", f"Could not process logo:\n{e}")
                return

        # 4. Final Steps
        # ----------------------------------------------------------------------
        # Store the fully watermarked image in an instance variable.
        self.watermarked_image = result
        # Display this watermarked image in the preview panel.
        self.display_image(result, self.preview_label)




    # ---------------------------- SAVE FINAL IMAGE ------------------------------- #
    # ------------------------------------------------------------------------------------ #

    def save_image(self):
        """
        Open save-as dialog, convert to RGB if JPEG selected, save file with PIL,
        and show success/error message.
        """
        # 1. Initial Check: Ensure there's an image to save.
        #    - `self.watermarked_image` will be `None` if `apply_watermark()` hasn't been called yet
        #      or if it failed.
        #    - If there's nothing to save, a warning message box is shown to the user, and the function exits.
        if self.watermarked_image is None:
            messagebox.showwarning("Nothing to save", "Apply a watermark first!")
            return

        # 2. Open "Save As" file dialog.
        #    - `filedialog.asksaveasfilename()`: This Tkinter function opens a standard "Save As" dialog.
        #      It returns a string containing the full, absolute file path where the user wants to save the image.
        #    - `defaultextension=".png"`: If the user types a filename without an extension (e.g., "my_watermark"),
        #      it will automatically append ".png".
        #    - `filetypes=[...]`: This list of tuples defines the file format options presented to the user
        #      in the dialog's "Save as type" dropdown.
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg *.jpeg"), ("All files", "*.*")]
        )

        # 3. Check if the user cancelled the dialog.
        #    - If `file_path` is an empty string, it means the user closed the dialog without selecting a file
        #      or clicking "Save". In this case, the function simply exits.
        if not file_path:
            return

        # 4. Attempt to save the image.
        try:
            #    - `to_save = self.watermarked_image`: A reference to the watermarked image (a Pillow Image object)
            #      is stored in a local variable. This image is currently in "RGBA" mode because watermarks
            #      involve transparency.
            to_save = self.watermarked_image

            # 5. Handle JPEG format limitations.
            #    - `if file_path.lower().endswith((".jpg", ".jpeg")):`: Checks if the user chose to save the
            #      file with a .jpg or .jpeg extension (case-insensitive).
            #    - `to_save = to_save.convert("RGB")`: The JPEG image format
            #      does not support transparency (alpha channel)
            if file_path.lower().endswith((".jpg", ".jpeg")):
                to_save = to_save.convert("RGB")

            # 6. Save the image file.
            #    - `to_save.save(file_path)`: This Pillow method writes the image data to the specified file path
            #      on the user's system, in the format inferred from the file extension.
            to_save.save(file_path)

            # 7. Show success message.
            #    - If saving is successful, a message box informs the user and shows the full path to the saved file.
            messagebox.showinfo("Saved!", f"Watermarked image saved!\n\n{file_path}")

        # 8. Handle any errors during saving.
        except Exception as e:
            #    - If any error occurs during the saving process (e.g., permissions issue, disk full),
            #      an error message box is displayed with the details of the exception.
            messagebox.showerror("Save Error", str(e))






# ---------------------------- START APPLICATION ------------------------------- #
# ------------------------------------------------------------------------------------ #
if __name__ == "__main__":
    app = WatermarkApp()
    app.mainloop()









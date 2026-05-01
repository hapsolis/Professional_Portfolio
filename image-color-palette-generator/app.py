"""
PIPELINE: FROM PIXELS TO PALETTE
--------------------------------
1. INPUT (Pillow):
   - Load image as a 3D object (Height, Width, RGB).
   - Resize via .thumbnail() to reduce math load without distorting the 'vibe'.

2. TRANSLATION (NumPy):
   - Convert the Pillow object into a 3D Numerical Matrix.
   - Execute .reshape(-1, 3): Flatten the 3D 'Cube' into a 2D 'Table'.
   - Result: A long list of individual colors (Observations) with 3 features (R, G, B).

3. LEARNING (Scikit-Learn / K-Means):
   - Algorithm treats each row in the 2D table as a point in 3D space.
   - It 'clusters' thousands of pixels into 10 mathematical 'neighborhoods'.
   - The 'Centroid' (center) of each neighborhood becomes a Dominant Color.

4. OUTPUT (Python/Flask):
   - Map the clusters to their percentage of the total pixel count.
   - Convert the RGB centroids into Web-friendly HEX codes.
   - Return a sorted JSON list to the frontend for display.
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename  #Path Traversal Prevention
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import uuid    #  Universally Unique Identifiers (UUIDs) generator

# ──────────────────────────────────────────────────────────────────────────
# CONFIGURATION & CONSTANTS
# ──────────────────────────────────────────────────────────────────────────

app = Flask(__name__) #  Web Application Flask object.

# Folder setup
UPLOAD_FOLDER = os.path.join('static', 'uploads')   # Result: C:\Users\Hector\Project\static\uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

# Blank Dictionary object where Flask stores its settings
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Number of dominant colors to extract
NUM_COLORS = 10




def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension.

    Args:
        filename (str): Name of the uploaded file.

    Returns:
        bool: True if extension is allowed, False otherwise.
    """
    return ('.' in filename) and (filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS)


def rgb_to_hex(rgb: tuple) -> str:
    """Convert RGB tuple to HEX color code.

    Args:
        rgb (tuple): Tuple of (R, G, B) values (0-255).

    Returns:
        str: HEX color string (e.g., '#FF5733').
    """
    # x: Stands for Hexadecimal.
    # 2: Minimum width
    # 0: Padding. Use a zero instead A space.
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def extract_dominant_colors(image_path: str, n_colors: int = NUM_COLORS):
    """Extract dominant colors from an image using K-Means clustering.

    Logic:
    1. Open and resize image to 200x200 (or keep aspect if smaller) for speed.
    2. Convert to numpy array of RGB pixels.
    3. Run KMeans on the pixel colors.
    4. Calculate percentage of pixels belonging to each cluster.
    5. Sort by dominance (percentage descending).

    Why resize? High-resolution images can have 10M+ pixels → KMeans becomes slow.
    Resizing preserves the overall color distribution very well for palette generation.

    Args:
        image_path (str): Path to the uploaded image.
        n_colors (int): Number of dominant colors to extract (default: 10).

    Returns:
        list[dict]: List of dictionaries with 'hex', 'rgb', and 'percentage' keys.
    """
    # Open image and convert to RGB
    img = Image.open(image_path).convert('RGB')

    # Resize for performance while keeping aspect ratio roughly, thumbnail equally reduce the image size ratio
    max_size = (200, 200)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)# Using LANCZOS for high quality.

    # Convert to numpy array: shape (height, width, 3)
    img_array = np.array(img)

    # Reshape to (pixels, 3) for KMeans, -1 is a NumPy placeholder
    pixels = img_array.reshape(-1, 3)

    # *************************************** Key section of the function *******************************************
    # Create the model:
    # n_clusters=10: we want 10 final colors.
    # n_init=10: runs the 'finding' process 10 times to pick the best/most accurate result (where pixels were closest to their centers).
    # random_state=42 ensures the 'random' starts are the same every time we run the code.
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10) #Object Class Instance

    # fit_predict assigns each pixel a 'Group ID' (0-9) based on which color center is closest.
    labels = kmeans.fit_predict(pixels) # integers ID List for each pixel

    # cluster_centers_ stores the average RGB color for each of those 10 groups (2D array that contains 10 RGB triplets).
    centers = kmeans.cluster_centers_
    # ***************************************************************************************************************

    # Count pixels per cluster and calculate percentages
    _, counts = np.unique(labels, return_counts=True)
    # counts is a NumPy array, it divides every number inside the list individually
    percentages = counts / len(labels) * 100

    # Create list of color info and sort by percentage (most dominant first)
    color_info = []
    for i, center in enumerate(centers):
        hex_color = rgb_to_hex(center)   # <====================== Helper Function
        percentage = percentages[i]
        color_info.append({
            'hex': hex_color,
            'rgb': tuple(map(int, center)), # tuple is needed because map returns a map object
            'percentage': round(percentage, 2)
        })

    # Sort by percentage
    color_info.sort(key=lambda x: x['percentage'], reverse=True)

    return color_info # Ascending List of Dictionaries


# ──────────────────────────────────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    """Render the main page with upload interface."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload and color extraction.

    Returns JSON with image URL and list of dominant colors,
    or error message if something fails.
    Triggered by: index.html -> JavaScript fetch('/upload', {method: 'POST'})

    Data Flow:
    1. IN: Receives 'multipart/form-data' containing the image file.
    2. VALIDATION: Checks for file existence and allowed extensions.
    3. SECURITY: Sanitizes filename and adds a UUID to prevent file collisions.
    4. PROCESSING: Saves file to disk and calls extract_dominant_colors().
    5. OUT: Returns a JSON object with:
       - success (bool)
       - image_url (str) -> Path used by index.html to display the image.
       - colors (list) -> The extracted color palette data.
    """

    # Flask parses the incoming 'multipart/form-data' and stores it in request.files dictionary-like object.
    # We check if 'file' exists because that is the key name we defined in JavaScript (formData.append('file', file)).
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    #  request.files['file'] is a FileStorage object from Flask.
    file = request.files['file']

    # It ensures that an actual file was selected
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400 # JavaScript cannot read Python dictionaries

    if file and allowed_file(file.filename):    # <====================== Helper Function

        # Secure the filename and add unique ID to prevent collisions
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())[:8]

        secure_name = f"{unique_id}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)

        try:
            file.save(filepath)

            # Extract dominant colors
            colors = extract_dominant_colors(filepath)      # <====================== Helper Function

            # Return relative URL for the uploaded image based on the location of the running Flask app
            image_url = f"/static/uploads/{secure_name}"

            # Convert the Python dictionary into a JSON string and send it to the browser.
            # This is a temporary message for the frontend, NOT a global app configuration.
            # Data send to index.html
            return jsonify({
                'success': True,
                'image_url': image_url,
                'colors': colors
            })

        except Exception as e:
            # Clean up file if processing fails
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Processing error: {str(e)}'}), 500

    return jsonify({'error': 'File type not allowed'}), 400


@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    """
    Serves the physical image file back to the browser.

    Triggered by: index.html -> <img src="/static/uploads/filename.jpg">
    - This route is activated AUTOMATICALLY by the browser once the
      <img> element in index.html receives its 'src' attribute.
    - This assignment happens in the JavaScript showResults() function
      immediately after the upload_image route returns the file path.

    Data Flow:
    1. Browser detects the new URL in the <img> src.
    2. Browser sends a GET request to this endpoint.
    3. Flask uses send_from_directory to find the file in UPLOAD_FOLDER and stream it back.
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



if __name__ == '__main__':
    app.run(debug=True)
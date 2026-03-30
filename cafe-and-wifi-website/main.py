from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, URL, Length
import os

# =====================================================
# FLASK APP SETUP
# =====================================================
app = Flask(__name__)

# Flask uses to encrypt data in Flask-WTF (Forms)
app.config['SECRET_KEY'] = 'cafe-and-wifi-website-secret-key-2026'

# Database Configuration

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'   # Automatic pathfinder

# keeps the console clean and the app fast, free memory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# the library creates its own internal DeclarativeBase automatically
db = SQLAlchemy()
db.init_app(app)


# =====================================================
# CAFE MODEL
# =====================================================
class Cafe(db.Model):
    """
    SQLAlchemy model representing a 'Work-Friendly' Cafe for the Portfolio Website.

    This class serves as a source for the 'cafe&wifi_portfolio' table in cafes.db.
    It maps Python objects to SQLite rows, enabling the website to display, add,
    and delete cafe data dynamically.

    Main Responsibilities:
    • Data Storage: Manages Cafe details including location, connectivity (WiFi/Sockets),
      and accessibility (Calls/Toilets).
    • Template Powering: Provides the data used to populate the Bootstrap tables
      on the home page (index.html).
    • Form Integration: Receives validated data from 'AddCafeForm' to create
      new database records.
    • UI Logic: Handles data formatting (like the 'coffee_price' fallback) to ensure
      the website UI stays clean even if data is missing.

    Helper Method:
    • to_dict() -> Returns a dictionary of the cafe's attributes.
    """
    __tablename__ = 'cafe'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'map_url': self.map_url,
            'img_url': self.img_url,
            'location': self.location,
            'seats': self.seats,
            'has_toilet': self.has_toilet,
            'has_wifi': self.has_wifi,
            'has_sockets': self.has_sockets,
            'can_take_calls': self.can_take_calls,
            'coffee_price': self.coffee_price or '£?',
        }


# =====================================================
# ADD CAFE FORM
# =====================================================
class AddCafeForm(FlaskForm):
    """
        Flask-WTF form representing the 'Add New Cafe' interface for the Website.

        This class bridges the gap between the HTML frontend (add_cafe.html) and
        the SQLAlchemy model (cafe&wifi_portfolio'). It defines the layout, validation rules,
        and security for user-submitted data.

        Main Responsibilities:
        • UI Rendering: Automatically generates Bootstrap-compatible HTML inputs
          (Text boxes, Checkboxes, Buttons) for the 'Add Cafe' page.
        • Data Validation: Enforces rules like 'DataRequired()' and 'URL()' to ensure
          users don't submit empty fields or broken website links.
        • Security (CSRF): Automatically includes a hidden 'Synchronizer Token'
          that prevents cross-site hacking attempts (requires app.config['SECRET_KEY']).
        • Type Conversion: Handles the logic of converting HTML checkbox states
          (on/off) into Python Boolean values (True/False) for the database.

        Key Features:
        • validators=[URL()]: Specifically checks that the 'map_url' and 'img_url'
          are formatted correctly before the form can even be submitted.
        • default=True: Pre-sets common amenities (WiFi, Sockets) to 'checked'
          to save the user time during data entry.
        """
    name = StringField('Cafe Name', validators=[DataRequired(), Length(max=250)])
    map_url = StringField('Google Maps URL', validators=[DataRequired(), URL()])
    img_url = StringField('Cafe Image URL (https)', validators=[DataRequired(), URL()])
    location = StringField('Location', validators=[DataRequired(), Length(max=250)])
    seats = StringField('Seats (e.g. 20-30, 50+)', validators=[DataRequired()])

    has_toilet = BooleanField('Has Toilet')
    has_wifi = BooleanField('Has WiFi', default=True)
    has_sockets = BooleanField('Has Power Sockets', default=True)
    can_take_calls = BooleanField('Can Take Calls')

    coffee_price = StringField('Coffee Price (e.g. £3.50)')

    submit = SubmitField('Add Cafe')


# =====================================================
# CREATE TABLES (Safe version)
# =====================================================
with app.app_context():
    db.create_all()


# =====================================================
# ROUTES
# =====================================================

# routes already have GET enabled by default
@app.route("/")
def home():
    """
    Main Route – Fetches and displays cafes, with optional location filtering.

    This function serves as the central hub. It handles both the initial page load
    (showing all cafes) and search queries (filtering by location) via GET requests.

    Process Flow:
    1. Input Catching: Checks the URL for a 'loc' parameter using 'request.args.get'.
    2. Logic Branching:
       - If a search term exists: Filters the 'Cafe' table where the location matches
         the term (case-insensitive in SQLite).
       - If no search term: Prepares a query to select all records.
    3. Execution: Executes the chosen SQLAlchemy statement and converts results
       into a Python list of objects.
    4. Rendering: Passes the list to 'index.html' to be displayed in the table.
    """
    # Look for the 'loc' data in the URL (The GET data)
    search_location = request.args.get("loc")

    if search_location:
        # Filter the database
        result = db.session.execute(
            # .contains() is case-insensitive by default
            db.select(Cafe).where(Cafe.location.contains(search_location)).order_by(Cafe.name)
        )
    else:
        # Show everything if no search
        result = db.session.execute(db.select(Cafe).order_by(Cafe.name))

    all_cafes = result.scalars().all()
    return render_template("index.html", cafes=all_cafes)


@app.route("/add", methods=["GET", "POST"])
def add_cafe():

    # GET Request
    form = AddCafeForm()

    # POST Request
    if form.validate_on_submit():
        # Get the form data
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            seats=form.seats.data,
            has_toilet=form.has_toilet.data,
            has_wifi=form.has_wifi.data,
            has_sockets=form.has_sockets.data,
            can_take_calls=form.can_take_calls.data,
            coffee_price=form.coffee_price.data or None,
        )

        db.session.add(new_cafe)
        db.session.commit()

        # Flask helper function
        flash(f"✅ Successfully added '{new_cafe.name}'!", "success")
        return redirect(url_for('home'))

    # Rendered on the GET request section, before clicking the submit button
    return render_template("add_cafe.html", form=form)


@app.route("/delete/<int:cafe_id>")
def delete_cafe(cafe_id):
    """
    Delete Route – Removes a cafe record from the database.

    This function performs the 'Delete' part of CRUD. It identifies a
    specific record using a Path Variable (cafe_id) passed via the URL.

    Process Flow:
    1. Retrieval: Uses 'get_or_404' to find the Cafe object by its Primary Key.
       If the ID is invalid, the user receives a 404 error instead of a crash.
    2. Deletion: Marks the retrieved object for removal from the database session.
    3. Persistence: Commits the session to permanently update the '.db' file.
    4. UX Feedback: Flashes a 'danger' (red) alert to notify the user and
       redirects to the home page.
    """
    cafe = db.session.get(Cafe, cafe_id)
    if cafe:
        db.session.delete(cafe)
        db.session.commit()
        flash(f"🗑️ '{cafe.name}' has been removed.", "danger")
    else:
        flash("⚠️ Cafe not found.", "danger")
    return redirect(url_for('home'))


# =====================================================
# RUN THE APP
# =====================================================
if __name__ == "__main__":
    app.run(debug=True)
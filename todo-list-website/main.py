# ---------------------------- TO DO LIST WEBSITE - DAY 89 ------------------------------- #
# This is a professional To do List application built with Flask.
# It demonstrates full CRUD operations with SQLAlchemy, responsive Bootstrap 5 design,
# form validation with WTForms, and user feedback via flash messages.
#
# Why this structure? Same professional pattern as Day 88 Café & WiFi:
# - Clear separation of concerns (models, routes, forms)
# - Constants at the top
# - Detailed comments explaining "why" and "how"
# - Flash messages for better UX
# - Responsive design that works on mobile/desktop

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired, Length, Optional

from datetime import datetime, timezone
import os

# ---------------------------- CONSTANTS & APP SETUP ------------------------------- #
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)  # Required for WTForms and flash messages

# Database configuration - SQLite for simplicity and portability
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ---------------------------- DATABASE MODEL ------------------------------- #
class Todo(db.Model):
    """
    Represents the 'todo' table in the SQLite database.

    This model utilizes SQLAlchemy ORM to map Python attributes to database columns.
    It tracks task metadata including priority levels and completion status,
    allowing for complex queries and sorting logic in the controller routes.
    """
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(250), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), nullable=False, default="Medium")
    completed = db.Column(db.Boolean, nullable=False, default=False)
    date_added = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        """Provides a readable string representation of the object for debugging.
        Instead of showing a memory address, it displays the task name,
        making it easier to identify specific records in the console or logs."""
        return f'<Todo {self.task}>'


# ---------------------------- WTForms ------------------------------- #
class AddTaskForm(FlaskForm):
    """
    Defines the schema, constraints, and CSRF protection for task input using WTForms.

        1. Security: Automatically handles CSRF (Cross-Site Request Forgery) tokens.
        2. Validation: The 'DataRequired' and 'Length' validators ensure the database
           never receives empty strings or excessively long text that could break the UI.
        3. Mapping: It maps HTML input types (like Date or Select) directly to Python
           objects, making the 'home' route logic much cleaner.
    """
    task = StringField('Task', validators=[DataRequired(), Length(min=3, max=250)])
    due_date = DateField('Due Date (optional)', validators=[Optional()], format='%Y-%m-%d') # Calendar Picker
    priority = SelectField('Priority', choices=[
                                                        ('Low', 'Low Priority'),
                                                        ('Medium', 'Medium Priority'),
                                                        ('High', 'High Priority')
                                                    ],
                                            default='Medium'
                           )
    submit = SubmitField('Add Task')


# ---------------------------- CREATE DATABASE ------------------------------- #
with app.app_context():
    db.create_all()  # Creates todos.db and tables if they don't exist


# ---------------------------- ROUTES ------------------------------- #
@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Controller for the index page. Handles both data display and task creation.

    - GET: Queries the database for all tasks, applying a multi-level sort
          (Priority first, then Due Date) before passing the collection to the
          Jinja2 engine for rendering.

    - POST: Validates the AddTaskForm via WTForms. If valid, it instantiates a
      new Todo object and commits it to the database session.
    """
    form = AddTaskForm()

    if form.validate_on_submit():
        new_task = Todo(
            task=form.task.data,
            due_date=form.due_date.data,
            priority=form.priority.data
        )

        db.session.add(new_task)
        db.session.commit()

        flash(f'{new_task.task.capitalize()} Task added successfully!', 'success')
        return redirect(url_for('home'))

    # Query all tasks, ordered by priority frist and then by due date for better UX
    todos = Todo.query.order_by(
                                    db.case(
                                            (Todo.priority == 'High', 1),
                                            (Todo.priority == 'Medium', 2),
                                            (Todo.priority == 'Low', 3)
                                            ),
                                    Todo.due_date.asc().nulls_last(),
                                    Todo.date_added.desc()
                                ).all()

    return render_template('index.html', todos=todos, form=form)




@app.route('/complete/<int:task_id>')
def complete(task_id):
    """
    Removes a specific task from the database and updates the view.

    Uses the task_id to locate the unique record in the database.
    It executes a delete operation via SQLAlchemy and commits the
    change, ensuring the task is permanently removed before
    redirecting the user back to the updated list.
    """
    task = Todo.query.get_or_404(task_id)

    # If it was False, it becomes True. If it was True, it becomes False.
    task.completed = not task.completed
    db.session.commit()

    status = "completed" if task.completed else "marked as incomplete"

    flash(f'Task "{task.task}" {status}!', 'info')
    return redirect(url_for('home'))


@app.route('/delete/<int:task_id>')
def delete(task_id):
    """
    Defines the schema and validation rules for the task creation form.

    By using WTForms, we gain built-in CSRF (Cross-Site Request Forgery)
    protection and server-side validation. This ensures that 'task'
    descriptions meet length requirements before any database interaction occurs.
    """
    task = Todo.query.get_or_404(task_id)

    db.session.delete(task)
    db.session.commit()

    flash(f'Task "{task.task}" deleted.', 'danger')
    return redirect(url_for('home'))


# ---------------------------- RUN THE APP ------------------------------- #
if __name__ == "__main__":
    app.run(debug=True)
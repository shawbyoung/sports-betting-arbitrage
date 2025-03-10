# web_display.py
from flask import Flask, render_template
import threading

# Global variable to store the current odds table (HTML)
odds_table = ""

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("odds.html", odds_table=odds_table)

@app.route("/odds")
def get_odds():
    # Return the current odds table as HTML.
    return odds_table

def update_odds(new_table: str):
    """Update the global odds table variable."""
    global odds_table
    odds_table = new_table

def run_flask_app():
    app.run(host="0.0.0.0", port=5000, debug=False)

def start():
    thread = threading.Thread(target=run_flask_app)
    thread.daemon = True
    thread.start()

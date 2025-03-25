from flask import Flask, g, render_template, request, redirect
import sqlite3

app = Flask(__name__)

DATABASE = 'NZ_Wildlife.db'

def get_db():
    if not hasattr(g, '_database'):
        g._database = sqlite3.connect(DATABASE)
        g._database.row_factory = sqlite3.Row  
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def home():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM species")
    results = cursor.fetchall()
    cursor.close()
    return render_template("index.html", species=results)

@app.route('/add', methods=["GET", "POST"])
def add():
    if request.method == "POST":
        try:
            new_name = request.form.get("item_name")
            new_description = request.form.get("item_description")

            if new_name and new_description:  
                cursor = get_db().cursor()
                cursor.execute("INSERT INTO species (name, description) VALUES (?, ?)", (new_name, new_description))
                get_db().commit()
                cursor.close()
        except sqlite3.Error as e:
            print("Database error:", e)

    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
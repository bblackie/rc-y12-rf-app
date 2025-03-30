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
    db = get_db()
    cursor = db.cursor()
    
    # Get the selected field from the query parameter
    selected_field = request.args.get('field', default=None)
    
    # Get all data from the Species table
    cursor.execute("SELECT * FROM Species")
    species_results = cursor.fetchall()
    
    # Get all data from the Origin_Status table
    cursor.execute("SELECT * FROM Origin_Status")
    origin_status_results = cursor.fetchall()
    
    # Get all data from the Species_Type table
    cursor.execute("SELECT * FROM Species_Type")
    species_type_results = cursor.fetchall()
    
    # Get all data from the Status table
    cursor.execute("SELECT * FROM Status")
    status_results = cursor.fetchall()
    
    cursor.close()
    
    # Map column indices for different fields
    field_indices = {
        'species_name': 1,
        'scientific_name': 2,
        'species_type': 3,
        'origin_status': 4,
        'predator': 5,
        'prey': 6,
        'status': 7,
        'family': 8,
        'numbers': 9
    }
    
    return render_template(
        "index.html", 
        species=species_results,
        origin_status=origin_status_results,
        species_type=species_type_results,
        status=status_results,
        selected_field=selected_field,
        field_indices=field_indices
    )


@app.route("/species")
def species():
    cursor = get_db().cursor()
    field = request.args.get('field', default='species_name', type=str)
    search_query = request.args.get('name', default='', type=str)
    
    cursor.execute("SELECT * FROM species")
    results = cursor.fetchall()
    cursor.close()
    return render_template("species.html", species=results, search_query=search_query)


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
from flask import Flask, g, render_template, request, redirect, flash, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flashing messages

DATABASE = 'NZ_Wildlife.db'

def get_db():
    if not hasattr(g, '_database'):
        try:
            g._database = sqlite3.connect(DATABASE)
            g._database.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def home():
    try:
        cursor = get_db().cursor()
        
        # Get species data
        cursor.execute("""
            SELECT species_Id, species_name, scientific_name, species_type, 
                   origin_status, status, family, numbers, predator, prey,
                   image_path
            FROM species
        """)
        species_results = cursor.fetchall()
        
        # Get Status data
        cursor.execute("SELECT * FROM Status")
        status_results = cursor.fetchall()
        
        # Get Origin_Status data
        cursor.execute("SELECT * FROM Origin_Status")
        origin_status_results = cursor.fetchall()
        
        # Get Species_Type data
        cursor.execute("SELECT * FROM Species_Type")
        species_type_results = cursor.fetchall()
        
        cursor.close()
        
        return render_template('index.html',
                             species=species_results,
                             status=status_results,
                             origin_status=origin_status_results,
                             species_type=species_type_results)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        flash('An error occurred while fetching data', 'error')
        return render_template('index.html', species=[], status=[], origin_status=[], species_type=[])
    except Exception as e:
        print(f"Error in home route: {e}")
        return "Error loading data"


@app.route("/species")
def species():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM species")
    results = cursor.fetchall()
    cursor.close()
    return render_template("species.html", species=results)



@app.route('/add', methods=["GET", "POST"])
def add():
    if request.method == "POST":
        new_name = request.form.get("item_name", '').strip()
        new_description = request.form.get("item_description", '').strip()

        if not new_name or not new_description:
            return redirect('/')  # Return early if data is invalid

        try:
            cursor = get_db().cursor()
            cursor.execute("INSERT INTO species (name, description) VALUES (?, ?)", 
                         (new_name, new_description))
            get_db().commit()
            cursor.close()
        except sqlite3.Error as e:
            print(f"Database error in add route: {e}")
        except Exception as e:
            print(f"Unexpected error in add route: {e}")

    return redirect('/')

@app.route('/add_species', methods=['POST'])
def add_species():
    try:
        # Get form data
        species_name = request.form.get('species_name')
        scientific_name = request.form.get('scientific_name')
        species_type = request.form.get('species_type')
        origin_status = request.form.get('origin_status')
        status = request.form.get('status')
        family = request.form.get('family')
        numbers = request.form.get('numbers')
        predator = request.form.get('predator')
        prey = request.form.get('prey')
        image_path = request.form.get('image_path')

        # Validate required fields
        if not all([species_name, scientific_name, species_type, origin_status, status]):
            flash('Please fill in all required fields', 'error')
            return redirect('/')

        # Insert into database
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO species (
                species_name, scientific_name, species_type, origin_status,
                status, family, numbers, predator, prey, image_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (species_name, scientific_name, species_type, origin_status,
              status, family, numbers, predator, prey, image_path))
        
        db.commit()
        cursor.close()
        flash('Species added successfully!', 'success')
        return redirect('/')

    except sqlite3.Error as e:
        flash(f'Database error: {str(e)}', 'error')
        return redirect('/')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
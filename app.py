import sqlite3

conn = sqlite3.connect("notes.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS notes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT,
    pinned INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    edited_at TIMESTAMP
)
""")

conn.commit()
conn.close()

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    search = request.args.get("search")

    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    if not search:
        cursor.execute("SELECT * FROM notes ORDER BY pinned DESC, created_at DESC")
    
    else:
        cursor.execute("""
            SELECT * FROM notes WHERE title LIKE ? OR content LIKE ?
            ORDER BY pinned DESC, created_at DESC""",
            ("%" + search + "%", "%" + search + "%")
        )

    notes = cursor.fetchall()
    conn.close()

    return render_template("home.html", notes=notes)

@app.route("/add", methods=["GET", "POST"])
def add_note():
    if request.method == "POST":
        conn = sqlite3.connect("notes.db")
        cursor = conn.cursor()

        title = request.form.get("title")
        content = request.form.get("content")

        cursor.execute("""
            INSERT INTO notes(title, content)
            VALUES(?, ?)""",
            (title, content)
            )
        
        conn.commit()
        conn.close()  

        return redirect(url_for("home"))
    
    return render_template("add_note.html")

@app.route("/edit/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):
    
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    if request.method == "GET":
        
        cursor.execute(
            "SELECT * FROM notes WHERE id = ?",
            (note_id,)
        )
        note = cursor.fetchone()
        
        return render_template("edit_note.html", note=note)

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        cursor.execute("""
            UPDATE notes
            SET
            title = ?,
            content =?,
            edited_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """,
        (title, content, note_id)
        )

        conn.commit()
        conn.close()
        return redirect(url_for("home"))
    

@app.route("/delete/<int:note_id>")
def delete(note_id):
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM notes WHERE id = ?",
        (note_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))

@app.route("/pin/<int:note_id>/<int:pin_value>")
def pin_note(note_id, pin_value):
    if pin_value == 0:
        new_pin = 1
    else:
        new_pin = 0
    
    conn = sqlite3.connect("notes.db")
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE notes
    SET pinned = ?
    WHERE id = ?
    """,
    (new_pin, note_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
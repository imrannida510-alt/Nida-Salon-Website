from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = "nida_salon_secret_key"


def create_database():
    connection = sqlite3.connect("bookings.db")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            service TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def add_status_column():
    connection = sqlite3.connect("bookings.db")

    try:
        connection.execute(
            "ALTER TABLE bookings ADD COLUMN status TEXT NOT NULL DEFAULT 'Confirmed'"
        )
        connection.commit()
    except sqlite3.OperationalError:
        pass

    connection.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/book", methods=["POST"])
def book():

    data = request.get_json()

    name = data.get("name")
    service = data.get("service")
    date = data.get("date")
    time = data.get("time")

    connection = sqlite3.connect("bookings.db")

    connection.execute(
        """
        INSERT INTO bookings (name, service, date, time, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, service, date, time, "Confirmed")
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Booking saved successfully!"
    })


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":

            session["admin_logged_in"] = True

            return redirect("/admin")

    return render_template("login.html")


@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    connection = sqlite3.connect("bookings.db")

    bookings = connection.execute(
        "SELECT * FROM bookings"
    ).fetchall()

    connection.close()

    return render_template("admin.html", bookings=bookings)


@app.route("/delete/<int:booking_id>")
def delete_booking(booking_id):

    if not session.get("admin_logged_in"):
        return redirect("/login")

    connection = sqlite3.connect("bookings.db")

    connection.execute(
        "DELETE FROM bookings WHERE id = ?",
        (booking_id,)
    )

    connection.commit()
    connection.close()

    return redirect("/admin")


@app.route("/edit/<int:booking_id>", methods=["GET", "POST"])
def edit_booking(booking_id):

    if not session.get("admin_logged_in"):
        return redirect("/login")

    connection = sqlite3.connect("bookings.db")

    if request.method == "POST":

        name = request.form["name"]
        service = request.form["service"]
        date = request.form["date"]
        time = request.form["time"]

        connection.execute(
            """
            UPDATE bookings
            SET name = ?, service = ?, date = ?, time = ?
            WHERE id = ?
            """,
            (name, service, date, time, booking_id)
        )

        connection.commit()
        connection.close()

        return redirect("/admin")

    booking = connection.execute(
        "SELECT * FROM bookings WHERE id = ?",
        (booking_id,)
    ).fetchone()

    connection.close()

    return render_template("edit.html", booking=booking)


@app.route("/status/<int:booking_id>", methods=["POST"])
def update_status(booking_id):

    if not session.get("admin_logged_in"):
        return redirect("/login")

    status = request.form["status"]

    connection = sqlite3.connect("bookings.db")

    connection.execute(
        "UPDATE bookings SET status = ? WHERE id = ?",
        (status, booking_id)
    )

    connection.commit()
    connection.close()

    return redirect("/admin")


@app.route("/dashboard")
def dashboard():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    connection = sqlite3.connect("bookings.db")

    total = connection.execute(
        "SELECT COUNT(*) FROM bookings"
    ).fetchone()[0]

    confirmed = connection.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = 'Confirmed'"
    ).fetchone()[0]

    completed = connection.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = 'Completed'"
    ).fetchone()[0]

    cancelled = connection.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = 'Cancelled'"
    ).fetchone()[0]

    connection.close()

    return render_template(
        "dashboard.html",
        total=total,
        confirmed=confirmed,
        completed=completed,
        cancelled=cancelled
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    create_database()
    add_status_column()
    app.run(debug=True)
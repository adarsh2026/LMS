from flask import Flask, render_template, request, jsonify
import psycopg2
from datetime import datetime

app = Flask(__name__)

# DATABASE CONNECTION
def connect_db():
    return psycopg2.connect(
        host="localhost",
        database="library_db",
        user="postgres",
        password="Admin123",
        port="5432"
    )


# HOME
@app.route("/")
def home():
    return render_template("index.html")


# ADMIN LOGIN
@app.route("/auth/login", methods=["POST"])
def admin_login():

    try:

        data = request.json

        if not data:
            return jsonify({
                "status":"error",
                "message":"No data received"
            })

        admin_id = data.get("id")
        password = data.get("password")

        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM public.admins WHERE id=%s AND password=%s",
            (admin_id,password)
        )

        admin = cur.fetchone()

        cur.close()
        conn.close()

        if admin:
            return jsonify({
                "status":"success",
                "message":"Login successful"
            })
        else:
            return jsonify({
                "status":"error",
                "message":"Invalid ID or Password"
            })

    except Exception as e:

        print("LOGIN ERROR:",e)

        return jsonify({
            "status":"error",
            "message":"Server error"
        })


# ADD BOOK
@app.route("/books/add", methods=["POST"])
def add_book():

    try:

        data = request.json

        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO public.books (id,title,author,total,available)
            VALUES (%s,%s,%s,%s,%s)
            """,
            (
                data["id"],
                data["title"],
                data["author"],
                data["total"],
                data["total"]
            )
        )

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"message":"Book added"})

    except Exception as e:
        print("BOOK ERROR:",e)
        return jsonify({"message":"Error adding book"})


# LIST BOOKS
@app.route("/books/list")
def list_books():

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM public.books")

    rows = cur.fetchall()

    books = []

    for r in rows:
        books.append({
            "id":r[0],
            "title":r[1],
            "author":r[2],
            "total":r[3],
            "available":r[4]
        })

    cur.close()
    conn.close()

    return jsonify(books)


# DELETE BOOK
@app.route("/books/delete/<id>", methods=["DELETE"])
def delete_book(id):

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM public.books WHERE id=%s",(id,))

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message":"Book deleted"})


# ADD STUDENT
@app.route("/students/add", methods=["POST"])
def add_student():

    try:

        data = request.json

        conn = connect_db()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO public.students (id,name,course)
            VALUES (%s,%s,%s)
            """,
            (
                data["id"],
                data["name"],
                data["course"]
            )
        )

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"message":"Student added"})

    except Exception as e:
        print("STUDENT ERROR:",e)
        return jsonify({"message":"Error adding student"})


# LIST STUDENTS
@app.route("/students/list")
def list_students():

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM public.students")

    rows = cur.fetchall()

    students = []

    for r in rows:
        students.append({
            "id":r[0],
            "name":r[1],
            "course":r[2]
        })

    cur.close()
    conn.close()

    return jsonify(students)


# DELETE STUDENT
@app.route("/students/delete/<id>", methods=["DELETE"])
def delete_student(id):

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM public.students WHERE id=%s",(id,))

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message":"Student deleted"})


# ISSUE BOOK
@app.route("/issue", methods=["POST"])
def issue_book():

    data = request.json
    book_id = data["book_id"]
    student_id = data["student_id"]

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT id FROM public.students WHERE id=%s",(student_id,))
    student = cur.fetchone()

    if not student:
        cur.close()
        conn.close()
        return jsonify({"message":"Student not found"})

    cur.execute("SELECT available FROM public.books WHERE id=%s",(book_id,))
    book = cur.fetchone()

    if not book:
        cur.close()
        conn.close()
        return jsonify({"message":"Book not found"})

    if book[0] <= 0:
        cur.close()
        conn.close()
        return jsonify({"message":"Book not available"})

    cur.execute(
        "UPDATE public.books SET available=available-1 WHERE id=%s",
        (book_id,)
    )

    cur.execute(
        """
        INSERT INTO public.transactions
        (book_id,student_id,action,time)
        VALUES (%s,%s,%s,%s)
        """,
        (book_id,student_id,"issue",datetime.now())
    )

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message":"Book issued"})


# RETURN BOOK
@app.route("/return", methods=["POST"])
def return_book():

    data = request.json
    book_id = data["book_id"]
    student_id = data["student_id"]

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "UPDATE public.books SET available=available+1 WHERE id=%s",
        (book_id,)
    )

    cur.execute(
        """
        INSERT INTO public.transactions
        (book_id,student_id,action,time)
        VALUES (%s,%s,%s,%s)
        """,
        (book_id,student_id,"return",datetime.now())
    )

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message":"Book returned"})


# LIST TRANSACTIONS
@app.route("/transactions/list")
def transactions():

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id,book_id,student_id,action,time FROM public.transactions"
    )

    rows = cur.fetchall()

    data=[]

    for r in rows:
        data.append({
            "id":r[0],
            "book_id":r[1],
            "student_id":r[2],
            "action":r[3],
           "time": r[4].strftime("%Y-%m-%d %H:%M:%S")
        })

    cur.close()
    conn.close()

    return jsonify(data)


# DELETE TRANSACTION
@app.route("/transactions/delete/<int:id>", methods=["DELETE"])
def delete_transaction(id):

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM public.transactions WHERE id=%s",(id,))

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message":"Transaction deleted"})


# RUN SERVER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
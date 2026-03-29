import tornado.ioloop
import tornado.web
from db import connect_db


# ---------------- BASE HANDLER ----------------

class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        return self.get_secure_cookie("user")

    def get_current_role(self):
        role = self.get_secure_cookie("role")
        if role:
            return role.decode()
        return None


# ---------------- LOGIN ----------------

class LoginHandler(BaseHandler):

    def get(self):
        self.render("login.html")

    async def post(self):

        username = self.get_argument("username")
        password = self.get_argument("password")

        conn = await connect_db()

        if not conn:
            self.write("Database Error")
            return

        admin = await conn.fetchrow(
            "SELECT * FROM admins WHERE username=$1 AND password=$2",
            username, password
        )

        if admin:
            self.set_secure_cookie("user", username)
            self.set_secure_cookie("role", "admin")
            self.redirect("/admin")
            return

        student = await conn.fetchrow(
            "SELECT * FROM students WHERE student_id=$1 AND password=$2",
            username, password
        )

        if student:
            self.set_secure_cookie("user", username)
            self.set_secure_cookie("role", "student")
            self.redirect("/student")
            return

        self.write("Invalid Login")


# ---------------- LOGOUT ----------------

class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie("user")
        self.clear_cookie("role")
        self.redirect("/")


# ---------------- ADMIN DASHBOARD ----------------

class AdminDashboardHandler(BaseHandler):

    @tornado.web.authenticated
    async def get(self):

        if self.get_current_role() != "admin":
            self.redirect("/")
            return

        data_type = self.get_argument("type", "")

        conn = await connect_db()

        total_books = await conn.fetchval("SELECT COUNT(*) FROM books")
        total_students = await conn.fetchval("SELECT COUNT(*) FROM students")
        issued_books = await conn.fetchval("SELECT COUNT(*) FROM issued_books")
        available_books = await conn.fetchval("SELECT COALESCE(SUM(quantity),0) FROM books")

        data = []

        if data_type == "books":

            data = await conn.fetch("""
            SELECT id,book_code,book_name,author,quantity
            FROM books
            ORDER BY id
            """)

        elif data_type == "students":

            data = await conn.fetch("""
            SELECT student_id,name,course
            FROM students
            ORDER BY student_id
            """)

        elif data_type == "history":

            data = await conn.fetch("""
            SELECT student_id,book_code,issue_date,return_date
            FROM issued_books
            ORDER BY issue_date DESC
            """)

        self.render(
            "admin_dashboard.html",
            total_books=total_books,
            total_students=total_students,
            issued_books=issued_books,
            available_books=available_books,
            data=data,
            type=data_type
        )


# ---------------- ADD BOOK ----------------

class BooksHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):

        if self.get_current_role() != "admin":
            self.redirect("/")
            return

        self.render("add_book.html")

    async def post(self):

        book_code = self.get_argument("book_code")
        book_name = self.get_argument("book_name")
        author = self.get_argument("author")
        quantity = self.get_argument("quantity")

        conn = await connect_db()

        await conn.execute("""
        INSERT INTO books(book_code,book_name,author,quantity)
        VALUES($1,$2,$3,$4)
        """, book_code, book_name, author, quantity)

        self.redirect("/admin?type=books")


# ---------------- ADD STUDENT ----------------

class StudentsHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):

        if self.get_current_role() != "admin":
            self.redirect("/")
            return

        self.render("add_student.html")

    async def post(self):

        student_id = self.get_argument("student_id")
        password = self.get_argument("password")
        name = self.get_argument("name")
        course = self.get_argument("course")

        conn = await connect_db()

        await conn.execute("""
        INSERT INTO students(student_id,password,name,course)
        VALUES($1,$2,$3,$4)
        """, student_id, password, name, course)

        self.redirect("/admin?type=students")


# ---------------- ISSUE BOOK ----------------

class IssueBookHandler(BaseHandler):

    @tornado.web.authenticated
    async def get(self):

        if self.get_current_role() != "student":
            self.redirect("/")
            return

        conn = await connect_db()

        books = await conn.fetch(
            "SELECT book_code,book_name FROM books WHERE quantity > 0"
        )

        self.render("issue_book.html", books=books)

    async def post(self):

        student_id = self.get_secure_cookie("user").decode()
        book_code = self.get_argument("book_code")

        conn = await connect_db()

        await conn.execute("""
        INSERT INTO issued_books(student_id,book_code,issue_date)
        VALUES($1,$2,CURRENT_DATE)
        """, student_id, book_code)

        await conn.execute("""
        UPDATE books
        SET quantity = quantity - 1
        WHERE book_code=$1
        """, book_code)

        self.redirect("/student")


# ---------------- RETURN BOOK ----------------

class ReturnBookHandler(BaseHandler):

    @tornado.web.authenticated
    async def get(self):

        if self.get_current_role() != "student":
            self.redirect("/")
            return

        student_id = self.get_secure_cookie("user").decode()

        conn = await connect_db()

        books = await conn.fetch("""
        SELECT book_code
        FROM issued_books
        WHERE student_id=$1 AND return_date IS NULL
        """, student_id)

        self.render("return_book.html", books=books)

    async def post(self):

        student_id = self.get_secure_cookie("user").decode()
        book_code = self.get_argument("book_code")

        conn = await connect_db()

        await conn.execute("""
        UPDATE issued_books
        SET return_date = CURRENT_DATE
        WHERE student_id=$1 AND book_code=$2
        """, student_id, book_code)

        await conn.execute("""
        UPDATE books
        SET quantity = quantity + 1
        WHERE book_code=$1
        """, book_code)

        self.redirect("/student")


# ---------------- STUDENT DASHBOARD ----------------

class StudentDashboardHandler(BaseHandler):

    @tornado.web.authenticated
    async def get(self):

        if self.get_current_role() != "student":
            self.redirect("/")
            return

        conn = await connect_db()

        books = await conn.fetch("""
        SELECT id,book_code,book_name,author,quantity
        FROM books
        ORDER BY id
        """)

        self.render("student_dashboard.html", books=books)


# ---------------- APPLICATION ----------------

def make_app():

    return tornado.web.Application(

        [

            (r"/", LoginHandler),
            (r"/logout", LogoutHandler),

            (r"/admin", AdminDashboardHandler),
            (r"/student", StudentDashboardHandler),

            (r"/books", BooksHandler),
            (r"/students", StudentsHandler),

            (r"/issue", IssueBookHandler),
            (r"/return", ReturnBookHandler),

        ],

        template_path="templates",
        static_path="static",

        cookie_secret="library_secret_key",
        login_url="/",

        debug=True
    )


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":

    app = make_app()

    app.listen(8888)

    print("Server Running : http://localhost:8888")

    tornado.ioloop.IOLoop.current().start()
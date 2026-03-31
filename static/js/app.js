$(document).ready(function () {

    const $loginScreen = $("#loginScreen")
    const $adminLoginBtn = $("#adminLoginBtn")
    const $adminCloseBtn = $("#adminCloseBtn")
    const $adminLogoutBtn = $("#adminLogoutBtn")
    const $loginForm = $("#loginForm")

    // ---------------- LOGIN UI ----------------

    $adminLoginBtn.click(() => $loginScreen.removeClass("d-none"))
    $adminCloseBtn.click(() => $loginScreen.addClass("d-none"))

    $loginForm.submit(async function (e) {
        e.preventDefault()

        const id = $("#loginId").val()
        const password = $("#loginPassword").val()

        const res = await fetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id, password })
        })

        const data = await res.json()

        if (data.status === "success") {

            alert("Admin Login Successful")

            $loginScreen.addClass("d-none")
            $adminLoginBtn.addClass("d-none")
            $adminLogoutBtn.removeClass("d-none")

            $(".admin-only").removeClass("d-none")

        } else {
            alert(data.message)
        }
    })

    $adminLogoutBtn.click(() => {
        $adminLoginBtn.removeClass("d-none")
        $adminLogoutBtn.addClass("d-none")
        $(".admin-only").addClass("d-none")
        alert("Logged out")
    })

    // ---------------- SIDEBAR ----------------

    $(".sidebar-link").click(function () {
        $(".sidebar-link").removeClass("active")
        $(this).addClass("active")

        const target = $(this).data("target")

        $(".tab-pane-custom").addClass("d-none")
        $("#" + target).removeClass("d-none")
    })

    // ---------------- BOOKS ----------------

    window.loadBooks = async function () {

        const res = await fetch("/books/list")
        const data = await res.json()

        const $table = $("#booksTableBody")
        $table.html("")

        let available = 0

        data.forEach(book => {

            available += book.available

            $table.append(`
                <tr>
                    <td>${book.id}</td>
                    <td>${book.title}</td>
                    <td>${book.author}</td>
                    <td>${book.total}</td>
                    <td>${book.available}</td>
                    <td class="admin-only d-none">
                        <button class="btn btn-danger btn-sm delete-book" data-id="${book.id}">Delete</button>
                    </td>
                </tr>
            `)
        })

        $("#statTotalBooks").text(data.length)
        $("#statAvailable").text(available)
    }

    $(document).on("click", ".delete-book", async function () {
        const id = $(this).data("id")

        if (!confirm("Delete book?")) return

        await fetch("/books/delete/" + id, { method: "DELETE" })
        loadBooks()
    })

    window.addBook = async function () {

        const id = $("#bookId").val()
        const title = $("#bookTitle").val()
        const author = $("#bookAuthor").val()
        const total = $("#bookTotal").val()

        const res = await fetch("/books/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id, title, author, total })
        })

        const data = await res.json()
        alert(data.message)

        loadBooks()
    }

    // ---------------- STUDENTS ----------------

    window.loadStudents = async function () {

        const res = await fetch("/students/list")
        const data = await res.json()

        const $table = $("#studentsTableBody2")
        $table.html("")

        data.forEach(student => {
            $table.append(`
                <tr>
                    <td>${student.id}</td>
                    <td>${student.name}</td>
                    <td>${student.course}</td>
                    <td class="admin-only d-none">
                        <button class="btn btn-danger btn-sm delete-student" data-id="${student.id}">Delete</button>
                    </td>
                </tr>
            `)
        })

        $("#statStudents").text(data.length)
    }

    $(document).on("click", ".delete-student", async function () {
        const id = $(this).data("id")

        if (!confirm("Delete student?")) return

        await fetch("/students/delete/" + id, { method: "DELETE" })
        loadStudents()
    })

    window.addStudent = async function () {

        const id = $("#studentId").val()
        const name = $("#studentName").val()
        const course = $("#studentCourse").val()

        const res = await fetch("/students/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id, name, course })
        })

        const data = await res.json()
        alert(data.message)

        loadStudents()
    }

    // ---------------- ISSUE / RETURN ----------------

    window.issueBook = async function () {

        const book_id = $("#issueBookId").val()
        const student_id = $("#issueStudentId").val()

        const res = await fetch("/issue", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ book_id, student_id })
        })

        const data = await res.json()
        alert(data.message)

        loadBooks()
        loadTransactions()
    }

    window.returnBook = async function () {

        const book_id = $("#returnBookId").val()
        const student_id = $("#returnStudentId").val()

        const res = await fetch("/return", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ book_id, student_id })
        })

        const data = await res.json()
        alert(data.message)

        loadBooks()
        loadTransactions()
    }

    // ---------------- TRANSACTIONS ----------------

    window.loadTransactions = async function () {

        const res = await fetch("/transactions/list")
        const data = await res.json()

        const $table = $("#transactionsTableBody")
        $table.html("")

        data.forEach((t, index) => {
            $table.append(`
                <tr>
                    <td>${index + 1}</td>
                    <td>${t.book_id}</td>
                    <td>${t.student_id}</td>
                    <td>${t.action}</td>
                    <td>${t.time}</td>
                    <td class="admin-only d-none">
                        <button class="btn btn-danger btn-sm delete-transaction" data-id="${t.id}">Delete</button>
                    </td>
                </tr>
            `)
        })

        $("#statTransactions").text(data.length)
    }

    $(document).on("click", ".delete-transaction", async function () {
        const id = $(this).data("id")

        if (!confirm("Delete transaction?")) return

        await fetch("/transactions/delete/" + id, { method: "DELETE" })
        loadTransactions()
    })

    // ---------------- INITIAL LOAD ----------------

    loadBooks()
    loadStudents()
    loadTransactions()

})
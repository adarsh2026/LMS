document.addEventListener("DOMContentLoaded", () => {

const loginScreen = document.getElementById("loginScreen")
const adminLoginBtn = document.getElementById("adminLoginBtn")
const adminCloseBtn = document.getElementById("adminCloseBtn")
const adminLogoutBtn = document.getElementById("adminLogoutBtn")
const loginForm = document.getElementById("loginForm")

adminLoginBtn.onclick = () => loginScreen.classList.remove("d-none")
adminCloseBtn.onclick = () => loginScreen.classList.add("d-none")

loginForm.addEventListener("submit", async (e)=>{

e.preventDefault()

const id = document.getElementById("loginId").value
const password = document.getElementById("loginPassword").value

const res = await fetch("/auth/login",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({id,password})
})

const data = await res.json()

if(data.status==="success"){

alert("Admin Login Successful")

loginScreen.classList.add("d-none")

adminLoginBtn.classList.add("d-none")
adminLogoutBtn.classList.remove("d-none")

document.querySelectorAll(".admin-only").forEach(el=>{
el.classList.remove("d-none")
})

}else{
alert(data.message)
}

})


adminLogoutBtn.onclick=()=>{

adminLoginBtn.classList.remove("d-none")
adminLogoutBtn.classList.add("d-none")

document.querySelectorAll(".admin-only").forEach(el=>{
el.classList.add("d-none")
})

alert("Logged out")

}


const sidebarLinks=document.querySelectorAll(".sidebar-link")
const tabs=document.querySelectorAll(".tab-pane-custom")

sidebarLinks.forEach(link=>{
link.onclick=()=>{
sidebarLinks.forEach(l=>l.classList.remove("active"))
link.classList.add("active")

const target=link.getAttribute("data-target")

tabs.forEach(tab=>tab.classList.add("d-none"))

document.getElementById(target).classList.remove("d-none")
}
})


window.loadBooks = async function(){

const res = await fetch("/books/list")
const data = await res.json()

const table=document.getElementById("booksTableBody")

table.innerHTML=""

let available=0

data.forEach(book=>{

available+=book.available

table.innerHTML+=`
<tr>
<td>${book.id}</td>
<td>${book.title}</td>
<td>${book.author}</td>
<td>${book.total}</td>
<td>${book.available}</td>
<td class="admin-only d-none">
<button class="btn btn-danger btn-sm" onclick="deleteBook('${book.id}')">Delete</button>
</td>
</tr>
`
})

document.getElementById("statTotalBooks").textContent=data.length
document.getElementById("statAvailable").textContent=available

}


window.addBook = async function(){

const id=document.getElementById("bookId").value
const title=document.getElementById("bookTitle").value
const author=document.getElementById("bookAuthor").value
const total=document.getElementById("bookTotal").value

const res=await fetch("/books/add",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({id,title,author,total})
})

const data=await res.json()

alert(data.message)

loadBooks()

}


window.deleteBook = async function(id){

if(!confirm("Delete book?")) return

await fetch("/books/delete/"+id,{method:"DELETE"})

loadBooks()

}


window.loadStudents = async function(){

const res=await fetch("/students/list")
const data=await res.json()

const table=document.getElementById("studentsTableBody2")

table.innerHTML=""

data.forEach(student=>{

table.innerHTML+=`
<tr>
<td>${student.id}</td>
<td>${student.name}</td>
<td>${student.course}</td>
<td class="admin-only d-none">
<button class="btn btn-danger btn-sm" onclick="deleteStudent('${student.id}')">Delete</button>
</td>
</tr>
`

})

document.getElementById("statStudents").textContent=data.length

}


window.addStudent = async function(){

const id=document.getElementById("studentId").value
const name=document.getElementById("studentName").value
const course=document.getElementById("studentCourse").value

const res=await fetch("/students/add",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({id,name,course})
})

const data=await res.json()

alert(data.message)

loadStudents()

}


window.deleteStudent = async function(id){

if(!confirm("Delete student?")) return

await fetch("/students/delete/"+id,{method:"DELETE"})

loadStudents()

}


window.issueBook = async function(){

const book_id=document.getElementById("issueBookId").value
const student_id=document.getElementById("issueStudentId").value

const res=await fetch("/issue",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({book_id,student_id})
})

const data=await res.json()

alert(data.message)

loadBooks()
loadTransactions()

}


window.returnBook = async function(){

const book_id=document.getElementById("returnBookId").value
const student_id=document.getElementById("returnStudentId").value

const res=await fetch("/return",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({book_id,student_id})
})

const data=await res.json()

alert(data.message)

loadBooks()
loadTransactions()

}


window.loadTransactions = async function(){

const res=await fetch("/transactions/list")
const data=await res.json()

const table=document.getElementById("transactionsTableBody")

table.innerHTML=""

data.forEach((t,index)=>{

table.innerHTML+=`
<tr>
<td>${index+1}</td>
<td>${t.book_id}</td>
<td>${t.student_id}</td>
<td>${t.action}</td>
<td>${t.time}</td>
<td class="admin-only d-none">
<button class="btn btn-danger btn-sm" onclick="deleteTransaction(${t.id})">Delete</button>
</td>
</tr>
`
})

document.getElementById("statTransactions").textContent=data.length

}


window.deleteTransaction = async function(id){

if(!confirm("Delete transaction?")) return

await fetch("/transactions/delete/"+id,{method:"DELETE"})

loadTransactions()

}


loadBooks()
loadStudents()
loadTransactions()

})
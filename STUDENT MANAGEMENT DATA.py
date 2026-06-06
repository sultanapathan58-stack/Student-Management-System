from tkinter import *
from tkinter import ttk, messagebox
import pymysql

# ---------------------------- MAIN WINDOW ----------------------------
app = Tk()
app.title("Student Data Management System")
app.state("zoomed")
app['bg'] = "white"

# ---------------------------- VARIABLES ----------------------------
name = StringVar()
age = IntVar()
adhar_no = StringVar()      # Changed to StringVar to handle large numbers properly
gender = StringVar()
mobile_no = StringVar()      # Changed to StringVar
city = StringVar()
course = StringVar()

# ---------------------------- DATABASE CONNECTION ----------------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "sultana",
    "database": "aaa_company"
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

def create_table_if_not_exists():
    """Create the application table if it doesn't exist"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS application (
                name VARCHAR(100),
                age INT,
                adhar_no VARCHAR(20) PRIMARY KEY,
                gender VARCHAR(10),
                mobile_no VARCHAR(15),
                city VARCHAR(50),
                course VARCHAR(50)
            )
        """)
        conn.commit()
        conn.close()
        print("Table ensured.")
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to create table:\n{e}")
        app.destroy()

# ---------------------------- FUNCTIONS ----------------------------
def fetch_data():
    """Fetch all records and display in Treeview"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, age, adhar_no, gender, mobile_no, city, course FROM application")
        rows = cur.fetchall()
        conn.close()

        student_table.delete(*student_table.get_children())
        for row in rows:
            student_table.insert('', END, values=row)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch data:\n{e}")

def add_data():
    """Insert new student record"""
    # Validation
    if not name.get().strip():
        messagebox.showwarning("Warning", "Name is required!")
        return
    if not age.get():
        messagebox.showwarning("Warning", "Age is required!")
        return
    if not adhar_no.get().strip():
        messagebox.showwarning("Warning", "Aadhar Number is required!")
        return
    if not gender.get():
        messagebox.showwarning("Warning", "Gender is required!")
        return
    if not mobile_no.get().strip():
        messagebox.showwarning("Warning", "Mobile Number is required!")
        return
    if not city.get().strip():
        messagebox.showwarning("Warning", "City is required!")
        return
    if not course.get():
        messagebox.showwarning("Warning", "Course is required!")
        return

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO application (name, age, adhar_no, gender, mobile_no, city, course) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (name.get().strip(), age.get(), adhar_no.get().strip(), gender.get(), mobile_no.get().strip(), city.get().strip(), course.get())
        )
        conn.commit()
        conn.close()
        fetch_data()
        clear_fields()
        messagebox.showinfo("Success", "Record added successfully!")
    except pymysql.IntegrityError:
        messagebox.showerror("Error", "Aadhar number already exists!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add record:\n{e}")

def update_data():
    """Update selected student record using Aadhar number"""
    if not adhar_no.get().strip():
        messagebox.showwarning("Warning", "Please select a record to update!")
        return

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE application SET name=%s, age=%s, gender=%s, mobile_no=%s, city=%s, course=%s WHERE adhar_no=%s",
            (name.get().strip(), age.get(), gender.get(), mobile_no.get().strip(), city.get().strip(), course.get(), adhar_no.get().strip())
        )
        conn.commit()
        conn.close()
        fetch_data()
        clear_fields()
        messagebox.showinfo("Success", "Record updated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update record:\n{e}")

def delete_data():
    """Delete record based on Aadhar number"""
    if not adhar_no.get().strip():
        messagebox.showwarning("Warning", "Please select a record to delete!")
        return

    if messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM application WHERE adhar_no=%s", (adhar_no.get().strip(),))
            conn.commit()
            conn.close()
            fetch_data()
            clear_fields()
            messagebox.showinfo("Success", "Record deleted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete record:\n{e}")

def clear_fields():
    """Clear all input fields"""
    name.set("")
    age.set(0)
    adhar_no.set("")
    gender.set("")
    mobile_no.set("")
    city.set("")
    course_combo.set("")

def search_data():
    """Search records based on selected column and keyword"""
    search_by = search_combo.get()
    keyword = search_entry.get().strip()

    if not search_by or not keyword:
        messagebox.showwarning("Warning", "Please select a search field and enter a keyword!")
        return

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        column_map = {
            "NAME": "name",
            "AGE": "age",
            "ADHAR NO": "adhar_no",
            "GENDER": "gender",
            "MOBILENO": "mobile_no",
            "CITY": "city",
            "COURSE": "course"
        }
        db_column = column_map.get(search_by, "name")
        # Use LIKE for all columns except numeric types (but we'll use LIKE for all for simplicity)
        query = f"SELECT name, age, adhar_no, gender, mobile_no, city, course FROM application WHERE {db_column} LIKE %s"
        cur.execute(query, (f"%{keyword}%",))
        rows = cur.fetchall()
        conn.close()

        student_table.delete(*student_table.get_children())
        for row in rows:
            student_table.insert('', END, values=row)

        if not rows:
            messagebox.showinfo("No Results", "No matching records found.")
    except Exception as e:
        messagebox.showerror("Error", f"Search failed:\n{e}")

def show_all():
    fetch_data()
    search_entry.delete(0, END)

def on_treeview_select(event):
    selected = student_table.selection()
    if not selected:
        return
    item = student_table.item(selected[0])
    values = item['values']
    if values:
        name.set(values[0])
        age.set(values[1])
        adhar_no.set(values[2])
        gender.set(values[3])
        mobile_no.set(values[4])
        city.set(values[5])
        course_combo.set(values[6])

def exit_app():
    if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
        app.destroy()

# ---------------------------- UI FRAMES ----------------------------
# Title Label
Label(app, text="STUDENT MANAGEMENT SYSTEM", font="arial 20 bold", fg="white", bg="blue", height=1).pack(fill="x")

# Frame 1: Student Details
frame1 = Frame(app, bd=5, bg="white")
frame1.place(x=4, y=50, height=180, width=1270)

Label(frame1, text="NAME:", fg="blue", font="arial 15 bold", bg="white").place(x=80, y=20)
Entry(frame1, bg="white", fg="black", bd=4, font="arial 15 bold", textvariable=name).place(x=160, y=20, width=250, height=30)

Label(frame1, text="ADHAR NO:", fg="blue", font="arial 15 bold", bg="white").place(x=440, y=20)
Entry(frame1, bg="white", fg="black", bd=4, font="arial 15 bold", textvariable=adhar_no).place(x=560, y=20, width=250, height=30)

Label(frame1, text="MOBILE NO:", fg="blue", font="arial 15 bold", bg="white").place(x=850, y=20)
Entry(frame1, bg="white", fg="black", bd=4, font="arial 15 bold", textvariable=mobile_no).place(x=990, y=20, width=250, height=30)

Label(frame1, text="AGE:", fg="blue", font="arial 15 bold", bg="white").place(x=80, y=90)
Entry(frame1, bg="white", fg="black", bd=4, font="arial 15 bold", textvariable=age).place(x=160, y=90, width=250, height=30)

Label(frame1, text="GENDER:", fg="blue", font="arial 15 bold", bg="white").place(x=440, y=90)
gender_combo = ttk.Combobox(frame1, font="arial 15 bold", textvariable=gender)
gender_combo['values'] = ("FEMALE", "MALE", "OTHER")
gender_combo.place(x=560, y=90, height=30, width=250)

Label(frame1, text="CITY:", fg="blue", font="arial 15 bold", bg="white").place(x=850, y=90)
Entry(frame1, bg="white", fg="black", bd=4, font="arial 15 bold", textvariable=city).place(x=990, y=90, width=250, height=30)

# Frame 2: Course & Search
frame2 = Frame(app, bd=5, bg="blue")
frame2.place(x=4, y=240, height=100, width=1270)

Label(frame2, text="COURSE:", fg="white", font="arial 15 bold", bg="blue").place(x=20, y=30)
course_combo = ttk.Combobox(frame2, font="arial 15 bold", textvariable=course)
course_combo['values'] = ("JAVA", "C++", "C", "PYTHON", "SQL", "JAVASCRIPT", "C#", "REACT JS", "CSS", "HTML", "RUBY", "SWIFT", "R", "RUST", "BASH", "ANGULAR", "PHP")
course_combo.place(x=120, y=30, height=30, width=250)

Label(frame2, text="SEARCH BY:", fg="white", font="arial 15 bold", bg="blue").place(x=380, y=30)
search_combo = ttk.Combobox(frame2, font="arial 15 bold")
search_combo['values'] = ("NAME", "AGE", "ADHAR NO", "GENDER", "MOBILENO", "CITY", "COURSE")
search_combo.place(x=510, y=30, height=30, width=150)

search_entry = Entry(frame2, bg="white", fg="black", bd=2, font="arial 15 bold")
search_entry.place(x=680, y=30, width=250, height=30)
Button(frame2, text="Search", fg="black", bg="lightblue", bd=3, font="arial 12 bold", command=search_data).place(x=940, y=28, height=35, width=80)
Button(frame2, text="Show All", fg="black", bg="white", bd=3, font="arial 12 bold", command=show_all).place(x=1030, y=28, height=35, width=100)

# Frame 3: Treeview Table
frame3 = Frame(app, bd=5, bg="white")
frame3.place(x=4, y=350, height=250, width=1270)

y_scroll = Scrollbar(frame3, orient=VERTICAL)
x_scroll = Scrollbar(frame3, orient=HORIZONTAL)

student_table = ttk.Treeview(frame3, columns=("NAME", "AGE", "ADHAR NO", "GENDER", "MOBILE NO", "CITY", "COURSE"),
                             yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
y_scroll.config(command=student_table.yview)
x_scroll.config(command=student_table.xview)

y_scroll.pack(side=RIGHT, fill=Y)
x_scroll.pack(side=BOTTOM, fill=X)
student_table.pack(fill=BOTH, expand=True)

student_table.heading("NAME", text="NAME")
student_table.heading("AGE", text="AGE")
student_table.heading("ADHAR NO", text="ADHAR NO")
student_table.heading("GENDER", text="GENDER")
student_table.heading("MOBILE NO", text="MOBILE NO")
student_table.heading("CITY", text="CITY")
student_table.heading("COURSE", text="COURSE")
student_table['show'] = "headings"

student_table.bind("<ButtonRelease-1>", on_treeview_select)

# Frame 4: Action Buttons
frame4 = Frame(app, bd=5, bg="blue")
frame4.place(x=4, y=610, height=70, width=1270)

Button(frame4, text="ADD", fg="black", bg="white", bd=3, font="arial 15 bold", width=10, command=add_data).place(x=100, y=10)
Button(frame4, text="UPDATE", fg="black", bg="white", bd=3, font="arial 15 bold", width=10, command=update_data).place(x=250, y=10)
Button(frame4, text="CLEAR", fg="black", bg="white", bd=3, font="arial 15 bold", width=10, command=clear_fields).place(x=400, y=10)
Button(frame4, text="DELETE", fg="black", bg="white", bd=3, font="arial 15 bold", width=10, command=delete_data).place(x=550, y=10)
Button(frame4, text="EXIT", fg="white", bg="red", bd=3, font="arial 15 bold", width=10, command=exit_app).place(x=950, y=10)

# ---------------------------- INITIAL SETUP ----------------------------
create_table_if_not_exists()
fetch_data()

# ---------------------------- MAIN LOOP ----------------------------
app.mainloop()
import json
from fpdf import FPDF

studentData = list()
validStudentData = list()
canSave = True


# ======================
# CREATE (ADD STUDENT)
# ======================
def addStudent():
    global canSave
    canSave = False
    student = dict()
    grades = list()

    name = input("Student Full Name: ")

    for i in range(5):
        grade = int(input(f"{name} Subject {i+1} Grades: "))
        grades.append(grade)

    student["name"] = name
    student["grades"] = grades

    studentData.append(student)


# ======================
# READ (SHOW STUDENT)
# ======================
def showStudents(data):
    print("\n===== ALL STUDENT LIST =====")
    for index, student in enumerate(data):
        print(f"{index+1}. {student['name']} - {student['grades']}")


# ======================
# UPDATE
# ======================
def updateStudent():
    global canSave
    showStudents(studentData)

    index = int(input("Select student index to update: ")) - 1

    if 0 <= index < len(studentData):
        canSave = False
        newName = input("New Name: ")

        newGrades = list()
        for i in range(5):
            grade = int(input(f"Subject {i+1} Grade: "))
            newGrades.append(grade)

        studentData[index]["name"] = newName
        studentData[index]["grades"] = newGrades

        print("Student Updated")
    else:
        print("Invalid Index")


# ======================
# DELETE
# ======================
def deleteStudent():
    showStudents(studentData)

    index = int(input("Select student index to delete: ")) - 1

    if 0 <= index < len(studentData):
        studentData.pop(index)
        print("Student Deleted")
    else:
        print("Invalid Index")


# ======================
# PROCESS DATA
# ======================
def processData(data):
    global canSave
    validStudentData.clear()

    for student in data:

        invalidGrades = list()
        invalidName = False

        # Validate Name
        if any(char.isdigit() for char in student["name"]):
            print(f"Invalid Name: {student['name']}")
            invalidName = True

        # Validate Grades
        for subject, grade in enumerate(student["grades"]):
            if not 0 <= grade <= 100:
                print(
                    f"Invalid Grade ({student['name']} - Subject {subject+1})")
                invalidGrades.append(grade)

        # If Valid
        if not invalidGrades and not invalidName:

            canSave = True

            sumGrade = sum(student["grades"])
            avgGrade = sumGrade / len(student["grades"])
            maxGrade = max(student["grades"])
            minGrade = min(student["grades"])

            validStudentData.append({
                "name": student["name"],
                "grades": student["grades"],
                "sum": sumGrade,
                "avg": avgGrade,
                "max": maxGrade,
                "min": minGrade
            })

        # If Not Valid
        else:
            canSave = False

    print("Data Has Been Processed!")

# ======================
# RANKING
# ======================


def showRankings(data):

    sortedData = sorted(data, key=lambda x: x["avg"], reverse=True)

    print("\n===== STUDENT RANKING =====")

    for index, student in enumerate(sortedData):
        print(
            f"Rank {index+1} | "
            f"{student['name']} | "
            f"AVG: {student['avg']:.2f} | "
            f"MAX: {student['max']} | "
            f"MIN: {student['min']}"
        )


# ======================
# SAVE FILE
# ======================
def saveFile():
    if canSave == True:
        with open("studentData.json", "w") as file:
            json.dump(studentData, file, indent=4)

        print("Data Saved")

    else:
        print("Process Data Before Saving")


# ======================
# LOAD FILE
# ======================
def loadFile():
    global studentData

    try:
        with open("studentData.json", "r") as file:
            studentData = json.load(file)

        print("Data Loaded")

    except:
        print("File Not Found")

# ======================
# EXPORT FILE
# ======================


def exportPDF(data):
    if canSave == True:
        if not data:
            print("No processed data. Run Process Data first.")
            return

        # Sort by average
        sortedData = sorted(data, key=lambda x: x["avg"], reverse=True)

        pdf = FPDF()
        pdf.add_page()

        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Student Report", ln=True, align="C")
        pdf.ln(5)

        # Header
        pdf.set_font("Arial", "B", 10)

        pdf.cell(15, 10, "Rank", 1)
        pdf.cell(35, 10, "Name", 1)

        for i in range(5):
            pdf.cell(18, 10, f"Subject {i+1}", 1)

        pdf.cell(20, 10, "Avg", 1)
        pdf.cell(15, 10, "Max", 1)
        pdf.cell(15, 10, "Min", 1)

        pdf.ln()

        # Data
        pdf.set_font("Arial", "", 10)

        for i, student in enumerate(sortedData):
            pdf.cell(15, 10, str(i+1), 1)
            pdf.cell(35, 10, student["name"], 1)

            for grade in student["grades"]:
                pdf.cell(18, 10, str(grade), 1)

            pdf.cell(20, 10, f"{student['avg']:.2f}", 1)
            pdf.cell(15, 10, str(student["max"]), 1)
            pdf.cell(15, 10, str(student["min"]), 1)

            pdf.ln()

            # New page if needed
            if pdf.get_y() > 270:
                pdf.add_page()

        pdf.output("student_report.pdf")
        print("PDF exported!")

    else:
        print("Process Data Before Exporting")


# ======================
# MENU
# ======================
def menu():

    while True:

        print("""
===== STUDENT REPORT SYSTEM =====
1. Add Student
2. Show Students
3. Update Student
4. Delete Student
5. Process Data
6. Show Ranking
7. Save File
8. Load File
9. Export PDF
10. Exit
""")

        choice = input("Choose: ")

        if choice == "1":
            addStudent()

        elif choice == "2":
            showStudents(studentData)

        elif choice == "3":
            updateStudent()

        elif choice == "4":
            deleteStudent()

        elif choice == "5":
            processData(studentData)

        elif choice == "6":
            showRankings(validStudentData)

        elif choice == "7":
            saveFile()

        elif choice == "8":
            loadFile()

        elif choice == "9":
            exportPDF(validStudentData)

        elif choice == "10":
            break

        else:
            print("Invalid Option")


menu()

# INTINYA PERTAMA addStudent()
# JADI KITA TAMBAHIN DULU SEMUA STUDENTNYA
# KEMUDIAN SETELAH SEMUA STUDENT SUDAH DIINPUT
# AKAN DIVALIDASI DULU NAMA DAN NILAINYA
# APAKAH NAMANYA VALID? (ADA ANGKA ATAU KARAKTER ANEH?)
# APAKAH NILAINYA DALAM RANGE 0-100
# JIKA IYA, TAMBAHKAN KE DALAM LIST AKHIR
# JIKA TIDAK, ABAIKAN DAN PRINT ADA ERROR
# SETELAH ITU SEMUA, DI DALAM LIST AKHIR AKAN DISORTIR LANGSUNG SESUAI DENGAN RANKING

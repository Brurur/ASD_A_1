import copy
import json

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None


# ======================
# COLLECTION DATA TYPES
# ======================
# list  : studentData, validStudentData, grades
# dict  : student object
# tuple : SUBJECTS
# set   : duplicate-name validation
SUBJECTS = tuple(f"Subject {index}" for index in range(1, 6))
DATA_FILE = "studentData.json"
REPORT_FILE = "student_report.pdf"


# ======================
# LINKED LIST
# ======================
class StudentNode:
    def __init__(self, data):
        self.data = data
        self.next = None


class StudentLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def append(self, data):
        node = StudentNode(data)

        if self.head is None:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node

        self.length += 1

    def __iter__(self):
        current = self.head

        while current is not None:
            yield current.data
            current = current.next

    @classmethod
    def fromList(cls, data):
        linkedList = cls()

        for item in data:
            linkedList.append(item)

        return linkedList


# ======================
# STACK
# ======================
class Stack:
    def __init__(self):
        self.items = list()

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.isEmpty():
            return None

        return self.items.pop()

    def isEmpty(self):
        return len(self.items) == 0


# ======================
# QUEUE
# ======================
class Queue:
    def __init__(self):
        self.items = list()
        self.frontIndex = 0

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if self.isEmpty():
            return None

        item = self.items[self.frontIndex]
        self.frontIndex += 1

        # Compact the queue occasionally so memory stays tidy for large data.
        if self.frontIndex > 50 and self.frontIndex * 2 >= len(self.items):
            self.items = self.items[self.frontIndex:]
            self.frontIndex = 0

        return item

    def isEmpty(self):
        return self.frontIndex >= len(self.items)


studentData = list()
validStudentData = list()
undoStack = Stack()
canSave = True


# ======================
# INPUT HELPERS
# ======================
def inputGrade(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Grade must be a number.")


def inputStudentIndex(prompt):
    try:
        return int(input(prompt)) - 1
    except ValueError:
        return -1


def inputGrades(name):
    grades = list()

    for subject in SUBJECTS:
        grade = inputGrade(f"{name} {subject} Grade: ")
        grades.append(grade)

    return grades


def markDataChanged():
    global canSave
    canSave = False
    validStudentData.clear()


def recordUndo(action):
    undoStack.push({
        "action": action,
        "studentData": copy.deepcopy(studentData),
        "validStudentData": copy.deepcopy(validStudentData),
        "canSave": canSave
    })


def normalizeName(name):
    return " ".join(str(name).strip().lower().split())


def isValidName(name):
    cleanName = str(name).strip()

    if cleanName == "":
        return False

    return all(char.isalpha() or char in " .'-" for char in cleanName)


# ======================
# RECURSIVE HELPERS
# ======================
def recursiveSum(values, index=0):
    if index == len(values):
        return 0

    return values[index] + recursiveSum(values, index + 1)


def recursiveMinMax(values, index=0, currentMin=None, currentMax=None):
    if index == len(values):
        return currentMin, currentMax

    value = values[index]

    if currentMin is None or value < currentMin:
        currentMin = value

    if currentMax is None or value > currentMax:
        currentMax = value

    return recursiveMinMax(values, index + 1, currentMin, currentMax)


def recursiveInvalidGrades(grades, index=0, invalidGrades=None):
    if invalidGrades is None:
        invalidGrades = list()

    if index == len(grades):
        return invalidGrades

    grade = grades[index]

    if not isinstance(grade, int) or not 0 <= grade <= 100:
        invalidGrades.append((index, grade))

    return recursiveInvalidGrades(grades, index + 1, invalidGrades)


# ======================
# SORTING & SEARCHING
# ======================
def sortValue(item, key):
    value = key(item)

    if isinstance(value, str):
        return value.lower()

    return value


def merge(left, right, key, reverse):
    result = list()
    leftIndex = 0
    rightIndex = 0

    while leftIndex < len(left) and rightIndex < len(right):
        leftValue = sortValue(left[leftIndex], key)
        rightValue = sortValue(right[rightIndex], key)

        if reverse:
            shouldTakeLeft = leftValue >= rightValue
        else:
            shouldTakeLeft = leftValue <= rightValue

        if shouldTakeLeft:
            result.append(left[leftIndex])
            leftIndex += 1
        else:
            result.append(right[rightIndex])
            rightIndex += 1

    result.extend(left[leftIndex:])
    result.extend(right[rightIndex:])
    return result


def mergeSort(data, key, reverse=False):
    if len(data) <= 1:
        return list(data)

    middle = len(data) // 2
    left = mergeSort(data[:middle], key, reverse)
    right = mergeSort(data[middle:], key, reverse)
    return merge(left, right, key, reverse)


def recursiveBinarySearch(data, targetName, left=0, right=None):
    if right is None:
        right = len(data) - 1

    if left > right:
        return None

    middle = (left + right) // 2
    middleName = normalizeName(data[middle]["name"])

    if middleName == targetName:
        return data[middle]

    if targetName < middleName:
        return recursiveBinarySearch(data, targetName, left, middle - 1)

    return recursiveBinarySearch(data, targetName, middle + 1, right)


# ======================
# CREATE (ADD STUDENT)
# ======================
def addStudent():
    student = dict()

    name = input("Student Full Name: ").strip()
    grades = inputGrades(name)

    recordUndo("Add Student")
    markDataChanged()

    student["name"] = name
    student["grades"] = grades

    studentData.append(student)
    print("Student Added")


# ======================
# READ (SHOW STUDENT)
# ======================
def showStudents(data):
    if not data:
        print("\nNo student data.")
        return

    linkedList = StudentLinkedList.fromList(data)

    print("\n===== ALL STUDENT LIST =====")

    for index, student in enumerate(linkedList, start=1):
        if "avg" in student:
            print(
                f"{index}. {student['name']} - {student['grades']} | "
                f"AVG: {student['avg']:.2f}"
            )
        else:
            print(f"{index}. {student['name']} - {student['grades']}")


# ======================
# UPDATE
# ======================
def updateStudent():
    showStudents(studentData)

    if not studentData:
        return

    index = inputStudentIndex("Select student index to update: ")

    if 0 <= index < len(studentData):
        newName = input("New Name: ").strip()
        newGrades = inputGrades(newName)

        recordUndo("Update Student")
        markDataChanged()

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

    if not studentData:
        return

    index = inputStudentIndex("Select student index to delete: ")

    if 0 <= index < len(studentData):
        recordUndo("Delete Student")
        markDataChanged()

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

    processQueue = Queue()
    linkedList = StudentLinkedList.fromList(data)
    seenNames = set()
    hasInvalidData = False

    for student in linkedList:
        processQueue.enqueue(student)

    while not processQueue.isEmpty():
        student = processQueue.dequeue()
        name = str(student.get("name", "")).strip()
        grades = student.get("grades", list())
        normalizedName = normalizeName(name)
        invalidStudent = False

        if not isValidName(name):
            print(f"Invalid Name: {name}")
            invalidStudent = True

        if normalizedName in seenNames:
            print(f"Duplicate Name: {name}")
            invalidStudent = True
        else:
            seenNames.add(normalizedName)

        if len(grades) != len(SUBJECTS):
            print(f"Invalid Grade Count ({name})")
            invalidStudent = True

        invalidGrades = recursiveInvalidGrades(grades)

        for subjectIndex, grade in invalidGrades:
            if subjectIndex < len(SUBJECTS):
                subjectName = SUBJECTS[subjectIndex]
            else:
                subjectName = f"Subject {subjectIndex + 1}"

            print(f"Invalid Grade ({name} - {subjectName}): {grade}")
            invalidStudent = True

        if invalidStudent:
            hasInvalidData = True
            continue

        sumGrade = recursiveSum(grades)
        minGrade, maxGrade = recursiveMinMax(grades)
        avgGrade = sumGrade / len(grades)

        validStudentData.append({
            "name": name,
            "grades": grades,
            "sum": sumGrade,
            "avg": avgGrade,
            "max": maxGrade,
            "min": minGrade
        })

    canSave = not hasInvalidData
    print("Data Has Been Processed!")


# ======================
# RANKING
# ======================
def showRankings(data):
    if canSave:
        if not data:
            print("No processed data. Run Process Data first.")
            return

        sortedData = mergeSort(data, key=lambda student: student["avg"], reverse=True)

        print("\n===== STUDENT RANKING =====")

        for index, student in enumerate(sortedData, start=1):
            print(
                f"Rank {index} | "
                f"{student['name']} | "
                f"AVG: {student['avg']:.2f} | "
                f"MAX: {student['max']} | "
                f"MIN: {student['min']}"
            )
    else:
        print("Process Data Before Show Rankings")


# ======================
# SEARCHING
# ======================
def searchStudent():
    if not studentData:
        print("No student data.")
        return

    targetName = normalizeName(input("Search student full name: "))
    sortedData = mergeSort(studentData, key=lambda student: student["name"])
    student = recursiveBinarySearch(sortedData, targetName)

    if student is None:
        print("Student Not Found")
        return

    print("\n===== SEARCH RESULT =====")
    print(f"Name   : {student['name']}")
    print(f"Grades : {student['grades']}")

    for processedStudent in validStudentData:
        if normalizeName(processedStudent["name"]) == targetName:
            print(f"AVG    : {processedStudent['avg']:.2f}")
            print(f"MAX    : {processedStudent['max']}")
            print(f"MIN    : {processedStudent['min']}")
            break


# ======================
# UNDO WITH STACK
# ======================
def undoLastAction():
    global studentData, validStudentData, canSave
    previousState = undoStack.pop()

    if previousState is None:
        print("No action to undo.")
        return

    studentData = previousState["studentData"]
    validStudentData = previousState["validStudentData"]
    canSave = previousState["canSave"]

    print(f"Undo Success: {previousState['action']}")


# ======================
# SAVE FILE
# ======================
def saveFile():
    if canSave:
        with open(DATA_FILE, "w") as file:
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
        with open(DATA_FILE, "r") as file:
            loadedData = json.load(file)

        recordUndo("Load File")
        studentData = loadedData
        markDataChanged()

        print("Data Loaded")
    except FileNotFoundError:
        print("File Not Found")
    except json.JSONDecodeError:
        print("File Is Not Valid JSON")


# ======================
# EXPORT FILE
# ======================
def exportPDF(data):
    if not canSave:
        print("Process Data Before Exporting")
        return

    if not data:
        print("No processed data. Run Process Data first.")
        return

    if FPDF is None:
        print("FPDF package is not installed.")
        return

    sortedData = mergeSort(data, key=lambda student: student["avg"], reverse=True)

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Student Report", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "B", 10)

    pdf.cell(15, 10, "Rank", 1)
    pdf.cell(35, 10, "Name", 1)

    for subject in SUBJECTS:
        pdf.cell(18, 10, subject, 1)

    pdf.cell(20, 10, "Avg", 1)
    pdf.cell(15, 10, "Max", 1)
    pdf.cell(15, 10, "Min", 1)

    pdf.ln()
    pdf.set_font("Arial", "", 10)

    for index, student in enumerate(sortedData, start=1):
        pdf.cell(15, 10, str(index), 1)
        pdf.cell(35, 10, student["name"][:16], 1)

        for grade in student["grades"]:
            pdf.cell(18, 10, str(grade), 1)

        pdf.cell(20, 10, f"{student['avg']:.2f}", 1)
        pdf.cell(15, 10, str(student["max"]), 1)
        pdf.cell(15, 10, str(student["min"]), 1)
        pdf.ln()

        if pdf.get_y() > 270:
            pdf.add_page()

    pdf.output(REPORT_FILE)
    print("PDF exported!")


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
10. Search Student
11. Undo Last Change
12. Exit
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
            searchStudent()
        elif choice == "11":
            undoLastAction()
        elif choice == "12":
            break
        else:
            print("Invalid Option")


if __name__ == "__main__":
    menu()

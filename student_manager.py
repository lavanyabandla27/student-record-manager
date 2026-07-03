import os
import re
import csv
import sys

# File name where student details will be saved
DATA_FILE = "students.txt"

# Regex Patterns for Validation
REGEX_ID = r"^STU\d{3}$"                                     # Format: STU followed by 3 digits (e.g., STU001)
REGEX_NAME = r"^[A-Za-z\s]{2,50}$"                            # 2-50 alphabetic characters and spaces
REGEX_EMAIL = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"   # Standard email format
REGEX_PHONE = r"^\d{10}$"                                    # Exactly 10 digits
REGEX_CGPA = r"^(?:[0-9](?:\.\d{1,2})?|10(?:\.0{1,2})?)$"      # Float between 0.0 and 10.0 (up to 2 decimal places)

# Plain text styling (ANSI colors disabled to prevent raw character codes from cluttering Windows console)
COLOR_HEADER = ""
COLOR_BLUE = ""
COLOR_GREEN = ""
COLOR_WARNING = ""
COLOR_FAIL = ""
COLOR_END = ""
COLOR_BOLD = ""

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def initialize_file():
    """
    Automatically creates the students.txt file with headers if it does not exist.
    Handles potential system permissions exceptions.
    """
    try:
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Student ID", "Name", "Email", "Phone", "CGPA"])
            print(f"Success: '{DATA_FILE}' has been created automatically.\n")
    except PermissionError:
        print(f"Error: Permission denied when trying to create '{DATA_FILE}'. Please check directory permissions.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error initializing file: {e}")
        sys.exit(1)

def load_students():
    """
    Reads the students.txt file and returns a list of dictionaries.
    Includes exception handling for file reading and parsing.
    Supports legacy 'GPA' header for backward compatibility.
    """
    students = []
    if not os.path.exists(DATA_FILE):
        return students

    try:
        with open(DATA_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if not reader.fieldnames:
                raise ValueError("Data file is empty or invalid.")
            
            # Support both CGPA (new) and GPA (legacy) headers to prevent crashing on existing files
            has_cgpa = "CGPA" in reader.fieldnames
            has_gpa = "GPA" in reader.fieldnames
            
            if not (has_cgpa or has_gpa) or "Student ID" not in reader.fieldnames or "Name" not in reader.fieldnames:
                raise ValueError("Data file has invalid column headers or structure.")
            
            gpa_key = "CGPA" if has_cgpa else "GPA"
            
            for row in reader:
                students.append({
                    "id": row["Student ID"].strip(),
                    "name": row["Name"].strip(),
                    "email": row["Email"].strip(),
                    "phone": row["Phone"].strip(),
                    "cgpa": row[gpa_key].strip()
                })
    except FileNotFoundError:
        print(f"Warning: '{DATA_FILE}' not found. A new one will be created.")
    except PermissionError:
        print(f"Error: Permission denied while reading '{DATA_FILE}'. Is it open in another program?")
    except ValueError as ve:
        print(f"Data Error: {ve}. The file may be corrupted.")
    except Exception as e:
        print(f"An unexpected error occurred while reading the data: {e}")
    
    return students

def save_all_students(students):
    """
    Overwrites the students.txt file with the current list of student dictionaries.
    Includes exception handling for writing.
    """
    try:
        with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Student ID", "Name", "Email", "Phone", "CGPA"])
            for student in students:
                writer.writerow([
                    student["id"],
                    student["name"],
                    student["email"],
                    student["phone"],
                    student["cgpa"]
                ])
        return True
    except PermissionError:
        print(f"\nError: Permission denied while writing to '{DATA_FILE}'. Please close any programs using it.")
        return False
    except Exception as e:
        print(f"\nAn unexpected error occurred while writing data: {e}")
        return False

def get_validated_input(prompt, pattern, error_message, allow_empty=False):
    """
    Helper function to prompt user for input and validate it using a regular expression.
    Handles KeyboardInterrupt to allow graceful exit.
    """
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:
                if allow_empty:
                    return ""
                print("Input cannot be empty. Please try again.")
                continue
            
            if re.match(pattern, user_input):
                return user_input
            else:
                print(f"Validation Error: {error_message}")
        except KeyboardInterrupt:
            print("\nInput cancelled by user.")
            raise KeyboardInterrupt

def check_id_exists(student_id, students):
    """Checks if a student ID already exists in the loaded student list."""
    for student in students:
        if student["id"].upper() == student_id.upper():
            return True
    return False

def add_student_screen():
    """Prompts the user for details, validates them with regex, and saves the student."""
    clear_screen()
    print("=========================================")
    print("           ADD NEW STUDENT               ")
    print("=========================================")
    
    students = load_students()
    
    try:
        # 1. Validate and get Student ID
        while True:
            student_id = get_validated_input(
                "Enter Student ID (e.g., STU001): ",
                REGEX_ID,
                "ID must start with 'STU' followed by exactly 3 digits (e.g., STU123)."
            ).upper()
            
            if check_id_exists(student_id, students):
                print(f"Error: A student with ID '{student_id}' already exists. Please use a unique ID.")
            else:
                break
        
        # 2. Validate and get Name
        name = get_validated_input(
            "Enter Full Name: ",
            REGEX_NAME,
            "Name must contain only alphabets and spaces (2-50 characters)."
        ).title()
        
        # 3. Validate and get Email
        email = get_validated_input(
            "Enter Email Address: ",
            REGEX_EMAIL,
            "Invalid email format (e.g., name@domain.com)."
        ).lower()
        
        # 4. Validate and get Phone Number
        phone = get_validated_input(
            "Enter 10-Digit Phone Number (e.g., 9876543210): ",
            REGEX_PHONE,
            "Phone number must be exactly 10 digits."
        )
        
        # 5. Validate and get CGPA (0.0 - 10.0)
        cgpa = get_validated_input(
            "Enter CGPA (0.0 - 10.0): ",
            REGEX_CGPA,
            "CGPA must be a number between 0.0 and 10.0."
        )
        
        # Format CGPA to 2 decimal places for consistency
        cgpa = f"{float(cgpa):.2f}"

        # Add to local list and save
        new_student = {
            "id": student_id,
            "name": name,
            "email": email,
            "phone": phone,
            "cgpa": cgpa
        }
        students.append(new_student)
        
        if save_all_students(students):
            print(f"\nSuccess: Student '{name}' ({student_id}) added and saved successfully!")
        else:
            print(f"\nFailed to save the new student due to a write error.")

    except KeyboardInterrupt:
        print("\nReturning to Main Menu...")
    
    input("\nPress Enter to continue...")

def delete_student_screen():
    """Prompts the user for a student ID, searches for it, and deletes the student if found."""
    clear_screen()
    print("=========================================")
    print("           DELETE A STUDENT              ")
    print("=========================================")
    
    students = load_students()
    
    if not students:
        print("No student records available to delete.")
        input("\nPress Enter to continue...")
        return

    try:
        student_id = get_validated_input(
            "Enter Student ID to delete (e.g., STU001): ",
            REGEX_ID,
            "ID must start with 'STU' followed by exactly 3 digits (e.g., STU123)."
        ).upper()
        
        # Find the student
        target_student = None
        for student in students:
            if student["id"] == student_id:
                target_student = student
                break
        
        if target_student:
            print("\nAre you sure you want to delete this student?")
            print(f"  ID:    {target_student['id']}")
            print(f"  Name:  {target_student['name']}")
            print(f"  CGPA:  {target_student['cgpa']}")
            
            confirm = input("\nType 'YES' to confirm deletion: ").strip().upper()
            if confirm == 'YES':
                students.remove(target_student)
                if save_all_students(students):
                    print(f"\nSuccess: Student '{target_student['name']}' has been deleted.")
                else:
                    print(f"\nFailed to save changes after deletion.")
            else:
                print("\nDeletion cancelled.")
        else:
            print(f"\nError: Student with ID '{student_id}' not found.")

    except KeyboardInterrupt:
        print("\nReturning to Main Menu...")
        
    input("\nPress Enter to continue...")

def display_report_screen():
    """Reads student data and displays a formatted ASCII table report."""
    clear_screen()
    print("=========================================================================================")
    print("                                STUDENT REPORT SUMMARY                                   ")
    print("=========================================================================================")
    
    students = load_students()
    
    if not students:
        print("\n                  No student records found. The database is empty.                       ")
        print("=========================================================================================")
        input("\nPress Enter to continue...")
        return

    # Print table header
    # Column widths: ID (8), Name (22), Email (28), Phone (14), CGPA (6)
    header_fmt = "| {:<8} | {:<22} | {:<28} | {:<14} | {:<6} |"
    row_divider = "+" + "-"*10 + "+" + "-"*24 + "+" + "-"*30 + "+" + "-"*16 + "+" + "-"*8 + "+"
    
    print(row_divider)
    print(header_fmt.format("ID", "Name", "Email", "Phone", "CGPA"))
    print(row_divider)
    
    total_cgpa = 0.0
    for student in students:
        # Truncate long fields if they exceed column width to prevent layout breaking
        name = student["name"][:22]
        email = student["email"][:28]
        phone = student["phone"][:14]
        cgpa_val = student["cgpa"]
        
        # Accumulate CGPA for class average
        try:
            total_cgpa += float(cgpa_val)
        except ValueError:
            pass

        print(header_fmt.format(student["id"], name, email, phone, cgpa_val))
    
    print(row_divider)
    
    # Calculate and display metrics
    class_average = total_cgpa / len(students)
    print(f"\nTotal Students Registered: {len(students)}")
    print(f"Class CGPA Average:        {class_average:.2f} / 10.00")
    print("=========================================================================================")
    input("\nPress Enter to return to Main Menu...")

def search_student_screen():
    """Prompts the user for a search query and displays matching students."""
    clear_screen()
    print("=========================================")
    print("           SEARCH STUDENT                ")
    print("=========================================")
    
    students = load_students()
    
    if not students:
        print("No student records available to search.")
        input("\nPress Enter to continue...")
        return

    try:
        query = input("Enter Student ID or Name to search: ").strip()
        if not query:
            print("\nSearch query cannot be empty.")
            input("\nPress Enter to continue...")
            return

        # Case-insensitive partial match search
        matches = []
        for student in students:
            if query.lower() in student["id"].lower() or query.lower() in student["name"].lower():
                matches.append(student)

        if not matches:
            print(f"\nNo student records found matching '{query}'.")
        else:
            print(f"\nFound {len(matches)} matching record(s):")
            # Print table header
            header_fmt = "| {:<8} | {:<22} | {:<28} | {:<14} | {:<6} |"
            row_divider = "+" + "-"*10 + "+" + "-"*24 + "+" + "-"*30 + "+" + "-"*16 + "+" + "-"*8 + "+"
            
            print(row_divider)
            print(header_fmt.format("ID", "Name", "Email", "Phone", "CGPA"))
            print(row_divider)
            
            for student in matches:
                name = student["name"][:22]
                email = student["email"][:28]
                phone = student["phone"][:14]
                cgpa_val = student["cgpa"]
                print(header_fmt.format(student["id"], name, email, phone, cgpa_val))
            
            print(row_divider)

    except KeyboardInterrupt:
        print("\nReturning to Main Menu...")

    input("\nPress Enter to continue...")

def update_student_screen():
    """Prompts the user for a student ID, shows current details, and allows updating fields."""
    clear_screen()
    print("=========================================")
    print("           UPDATE A STUDENT              ")
    print("=========================================")
    
    students = load_students()
    
    if not students:
        print("No student records available to update.")
        input("\nPress Enter to continue...")
        return

    try:
        student_id = get_validated_input(
            "Enter Student ID to update (e.g., STU001): ",
            REGEX_ID,
            "ID must start with 'STU' followed by exactly 3 digits (e.g., STU123)."
        ).upper()
        
        # Find the student
        target_student = None
        for student in students:
            if student["id"] == student_id:
                target_student = student
                break
        
        if not target_student:
            print(f"\nError: Student with ID '{student_id}' not found.")
            input("\nPress Enter to continue...")
            return

        print(f"\nStudent found. Current details:")
        print(f"  ID:    {target_student['id']}")
        print(f"  Name:  {target_student['name']}")
        print(f"  Email: {target_student['email']}")
        print(f"  Phone: {target_student['phone']}")
        print(f"  CGPA:  {target_student['cgpa']}")
        print("\nPress Enter to keep current value, or enter new details:")

        # 1. Update Name
        name_input = get_validated_input(
            f"Enter Name [{target_student['name']}]: ",
            REGEX_NAME,
            "Name must contain only alphabets and spaces (2-50 characters).",
            allow_empty=True
        )
        name = name_input.title() if name_input else target_student['name']

        # 2. Update Email
        email_input = get_validated_input(
            f"Enter Email [{target_student['email']}]: ",
            REGEX_EMAIL,
            "Invalid email format (e.g., name@domain.com).",
            allow_empty=True
        )
        email = email_input.lower() if email_input else target_student['email']

        # 3. Update Phone
        phone_input = get_validated_input(
            f"Enter Phone [{target_student['phone']}]: ",
            REGEX_PHONE,
            "Phone number must be exactly 10 digits.",
            allow_empty=True
        )
        phone = phone_input if phone_input else target_student['phone']

        # 4. Update CGPA
        cgpa_input = get_validated_input(
            f"Enter CGPA [{target_student['cgpa']}]: ",
            REGEX_CGPA,
            "CGPA must be a number between 0.0 and 10.0.",
            allow_empty=True
        )
        cgpa = f"{float(cgpa_input):.2f}" if cgpa_input else target_student['cgpa']

        # Check if anything changed
        if (name == target_student['name'] and 
            email == target_student['email'] and 
            phone == target_student['phone'] and 
            cgpa == target_student['cgpa']):
            print("\nNo changes were made.")
        else:
            # Apply changes
            target_student['name'] = name
            target_student['email'] = email
            target_student['phone'] = phone
            target_student['cgpa'] = cgpa

            if save_all_students(students):
                print(f"\nSuccess: Student '{name}' ({student_id}) details updated successfully!")
            else:
                print(f"\nFailed to save updated details due to a write error.")

    except KeyboardInterrupt:
        print("\nReturning to Main Menu...")

    input("\nPress Enter to continue...")

def main_menu():
    """Main application loop."""
    initialize_file()
    
    while True:
        clear_screen()
        print("=========================================")
        print("       STUDENT REPORT MANAGER            ")
        print("=========================================")
        print("1. Add New Student")
        print("2. Delete Student")
        print("3. Display Student Report")
        print("4. Search Student")
        print("5. Update Student")
        print("6. Exit")
        print("-----------------------------------------")
        print(f"Database Source: {DATA_FILE}")
        print("=========================================")
        
        try:
            choice = input("Select an option (1-6): ").strip()
            
            if choice == '1':
                add_student_screen()
            elif choice == '2':
                delete_student_screen()
            elif choice == '3':
                display_report_screen()
            elif choice == '4':
                search_student_screen()
            elif choice == '5':
                update_student_screen()
            elif choice == '6':
                clear_screen()
                print("\nThank you for using Student Report Manager. Goodbye!\n")
                break
            else:
                print("Invalid choice. Please select a number from 1 to 6.")
                input("Press Enter to try again...")
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            clear_screen()
            print("\nSession ended gracefully. Goodbye!\n")
            break
        except Exception as e:
            print(f"\nAn unexpected runtime error occurred: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main_menu()

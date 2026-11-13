
import csv
import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from scheduler import (
    greedy_schedule,
    backtracking_schedule,
    validate_schedule,
    count_slots,
    build_conflict_graph,
    get_subject_students,
)


class ExamTimetableApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Automated Exam Timetable Generator")
        self.root.geometry("1250x900")
        self.root.minsize(1050, 750)

        self.enrollments = {}
        self.rooms = {}
        self.last_schedule = None
        self.last_algorithm = ""

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(
            self.root,
            text="Automated Exam Timetable Generator",
            font=("Arial", 20, "bold")
        ).pack(pady=10)

        ttk.Label(
            self.root,
            text="Graph Coloring | Greedy | Backtracking | CSV Dataset"
        ).pack(pady=3)

        settings = ttk.LabelFrame(
            self.root, text="Scheduling Settings", padding=10
        )
        settings.pack(fill="x", padx=12, pady=6)

        ttk.Label(settings, text="Available Time Slots:").grid(
            row=0, column=0, padx=5, pady=5
        )

        self.slots_var = tk.StringVar(value="16")
        ttk.Entry(
            settings, textvariable=self.slots_var, width=10
        ).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(settings, text="Minimum Empty Slots:").grid(
            row=0, column=2, padx=5, pady=5
        )

        self.gap_var = tk.StringVar(value="0")
        ttk.Entry(
            settings, textvariable=self.gap_var, width=10
        ).grid(row=0, column=3, padx=5, pady=5)

        # Student and room panels
        data_frame = ttk.Frame(self.root)
        data_frame.pack(fill="both", expand=True, padx=12, pady=6)

        student_frame = ttk.LabelFrame(
            data_frame, text="Student Enrollments", padding=10
        )
        student_frame.pack(
            side="left", fill="both", expand=True, padx=(0, 6)
        )

        ttk.Label(
            student_frame,
            text="Student ID, followed by comma-separated subjects"
        ).pack(anchor="w")

        self.student_entry = ttk.Entry(student_frame)
        self.student_entry.pack(fill="x", pady=5)
        self.student_entry.insert(0, "S201,DAA,Python")

        ttk.Button(
            student_frame,
            text="Add Student",
            command=self.add_student
        ).pack(anchor="w", pady=4)

        self.student_list = tk.Listbox(student_frame, height=8)
        self.student_list.pack(fill="both", expand=True, pady=5)

        room_frame = ttk.LabelFrame(
            data_frame, text="Examination Rooms", padding=10
        )
        room_frame.pack(
            side="left", fill="both", expand=True, padx=(6, 0)
        )

        ttk.Label(
            room_frame,
            text="Room name and capacity (example: RoomF,100)"
        ).pack(anchor="w")

        self.room_entry = ttk.Entry(room_frame)
        self.room_entry.pack(fill="x", pady=5)
        self.room_entry.insert(0, "RoomF,100")

        ttk.Button(
            room_frame,
            text="Add Room",
            command=self.add_room
        ).pack(anchor="w", pady=4)

        self.room_list = tk.Listbox(room_frame, height=8)
        self.room_list.pack(fill="both", expand=True, pady=5)

        # Dataset management
        data_buttons = ttk.LabelFrame(
            self.root, text="Dataset Management", padding=8
        )
        data_buttons.pack(fill="x", padx=12, pady=5)

        ttk.Button(
            data_buttons,
            text="Load Sample Data",
            command=self.load_sample_data
        ).pack(side="left", padx=5, pady=5)

        ttk.Button(
            data_buttons,
            text="Import CSV Dataset",
            command=self.import_csv_dataset
        ).pack(side="left", padx=5, pady=5)

        # Scheduling tools
        algorithm_frame = ttk.LabelFrame(
            self.root, text="Scheduling Algorithms and Tools", padding=8
        )
        algorithm_frame.pack(fill="x", padx=12, pady=5)

        ttk.Button(
            algorithm_frame,
            text="Greedy Schedule",
            command=lambda: self.generate("Greedy")
        ).pack(side="left", padx=4, pady=5)

        ttk.Button(
            algorithm_frame,
            text="Backtracking Schedule",
            command=lambda: self.generate("Backtracking")
        ).pack(side="left", padx=4, pady=5)

        ttk.Button(
            algorithm_frame,
            text="Compare Algorithms",
            command=self.compare_algorithms
        ).pack(side="left", padx=4, pady=5)

        ttk.Button(
            algorithm_frame,
            text="View Conflict Graph",
            command=self.show_conflict_graph
        ).pack(side="left", padx=4, pady=5)

        ttk.Button(
            algorithm_frame,
            text="Export Timetable to CSV",
            command=self.export_timetable
        ).pack(side="left", padx=4, pady=5)

        # Results table
        result_frame = ttk.LabelFrame(
            self.root, text="Generated Examination Timetable", padding=8
        )
        result_frame.pack(
            fill="both", expand=True, padx=12, pady=6
        )

        columns = ("subject", "students", "slot", "room")

        self.table = ttk.Treeview(
            result_frame,
            columns=columns,
            show="headings",
            height=8
        )

        self.table.heading("subject", text="Subject")
        self.table.heading("students", text="Enrolled Students")
        self.table.heading("slot", text="Time Slot")
        self.table.heading("room", text="Room")

        self.table.column("subject", width=230)
        self.table.column("students", width=180)
        self.table.column("slot", width=150)
        self.table.column("room", width=180)

        scrollbar = ttk.Scrollbar(
            result_frame,
            orient="vertical",
            command=self.table.yview
        )

        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.status_var = tk.StringVar(
            value="Import your CSV datasets or load sample data."
        )

        ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w"
        ).pack(fill="x", side="bottom")

    # Add a student manually
    def add_student(self):
        parts = [
            p.strip() for p in self.student_entry.get().split(",")
        ]

        if len(parts) < 2 or any(not p for p in parts):
            messagebox.showerror(
                "Invalid Input",
                "Enter a student ID and subjects separated by commas."
            )
            return

        student_id = parts[0]
        subjects = list(dict.fromkeys(parts[1:]))

        if student_id in self.enrollments:
            messagebox.showerror(
                "Duplicate Student", "This student ID already exists."
            )
            return

        self.enrollments[student_id] = subjects
        self.student_entry.delete(0, tk.END)

        self.refresh_data_lists()
        self.invalidate_schedule()
        self.status_var.set(f"Added student {student_id}.")

    # Add a room manually
    def add_room(self):
        parts = [
            p.strip() for p in self.room_entry.get().split(",")
        ]

        if len(parts) != 2 or not parts[0]:
            messagebox.showerror(
                "Invalid Room",
                "Enter a room name and capacity, for example RoomF,100."
            )
            return

        name = parts[0]

        try:
            capacity = int(parts[1])
            if capacity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Capacity",
                "Room capacity must be a positive whole number."
            )
            return

        if name in self.rooms:
            messagebox.showerror(
                "Duplicate Room", "This room already exists."
            )
            return

        self.rooms[name] = capacity
        self.room_entry.delete(0, tk.END)

        self.refresh_data_lists()
        self.invalidate_schedule()
        self.status_var.set(f"Added room {name}.")

    # Load built-in sample data
    def load_sample_data(self):
        self.enrollments = {
            "S101": ["DAA", "Python"],
            "S102": ["Python", "DBMS"],
            "S103": ["DAA", "DBMS"],
            "S104": ["Java", "Python"],
            "S105": ["Java", "DBMS"],
        }

        self.rooms = {
            "RoomA": 30,
            "RoomB": 25,
            "RoomC": 20,
        }

        self.refresh_data_lists()
        self.invalidate_schedule()
        self.status_var.set("Built-in sample data loaded.")

    # Import student and room CSV files
    def import_csv_dataset(self):
        student_file = filedialog.askopenfilename(
            title="Select Student CSV",
            filetypes=[("CSV files", "*.csv")]
        )

        if not student_file:
            return

        room_file = filedialog.askopenfilename(
            title="Select Room CSV",
            filetypes=[("CSV files", "*.csv")]
        )

        if not room_file:
            return

        try:
            new_enrollments = {}
            new_rooms = {}

            with open(
                student_file, "r", encoding="utf-8-sig", newline=""
            ) as file:
                reader = csv.DictReader(file)

                if not {"Student_ID", "Subjects"}.issubset(
                    reader.fieldnames or []
                ):
                    raise ValueError(
                        "Student CSV needs Student_ID and Subjects columns."
                    )

                for row in reader:
                    student_id = (row.get("Student_ID") or "").strip()
                    text_subjects = (row.get("Subjects") or "").strip()

                    subjects = list(dict.fromkeys(
                        s.strip() for s in text_subjects.split(",")
                        if s.strip()
                    ))

                    if not student_id or not subjects:
                        raise ValueError(
                            "Each student must have an ID and subjects."
                        )

                    if student_id in new_enrollments:
                        raise ValueError(
                            f"Duplicate student ID: {student_id}"
                        )

                    new_enrollments[student_id] = subjects

            with open(
                room_file, "r", encoding="utf-8-sig", newline=""
            ) as file:
                reader = csv.DictReader(file)

                if not {"Room", "Capacity"}.issubset(
                    reader.fieldnames or []
                ):
                    raise ValueError(
                        "Room CSV needs Room and Capacity columns."
                    )

                for row in reader:
                    name = (row.get("Room") or "").strip()

                    try:
                        capacity = int(row.get("Capacity", ""))
                    except (TypeError, ValueError):
                        raise ValueError(
                            f"Invalid capacity for room {name}."
                        )

                    if not name or capacity <= 0:
                        raise ValueError(
                            "Room names and capacities must be valid."
                        )

                    if name in new_rooms:
                        raise ValueError(f"Duplicate room: {name}")

                    new_rooms[name] = capacity

            if not new_enrollments or not new_rooms:
                raise ValueError("Both CSV files must contain records.")

            self.enrollments = new_enrollments
            self.rooms = new_rooms

            self.refresh_data_lists()
            self.invalidate_schedule()

            subject_count = len({
                s for subjects in self.enrollments.values()
                for s in subjects
            })

            self.status_var.set(
                f"Imported {len(self.enrollments)} students, "
                f"{subject_count} subjects and {len(self.rooms)} rooms."
            )

            messagebox.showinfo(
                "Import Successful",
                f"Students: {len(self.enrollments)}\n"
                f"Subjects: {subject_count}\n"
                f"Rooms: {len(self.rooms)}"
            )

        except (OSError, ValueError, TypeError, csv.Error) as error:
            messagebox.showerror("CSV Import Error", str(error))

    def refresh_data_lists(self):
        self.student_list.delete(0, tk.END)
        self.room_list.delete(0, tk.END)

        for student, subjects in self.enrollments.items():
            self.student_list.insert(
                tk.END, f"{student}: {', '.join(subjects)}"
            )

        for name, capacity in self.rooms.items():
            self.room_list.insert(
                tk.END, f"{name}: Capacity {capacity}"
            )

    def invalidate_schedule(self):
        self.last_schedule = None
        self.last_algorithm = ""
        self.clear_table()

    def get_settings(self):
        try:
            slots = int(self.slots_var.get())
            gap = int(self.gap_var.get())

            if slots < 1 or gap < 0:
                raise ValueError

            return slots, gap

        except ValueError:
            messagebox.showerror(
                "Invalid Settings",
                "Available slots must be at least 1 and minimum "
                "empty slots must be 0 or greater."
            )
            return None

    def clear_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

    def display_schedule(self, schedule):
        self.clear_table()

        if schedule is None:
            return

        subject_students = get_subject_students(self.enrollments)

        for subject, (slot, room) in sorted(
            schedule.items(),
            key=lambda item: (item[1][0], item[0])
        ):
            self.table.insert(
                "",
                tk.END,
                values=(
                    subject,
                    len(subject_students.get(subject, set())),
                    f"Slot {slot}",
                    room
                )
            )

    # Generate timetable and print diagnostics to terminal
    def generate(self, algorithm):
        if not self.enrollments or not self.rooms:
            messagebox.showwarning(
                "Missing Data",
                "Import CSV data or add students and rooms first."
            )
            return

        settings = self.get_settings()
        if settings is None:
            return

        slots, gap = settings

        subject_students = get_subject_students(self.enrollments)

        print("\n--- SUBJECT ENROLLMENT COUNTS ---")
        print("Total students:", len(self.enrollments))
        print("Room capacities:", self.rooms)

        for subject, students in subject_students.items():
            print(subject, ":", len(students), "students")

        too_large = {
            subject: len(students)
            for subject, students in subject_students.items()
            if not any(
                capacity >= len(students)
                for capacity in self.rooms.values()
            )
        }

        if too_large:
            messagebox.showerror(
                "Room Capacity Problem",
                "These subjects do not fit in any single room:\n\n"
                + "\n".join(
                    f"{subject}: {count} students"
                    for subject, count in too_large.items()
                )
                + "\n\nAdd a room large enough for each subject."
            )
            return

        if algorithm == "Greedy":
            schedule, elapsed = greedy_schedule(
                self.enrollments, self.rooms, slots, gap
            )
        else:
            schedule, elapsed = backtracking_schedule(
                self.enrollments, self.rooms, slots, gap
            )

        self.last_schedule = schedule
        self.last_algorithm = algorithm

        if schedule is None:
            self.clear_table()
            self.status_var.set(
                f"{algorithm}: No valid timetable found."
            )

            messagebox.showwarning(
                "No Valid Timetable",
                "No valid timetable was found with the current settings.\n"
                "Try more slots or reduce the minimum gap."
            )
            return

        self.display_schedule(schedule)

        valid = validate_schedule(
            schedule, self.enrollments, self.rooms, gap
        )

        self.status_var.set(
            f"{algorithm} | Valid: {valid} | "
            f"Slots used: {count_slots(schedule)} | "
            f"Execution time: {elapsed:.6f} seconds"
        )

    # Compare algorithms
    def compare_algorithms(self):
        if not self.enrollments or not self.rooms:
            messagebox.showwarning(
                "Missing Data", "Import data or add students and rooms first."
            )
            return

        settings = self.get_settings()
        if settings is None:
            return

        slots, gap = settings

        greedy_result, greedy_time = greedy_schedule(
            self.enrollments, self.rooms, slots, gap
        )

        back_result, back_time = backtracking_schedule(
            self.enrollments, self.rooms, slots, gap
        )

        self.last_schedule = (
            back_result if back_result is not None else greedy_result
        )

        self.last_algorithm = (
            "Backtracking" if back_result is not None else "Greedy"
        )

        self.display_schedule(self.last_schedule)

        window = tk.Toplevel(self.root)
        window.title("Algorithm Comparison")
        window.geometry("760x350")

        ttk.Label(
            window,
            text="Algorithm Performance Comparison",
            font=("Arial", 15, "bold")
        ).pack(pady=12)

        columns = ("algorithm", "success", "slots", "time", "valid")
        table = ttk.Treeview(
            window, columns=columns, show="headings", height=5
        )

        headings = {
            "algorithm": "Algorithm",
            "success": "Schedule Found",
            "slots": "Slots Used",
            "time": "Execution Time (sec)",
            "valid": "Valid Schedule"
        }

        for col, heading in headings.items():
            table.heading(col, text=heading)
            table.column(col, width=140, anchor="center")

        for name, schedule, elapsed in [
            ("Greedy", greedy_result, greedy_time),
            ("Backtracking", back_result, back_time)
        ]:
            success = schedule is not None
            valid = (
                validate_schedule(
                    schedule, self.enrollments, self.rooms, gap
                ) if success else False
            )

            table.insert(
                "",
                tk.END,
                values=(
                    name,
                    "Yes" if success else "No",
                    count_slots(schedule) if success else "-",
                    f"{elapsed:.6f}",
                    "Yes" if valid else "No"
                )
            )

        table.pack(fill="x", padx=12, pady=10)

    # Draw conflict graph
    def show_conflict_graph(self):
        if not self.enrollments:
            messagebox.showwarning(
                "No Data", "Import or load a dataset first."
            )
            return

        graph = build_conflict_graph(self.enrollments)
        subjects = list(graph)

        if not subjects:
            messagebox.showinfo(
                "Empty Graph", "No subjects to display."
            )
            return

        window = tk.Toplevel(self.root)
        window.title("Subject Conflict Graph")
        window.geometry("800x620")

        ttk.Label(
            window,
            text="Subject Conflict Graph",
            font=("Arial", 16, "bold")
        ).pack(pady=8)

        ttk.Label(
            window,
            text="An edge means at least one student takes both subjects."
        ).pack(pady=4)

        canvas = tk.Canvas(window, bg="white", height=480)
        canvas.pack(fill="both", expand=True, padx=10, pady=10)

        window.update_idletasks()

        width = max(canvas.winfo_width(), 700)
        height = max(canvas.winfo_height(), 450)
        cx, cy = width / 2, height / 2
        radius = min(width, height) * 0.34
        positions = {}

        for i, subject in enumerate(subjects):
            angle = 2 * math.pi * i / len(subjects) - math.pi / 2
            positions[subject] = (
                cx + radius * math.cos(angle),
                cy + radius * math.sin(angle)
            )

        for subject in subjects:
            x1, y1 = positions[subject]

            for neighbor in graph[subject]:
                if subjects.index(subject) < subjects.index(neighbor):
                    x2, y2 = positions[neighbor]
                    canvas.create_line(
                        x1, y1, x2, y2, fill="gray", width=2
                    )

        colors = [
            "#A7D8F0", "#F6C5A5", "#B7E4C7",
            "#D7C3F1", "#FFE699", "#F4B6C2"
        ]

        for subject in subjects:
            x, y = positions[subject]
            color = "#D9EAF7"

            if self.last_schedule and subject in self.last_schedule:
                slot = self.last_schedule[subject][0]
                color = colors[(slot - 1) % len(colors)]

            canvas.create_oval(
                x - 48, y - 26, x + 48, y + 26,
                fill=color, outline="#234", width=2
            )
            canvas.create_text(
                x, y, text=subject, font=("Arial", 10, "bold")
            )

    # Export timetable to CSV
    def export_timetable(self):
        if not self.last_schedule:
            messagebox.showwarning(
                "No Timetable", "Generate a timetable before exporting."
            )
            return

        file_path = filedialog.asksaveasfilename(
            title="Save Examination Timetable",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )

        if not file_path:
            return

        try:
            subject_students = get_subject_students(self.enrollments)

            with open(
                file_path, "w", encoding="utf-8-sig", newline=""
            ) as file:
                writer = csv.writer(file)

                writer.writerow([
                    "Subject",
                    "Number_of_Students",
                    "Time_Slot",
                    "Room"
                ])

                for subject, (slot, room) in sorted(
                    self.last_schedule.items(),
                    key=lambda item: (item[1][0], item[0])
                ):
                    writer.writerow([
                        subject,
                        len(subject_students.get(subject, set())),
                        f"Slot {slot}",
                        room
                    ])

            messagebox.showinfo(
                "Export Successful",
                f"Timetable saved to:\n{file_path}"
            )

        except OSError as error:
            messagebox.showerror("Export Error", str(error))


if __name__ == "__main__":
    root = tk.Tk()
    app = ExamTimetableApp(root)
    root.mainloop()

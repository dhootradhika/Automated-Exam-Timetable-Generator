
from time import perf_counter


def get_subject_students(enrollments):
    subject_students = {}

    for student, subjects in enrollments.items():
        for subject in subjects:
            subject_students.setdefault(subject, set()).add(student)

    return subject_students


def build_conflict_graph(enrollments):
    subject_students = get_subject_students(enrollments)
    graph = {subject: set() for subject in subject_students}
    subjects = list(graph)

    for i in range(len(subjects)):
        for j in range(i + 1, len(subjects)):
            a, b = subjects[i], subjects[j]

            if subject_students[a] & subject_students[b]:
                graph[a].add(b)
                graph[b].add(a)

    return graph


def is_valid(subject, slot, room, schedule, graph, rooms,
             subject_students, min_gap):
    if room not in rooms:
        return False

    if rooms[room] < len(subject_students.get(subject, set())):
        return False

    for other, (other_slot, other_room) in schedule.items():
        if slot == other_slot and room == other_room:
            return False

        if other in graph.get(subject, set()):
            if abs(slot - other_slot) <= min_gap:
                return False

    return True


def validate_schedule(schedule, enrollments, rooms, min_gap):
    if schedule is None:
        return False

    graph = build_conflict_graph(enrollments)
    subject_students = get_subject_students(enrollments)

    if set(schedule) != set(subject_students):
        return False

    for subject, (slot, room) in schedule.items():
        if not isinstance(slot, int) or slot < 1:
            return False

        if room not in rooms:
            return False

        if rooms[room] < len(subject_students[subject]):
            return False

    subjects = list(schedule)

    for i in range(len(subjects)):
        a = subjects[i]
        slot_a, room_a = schedule[a]

        for j in range(i + 1, len(subjects)):
            b = subjects[j]
            slot_b, room_b = schedule[b]

            if slot_a == slot_b and room_a == room_b:
                return False

            if b in graph[a] and abs(slot_a - slot_b) <= min_gap:
                return False

    return True


def count_slots(schedule):
    if not schedule:
        return 0

    return len({slot for slot, room in schedule.values()})


def greedy_schedule(enrollments, rooms, available_slots, min_gap):
    start = perf_counter()

    if available_slots < 1 or min_gap < 0 or not rooms:
        return None, perf_counter() - start

    graph = build_conflict_graph(enrollments)
    subject_students = get_subject_students(enrollments)

    for subject, students in subject_students.items():
        if not any(
            capacity >= len(students)
            for capacity in rooms.values()
        ):
            return None, perf_counter() - start

    schedule = {}

    subjects = sorted(
        graph,
        key=lambda s: (len(graph[s]), len(subject_students[s])),
        reverse=True
    )

    for subject in subjects:
        assigned = False

        for slot in range(1, available_slots + 1):
            for room in rooms:
                if is_valid(
                    subject, slot, room, schedule, graph,
                    rooms, subject_students, min_gap
                ):
                    schedule[subject] = (slot, room)
                    assigned = True
                    break

            if assigned:
                break

        if not assigned:
            return None, perf_counter() - start

    elapsed = perf_counter() - start

    if not validate_schedule(schedule, enrollments, rooms, min_gap):
        return None, elapsed

    return schedule, elapsed


def backtracking_schedule(enrollments, rooms, available_slots, min_gap):
    start = perf_counter()

    if available_slots < 1 or min_gap < 0 or not rooms:
        return None, perf_counter() - start

    graph = build_conflict_graph(enrollments)
    subject_students = get_subject_students(enrollments)

    for subject, students in subject_students.items():
        if not any(
            capacity >= len(students)
            for capacity in rooms.values()
        ):
            return None, perf_counter() - start

    schedule = {}

    subjects = sorted(
        graph,
        key=lambda s: (len(graph[s]), len(subject_students[s])),
        reverse=True
    )

    def solve(index):
        if index == len(subjects):
            return True

        subject = subjects[index]

        for slot in range(1, available_slots + 1):
            for room in rooms:
                if is_valid(
                    subject, slot, room, schedule, graph,
                    rooms, subject_students, min_gap
                ):
                    schedule[subject] = (slot, room)

                    if solve(index + 1):
                        return True

                    del schedule[subject]

        return False

    success = solve(0)
    elapsed = perf_counter() - start

    if success and validate_schedule(
        schedule, enrollments, rooms, min_gap
    ):
        return schedule.copy(), elapsed

    return None, elapsed

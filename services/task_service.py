import json, os
from datetime import datetime
from models.task_model import Task

DATA_FILE = "data/tasks.json"
DATE_FMT = "%d-%m-%Y %H:%M"


class TaskService:
    def __init__(self):
        self.tasks = self.load_tasks()
        self.sort_tasks()

    # Utility
    def now_str(self):
        return datetime.now().strftime(DATE_FMT)

    def parse_dt(self, s):
        return datetime.strptime(s, DATE_FMT)

    #  CRUD
    def add_task(self, title, detail, deadline, priority):
        task = Task(title, detail, deadline, priority)
        self.tasks.append(task)
        self.sort_tasks()
        self.save_tasks()

    def update_task(self, idx, title, detail, deadline, priority):
        t = self.tasks[idx]
        t.title = title
        t.detail = detail
        t.deadline = deadline
        t.priority = priority
        self.sort_tasks()
        self.save_tasks()

    def delete_task(self, idx):
        self.tasks.pop(idx)
        self.save_tasks()

    def mark_done(self, idx):
        self.tasks[idx].done = True
        self.sort_tasks()
        self.save_tasks()

    #  Load / Save
    def load_tasks(self):
        if not os.path.exists(DATA_FILE):
            return []
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Task.from_dict(t) for t in data]
        except:
            return []

    def save_tasks(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                [t.to_dict() for t in self.tasks], f, ensure_ascii=False, indent=2
            )

    # Sorting
    def sort_tasks(self):
        def key(t: Task):
            done = t.done
            try:
                dl = (
                    datetime.strptime(t.deadline, DATE_FMT)
                    if t.deadline
                    else datetime.max
                )
            except:
                dl = datetime.max
            priority_rank = {"Cao": 0, "Trung bình": 1, "Thấp": 2}.get(t.priority, 1)
            return (done, dl, priority_rank)

        self.tasks.sort(key=key)

    #  Format row for UI
    def fmt_row(self, t: Task):
        status = "✔" if t.done else "X"
        overdue = ""
        if t.deadline:
            try:
                if self.parse_dt(t.deadline) < datetime.now() and not t.done:
                    overdue = " [QUÁ HẠN]"
            except:
                pass

        return f"{status} [{t.priority}] {t.title} — {t.deadline}{overdue}"

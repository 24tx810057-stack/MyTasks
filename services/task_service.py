import json, os
from datetime import datetime
from models.task_model import Task

DATA_FILE = "data/tasks.json"
DATE_FMT = "%d-%m-%Y %H:%M"

# == Helpers =
def now_str():
    return datetime.now().strftime(DATE_FMT)

def parse_dt(s):
    return datetime.strptime(s, DATE_FMT)

# == CRUD & Utils ====
def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Task.from_dict(t) for t in data]
    except Exception:
        return []

def save_tasks(tasks):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([t.to_dict() for t in tasks], f, ensure_ascii=False, indent=2)

def sort_tasks(tasks):
    def key(t: Task):
        done = t.done
        try:
            dl = datetime.strptime(t.deadline, DATE_FMT) if t.deadline else datetime.max
        except:
            dl = datetime.max
        priority_rank = {"Cao": 0, "Trung bình": 1, "Thấp": 2}.get(t.priority, 1)
        return (done, dl, priority_rank)
    tasks.sort(key=key)

def fmt_row(t: Task):
    status = "✔ " if t.done else "X"
    overdue = ""
    if t.deadline:
        try:
            if parse_dt(t.deadline) < datetime.now() and not t.done:
                overdue = " [QUÁ HẠN]"
        except:
            pass
    return f"{status} [{t.priority}] {t.title} — {t.deadline}{overdue}"

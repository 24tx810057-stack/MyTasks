import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from services.task_service import TaskService

DATE_FMT = "%d-%m-%Y %H:%M"


# Hộp chọn giờ
class TimeBox(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.hour = tk.StringVar(value="00")
        self.minute = tk.StringVar(value="00")

        spin_style = {"justify": "center", "width": 2, "wrap": True}

        ttk.Spinbox(self, from_=0, to=23, textvariable=self.hour, **spin_style).grid(
            row=0, column=0, padx=(0, 2)
        )
        ttk.Label(self, text=":", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=1, padx=(0, 2)
        )
        ttk.Spinbox(self, from_=0, to=59, textvariable=self.minute, **spin_style).grid(
            row=0, column=2
        )

    def get(self):
        return f"{self.hour.get().zfill(2)}:{self.minute.get().zfill(2)}"

    def set(self, time_str):
        try:
            h, m = time_str.split(":")
            self.hour.set(h)
            self.minute.set(m)
        except ValueError:
            self.hour.set("00")
            self.minute.set("00")


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MyTasks - Quản lý công việc cá nhân")
        self.updating = False
        self.editing_priority = False

        # dùng service
        self.service = TaskService()
        self.tasks = self.service.tasks

        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))

        header = ttk.Frame(root, padding=10)
        header.pack(fill="x")
        ttk.Label(
            header, text=" Quản lý công việc", font=("Segoe UI", 18, "bold")
        ).pack(side="left")
        ttk.Label(
            header, text="Theo dõi - Sắp xếp - Hoàn thành", bootstyle="secondary"
        ).pack(side="left", padx=10)

        frm = ttk.Labelframe(
            root, text=" Thông tin công việc ", padding=10, bootstyle="info"
        )
        frm.pack(fill="x", padx=12, pady=8)

        ttk.Label(frm, text="Tiêu đề:").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_title = ttk.Entry(frm, width=48)
        self.ent_title.grid(row=0, column=1, columnspan=3, sticky="we", padx=6, pady=4)

        ttk.Label(frm, text="Ngày hết hạn:").grid(row=1, column=0, sticky="w", pady=4)
        self.date_deadline = DateEntry(frm, width=12, dateformat="%d-%m-%Y")
        self.date_deadline.grid(row=1, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(frm, text="Giờ:").grid(row=1, column=2, sticky="e", pady=4)
        self.time_deadline = TimeBox(frm)
        self.time_deadline.grid(row=1, column=3, sticky="w", pady=4)

        ttk.Label(frm, text="Ưu tiên:").grid(row=2, column=0, sticky="w", pady=4)
        self.priority_var = tk.StringVar(value="Trung bình")
        self.btn_priority = ttk.Button(
            frm,
            text="Trung bình ",
            bootstyle="warning",
            width=12,
            command=self.show_priority_popup,
        )
        self.btn_priority.grid(row=2, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(frm, text="Chi tiết:").grid(row=3, column=0, sticky="nw", pady=4)

        self.txt_detail = tk.Text(frm, height=4, width=100)
        self.txt_detail.grid(
            row=3, column=1, columnspan=3, sticky="nswe", padx=6, pady=4
        )
        # giãn khung theo kích thước app
        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(2, weight=1)
        frm.columnconfigure(3, weight=1)
        frm.rowconfigure(3, weight=1)

        # button
        btns = ttk.Frame(root, padding=(10, 0))
        btns.pack(fill="x", pady=(2, 8))
        ttk.Button(
            btns, text="Thêm", command=self.add_task, bootstyle="success-outline"
        ).pack(side="left", padx=4)
        ttk.Button(
            btns, text="Cập nhật", command=self.update_task, bootstyle="info-outline"
        ).pack(side="left", padx=4)
        ttk.Button(
            btns, text="Hoàn thành", command=self.mark_done, bootstyle="success"
        ).pack(side="left", padx=4)
        ttk.Button(btns, text="Xóa", command=self.delete_task, bootstyle="danger").pack(
            side="left", padx=4
        )
        ttk.Button(
            btns, text="Làm mới", command=self.refresh, bootstyle="warning-outline"
        ).pack(side="left", padx=4)

        # Ds cv
        listfrm = ttk.Labelframe(root, text=" Danh sách công việc ", padding=8)
        listfrm.pack(fill="both", expand=True, padx=5, pady=5)

        # Bộ lọc
        filter_bar = ttk.Frame(listfrm)
        filter_bar.pack(fill="x", pady=(0, 8))

        # Lọc trạng thái
        ttk.Label(filter_bar, text="Trạng thái:").pack(side="left", padx=(0, 4))
        self.filter_status = tk.StringVar(value="Tất cả")
        cb_status = ttk.Combobox(
            filter_bar,
            textvariable=self.filter_status,
            values=["Tất cả", "Hoàn thành", "Chưa hoàn thành"],
            width=16,
            state="readonly",
        )
        cb_status.pack(side="left", padx=(0, 20))
        cb_status.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        # Lọc ưu tiên
        ttk.Label(filter_bar, text="Ưu tiên:").pack(side="left", padx=(0, 4))
        self.filter_priority = tk.StringVar(value="Tất cả")
        cb_priority = ttk.Combobox(
            filter_bar,
            textvariable=self.filter_priority,
            values=["Tất cả", "Cao", "Trung bình", "Thấp"],
            width=10,
            state="readonly",
        )
        cb_priority.pack(side="left")
        cb_priority.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        self.listbox = tk.Listbox(
            listfrm, height=8, activestyle="dotbox", font=("Segoe UI", 10)
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        sb = ttk.Scrollbar(listfrm, orient="vertical", command=self.listbox.yview)
        sb.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=sb.set)

        info = ttk.Labelframe(
            root,
            text=" Chi tiết ",
            padding=12,
            bootstyle="secondary",
        )
        info.pack(fill="x", padx=14, pady=(10, 14))

        self.lbl_info = ttk.Label(
            info,
            text="Chọn 1 công việc để xem chi tiết…",
            justify="left",
            anchor="w",
        )
        self.lbl_info.pack(fill="x", expand=True, padx=4, pady=4)

        def _auto_wrap(event):
            self.lbl_info.configure(wraplength=event.width - 20)

        info.bind("<Configure>", _auto_wrap)

        self.refresh()

    # CRUD
    def add_task(self):
        title = self.ent_title.get().strip()
        date_str = self.date_deadline.entry.get().strip()
        time_str = self.time_deadline.get()
        deadline = f"{date_str} {time_str}"
        priority = self.priority_var.get().strip()
        detail = self.txt_detail.get("1.0", "end").strip()

        if not title:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tiêu đề.")
            return

        try:
            self.service.parse_dt(deadline)
        except:
            messagebox.showwarning(
                "Sai định dạng", f"Deadline phải theo định dạng {DATE_FMT}"
            )
            return

        self.service.add_task(title, detail, deadline, priority)

        self.clear_form()
        self.refresh()
        messagebox.showinfo("Thành công", "Đã thêm công việc.")

    def update_task(self):
        idx = self.current_index()
        if idx is None:
            messagebox.showwarning(
                "Thiếu lựa chọn", "Vui lòng chọn một công việc trong danh sách!"
            )
            return

        title = self.ent_title.get().strip()
        date_str = self.date_deadline.entry.get().strip()
        time_str = self.time_deadline.get()
        deadline = f"{date_str} {time_str}"
        priority = self.priority_var.get().strip()
        detail = self.txt_detail.get("1.0", "end").strip()

        try:
            self.service.parse_dt(deadline)
        except:
            messagebox.showwarning(
                "Sai định dạng", f"Deadline phải theo định dạng {DATE_FMT}"
            )
            return

        self.service.update_task(idx, title, detail, deadline, priority)

        self.refresh()
        messagebox.showinfo("OK", "Đã cập nhật.")

    def delete_task(self):
        idx = self.current_index()
        if idx is None:
            return

        if messagebox.askyesno("Xóa", "Xác nhận xóa?"):
            self.service.delete_task(idx)
            self.clear_form()
            self.refresh()

    def mark_done(self):
        idx = self.current_index()
        if idx is None:
            return
        self.service.mark_done(idx)
        self.refresh()

    # Popup chọn ưu tiên
    def show_priority_popup(self):
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.geometry(
            "+%d+%d"
            % (self.btn_priority.winfo_rootx(), self.btn_priority.winfo_rooty() + 30)
        )
        popup.config(bg="#f0f0f0", padx=4, pady=4)

        options = [
            ("Cao", "danger"),
            ("Trung bình", "warning"),
            ("Thấp", "success"),
        ]

        def select_priority(value, style):
            self.priority_var.set(value)
            self.btn_priority.config(text=value, bootstyle=style)
            popup.destroy()

        for text, style in options:
            ttk.Button(
                popup,
                text=text,
                bootstyle=style,
                width=14,
                command=lambda t=text, s=style: select_priority(t, s),
            ).pack(fill="x", pady=2)

        try:
            popup.focus_set()
            popup.grab_set()
        except:
            pass

    # Lấy index hiện tại
    def current_index(self):
        sel = self.listbox.curselection()
        return sel[0] if sel else None

    # Clear sạch form
    def clear_form(self):
        # tiêu đề
        self.ent_title.delete(0, tk.END)

        # chi tiết
        self.txt_detail.delete("1.0", tk.END)

        # reset ngày
        try:
            self.date_deadline.entry.delete(0, tk.END)
            from datetime import datetime

            self.date_deadline.entry.insert(0, datetime.now().strftime("%d-%m-%Y"))
        except:
            pass

        # reset giờ
        self.time_deadline.set("00:00")

        # reset ưu tiên
        self.priority_var.set("Trung bình")
        self.btn_priority.config(text="Trung bình", bootstyle="warning")

    # Cập nhật listbox
    def update_listbox(self, data):
        self.listbox.delete(0, tk.END)

        for i, t in enumerate(data):
            label = self.service.fmt_row(t)
            self.listbox.insert(i, label)

            if t.done:
                color = "#FFFFFF"
            else:
                if t.priority == "Cao":
                    color = "#DD4F4F"
                elif t.priority == "Thấp":
                    color = "#79F7A5"
                else:
                    color = "#EEDC8E"

            self.listbox.itemconfig(i, bg=color)

    # Áp dụng bộ lọc
    def apply_filter(self):
        status = self.filter_status.get()
        priority = self.filter_priority.get()

        filtered = self.tasks

        # lọc trạng thái
        if status == "Hoàn thành":
            filtered = [t for t in filtered if t.done]
        elif status == "Chưa hoàn thành":
            filtered = [t for t in filtered if not t.done]

        # lọc ưu tiên
        if priority != "Tất cả":
            filtered = [t for t in filtered if t.priority == priority]

        # cập nhật listbox
        self.update_listbox(filtered)

    # Refesh lại
    def refresh(self):
        # luôn sync lại
        self.tasks = self.service.tasks

        # Sắp xếp theo deadline
        try:
            self.tasks.sort(
                key=lambda t: (
                    self.service.parse_dt(t.deadline) if t.deadline else float("inf")
                )
            )
        except:
            pass

        #  Reset hết ô nhập mỗi lần refresh
        self.clear_form()
        self.apply_filter()

    def on_select(self, _evt):
        idx = self.current_index()
        if idx is None or idx >= len(self.tasks):
            return
        t = self.tasks[idx]
        self.ent_title.delete(0, tk.END)
        self.ent_title.insert(0, t.title)
        self.txt_detail.delete("1.0", tk.END)
        self.txt_detail.insert("1.0", t.detail)
        if t.deadline:
            try:
                dt = self.service.parse_dt(t.deadline)
                self.date_deadline.entry.delete(0, tk.END)
                self.date_deadline.entry.insert(0, dt.strftime("%d-%m-%Y"))
                self.time_deadline.set(dt.strftime("%H:%M"))
            except:
                pass

        info = (
            f"Tiêu đề: {t.title}\n"
            f"Chi tiết: {t.detail}\n"
            f"Ưu tiên: {t.priority}\n"
            f"Deadline: {t.deadline or '(chưa đặt)'}\n"
            f"Tạo lúc: {t.created_at}\n"
            f"Trạng thái: {'Hoàn thành' if t.done else 'Chưa xong'}"
        )
        self.lbl_info.config(text=info)

        style_map = {
            "Cao": "danger",
            "Trung bình": "warning",
            "Thấp": "success",
        }
        style = style_map.get(t.priority, "secondary")
        self.priority_var.set(t.priority)
        self.btn_priority.config(text=f" {t.priority}", bootstyle=style)


def run_app():
    # Các theme: cosmo, united, yeti, solar, simplex, pulse, minty, flatly
    root = ttk.Window(themename="pulse", size=(600, 400))
    # căn giữa khi khởi động
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - 600) // 2
    y = (sh - 400) // 2
    root.geometry(f"600x400+{x}+{y}")

    root.title("MyTasks - Đang khởi động...")

    # Splash screen
    splash = ttk.Frame(root, padding=60)
    ttk.Label(
        splash, text="Đang khởi động MyTasks...", font=("Roboto", 16, "bold")
    ).pack(pady=20)
    bar = ttk.Progressbar(splash, mode="indeterminate", bootstyle="info-striped")
    bar.pack(fill="x", padx=40, pady=10)
    bar.start(10)
    splash.pack(expand=True)

    root.update()

    # Load 2s
    root.after(2000, lambda: start_main_app(root, splash))
    root.mainloop()


def start_main_app(root, splash):
    # Hủy, khởi tạo app chính
    splash.destroy()
    root.iconbitmap("assets/logo.ico")
    app = TodoApp(root)

    # Căn giữa cửa sổ
    w, h = 600, 800
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")


if __name__ == "__main__":
    run_app()

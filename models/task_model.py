from datetime import datetime

DATE_FMT = "%d-%m-%Y %H:%M"


# định nghĩa dữ liệu
class Task:
    def __init__(
        self,
        title,
        detail="",
        deadline="",
        priority="Trung bình",
        done=False,
        created_at=None,
    ):
        self.title = title
        self.detail = detail
        self.deadline = deadline
        self.priority = priority
        self.done = done
        self.created_at = created_at or datetime.now().strftime(DATE_FMT)

    # chuyển object thành dạng dictionary
    def to_dict(self):
        return self.__dict__

    # chuyển dictionary thành object
    @staticmethod
    def from_dict(d):
        return Task(**d)

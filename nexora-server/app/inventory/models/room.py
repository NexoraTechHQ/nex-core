class Room:
    def __init__(self, record):
        self.id = record.get("id")
        self.name = record.get("name")
        self.department_id = record.get("department_id", None)
        self.disabled = record.get("disabled")
        self.created = record.get("created")
        self.updated = record.get("updated")

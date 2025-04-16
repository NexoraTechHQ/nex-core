class Role:
    def __init__(self, record):
        self.id = record.get("id")
        self.name = record.get("name")
        self.permissions = record.get("permissions", [])
        self.disabled = record.get("disabled")
        self.created = record.get("created")
        self.updated = record.get("updated")

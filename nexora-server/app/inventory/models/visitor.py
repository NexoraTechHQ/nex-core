class Visitor:
    def __init__(self, record):
        self.id = record.get("id")
        self.name = record.get("name")
        self.email = record.get("email")
        self.images = record.get("images", [])  # List of image URLs
        self.is_deleted = record.get("is_deleted", False)
        self.created = record.get("created")
        self.updated = record.get("updated")

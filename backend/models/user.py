from datetime import datetime


class User:

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
        self.created_at = datetime.now()
        self.total_designs = 0

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at,
            "total_designs": self.total_designs
        }

    def validate(self):
        """Validate user data before saving."""

        # Check name
        if not self.name or len(self.name) < 2:
            return False, "Name must be at least 2 characters"

        # Check email
        if not self.email or "@" not in self.email:
            return False, "Invalid email address"

        # Check password
        if not self.password or len(self.password) < 6:
            return False, "Password must be at least 6 characters"

        return True, "Valid"

    def __str__(self):
        return f"User(name={self.name}, email={self.email})"    
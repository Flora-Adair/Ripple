from datetime import datetime

# In-memory "database"
users = []
mood_entries = []

class User:
    """
    Represents a user in the system.
    """
    def __init__(self, first_name, last_name, dorm=None, email=None, password=None, is_dorm_parent=False):
        self.id = len(users) + 1  # Auto-increment user ID
        self.first_name = first_name
        self.last_name = last_name
        self.dorm = dorm
        self.email = email
        self.password = password  # Only used by dorm parents; should be hashed in production
        self.is_dorm_parent = is_dorm_parent
        users.append(self)

    def __repr__(self):
        return (f"User(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, "
                f"dorm={self.dorm}, email={self.email}, is_dorm_parent={self.is_dorm_parent})")

class MoodEntry:
    """
    Represents a mood entry submitted by a student.
    """
    def __init__(self, user_id, mood_score, mood_description):
        self.id = len(mood_entries) + 1  # Auto-increment mood entry ID
        self.user_id = user_id
        self.mood_score = mood_score
        self.mood_description = mood_description
        self.timestamp = datetime.utcnow()
        mood_entries.append(self)

    def __repr__(self):
        return (f"MoodEntry(id={self.id}, user_id={self.user_id}, mood_score={self.mood_score}, "
                f"mood_description={self.mood_description}, timestamp={self.timestamp})")

    @staticmethod
    def get_moods_for_user(user_id):
        """
        Returns all mood entries submitted by a specific user.
        """
        if not user_id:
            raise ValueError("A valid user ID must be provided.")
        return [mood for mood in mood_entries if mood.user_id == user_id]

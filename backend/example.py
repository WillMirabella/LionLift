from models.user import User
import db

db.clear_relations()
db.create_relations()

User.to_db(User("jd@gmail.com", None, "Alice", "A", "1234567890", "female", "This is my description.", 2028, "Computer Science", None, None, "PA", "18940", 40.22840, -74.93234, None, None))
User.to_db(User("jd@gmail.com", None, "Bob", "B", "1234567890", "male", "This is my description.", 2028, "Computer Science", None, None, "PA", "18940", 39.95287, -75.16548, None, None))
User.to_db(User("jd@gmail.com", None, "Charlie", "C", "1234567890", "male", "This is my description.", 2028, "Computer Science", None, None, "PA", "18940", 40.06967, -75.12552, None, None))

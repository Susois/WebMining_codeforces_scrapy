from mongoengine import Document, StringField, ListField, IntField, FloatField

class Problem(Document):
    problem_id = StringField(required=True, unique=True)
    title = StringField(required=True)
    tags = ListField(StringField())
    difficulty = FloatField()
    submission_count = IntField()
    accepted_count = IntField()

class Contest(Document):
    contest_id = StringField(required=True, unique=True)
    title = StringField(required=True)
    problems = ListField(StringField())  # List of problem IDs associated with the contest

class User(Document):
    user_id = StringField(required=True, unique=True)
    username = StringField(required=True)
    solved_problems = ListField(StringField())  # List of problem IDs solved by the user
    submissions = IntField()  # Total number of submissions by the user

class Tag(Document):
    name = StringField(required=True, unique=True)
    problems = ListField(StringField())  # List of problem IDs associated with the tag
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from datetime import datetime


metadata = MetaData()

db = SQLAlchemy(metadata=metadata)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    # Relationships
    problems = db.relationship('Problem', backref='author', lazy=True)  
    solutions = db.relationship('Solution', backref='author', lazy=True)  
    votes = db.relationship('Vote', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

class Problem(db.Model):
    __tablename__ = 'problems'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=True)
    # Relationships
    solutions = db.relationship('Solution', backref='problem', lazy=True)

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    # Relationships
    solutions = db.relationship('Solution', backref='tag', lazy=True)
    problems = db.relationship('Problem', backref='tag', lazy=True)

class Solution(db.Model):
    __tablename__ = 'solutions'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=True)  # New relationship
    # Relationships
    votes = db.relationship('Vote', backref='solution', lazy=True)

    def get_vote_counts(self):
        likes = Vote.query.filter_by(solution_id=self.id, vote_type=1).count()
        dislikes = Vote.query.filter_by(solution_id=self.id, vote_type=-1).count()
        return {'likes': likes, 'dislikes': dislikes}

class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    solution_id = db.Column(db.Integer, db.ForeignKey('solutions.id'), nullable=False)
    vote_type = db.Column(db.Integer, nullable=False)  # 1 for like, -1 for dislike
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    
class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'vote', 'reply'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reference_id = db.Column(db.Integer)  # Optional: ID of related entity (e.g., solution_id)

class Faq(db.Model):
    __tablename__ = 'faqs'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    
    def _repr_(self):
        return f"<FAQ {self.question} {self.answer}>"



class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)
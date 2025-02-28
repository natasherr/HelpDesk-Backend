from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.sql import select
from sqlalchemy import func
from sqlalchemy import case

metadata = MetaData()
db = SQLAlchemy(metadata=metadata)



class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    
    
    # Relationships   
    votes = db.relationship('Vote', backref='user', lazy=True)
    subscriptions = db.relationship('Subscription', backref='user', lazy=True)  # Added for follow/subscription feature

    
    
class Problem(db.Model):
    __tablename__ = 'problems'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    solutions = db.relationship("Solution", back_populates="problem", cascade="all, delete-orphan")
    user = db.relationship('User', backref='problems')
    tag = db.relationship("Tag", back_populates="problems", lazy="joined")
    subscriptions = db.relationship('Subscription', backref='problem', lazy=True)  # Added for follow/subscription feature


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # Relationship
    solutions = db.relationship('Solution', back_populates='tag', lazy=True)
    problems = db.relationship('Problem', back_populates='tag', lazy=True)


class Solution(db.Model):
    __tablename__ = 'solutions'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    
    # Relationship
    tag = db.relationship("Tag", back_populates="solutions")
    votes = db.relationship('Vote', backref='solution', lazy=True)
    user = db.relationship('User', backref='solutions')
    problem = db.relationship("Problem", back_populates="solutions")

    def get_vote_counts(self):
        vote_counts = db.session.query(
            func.sum(case((Vote.vote_type == 1, 1), else_=0)).label("likes"),
            func.sum(case((Vote.vote_type == -1, 1), else_=0)).label("dislikes")
        ).filter(Vote.solution_id == self.id).first()

        return {
            "likes": vote_counts.likes or 0,
            "dislikes": vote_counts.dislikes or 0
        }



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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Notification recipient
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User who performed the action
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'vote', 'reply'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reference_id = db.Column(db.Integer)  # Optional: ID of related entity (e.g., solution_id)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='notifications')  # Notification recipient
    actor = db.relationship('User', foreign_keys=[actor_id])  # User who performed the action


class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Add a unique constraint to ensure a user can only subscribe to a problem once
    __table_args__ = (
        db.UniqueConstraint('user_id', 'problem_id', name='unique_user_problem_subscription'),
    )

class Faq(db.Model):
    __tablename__ = 'faqs'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f"<FAQ {self.question} {self.answer}>"


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)



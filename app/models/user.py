from app.extensions import db
from launchable.Launchable import Launchable
from sqlalchemy.exc import IntegrityError

import datetime
import bcrypt
from flask_login import UserMixin

class User(db.Model, Launchable, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    name = db.Column(db.Text, nullable=True)
    surname = db.Column(db.Text, nullable=True)
    icon = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, nullable=True)
    birthday = db.Column(db.Text, nullable=True)
    country = db.Column(db.Text, nullable=True)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    last_logged_in = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    last_flag = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer, nullable=False)
    ctftime = db.Column(db.Integer, nullable=True)
    github = db.Column(db.Text, nullable=True)
    webpage = db.Column(db.Text, nullable=True)
    user_is_hidden = db.Column(db.Boolean, nullable=False, default=False)
    user_is_admin = db.Column(db.Boolean, nullable=False, default=False)
    user_is_active = db.Column(db.Boolean, nullable=False, default=True)
    user_is_banned = db.Column(db.Boolean, nullable=False, default=False)

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    team = db.relationship('Team', backref=db.backref('team_members', lazy='dynamic'), foreign_keys=[team_id], overlaps='team,team_members')
    solved_challenges = db.relationship('Challenge', secondary='user_challenge_link', backref=db.backref('user_solvers', lazy='dynamic'), overlaps='solved_by_users')

    def __init__(self, username:str, name:str='', surname:str='', icon:str='', email:str='', birthday:str='', country:str='', password:str='', created_at:str=None, last_logged_in:str=None, last_flag:str=None, score:int=0, ctftime:int=0, github:str='', webpage:str='', user_is_hidden:bool=False, user_is_admin:bool=False, user_is_active:bool=True):
        self.username = username
        self.name = name
        self.surname = surname
        self.icon = icon
        self.email = email
        self.birthday = birthday
        self.country = country
        self.password = password
        if created_at is None: self.created_at = datetime.datetime.now()
        else: self.created_at = created_at
        if created_at is None: self.last_logged_in = self.created_at
        else: self.last_logged_in = last_logged_in
        self.last_flag = last_flag
        if score != 0: self.score = 0
        else: self.score = score
        self.ctftime = ctftime if ctftime != 0 else None
        self.github = github
        self.webpage = webpage
        self.user_is_hidden = user_is_hidden
        self.user_is_admin = user_is_admin
        self.user_is_active = user_is_active

    def get_id(self):
        return str(self.username)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
    
    def __repr__(self) -> str:
        return super().__repr__()

    def __str__(self) -> str:
        return str(self.username) 

    def __insert(self, password:str=None, admin:bool=False, hidden:bool=False, active:bool=True, icon:str=None, banned:bool=False) -> bool:
        if any([password is None, password == '', self.__found(username=self.username), not isinstance(admin, bool), not isinstance(hidden, bool), not isinstance(active, bool), not isinstance(banned, bool)]): return False
        salt = bcrypt.gensalt()
        self.password = (salt + bcrypt.hashpw(password.encode('utf-8'), salt)).decode('utf-8')
        self.user_is_admin = admin
        if admin: self.user_is_hidden = True # Always Hidden if ZeroAdmin
        else: self.user_is_hidden = hidden
        self.user_is_active = active
        self.icon = icon
        self.user_is_banned = banned
        try: 
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError: 
            db.session.rollback()
            return False 

    @classmethod
    def __verify(cls, username:str=None, password:str=None) -> bool:
        if any([username is None, username == '', password is None, password == '', not cls.__found(username=username)]): return False
        user:User = cls.found(username=username)
        if not user.user_is_active: return False
        hashed = str(user.password).encode('utf-8')
        salt = hashed[0:29]
        hashed_password = salt + bcrypt.hashpw(password.encode('utf-8'), salt)
        if hashed_password == hashed: 
            cls.update(username=username, last_logged_in=datetime.datetime.now())
            return True
        return False
    
    @classmethod
    def __update(cls, username:str=None, email:str=None, name:str=None, surname:str=None, birthday:str=None, location:str=None, last_logged_in:datetime.datetime=None, ctftime:int=0, github:str=None, webpage:str=None, user_is_active:bool=None, user_is_admin:bool=None, user_is_hidden:bool=None, user_is_banned:bool=None, icon:str=None, password:str=None) -> bool:
       
        if all([username == '', username is None, email == '', email is None, name == '', name is None, surname == '', birthday == '', birthday is None, location == '', location is None, not isinstance(last_logged_in, datetime.datetime), not isinstance(ctftime, int), github == '', github is None, webpage == '', webpage is None, not isinstance(user_is_active, bool), not isinstance(user_is_admin, bool), not isinstance(user_is_hidden, bool), not isinstance(user_is_banned, bool), icon == '', icon is None, password == '', password is None]) or not cls.found(username=username): return False
        
        user:User = cls.found(username=username)
        user.email = email if email is not None else user.email
        user.name = name if name is not None else user.name
        user.surname = surname if surname is not None else user.surname
        user.birthday = birthday if birthday is not None else user.birthday
        user.country = location if location is not None else user.country
        user.last_logged_in = last_logged_in if last_logged_in is not None else user.last_logged_in
        user.icon = icon if icon is not None else user.icon
        user.ctftime = ctftime if ctftime != 0 else user.ctftime
        user.github = github if github is not None else user.github
        user.webpage = webpage if webpage is not None else user.webpage
        user.user_is_active = user_is_active if user_is_active is not None else user.user_is_active
        user.user_is_admin = user_is_admin if user_is_admin is not None else user.user_is_admin
        user.user_is_hidden = user_is_hidden if user_is_hidden is not None else user.user_is_hidden
        user.user_is_banned = user_is_banned if user_is_banned is not None else user.user_is_banned
        user.password = password if password is not None else user.password

        try: 
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            return False
        
    @classmethod
    def __passwdupdate(cls, username:str=None, password:str=None) -> bool:
        if any([username == '', username is None, password == '', password is None]): return False
        user:User = cls.found(username=username)
        salt = bcrypt.gensalt()
        user.password = (salt + bcrypt.hashpw(password.encode('utf-8'), salt)).decode('utf-8')
        try: 
            db.session.commit()
            return True
        except IntegrityError: 
            db.session.rollback()
            return False 
    
    @classmethod
    def __get_db_id(cls, username:str=None) -> int:
        if any([username is None, username == '', not cls.found(username=username)]): return 0
        user:User = cls.found(username=username)
        return user.id

    @classmethod
    def __found(cls, username:str=None) -> 'User':
        if any([username is None, username == '']): return False
        found:User = cls.query.filter_by(username=username).first()
        if found is None: return False 
        return found
    
    @classmethod
    def add_user(cls, username:str=None, password:str=None, admin:bool=False, hidden:bool=False, active:bool=True, icon:str=None, banned:bool=False) -> bool:
        if any([username == '', username is None, password == '', password is None, not isinstance(admin, bool), not isinstance(hidden, bool), not isinstance(active, bool), not isinstance(banned, bool)]): return False
        return cls(username=username).__insert(password=password, admin=admin, hidden=hidden, active=active, icon=icon, banned=banned)

    @classmethod
    def verify(cls, username:str=None, password:str=None) -> bool:
        return cls.__verify(username=username, password=password)
    
    @classmethod
    def update(cls, username:str=None, email:str=None, name:str=None, surname:str=None, birthday:str=None, location:str=None, last_logged_in:datetime.datetime=None, ctftime:int=0, github:str=None, webpage:str=None, user_is_hidden:bool=None, user_is_admin:bool=None, user_is_active:bool=None, user_is_banned:bool=None, icon:str=None, password:str=None) -> bool:
        return cls.__update(username=username, email=email, name=name, surname=surname, birthday=birthday, location=location, last_logged_in=last_logged_in, ctftime=ctftime, github=github, webpage=webpage, user_is_active=user_is_active, user_is_hidden=user_is_hidden, user_is_admin=user_is_admin, user_is_banned=user_is_banned, icon=icon, password=password)

    @classmethod
    def passwdupdate(cls, username:str=None, password:str=None) -> bool:
        return cls.__passwdupdate(username=username, password=password)

    @classmethod
    def find_id(cls, username:str=None) -> int:
        return cls.__get_db_id(username=username)

    @classmethod
    def found(cls, username:str=None) -> 'User':
        return cls.__found(username=username)
    
    @classmethod
    def remove(cls, username:str=None) -> bool:
        if any([username == '', username is None, not cls.found(username=username)]): return False
        user:User = cls.found(username=username)
        try:
            if bool(user.team):
                user.team_id = None
                user.team = None
                user.solved_challenges.clear()
            db.session.delete(user)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    @classmethod
    def challenges(cls, username:str=None) -> list:
        if any([username == '', username is None, not cls.found(username=username)]): return False
        user:User = cls.found(username=username)
        return user.solved_challenges
    
    @classmethod
    def position(cls, username:str=None) -> int:
        if any([username == '', username is None, not cls.found(username=username)]): return False
        user:User = cls.found(username=username) 
        if not user.user_is_active or user.user_is_hidden: return 0
        users:list['User'] = cls.select()
        users:list['User'] = [u for u in users if (u.user_is_hidden == False and u.user_is_active == True)]
        if len(users) == 0: return False
        users:list['User'] = sorted(users, key=lambda user: user.score, reverse=True)
        user_id = cls.find_id(username=username)
        user_rank = [user.id for user in users].index(user_id) + 1
        return user_rank


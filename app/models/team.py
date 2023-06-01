from app.extensions import db
from launchable.Launchable import Launchable
from .user import User
from .challenge import Challenge
from sqlalchemy.exc import IntegrityError

import bcrypt
import datetime

class Team(db.Model, Launchable):
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    teamname = db.Column(db.String(60), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    score = db.Column(db.Integer, nullable=False)
    password = db.Column(db.Text, nullable=False)
    country = db.Column(db.Text, nullable=True)
    ctftime = db.Column(db.Integer, nullable=True)
    github = db.Column(db.Text, nullable=True)
    webpage = db.Column(db.Text, nullable=True)
    email = db.Column(db.Text, nullable=True)
    icon = db.Column(db.Text, nullable=True)
    team_is_hidden = db.Column(db.Boolean, nullable=False, default=False)
    team_is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    leader_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    members = db.relationship('User', backref=db.backref('team_players', uselist=False), foreign_keys='User.team_id', overlaps='team,team_members', lazy=True, cascade="all, delete-orphan")
    solved_challenges = db.relationship('Challenge', secondary='team_challenge_link', backref=db.backref('team_solvers', lazy='dynamic'), overlaps='solved_by_teams')
    
    def __init__(self, teamname:str, password:str='', created_at:str=None, score:int=0, leader_id:str=0, country:str='', webpage:str='', ctftime:int=0, github:str='', email:str='', icon:str='', team_is_hidden:bool=False, team_is_active:bool=True) -> None:
        self.teamname = teamname
        self.password = password
        if created_at is None: self.created_at = datetime.datetime.now()
        else: self.created_at = created_at  
        if score != 0: self.score = 0
        else: self.score = score
        if leader_id != 0: self.leader_id = leader_id
        else: self.leader_id = leader_id
        self.country = country
        self.ctftime = ctftime if ctftime != 0 else None
        self.github = github
        self.webpage = webpage
        self.email = email
        self.icon = icon
        self.team_is_hidden = team_is_hidden
        self.team_is_active = team_is_active

    def __repr__(self) -> str:
        return super().__repr__()

    def __str__(self) -> str:
        return str(self.teamname)

    def __insert(self, username:str=None, password:str=None, hidden:bool=False, active:bool=True) -> bool:
        if any([username is None, username == '', password is None, password == '', self.__found(teamname=self.teamname), not isinstance(hidden, bool), not isinstance(active, bool)]): return False
        salt = bcrypt.gensalt()
        self.password = (salt + bcrypt.hashpw(password.encode('utf-8'), salt)).decode('utf-8')
        if not self.__add_leader(username=username): return False
        self.team_is_hidden = hidden
        self.team_is_active = active
        try: 
            db.session.add(self)
            if not self.add_member(username=username, teamname=self.teamname): 
                db.session.rollback()
                return False
            db.session.commit()
            return True
        except IntegrityError or Exception: 
            db.session.rollback()
            return False 

    def __add_leader(self, username:str=None) -> bool:
        if any([username is None, username == '', not User.found(username=username)]): return False
        user = User.found(username=username)
        if user.team is not None: return False
        self.leader_id = user.id
        return True
    
    @classmethod
    def __verify(cls, teamname:str=None, password:str=None) -> bool:
        if any([teamname is None, teamname == '', password is None, password == '', not cls.__found(teamname=teamname)]): return False
        team:Team = cls.__found(teamname=teamname)
        hashed = str(team.password).encode('utf-8')
        salt = hashed[0:29]
        hashed_password = salt + bcrypt.hashpw(password.encode('utf-8'), salt)
        if hashed_password == hashed: return True
        return False
    
    @classmethod
    def __update(cls, teamname:str=None, email:str=None, location:str=None, ctftime:int=0, github:str=None, webpage:str=None, team_is_hidden:bool=None, team_is_active:bool=None) -> bool:
        if all([teamname == '', teamname is None, email == '', email is None, location == '', location is None, not isinstance(ctftime, int), github == '', github is None, webpage == '', webpage is None, team_is_hidden == '', team_is_hidden is None, team_is_active == '', team_is_active is None]) or not cls.found(teamname=teamname): return False
        
        team:Team = cls.found(teamname=teamname)
        team.email = email if email is not None else team.email
        team.country = location if location is not None else team.country
        team.ctftime = ctftime if ctftime != 0 else team.ctftime
        team.github = github if github is not None else team.github
        team.webpage = webpage if webpage is not None else team.webpage
        team.team_is_hidden = team_is_hidden if team_is_hidden is not None else team.team_is_hidden
        team.team_is_active = team_is_active if team_is_active is not None else team.team_is_active

        try: 
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            return False 
        
    @classmethod
    def __passwdupdate(cls, teamname:str=None, password:str=None) -> bool:
        if any([teamname == '', teamname is None, password == '', password is None]): return False
        team:Team = cls.found(teamname=teamname)
        salt = bcrypt.gensalt()
        team.password = (salt + bcrypt.hashpw(password.encode('utf-8'), salt)).decode('utf-8')
        try: 
            db.session.commit()
            return True
        except IntegrityError: 
            db.session.rollback()
            return False 
    
    @classmethod
    def __leaderupdate(cls, teamname:str=None, leader:str=None) -> bool:
        team:Team = cls.found(teamname=teamname)
        user:User = User.found(username=leader.username)
        team.leader_id = user.id
        try:
            db.session.commit()
            return True
        except IntegrityError: 
            db.session.rollback()
            return False 

    @classmethod
    def __get_db_id(cls, teamname:str=None) -> int:
        if any([teamname is None, teamname == '', not cls.found(teamname=teamname)]): return 0
        team:Team = cls.__found(teamname=teamname)
        return team.id
     
    @classmethod
    def __found(cls, teamname:str=None) -> 'Team':
        if any([teamname is None, teamname == '']): return False
        found = cls.query.filter_by(teamname=teamname).first()
        if found is None: return False 
        return found

    @classmethod
    def add_team(cls, teamname:str=None, username:str=None, password:str=None, hidden:bool=False, active:bool=True) -> bool:
        if any([teamname is None, teamname == '', username is None, username == '', password is None, password == '', not isinstance(hidden, bool), not isinstance(active, bool)]): return False
        return cls(teamname=teamname).__insert(username=username, password=password)

    @classmethod
    def verify(cls, teamname:str=None, password:str=None) -> bool:
        if any([teamname is None, teamname == '', password is None, password == '']): return False
        return cls.__verify(teamname=teamname, password=password)

    @classmethod
    def update(cls, teamname:str=None, email:str=None, location:str=None, ctftime:int=0, github:str=None, webpage:str=None, team_is_active:bool=None, team_is_hidden:bool=None) -> bool:
        return cls.__update(teamname=teamname, email=email, location=location, ctftime=ctftime, github=github, webpage=webpage, team_is_active=team_is_active, team_is_hidden=team_is_hidden)

    @classmethod
    def passwdupdate(cls, teamname:str=None, password:str=None) -> bool:
        return cls.__passwdupdate(teamname=teamname, password=password)

    @classmethod
    def find_id(cls, teamname:str=None) -> int:
        if teamname == '' or teamname is None: return False
        return cls.__get_db_id(teamname=teamname)
    
    @classmethod
    def found(cls, teamname:str=None) -> 'Team':
        if teamname == '' or teamname is None: return False
        return cls.__found(teamname=teamname)
    
    @classmethod
    def add_member(cls, username:str=None, teamname:str=None) -> bool:
        if any([username is None, username == '', teamname is None, teamname == '', not cls.found(teamname=teamname), not User.found(username=username)]): return False
        user = User.found(username=username)
        if any([user.user_is_hidden, not user.user_is_active]): return False
        if bool(user.team): return False
        team = cls.found(teamname=teamname)
        user.team = team

        team_solved_challenges:list[Challenge] = team.solved_challenges
        user_solved_challenges:list[Challenge] = user.solved_challenges

        to_add:list = []
        score = team.score
        for challenge in user_solved_challenges:
            if challenge not in team_solved_challenges:
                score += challenge.value
                to_add.append(challenge)

        team.score = score
        team_solved_challenges.extend(to_add)
        team.solved_challenges = list(set(team_solved_challenges))

        db.session.commit()
        return True
    
    @classmethod
    def kickout_member(cls, username:str=None, teamname:str=None) -> bool:
        if any([username is None, username == '', teamname is None, teamname == '', not cls.found(teamname=teamname), not User.found(username=username)]): return False
        user = User.found(username=username)
        team = cls.found(teamname=teamname)
        if any([not user.user_is_active, user.user_is_hidden, not team.team_is_active, team.team_is_hidden]): return False
        if not bool(user.team): return False
        points = 0
        challenges:list = user.solved_challenges
        for challenge in challenges: points += challenge.value
        team.score -= points        
        user.team = None
        db.session.commit()
        return True
    
    @classmethod
    def remove(cls, username:str=None, teamname:str=None) -> bool:
        if any([teamname == '', teamname is None, not cls.found(teamname=teamname)]): return False
        team:Team = cls.found(teamname=teamname)
        if len(team.members) > 0:
            if any([username == '', username is None, not User.found(username=username), team.leader_id != User.find_id(username=username)]): return False
            if not all([cls.kickout_member(username=u.username, teamname=teamname) for u in team.members]): return False
        team = cls.found(teamname=teamname)
        try:
            team.members.clear()
            team.solved_challenges.clear()
            db.session.delete(team)
            db.session.commit()
            return True
        except Exception as e:
            import traceback
            print(traceback.format_exc(e))
            db.session.rollback()
            return False
        
    @classmethod
    def update_leader(cls, newleader:str=None, teamname:str=None) -> bool:
        if any([newleader == '', newleader is None, teamname == '', teamname is None, not User.found(username=newleader.username), not cls.found(teamname=teamname)]): return False
        return cls.__leaderupdate(leader=newleader, teamname=teamname)
        
    @classmethod
    def challenges(cls, teamname:str=None) -> list:
        if any([teamname == '', teamname is None, not cls.found(teamname=teamname)]): return False
        team:Team = cls.found(teamname=teamname)
        return team.solved_challenges
    
    @classmethod
    def position(cls, teamname:str=None) -> int:
        if any([teamname == '', teamname is None, not cls.found(teamname=teamname)]): return False
        team:Team = cls.found(teamname=teamname)
        if not team.team_is_active or team.team_is_hidden: return 0
        teams:list['Team'] = cls.select()
        teams:list['Team'] = [t for t in teams if (t.team_is_hidden == False and t.team_is_active == True)]
        if len(teams) == 0: return False
        teams:list['Team'] = sorted(teams, key=lambda team: team.score, reverse=True)
        team_id = cls.find_id(teamname=teamname)
        team_rank = [team.id for team in teams].index(team_id) + 1
        return team_rank
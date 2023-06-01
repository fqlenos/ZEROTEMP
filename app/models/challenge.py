from app.extensions import db
from launchable.Launchable import Launchable
import datetime
from sqlalchemy.exc import IntegrityError

class Challenge(db.Model, Launchable):
    __tablename__ = 'challenges'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    challenge_is_hidden = db.Column(db.Boolean, nullable=False, default=True)
    is_multiflag = db.Column(db.Boolean, nullable=False, default=False)
    flag = db.Column(db.String(60), nullable=True)
    file = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=True)

    solved_by_users = db.relationship('User', secondary='user_challenge_link', backref=db.backref('solved_by_users', lazy='dynamic'), overlaps='solved_challenges,user_solvers')
    solved_by_teams = db.relationship('Team', secondary='team_challenge_link', backref=db.backref('solved_by_teams', lazy='dynamic'), overlaps='solved_challenges,team_solvers')

    def __init__(self, name:str, description:str, category:str, value:int, flag:str=None, challenge_is_hidden:bool=True, is_multiflag:bool=False, file:str=None, url:str=None) -> None:
        self.name = name
        self.value = value
        self.category = category
        self.description = description
        self.challenge_is_hidden = challenge_is_hidden
        self.is_multiflag = is_multiflag
        self.flag = flag
        self.file = file
        self.url = url

    def __repr__(self) -> str:
        return super().__repr__()

    def __str__(self) -> str:
        return str(self.name) 

    def __insert(self) -> bool:
        if self.__found(name=self.name): return False
        try: 
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError: 
            db.session.rollback()
            return False 
    
    @classmethod
    def __update(cls, name:str, value:int=0, description:str=None, category:str=None, challenge_is_hidden:bool=None, flag:str=None, is_multiflag:bool=None, file:str=None, url:str=None) -> bool:
        if all([name == '', name is None, not isinstance(value, int), description == '', description is None, category == '', category is None, challenge_is_hidden == '', challenge_is_hidden is None, flag == '', flag is None, is_multiflag == '', is_multiflag is None, file == '', file is None, url == '', url is None]) or not cls.found(name=name): return False
        
        challenge:Challenge = cls.found(name=name)
        challenge.value = value if value != 0 else challenge.value
        challenge.category = category if category is not None else challenge.category
        challenge.description = description if description is not None else challenge.description
        challenge.challenge_is_hidden = challenge_is_hidden if challenge_is_hidden is not None else challenge.challenge_is_hidden
        challenge.flag = flag if flag is not None else challenge.flag
        challenge.is_multiflag = is_multiflag if is_multiflag is not None else challenge.is_multiflag
        challenge.file = file if file is not None else challenge.file
        challenge.url = url if url is not None else challenge.url

        try: 
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            return False
    
    @classmethod
    def __found(cls, name:str=None) -> 'Challenge':
        if any([name is None, name == '']): return False
        found = cls.query.filter_by(name=name).first()
        if found is None: return False 
        return found

    @classmethod
    def __get_db_id(cls, name:str=None) -> int:
        if any([name is None, name == '', not cls.found(name=name)]): return 0
        challenge:Challenge = cls.__found(name=name)
        return challenge.id
        
    @classmethod
    def add_challenge(cls, name:str=None, description:str=None, category:str=None, value:int=0, hidden:bool=True, is_multiflag:bool=False, flag:str=None, file:str=None, url:str=None) -> bool:
        if any([name == '', name is None, value == 0, value is None, value == '', category is None, category == '', not isinstance(hidden, bool), not isinstance(is_multiflag, bool)]): return False
        return cls(name=name, description=description, category=category, value=value, challenge_is_hidden=hidden, is_multiflag=is_multiflag, flag=flag, file=file, url=url).__insert()

    @classmethod
    def verify(cls, name:str=None, password:str=None) -> bool:
        if any([name == '', name is None, password == '', password is None]): return False
        return cls.__verify(name=name, password=password)
    
    @classmethod
    def update(cls, name:str, value:int=0, description:str=None, category:str=None, challenge_is_hidden:bool=None, flag:str=None, is_multiflag:bool=None, file:str=None, url:str=None) -> bool:
        return cls.__update(name=name, value=value, description=description, category=category, challenge_is_hidden=challenge_is_hidden, flag=flag, is_multiflag=is_multiflag, file=file, url=url)

    @classmethod
    def find_id(cls, name:str=None) -> int:
        if name == '' or name is None: return False
        return cls.__get_db_id(name=name)

    @classmethod
    def found(cls, name:str=None) -> 'Challenge':
        if name == '' or name is None: return False
        return cls.__found(name=name)
    
    @classmethod
    def remove(cls, name:str=None) -> bool:
        if any([name == '', name is None, not cls.found(name=name)]): return False
        challenge:Challenge = cls.found(name=name)
        try:
            challenge.solved_by_users.clear()
            challenge.solved_by_teams.clear()
            db.session.delete(challenge)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            db.session.rollback()
            return False
    
    @classmethod
    def get_challenges_count_by_category(cls) -> dict:
        challenges_counts = {}
        challenges: list[Challenge] = [challenge for challenge in cls.select() if not challenge.challenge_is_hidden]
        for challenge in challenges:
            if challenge.category in challenges_counts: continue
            num_challenges_in_category = len([challenge for challenge in cls.query.filter_by(category=challenge.category).all() if not challenge.challenge_is_hidden])
            challenges_counts[challenge.category] = num_challenges_in_category
        return challenges_counts

    @classmethod
    def get_solves_count_by_challenges(cls) -> dict:
        solves_counts = {}
        challenges:list[Challenge] = [challenge for challenge in cls.select() if not challenge.challenge_is_hidden]
        for challenge in challenges:
            solves = len([user for user in challenge.solved_by_users if not user.team])
            solves += len(challenge.solved_by_teams)
            solves_counts[challenge.name] = solves
        return solves_counts
    
    @classmethod
    def get_solves_count_by_category(cls, foruser:bool, username:str=None, teamname:str=None) -> dict:
        solves_counts = {}
        challenges:list[Challenge] = [challenge for challenge in cls.select() if not challenge.challenge_is_hidden]
        for challenge in challenges:
            solves = 0
            if foruser: solves = len([user for user in challenge.solved_by_users if user.username == username])
            else: solves = len([team for team in challenge.solved_by_teams if team.teamname == teamname])
            if challenge.category in solves_counts: solves_counts[challenge.category] += solves
            else: solves_counts[challenge.category] = solves
        return dict(sorted(solves_counts.items()))
    
    @classmethod
    def __get_solves_count_by_user(cls, users:list) -> dict:
        solves_count = {}
        challenges:list[Challenge] = [challenge for challenge in cls.select() if not challenge.challenge_is_hidden]
        for user in users:
            solves_count[user.username] = {}
            for challenge in challenges:
                if user not in challenge.solved_by_users: continue
                if challenge.category in solves_count[user.username]: solves_count[user.username][challenge.category] += 1
                else: solves_count[user.username][challenge.category] = 1
        return solves_count
    
    @classmethod
    def __get_solves_count_by_team(cls, teams:list) -> dict:
        solves_count = {}
        challenges:list[Challenge] = [challenge for challenge in cls.select() if not challenge.challenge_is_hidden]
        for team in teams:
            solves_count[team.teamname] = {}
            for challenge in challenges:
                if team not in challenge.solved_by_teams: continue
                if challenge.category in solves_count[team.teamname]: solves_count[team.teamname][challenge.category] += 1
                else: solves_count[team.teamname][challenge.category] = 1
        return solves_count

    @classmethod
    def get_users_average_solves_by_category(cls, users:list) -> dict:
        average_count = {}
        user_count = {}
        solves_count = cls.__get_solves_count_by_user(users=users)
        challenges_count = cls.get_challenges_count_by_category()
        categories:list[str] = list(set([challenge.category for challenge in [challenge for challenge in cls.select() if not challenge.challenge_is_hidden]]))
        for category in categories:
            average_count[category] = 0
            user_count[category] = 0
            for _, categories in solves_count.items():
                if category in categories:
                    user_count[category] += 1
                    average_count[category] += categories[category]
            if user_count[category] > 0: average_count[category] = ((average_count[category]/challenges_count[category])/user_count[category]) * challenges_count[category]
            else: average_count[category] = 0
        return average_count

    @classmethod
    def get_teams_average_solves_by_category(cls, teams:list) -> dict:
        average_count = {}
        team_count = {}
        solves_count = cls.__get_solves_count_by_team(teams=teams)
        challenges_count = cls.get_challenges_count_by_category()
        categories:list[str] = list(set([challenge.category for challenge in [challenge for challenge in cls.select() if not challenge.challenge_is_hidden]]))
        for category in categories:
            average_count[category] = 0
            team_count[category] = 0
            for _, categories in solves_count.items():
                if category in categories:
                    team_count[category] += 1
                    average_count[category] += categories[category]
            if team_count[category] > 0: average_count[category] = ((average_count[category]/challenges_count[category])/team_count[category]) * challenges_count[category]
            else: average_count[category] = 0
        return average_count   
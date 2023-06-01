from app.extensions import db
from launchable.Launchable import Launchable
from sqlalchemy.exc import IntegrityError
import datetime

from .user import User
from .challenge import Challenge
from .team import Team
from .team_challenge_link import TeamChallengeLink
from .flag import MultiFlag

class UserChallengeLink(db.Model, Launchable):
    __tablename__ = 'user_challenge_link'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), primary_key=True)

    def __init__(self, user_id:int=0, challenge_id:int=0) -> None:
        self.user_id = user_id
        self.challenge_id = challenge_id
    
    def add_challenge(self, input_flag:str='err') -> bool:
        flag_ok = False
        user:User = User.select_by_id(id=self.user_id)
        if any([not bool(user), not user.user_is_active, user.user_is_hidden]): return False
        
        challenge:Challenge = Challenge.select_by_id(id=self.challenge_id)
        if not challenge.is_multiflag:
            if input_flag == challenge.flag:
                flag_ok = True
        else:
            multiflags:list[MultiFlag] = MultiFlag.select()
            for multiflag in multiflags:
                if all([multiflag.challenge_id == challenge.id, multiflag.is_used == False, multiflag.flag == input_flag]):
                    MultiFlag.update(challenge_id=challenge.id, flag=input_flag, is_used=True)
                    flag_ok = True
                    break

        if flag_ok:

            if user.team is not None:
                added = TeamChallengeLink(team_id=user.team.id, challenge_id=self.challenge_id).add_challenge()
                if not added: return False

                team:Team = Team.select_by_id(id=user.team.id)
                team.score = int(team.score) + int(challenge.value)
        
            user.score = int(user.score) + int(challenge.value)
            user.last_flag = datetime.datetime.now()
            
            try:
                db.session.add(self)
                db.session.commit()
                return True
            except IntegrityError: 
                db.session.rollback()

        return False
    
    @classmethod
    def remove_challenge(cls, username:str=None, challengename:str=None) -> bool:
        if any([username == '', username is None, challengename == '', challengename is None, not User.found(username=username), not Challenge.found(name=challengename)]): return False
        user:User = User.found(username=username)
        challenge:Challenge = Challenge.found(name=challengename)
        link = cls.query.filter_by(user_id=user.id, challenge_id=challenge.id).first()
        if not link: return False
        try:
            points = 0
            challenges:list['Challenge'] = user.solved_challenges
            if challenge.id in [c.id for c in challenges]: points += challenge.value
            user.score -= points
            db.session.delete(link)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
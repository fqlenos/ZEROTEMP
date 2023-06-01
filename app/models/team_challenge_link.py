from app.extensions import db
from launchable.Launchable import Launchable
from sqlalchemy.exc import IntegrityError
from app.models.challenge import Challenge
from app.models.team import Team
from app.models.user import User

class TeamChallengeLink(db.Model, Launchable):
    __tablename__ = 'team_challenge_link'
    
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), primary_key=True)

    def __init__(self, team_id:int=0, challenge_id:int=0) -> None:
        self.team_id = team_id
        self.challenge_id = challenge_id
    
    def add_challenge(self) -> bool:
        try: 
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError: 
            db.session.rollback()
            return False
    
    @classmethod
    def remove_challenge(cls, teamname:str=None, challengename:str=None) -> bool:
        if any([teamname == '', teamname is None, challengename == '', challengename is None, not Team.found(teamname=teamname), not Challenge.found(name=challengename)]): return False
        team:Team = Team.found(teamname=teamname)
        challenge:Challenge = Challenge.found(name=challengename)
        link = cls.query.filter_by(team_id=team.id, challenge_id=challenge.id).first()
        if not link: return False
        try:
            points = 0
            members:list[User] = team.members
            for member in members: points += member.score
            team.score = points
            db.session.delete(link)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            db.session.rollback()
            return False
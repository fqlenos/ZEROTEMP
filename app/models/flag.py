from app.extensions import db
from launchable.Launchable import Launchable
from sqlalchemy.exc import IntegrityError
import secrets

class MultiFlag(db.Model, Launchable):
    __tablename__ = 'flags'
    
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    is_used = db.Column(db.Boolean, nullable=False, default=False)
    url = db.Column(db.Text, nullable=True)
    flag = db.Column(db.String(60), nullable=False)
    is_downloaded = db.Column(db.Boolean, nullable=False, default=False)

    challenge = db.relationship('Challenge', backref=db.backref('flags', lazy='dynamic'))
    #user = db.relationship('User', backref=db.backref('flags', lazy='dynamic'))

    def __init__(self, url:str, challenge_id:int=0, is_used:bool=False, is_downloaded:bool=False) -> None:
        self.challenge_id = challenge_id
        #self.user_id = user_id
        self.is_used = bool(is_used)
        self.url = url
        self.flag = f'zero{{{secrets.token_hex(32 // 2)}}}'
        self.is_downloaded = bool(is_downloaded)

    def add_flag(self) -> bool:
        try: 
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    @classmethod
    def __update(cls, challenge_id:int, is_used:bool=None, is_downloaded:bool=None, flag:str='', url:str=None) -> bool:
        if all([not isinstance(challenge_id, int), is_used is None, is_downloaded is None, flag == '', url is None, url == '']): return False

        multiflag:MultiFlag = cls.found(challenge_id=challenge_id, flag=flag)
        if not multiflag: return False

        multiflag.is_used = is_used if is_used is not None else multiflag.is_used
        multiflag.is_downloaded = is_downloaded if is_downloaded is not None else multiflag.is_downloaded
        multiflag.url = url if url is not None else multiflag.url

        try:
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            return False

    @classmethod
    def update(cls, challenge_id:int, is_used:bool=None, is_downloaded:bool=None, flag:str='', url:str=None) -> bool:
        if all([not isinstance(challenge_id, int), is_used is None, is_downloaded is None, flag == '', url is None, url == '']): return False
        return cls.__update(challenge_id=challenge_id, is_used=is_used, flag=flag, is_downloaded=is_downloaded, url=url)

    @classmethod
    def __found(cls, challenge_id:int=None, flag:str=None) -> 'MultiFlag':
        if any([not isinstance(challenge_id, int), challenge_id is None, challenge_id == '', flag == '', flag is None]): return False
        found = cls.query.filter_by(challenge_id=challenge_id, flag=flag).first()
        if found is None: return False 
        return found
    
    @classmethod
    def found(cls, challenge_id:int=None, flag:str=None) -> 'MultiFlag':
        if any([not isinstance(challenge_id, int), challenge_id is None, challenge_id == '', flag == '', flag is None]): return False
        return cls.__found(challenge_id=challenge_id, flag=flag)
    
    @classmethod
    def remove_challenge(cls, challenge_id:int) -> bool:
        try:
            cls.query.filter_by(challenge_id=challenge_id).delete()
            db.session.commit()
            return True
        except Exception as e:
            import traceback
            print(traceback.format_exc(e))
            db.session.rollback()
            return False        
    
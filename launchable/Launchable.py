from app.extensions import db
from sqlalchemy.orm import Query

class Launchable:
    def insert(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError
    
    def run(self):
        raise NotImplementedError
    
    def start(self):
        raise NotImplementedError
    
    def stop(self):
        raise NotImplementedError
    
    """     
    def to_dict(self) -> dict:
        attrs = [a for a in dir(self) if not a.startswith('_') and not callable(getattr(self, a)) and a != 'query' and a != 'registry' and a != 'metadata']
        return { a: getattr(self, a) for a in attrs } 
    """
    def to_dict(self):
        attrs = [a for a in dir(self) if not a.startswith('_') and not callable(getattr(self, a)) and a != 'query' and a != 'registry' and a != 'metadata']
        result = {}
        for a in attrs:
            value = getattr(self, a)
            if isinstance(value, db.Model):
                result[a] = value.id
            elif isinstance(value, Query):
                result[a] = [obj.id for obj in value.all()]
            elif isinstance(value, list):
                result[a] = [v.id if isinstance(v, db.Model) else v for v in value]
            else:
                result[a] = value
        return result

    @classmethod
    def select(cls) -> list:
        if hasattr(cls, '__tablename__'):
            select = cls.query.all()
            return select
        return None

    @classmethod
    def select_by_id(cls, id:int=-1):
        if hasattr(cls, '__tablename__'):
            if id == -1: return False
            found = cls.query.filter_by(id=id).first()
            if found is None: return False
            return found
        return False
        
    @classmethod
    def count(cls) -> int:
        if hasattr(cls, '__tablename__'):
            total = cls.select()
            if 'User' in str(cls): total = [t for t in total if (not t.user_is_hidden and t.user_is_active)]
            if 'Team' in str(cls): total = [t for t in total if (not t.team_is_hidden and t.team_is_active)]
            if 'Challenge' in str(cls): total = [t for t in total if not t.challenge_is_hidden]
            return len(total)
        return 0
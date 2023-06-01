from app.extensions import db
from launchable.Launchable import Launchable
from sqlalchemy.exc import IntegrityError


class CTF(db.Model, Launchable):
    __tablename__ = 'ctf'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    edition = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    link_one_name = db.Column(db.Text, nullable=True)
    link_one_name_href = db.Column(db.Text, nullable=True)
    link_two_name = db.Column(db.Text, nullable=True)
    link_two_name_href = db.Column(db.Text, nullable=True)
    telegram_group_link = db.Column(db.Text, nullable=True)
    discord_group_link = db.Column(db.Text, nullable=True)
    sponsors = db.Column(db.Text, nullable=True)
    custom_title = db.Column(db.Text, nullable=True)
    custom_description = db.Column(db.Text, nullable=True)
    custom_btn_name = db.Column(db.Text, nullable=True)
    custom_btn_href = db.Column(db.Text, nullable=True)
    ctf_active = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name:str, edition:str='', description:str='', link_one_name:str='', link_one_name_href:str='', link_two_name:str='', link_two_name_href:str='', telegram_group_link:str='', discord_group_link:str='', sponsors:str='', custom_title:str='', custom_description:str='', custom_btn_name:str='', custom_btn_href:str='', ctf_active:bool=False):
        self.name = name
        self.edition = edition
        self.description = description
        self.link_one_name = link_one_name
        self.link_one_name_href = link_one_name_href
        self.link_two_name = link_two_name
        self.link_two_name_href = link_two_name_href  
        self.telegram_group_link = telegram_group_link 
        self.discord_group_link = discord_group_link
        self.sponsors = sponsors
        self.custom_title = custom_title
        self.custom_description = custom_description
        self.custom_btn_name = custom_btn_name
        self.custom_btn_href = custom_btn_href
        self.ctf_active = ctf_active 
    
    def __repr__(self) -> str:
        return super().__repr__()

    def __str__(self) -> str:
        return str(self.name)
    
    @classmethod
    def __update(cls, name:str=None, edition:str=None, description:str=None, link_one_name:str=None, link_one_name_href:str=None, link_two_name:str=None, link_two_name_href:str=None, telegram_group_link:str=None, discord_group_link:str=None, sponsors:str=None, custom_title:str=None, custom_description:str=None, custom_btn_name:str=None, custom_btn_href:str=None, ctf_active:bool=None) -> bool:
        if all([name is None,  edition is None,  description is None,  link_one_name is None,  link_one_name_href is None,  link_two_name is None,  link_two_name_href is None,  telegram_group_link is None,  discord_group_link is None,  sponsors is None,  custom_title is None,  custom_description is None,  custom_btn_name is None, custom_btn_href is None, not isinstance(ctf_active, bool)]): return False

        ctf:CTF = cls.select()[0]
        ctf.name = name if name is not None and name != '' else ctf.name
        ctf.edition = edition if edition is not None and edition != '' else ctf.edition
        ctf.description = description if description is not None and description != '' else ctf.description
        ctf.link_one_name = link_one_name if link_one_name is not None and link_one_name != '' else ctf.link_one_name
        ctf.link_one_name_href = link_one_name_href if link_one_name_href is not None and link_one_name_href != '' else ctf.link_one_name_href
        ctf.link_two_name = link_two_name if link_two_name is not None and link_two_name != '' else ctf.link_two_name
        ctf.link_two_name_href = link_two_name_href if link_two_name_href is not None and link_two_name_href != '' else ctf.link_two_name_href
        ctf.telegram_group_link = telegram_group_link if telegram_group_link is not None and telegram_group_link != '' else ctf.telegram_group_link
        ctf.discord_group_link = discord_group_link if discord_group_link is not None and discord_group_link != '' else ctf.discord_group_link
        ctf.sponsors = sponsors if sponsors is not None and sponsors != '' else ctf.sponsors
        ctf.custom_title = custom_title if custom_title is not None and custom_title != '' else ctf.custom_title
        ctf.custom_description = custom_description if custom_description is not None and custom_description != '' else ctf.custom_description
        ctf.custom_btn_name = custom_btn_name if custom_btn_name is not None and custom_btn_name != '' else ctf.custom_btn_name
        ctf.custom_btn_href = custom_btn_href if custom_btn_href is not None and custom_btn_href != '' else ctf.custom_btn_href
        ctf.ctf_active = ctf_active if ctf_active is not None and ctf_active != '' else ctf.ctf_active

        try:
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            return False

    def __insert(self) -> bool:
        try: 
            db.session.add(self)
            db.session.commit()
            return True
        except IntegrityError and Exception: 
            db.session.rollback()
            return False 

    @classmethod
    def __found(cls, name:str=None) -> 'CTF':
        if any([name is None, name == '']): return False
        found = cls.query.filter_by(name=name).first()
        if found is None: return False 
        return found
    
    @classmethod
    def found(cls, name:str=None) -> 'CTF':
        if name == '' and name is None: return False
        return cls.__found(name=name)
    
    @classmethod
    def update(cls, name:str=None, edition:str=None, description:str=None, link_one_name:str=None, link_one_name_href:str=None, link_two_name:str=None, link_two_name_href:str=None, telegram_group_link:str=None, discord_group_link:str=None, sponsors:str=None, custom_title:str=None, custom_description:str=None, custom_btn_name:str=None, custom_btn_href:str=None, ctf_active:bool=None) -> bool:
        if all([name is None,  edition is None,  description is None,  link_one_name is None,  link_one_name_href is None,  link_two_name is None,  link_two_name_href is None,  telegram_group_link is None,  discord_group_link is None,  sponsors is None,  custom_title is None,  custom_description is None,  custom_btn_name is None,  custom_btn_href is None, not isinstance(ctf_active, bool)]): return False
        return cls.__update(name, edition, description, link_one_name, link_one_name_href, link_two_name, link_two_name_href, telegram_group_link, discord_group_link, sponsors, custom_title, custom_description, custom_btn_name, custom_btn_href, ctf_active)
    
    @classmethod
    def add(cls, name:str) -> bool:
        if name == '': return False
        try:
            if len(cls.select()) > 0: return False
        except: pass
        if cls.found(name=name): return False
        return cls(name=name).__insert()
   
from wtforms import Form, StringField, PasswordField, validators, BooleanField, IntegerField, SelectField, TextAreaField, MultipleFileField
from flask_wtf.file import FileField, FileAllowed

class LoginUser(Form):
    login_username = StringField('Username', validators=[validators.Length(min=4, max=30)], render_kw={"class": "form-control"})
    login_password = PasswordField('Password', validators=[validators.Length(min=5, max=40)], render_kw={"class": "form-control"})

class RegisterUser(Form):
    register_username = StringField('Username', validators=[validators.Length(min=4, max=30)], render_kw={"class": "form-control"})
    register_password = PasswordField('Password', validators=[validators.Length(min=5, max=40)], render_kw={"class": "form-control"})
    register_confirm_password = PasswordField('Confirm Password', validators=[validators.EqualTo('register_password', message='Passwords do not match')], render_kw={"class": "form-control"})

class CreateUser(Form):
    username = StringField('Username', validators=[validators.Length(min=4, max=30)], render_kw={"class": "form-control"})
    password = PasswordField('Password', validators=[validators.Length(min=5, max=40)], render_kw={"class": "form-control"})
    confirm_password = PasswordField('Confirm Password', validators=[validators.EqualTo('password', message='Passwords do not match')], render_kw={"class": "form-control"})
    user_is_hidden = BooleanField('User is Hidden', validators=[], render_kw={"class": "form-check-input"})
    user_is_active = BooleanField('User is Active', validators=[], render_kw={"class": "form-check-input", "checked": ""})
    user_is_admin = BooleanField('User is ZeroAdmin', validators=[], render_kw={"class": "form-check-input"})
    icon = FileField('User Icon', validators=[FileAllowed(['jpeg', 'jpg', 'png'], 'Images only! (jpeg, jpg, png)')], render_kw={"accept": "image/jpeg, image/jpg, image/png"}) 

class ManageUser(Form):
    user_select = SelectField('Select User', choices=[], render_kw={"class": "form-select selectpicker"})
    user_is_hidden = BooleanField('User is Hidden', validators=[], render_kw={"class": "form-check-input"})
    user_is_active = BooleanField('User is Active', validators=[], render_kw={"class": "form-check-input", "checked": ""})
    user_is_admin = BooleanField('User is ZeroAdmin', validators=[], render_kw={"class": "form-check-input"})
    user_is_banned = BooleanField('User is Banned', validators=[], render_kw={"class": "form-check-input"})
    mng_password = PasswordField('Admin Password', validators=[validators.InputRequired(message='Your password is required.'), validators.Length(min=4, max=30)], render_kw={"class": "form-control"})
    icon = FileField('User Icon', validators=[FileAllowed(['jpeg', 'jpg', 'png'], 'Images only! (jpeg, jpg, png)')], render_kw={"accept": "image/jpeg, image/jpg, image/png"})

    def __init__(self, users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(username, username) for username in users]
        self.user_select.choices = choices

class RemoveUser(Form):
    user_select = SelectField('Select User', choices=[], render_kw={"class": "form-select"})
    remove_password = PasswordField('Admin Password', validators=[validators.InputRequired(message='Your password is required.'), validators.Length(min=4, max=30)], render_kw={"class": "form-control"})

    def __init__(self, users, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(username, username) for username in users]
        self.user_select.choices = choices

class CreateTeam(Form):
    leader = StringField('Team Leader', validators=[validators.Length(min=4, max=30)], render_kw={"class": "form-control"})
    teamname = StringField('Team Name', validators=[validators.Length(min=4, max=30)], render_kw={"class": "form-control"})
    password = PasswordField('Password', validators=[validators.Length(min=5, max=40)], render_kw={"class": "form-control"})
    confirm_password = PasswordField('Confirm Password', validators=[validators.EqualTo('password', message='Passwords do not match')], render_kw={"class": "form-control"})
    team_is_hidden = BooleanField('Team is Hidden', validators=[], render_kw={"class": "form-check-input"})
    team_is_active = BooleanField('Team is Active', validators=[], render_kw={"class": "form-check-input", "checked": ""})

class ManageTeam(Form):
    team_select = SelectField('Select Team', choices=[], render_kw={"class": "form-select"})
    team_is_hidden = BooleanField('Team is Hidden', validators=[], render_kw={"class": "form-check-input"})
    team_is_active = BooleanField('Team is Active', validators=[], render_kw={"class": "form-check-input", "checked": ""})
    mng_password = PasswordField('Admin Password', validators=[validators.InputRequired(message='Your password is required.'), validators.Length(min=4, max=30)], render_kw={"class": "form-control"})

    def __init__(self, teams, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(teamname, teamname) for teamname in teams]
        self.team_select.choices = choices

class RemoveTeam(Form):
    team_select = SelectField('Select Team', choices=[], render_kw={"class": "form-select"})
    remove_password = PasswordField('Admin Password', validators=[validators.InputRequired(message='Your password is required.'), validators.Length(min=4, max=30)], render_kw={"class": "form-control"})

    def __init__(self, teams, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(teamname, teamname) for teamname in teams]
        self.team_select.choices = choices

class CreateChallenge(Form):
    challengename = StringField('Challenge Name', validators=[validators.Length(min=4, max=50)], render_kw={"class": "form-control"})
    description = TextAreaField('Description', validators=[validators.Length(max=255)], render_kw={"class": "form-control"})
    category = StringField('Category', validators=[validators.Length(min=2, max=15)], render_kw={"class": "form-control"})
    value = IntegerField('Challenge Value', validators=[validators.NumberRange(min=1)], render_kw={"class": "form-control"})
    challenge_is_hidden = BooleanField('Challenge is Hidden', validators=[], render_kw={"class": "form-check-input", "checked": ""})
    is_multiflag = BooleanField('Challenge with multiflag', validators=[], render_kw={"class": "form-check-input"})
    file = FileField('Add ZIP', validators=[FileAllowed(['zip'], 'ZIP files only! (.zip)')], render_kw={"accept": "zip,application/octet-stream,application/zip,application/x-zip,application/x-zip-compressed"})
    flag = StringField('Flag', validators=[validators.Length(max=60, message='Max 60 chars long.')], render_kw={"class": "form-control"})
    url = StringField('Website URL', validators=[validators.Length(max=60, message='Max 60 chars long.')], render_kw={"class": "form-control"})
   
class ManageChallenge(Form):
    challenge_select = SelectField('Select Challenge', choices=[], render_kw={"class": "form-select"})
    challengename = StringField('Challenge Name', validators=[validators.Length(max=50)], render_kw={"class": "form-control"})
    description = TextAreaField('Description', validators=[validators.Length(max=255)], render_kw={"class": "form-control"})
    category = StringField('Category', validators=[validators.Length(max=15)], render_kw={"class": "form-control"})
    value = IntegerField('Challenge Value', validators=[], render_kw={"class": "form-control"})
    challenge_is_hidden = BooleanField('Challenge is Hidden', validators=[], render_kw={"class": "form-check-input", "id": "challenge_is_hidden"})
    is_multiflag = BooleanField('Challenge with multiflag', validators=[], render_kw={"class": "form-check-input", "id": "is_multiflag"})
    file = FileField('Add ZIP', validators=[FileAllowed(['zip'], 'ZIP files only! (.zip)')], render_kw={"accept": "zip,application/octet-stream,application/zip,application/x-zip,application/x-zip-compressed"})
    flag = StringField('Flag', validators=[validators.Length(max=60, message='Max 60 chars long.')], render_kw={"class": "form-control"})
    url = StringField('Website URL', validators=[validators.Length(max=60, message='Max 60 chars long.')], render_kw={"class": "form-control"})
    mng_password = PasswordField('Admin Password', validators=[validators.InputRequired(message='Your password is required.'), validators.Length(min=4, max=30)], render_kw={"class": "form-control"})

    def __init__(self, challenges:list=[], challenge=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(challenges) > 0:
            choices = [(challenge.name, f'[{str(challenge.category).upper()}] {challenge.name}') for challenge in challenges]
            self.challenge_select.choices = choices
        if challenge is not None:
            choices = [('Empty', 'Empty')]
            self.challenge_select.choices = choices
            self.challenge_select.data = 'Empty'
            self.challengename.render_kw["value"] = challenge.name if challenge.name is not None else ''
            self.description.data = challenge.description if challenge.description is not None else ''
            self.category.render_kw["value"] = challenge.category if challenge.category is not None else ''
            if bool(challenge.challenge_is_hidden): 
                self.challenge_is_hidden.render_kw["checked"] = True
            if bool(challenge.is_multiflag):
                self.is_multiflag.render_kw["checked"] = True
            self.url.render_kw["value"] = challenge.url if challenge.url is not None else ''
            self.flag.render_kw["value"] = challenge.flag if challenge.flag is not None else ''

class RemoveChallenge(Form):
    challenge_select = SelectField('Select Challenge', choices=[], render_kw={"class": "form-select"})
    remove_password = PasswordField('Admin Password', validators=[validators.InputRequired(message='Your password is required.'), validators.Length(min=4, max=30)], render_kw={"class": "form-control"})

    def __init__(self, challenges:list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(challenge.name, f'[{str(challenge.category).upper()}] {challenge.name}') for challenge in challenges]
        self.challenge_select.choices = choices

class SubmitFlag(Form):
    flag = StringField('Submit Flag', validators=[validators.Length(min=1, max=60, message='Flag must be between 1 and 60 chars long.')], render_kw={"class": "form-control", "style": "width: 100%"})

class ManageLandingPage(Form):
    ctf_name = StringField('CTF Name', validators=[validators.Length(max=30)], render_kw={"class": "form-control"})
    ctf_editon = StringField('Edition', render_kw={"class": "form-control"})
    ctf_description = TextAreaField('Description', validators=[validators.Length(max=255, message="Description length between 20-255 chars.")], render_kw={"class": "form-control"})
    ctf_link_one = StringField('Link One Name', render_kw={"class": "form-control"})
    ctf_link_one_href = StringField('Link One', render_kw={"class": "form-control"})
    ctf_link_two = StringField('Link Two', render_kw={"class": "form-control"})
    ctf_link_two_href = StringField('Link Two Name', render_kw={"class": "form-control"})
    ctf_active = BooleanField('Allow User Registration', validators=[], render_kw={"class": "form-check-input"})
    mng_password = PasswordField('Admin Password', validators=[validators.InputRequired(message='Your password is required.'), validators.Length(min=4, max=30)], render_kw={"class": "form-control", "id": "floatingMngPass"})

    def __init__(self, ctf, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctf_name.render_kw["value"] = ctf.name
        self.ctf_editon.render_kw["value"] = ctf.edition
        self.ctf_description.data = ctf.description
        self.ctf_link_one.render_kw["value"] = ctf.link_one_name
        self.ctf_link_one_href.render_kw["value"] = ctf.link_one_name_href
        if bool(ctf.ctf_active):
            self.ctf_active.render_kw["checked"] = True

class ManageSocial(Form):
    telegram_group_link = StringField('Telegram Group Link', render_kw={"class": "form-control"})
    discord_group_link = StringField('Discord Group Link', render_kw={"class": "form-control"})
    ctf_custom_title = StringField('Custom Title', render_kw={"class": "form-control"})
    ctf_custom_description = TextAreaField('Custom Description', validators=[validators.Length(max=255)], render_kw={"class": "form-control"})
    ctf_custom_link = StringField('Custom Button Name', render_kw={"class": "form-control"})
    ctf_custom_link_href = StringField('Custom Button Link', render_kw={"class": "form-control"})
    ctf_sponsors = MultipleFileField('Add New Sponsors', validators=[FileAllowed(['jpeg', 'jpg', 'png'], 'Images only! (jpeg, jpg, png)')], render_kw={"accept": "image/jpeg, image/jpg, image/png"})
    social_password = PasswordField('Admin Password', validators=[validators.InputRequired(message='Your password is required.'), validators.Length(min=4, max=30)], render_kw={"class": "form-control"})
    custom_ctfs = []

    def __init__(self, ctf, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.telegram_group_link.render_kw["value"] = ctf.telegram_group_link
        self.discord_group_link.render_kw["value"] = ctf.discord_group_link
        self.ctf_custom_title.render_kw["value"] = ctf.custom_title
        self.ctf_custom_description.data = ctf.custom_description
        self.ctf_custom_link.render_kw["value"] = ctf.custom_btn_name
        self.ctf_custom_link_href.render_kw["value"] = ctf.custom_btn_href
        self.custom_ctfs = []
        for sponsor in ctf.sponsors.split('::::::::'):
            self.custom_ctfs.append(sponsor)
            setattr(self, sponsor, BooleanField(sponsor, validators=[], render_kw={"class": "form-check-input", "checked": ""}))
        set(list(self.custom_ctfs))

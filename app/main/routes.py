from flask import render_template, request, redirect, url_for, abort
from flask_login import current_user, login_user, logout_user, login_required
import datetime

from app.forms.forms import LoginUser, RegisterUser
from zerotemp import __description__, __app_name__, __version__
from app.models.ctf import CTF
from config import CTFNAME

from flask import Blueprint
bp = Blueprint('main', __name__)

from app.models.user import User
from app.models.team import Team
from app.models.challenge import Challenge
from app.models.user_challenge_link import UserChallengeLink
from app.models.flag import MultiFlag
from app.extensions import cache, db

@bp.route('/populate')
def populate():

    users = User.select()
    admins = []
    if len(users) > 0:
        admins = [user for user in User.select() if user.user_is_admin]
        if not current_user.is_authenticated and len(admins) > 0: return abort(404)
        if not current_user.user_is_admin and len(admins) > 0: return abort(404)        
    
    db.drop_all()
    db.create_all()

    from names_generator import generate_name
    import random
    for i in range(19):
        username = generate_name(style='underscore')
        User.add_user(username=username, password='password')

    users:list[User] = User.select()
    for i in range(4):
        teamname = generate_name(style='capital')
        Team.add_team(teamname=teamname, password='password', username=users[i].username)
    
    teams:list[Team] = Team.select()
    for i in users[7:18]:
        user = random.choice(users)
        team = random.choice(teams)
        Team.add_member(teamname=team.teamname, username=user.username)

    Challenge.add_challenge(name='Misc or miscellaneus part 1', description='Misc as way or life', category='misc', value='300', hidden=False, flag='flag')
    Challenge.add_challenge(name='Misc or miscellaneus part 2', description='Misc as way or life', category='misc', value='400', hidden=False, flag='flag')
    Challenge.add_challenge(name='Misc or miscellaneus part 3', description='Misc as way or life', category='misc', value='500', hidden=False, flag='flag')
    Challenge.add_challenge(name='Unhackeable web', description='Hack me if you can :)', category='web', value='500', hidden=False, flag='flag')
    Challenge.add_challenge(name='This is pwneable, or not', description='Are you sure I\'m pwneable?', category='pwn', value='600', hidden=False, flag='flag')
    Challenge.add_challenge(name='Wow, is this your executable?', description='Come on...', category='pwn', value='100', hidden=False, flag='flag')

    challenges:list[Challenge] = Challenge.select()
    for i in range(0, len(users)+1):
        user = random.choice(users)
        challenge = random.choice(challenges)
        UserChallengeLink(user_id=user.id, challenge_id=challenge.id).add_challenge(input_flag='flag')
    
    User.add_user(username='4nimanegra', password='password')
    Team.add_team(teamname='TLM Hackers', password='password', username='4nimanegra')
    user_id = User.find_id(username='4nimanegra')
    challenges_length = len(challenges)+1
    for i in range(1, challenges_length):
        UserChallengeLink(user_id=user_id, challenge_id=i).add_challenge(input_flag='flag')

    User.add_user(username='admin', password='admin', admin=True, hidden=True)
    CTF.add(name=CTFNAME)

    return redirect(url_for('main.logout'))

@bp.route('/')
def landing():

    ctfs:list[CTF] = CTF.select()
    ctf:CTF = ctfs[0]
    
    context = {
        'title': ctf.name if ctf.name is not None else __app_name__,
        'ctf_name': ctf.name if ctf.name is not None else __app_name__,
        'ctf_edition': ctf.edition,
        'ctf_description': ctf.description,
        'ctf_link_one': ctf.link_one_name,
        'ctf_link_one_href': ctf.link_one_name_href,
        'ctf_link_two': ctf.link_two_name,
        'ctf_link_two_href': ctf.link_two_name_href,
        'custom_title': ctf.custom_title,
        'custom_description': ctf.custom_description,
        'custom_btn': ctf.custom_btn_name,
        'custom_btn_href': ctf.custom_btn_href,
        'discord_group_link': ctf.discord_group_link,
        'telegram_group_link': ctf.telegram_group_link,
        'ctf_link_one': ctf.link_one_name,
        'has_sponsors': True if len(ctf.sponsors.split('::::::::')) > 0 and ctf.sponsors.split('::::::::')[0] != '' else False,
        'sponsors': ctf.sponsors.split('::::::::')

    }

    if current_user.is_authenticated: return redirect(url_for('main.home'))

    return render_template('landing.html', **context)

@bp.route('/home')
@cache.cached(timeout=5)
@login_required
def home():
    username = current_user.username
    users_count:int = User.count()
    user_position:int = User.position(username=username)
    user:User = User.found(username=username)
    user_solves:dict = Challenge.get_solves_count_by_category(foruser=True, username=username)
    user_has_solves = True if any(user_solves.values()) else False
    user_average:dict = Challenge.get_users_average_solves_by_category(users=User.select())
    user_score:int = user.score
    teams_count:int = Team.count()
    team:Team = user.team
    has_team:bool = bool(team)
    if has_team:
        teamname = team.teamname
        team_solves:dict = Challenge.get_solves_count_by_category(foruser=False, teamname=teamname)
        team_average:dict = Challenge.get_teams_average_solves_by_category(teams=Team.select())
        team_position:int = Team.position(teamname=teamname)
        team_score:int = team.score
    else: team_solves = team_average = teamname = team_position = team_score = None
    category_challenges = Challenge.get_challenges_count_by_category()

    # For ZeroAdmin Panel
    flag_to_download = False
    if current_user.user_is_admin:
        multiflags:list[MultiFlag] = [flag for flag in MultiFlag.select() if not flag.is_downloaded]
        if len(multiflags) > 0:
            flag_to_download = True

    return render_template(
        'home.html', 
        title=f'Welcome {username}',
        users_count=users_count, 
        user_position=user_position,
        username=user.username,
        user_has_solves = user_has_solves,
        user_solves=user_solves, 
        user_average=user_average,
        user_score=user_score,
        has_team=has_team,
        teamname=teamname,
        teams_count=teams_count,
        team_position = team_position,
        team_solves=team_solves,        
        team_average=team_average,
        team_score=team_score,
        category_challenges=category_challenges,
        zeroadmin=current_user.user_is_admin,
        flag_to_download=flag_to_download
        )

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.landing'))

@bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated: return redirect(url_for('main.home'))

    form_login = LoginUser(formdata=request.form)
    form_register = RegisterUser(formdata=request.form)

    ctf:CTF = CTF.select()[0]

    context = {
        'title': 'Login/Register',
        'form_login': form_login,
        'form_register': form_register,
        'error_login': '',
        'error_register': '',
        'login': True,
        'ctf_active': bool(ctf.ctf_active)
    }

    if request.method == 'POST':
        
        if form_register.validate():

            username = form_register.register_username.data
            password = form_register.register_password.data
            
            user_added = User.add_user(username=username, password=password)

            if not user_added:
                context['error_register'] = 'Username already exists.'
                return render_template('login.html', **context)

            user = User.found(username=username)
            login_user(user)

            challenges:list[Challenge] = Challenge.select()
            for challenge in challenges:
                if challenge.is_multiflag:
                    MultiFlag(challenge_id=challenge.id).add_flag()

            return redirect(url_for('main.home'))
        
        elif form_login.validate():

            username = form_login.login_username.data
            password = form_login.login_password.data

            verified = User.verify(username=username, password=password)

            if not verified:
                context['error_login'] = 'Incorrect username or password.'
                return render_template('login.html', **context)
            
            user = User.found(username=username)
            login_user(user)
            User.update(username=user.username, last_logged_in=datetime.datetime.now())
            return redirect(url_for('main.home'))

        else:
            form_name = request.form['form_name']

            if form_name == 'login':
                errors_dict = form_login.errors
                context['error_login'] = ', '.join(list(errors_dict.values())[0])
                context['login'] = True

            elif form_name == 'register':
                errors_dict = form_register.errors
                context['error_register'] = ', '.join(list(errors_dict.values())[0])
                context['login'] = False

            return render_template('login.html', **context)

    return render_template('login.html', **context)

""" 
@bp.route('/admin-reset', methods=['GET'])
def admin_account():

    users = User.select()
    admins = []
    if len(users) > 0:
        admins = [user for user in User.select() if user.user_is_admin]
        if not current_user.is_authenticated and len(admins) > 0: return abort(404)
        if not current_user.user_is_admin and len(admins) > 0: return abort(404)

    db.drop_all()
    db.create_all()

    User.add_user(username='admin', password='admin', admin=True, hidden=True)
    CTF.add(name=CTFNAME)

    return redirect(url_for('main.login'))
"""
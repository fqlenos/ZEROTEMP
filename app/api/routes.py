import secrets
from functools import wraps
import html
import os
import datetime
import json
from werkzeug.utils import secure_filename
from io import BytesIO
from rich.console import Console

from flask_httpauth import HTTPBasicAuth
from flask import Blueprint, jsonify, send_file, request, redirect, url_for, abort
from flask_login import current_user
bp = Blueprint('api', __name__, url_prefix='/api')

from app.extensions import db
from app.extensions import limiter
from app.models.team import Team
from app.models.user import User
from app.models.challenge import Challenge
from app.models.ctf import CTF
from app.models.flag import MultiFlag
from app.models.user_challenge_link import UserChallengeLink
import config

console = Console(color_system='truecolor')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.user_is_admin:
            return jsonify({'Error': 'Unauthorized access.'}), 401
        return f(*args, **kwargs)
    return decorated

def validate_json(data):
    try:
        json.loads(data.read().decode('utf-8'))
    except ValueError as err:
        return False
    return True

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    username = html.escape(str(username))
    user:User = User.found(username=username)
    if user:
        if user.user_is_admin:
            password = html.escape(str(password))
            verified = User.verify(username=username, password=password)
            if verified: return True
    return False

@bp.route('/alive', methods=['GET'])
@limiter.limit('10/seconds')
def alive():

    return jsonify({'info': 'It works!'}), 200

@bp.route('/create/flag')
@auth.login_required
@limiter.limit("10/second")
def get_random_flag():
    
    flag = f'zero{{{secrets.token_hex(32 // 2)}}}'
    return jsonify({'flag': flag}), 200

@bp.route('/download/flags')
@auth.login_required
@limiter.limit("10/second")
def get_flag_relation():

    relations:list[dict] = []
    flags:list[MultiFlag] = MultiFlag.select()
    for flag in flags:
        challenge:Challenge = Challenge.select_by_id(id=flag.challenge_id)
        relations.append({ 'used': flag.is_used , 'challenge': challenge.name, 'flag': flag.flag })
        MultiFlag.update(challenge_id=challenge.id, is_downloaded=True, flag=flag.flag)
    
    challenges:list[Challenge] = [c for c in Challenge.select() if not c.is_multiflag]
    for challenge in challenges:
        relations.append({ 'used': None, 'chalenge': challenge.name, 'flag': challenge.flag })

    if len(relations) == 0:
        relations = {'info': 'Nothing to download.'}

    filename = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_new_flags.json'
    filepath = os.path.join(config.Config.DOWNLOAD_FOLDER, config.DOWNLOAD_CTF_FOLDER, filename)
    with open(filepath, 'w+') as file:
        json.dump(relations, file, indent=4, default=str)

    return send_file(filepath, as_attachment=True)

@bp.route('/download/new-flags')
@auth.login_required
@limiter.limit("10/second")
def get_new_flags():

    relations:list[dict] = []
    flags:list[MultiFlag] = [flag for flag in MultiFlag.select() if not flag.is_downloaded]
    for flag in flags:
        challenge:Challenge = Challenge.select_by_id(id=flag.challenge_id)
        relations.append({ 'used': flag.is_used , 'challenge': challenge.name, 'flag': flag.flag })
        MultiFlag.update(challenge_id=challenge.id, is_downloaded=True, flag=flag.flag)
    
    if len(relations) == 0:
        relations = {'info': 'No new flags to download.'}

    filename = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_new_flags.json'
    filepath = os.path.join(config.Config.DOWNLOAD_FOLDER, config.DOWNLOAD_CTF_FOLDER, filename)
    with open(filepath, 'w+') as file:
        json.dump(relations, file, indent=4, default=str)
    
    return send_file(filepath, as_attachment=True)

@bp.route('/download/all')
@auth.login_required
@limiter.limit("1/second")
def get_all_data():

    return jsonify({'error': 'Not implemented endpoint.'})

    export:dict[list[dict]] = {}
    export_challenges:list[dict] = [item.to_dict() for item in Challenge.select()]
    export_users:list[dict] = [item.to_dict() for item in User.select()]
    export_teams:list[dict] = [item.to_dict() for item in Team.select()]
    export_ctf:list[dict] = [item.to_dict() for item in CTF.select()]

    export['challenges'] = export_challenges
    export['users'] = export_users
    export['teams'] = export_teams
    export['ctf'] = export_ctf[0]

    filename = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_all.json'
    filepath = os.path.join(config.Config.DOWNLOAD_FOLDER, config.DOWNLOAD_CTF_FOLDER, filename)

    with open(filepath, 'w+') as file:
        json.dump(export, file, indent=4, default=str)
    
    return send_file(filepath, as_attachment=True)

@bp.route('/download/challenges')
@auth.login_required
@limiter.limit("1/second")
def get_challenges():

    export:dict[list[dict]] = {}
    challenges:list[dict] = [item.to_dict() for item in Challenge.select()]
    export_challenges:list[dict] = challenges.copy()

    for pos, challenge in enumerate(challenges):
        export_challenges[pos]['solved_by_teams'] = []
        export_challenges[pos]['solved_by_users'] = []
        export_challenges[pos]['team_solvers'] = []
        export_challenges[pos]['user_solvers'] = []
        export_challenges[pos]['file'] = None

    export['challenges'] = export_challenges

    filename = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_challenges.json'
    filepath = os.path.join(config.Config.DOWNLOAD_FOLDER, config.DOWNLOAD_CTF_FOLDER, filename)

    with open(filepath, 'w+') as file:
        json.dump(export, file, indent=4, default=str)
    
    return send_file(filepath, as_attachment=True)

@bp.route('/import', methods=['POST'])
@auth.login_required
@limiter.limit("1/second")
def import_all_data():
    
    file = request.files['import']

    if file:
        filename = secure_filename(datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.json')
        if '.' in filename and filename.rsplit('.', 1)[1].lower() in ['json']:
            file_content = file.stream.read()
            validate = validate_json(BytesIO(file_content))

            if validate:
                
                if hasattr(auth.current_user(), 'user_is_admin'):
                    if not current_user.user_is_admin: return abort(404)
                
                if hasattr(auth.current_user(), 'is_authenticated'):
                    if not current_user.is_authenticated: return abort(404)
                
                data:dict[list[dict]] = json.loads(file_content)

                if all(['users' in data, 'teams' in data, 'ctf' in data, 'challenges' in data]):

                    db.drop_all()
                    db.create_all()
                    
                    users:list[dict] = sorted(data.get('users'), key=lambda x: x['id'])
                    for user in users:

                        User.add_user(username=user.get('username'), password='password_to_be_updated', admin=bool(user.get('user_is_admin')), hidden=bool(user.get('user_is_hidden')), active=bool(user.get('user_is_active')), banned=bool(user.get('user_is_banned')))
                        user_obj = User.found(username=user.get('username'))

                        user_obj.update(username=user.get('username'), email=user.get('email'), name=user.get('name'), surname=user.get('surname'), birthday=user.get('birthday'), location=user.get('location'), ctftime=user.get('ctftime'), github=user.get('github'), webpage=user.get('webpage'), password=str(user.get('password')).strip())

                    teams:list[dict] = sorted(data.get('teams'), key=lambda x: x['id'])
                    for team in teams:

                        user_obj:User = User.select_by_id(id=team.get('leader_id'))
                        Team.add_team(teamname=team.get('teamname'), password=team.get('password'), active=bool(team.get('team_is_active')), hidden=bool(team.get('team_is_hidden')), username=user_obj.username)

                        for user_id in team.get('members'):

                            user_obj:User = User.select_by_id(id=user_id)
                            Team.add_member(teamname=team.get('teamname'), username=user_obj.username)
                        
                        team_obj = Team.found(teamname=team.get('teamname'))
                        team_obj.update(teamname=team.get('teamname'), email=team.get('email'), location=team.get('location'), ctftime=team.get('ctftime'), github=team.get('github'), webpage=team.get('webpage'))

                    challenges:list[dict] = sorted(data.get('challenges'), key=lambda x: x['id'])
                    for challenge in challenges:
                        
                        Challenge.add_challenge(name=challenge.get('name'), description=challenge.get('description'), category=str(challenge.get('category')).lower(), value=str(challenge.get('value')), hidden=bool(challenge.get('challenge_is_hidden')), flag=challenge.get('flag'), is_multiflag=bool(challenge.get('is_multiflag')), url=challenge.get('url'))
                        
                        user_ids:list[int] = challenge.get('solved_by_users')
                        if not bool(challenge.get('is_multiflag')):

                            for user_id in user_ids:
                                UserChallengeLink(user_id=user_id, challenge_id=challenge.get('id')).add_challenge(input_flag=challenge.get('flag'))
                        
                        else:
                            
                            for pos, user_id in enumerate(user_ids):
                                MultiFlag(challenge_id=challenge.get('id')).add_flag()
                                flags:list[MultiFlag] = [flag for flag in MultiFlag.select() if flag.challenge_id == challenge.get('id')]
                                UserChallengeLink(user_id=user_id, challenge_id=challenge.get('id')).add_challenge(input_flag=flags[pos].flag)

                    ctf:dict = data.get('ctf')
                    CTF.add(name=ctf.get('name'))
                    ctf_obj:CTF = CTF.select()[0]
                    ctf_obj.update(name=ctf.get('name'), edition=ctf.get('edition'), description=ctf.get('description'), link_one_name=ctf.get('link_one_name'), link_one_name_href=ctf.get('link_one_name_href'), link_two_name=ctf.get('link_two_name'), link_two_name_href=ctf.get('link_two_name_href'), ctf_active=bool(ctf.get('ctf_active')), custom_title=ctf.get('custom_title'), custom_btn_name=ctf.get('custom_btn_name'), custom_btn_href=ctf.get('custom_btn_href'), custom_description=ctf.get('custom_description'), discord_group_link=ctf.get('discord_group_link'), telegram_group_link=ctf.get('telegram_group_link'))


                elif 'challenges' in data:

                    db.drop_all()
                    db.create_all()

                    User.add_user(username='admin', password='admin', admin=True, hidden=True)
                    CTF.add(name=config.CTFNAME)

                    users:list[User] = User.select()

                    try:
                        challenges:list[dict] = sorted(data.get('challenges'), key=lambda x: x['id'])
                    except:
                        challenges:list[dict] = sorted(data.get('challenges'), key=lambda x: x['name'])
                    for challenge in challenges:
                        Challenge.add_challenge(name=challenge.get('name'), description=challenge.get('description'), category=str(challenge.get('category')).lower(), value=str(challenge.get('value')), hidden=bool(challenge.get('challenge_is_hidden')), flag=challenge.get('flag'), is_multiflag=bool(challenge.get('is_multiflag')), url=challenge.get('url'))
                        
                        challenge_added:Challenge = Challenge.found(name=challenge.get('name'))
                        if not bool(challenge_added): 
                            console.print(f'[red]"{challenge.get("name")}" cannot be added.[/red]')
                            continue
                        else:
                            console.print(f'[green]"{challenge_added.name}" successfully added.[/green]')
                        
                        if challenge_added.is_multiflag:
                            for _ in users:
                                MultiFlag(challenge_id=challenge_added.id).add_flag()
            else:
                return jsonify({'Error': 'Bad Request.'}), 400

    return redirect(url_for('main.home'))

@bp.route('/create/user', methods=['POST'])
@auth.login_required
@limiter.limit("1/second")
def create_user():

    users:list[str, str, bool] = request.json.get('users')
    for user, password, is_admin in users:
        done = User.add_user(username=user, password=password, admin=is_admin, hidden=is_admin==True)
        if done:
            console.print(f'[green]"{user}" successfully added.[/green]')
        else:
            console.print(f'[red]"{user}" cannot be added. Check if already exists.[/red]')
    
    return redirect(url_for('main.home'))

@auth.error_handler
def unauthorized():
    return jsonify({'Error': 'Unauthorized access.'}), 401

from flask_login import current_user, login_required
from flask import Flask, render_template, request, abort
from wtforms import Form
import random
import os
from werkzeug.utils import secure_filename
import hashlib
from PIL import Image

from app.forms.forms import CreateUser, CreateTeam, CreateChallenge, ManageUser, ManageTeam, ManageChallenge, RemoveUser, RemoveTeam, RemoveChallenge, ManageLandingPage, ManageSocial
from app.models.user import User
from app.models.team import Team
from app.models.challenge import Challenge
from app.models.team_challenge_link import TeamChallengeLink
from app.models.user_challenge_link import UserChallengeLink
from app.models.flag import MultiFlag 
from app.models.ctf import CTF
import config
import io

from flask import Blueprint
bp = Blueprint('management', __name__, url_prefix='/manage')

basedir = os.path.abspath(os.path.dirname(__file__))
parentdir = os.path.abspath(os.path.join(basedir, os.pardir))

UPLOAD_FOLDER = config.Config.UPLOAD_FOLDER
UPLOAD_USER_FOLDER = config.UPLOAD_USER_FOLDER
UPLOAD_SPONSOR_FOLDER = config.UPLOAD_SPONSOR_FOLDER
UPLOAD_CHALLENGE_FOLDER = config.UPLOAD_CHALLENGE_FOLDER
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
ALLOWED_ZIP_EXTENSIONS = {'zip'}

def validate_image(stream) -> bool:
    try:
        img = Image.open(stream)
        if img.format.lower() in ALLOWED_EXTENSIONS:
            return True
        return False
    except:
        return False

def validate_zip(stream) -> bool:
    header = stream.read(4)
    if header == b'PK\x03\x04':
        # El archivo parece ser un archivo ZIP
        return True
    return False

def save_image(file, filename, upload_folder) -> bool:
    temp_stream = io.BytesIO(file.read())
    if '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS and validate_image(temp_stream):
        file.close()
        temp_stream.seek(0)
        with open(os.path.join(upload_folder,filename), 'wb') as f:
            f.write(temp_stream.read())
        return True
    return False

@bp.route('/user', methods=['GET', 'POST'])
@login_required
def user():

    if not current_user.user_is_admin: abort(401)

    form_create:Form = CreateUser(formdata=request.form)
    form_mng:Form = ManageUser(formdata=request.form, users=sorted([user.username for user in User.select() if user != current_user]))
    form_remove:Form = RemoveUser(formdata=request.form, users=sorted([user.username for user in User.select() if user != current_user]))

    context = {
        'title': 'User Management',
        'form_create': form_create,
        'form_mng': form_mng,
        'form_remove': form_remove,
        'zeroadmin': current_user.user_is_admin,
        'error_create': '',
        'error_mng': '',
        'error_remove': '',
        'success_create': '',
        'success_mng': '',
        'success_remove': ''
    }

    if request.method == 'POST':

        if form_create.validate():
            user:User = User.found(username=form_create.username.data)
            if bool(user):
                context['error_create'] = 'User already exists.'
                return render_template('management/index.html', **context)
            
            filename = None
            if 'icon' in request.files:
                file = request.files['icon']
                if file:
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = secure_filename(hashlib.sha1(str(f'{str(form_create.username)}_{str(file.filename)}').encode()).hexdigest() + f'.{ext}')
                    saved = save_image(file=file, filename=filename, upload_folder=os.path.join(UPLOAD_FOLDER, UPLOAD_USER_FOLDER))
                    if not saved:
                        context['error_mng'] = 'Invalid image format.'
                        return render_template('management/index.html', **context)

            user_added = User.add_user(username=form_create.username.data, password=form_create.password.data, admin=form_create.user_is_admin.data, hidden=form_create.user_is_hidden.data, active=form_create.user_is_active.data, icon=filename)
            if not user_added:
                context['error_create'] = 'An error ocurred while creating user. Wait or contact the administrator.'
                return render_template('management/index.html', **context)
            
            challenges:list[Challenge] = Challenge.select()
            user:User = User.found(username=form_create.username.data)
            for challenge in challenges:
                if challenge.is_multiflag:
                    MultiFlag(challenge_id=challenge.id).add_flag()

            context['success_create'] = 'User successfully created.'
            return render_template('management/index.html', **context)

        elif form_mng.validate():
            user:User = User.found(username=form_mng.user_select.data)
            if not bool(user):
                context['error_mng'] = 'User does not exist.'
                return render_template('management/index.html', **context)

            admin_validated = User.verify(username=current_user.username, password=form_mng.mng_password.data)
            if not admin_validated:
                context['error_mng'] = 'Invalid password.'
                return render_template('management/index.html', **context)
            
            filename = None
            if 'icon' in request.files:
                file = request.files['icon']
                if file:
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = secure_filename(hashlib.sha1(str(f'{str(user.username)}_{str(file.filename)}').encode()).hexdigest() + f'.{ext}')
                    saved = save_image(file=file, filename=filename, upload_folder=os.path.join(UPLOAD_FOLDER, UPLOAD_USER_FOLDER))
                    if not saved:
                        context['error_mng'] = 'Invalid image format.'
                        return render_template('management/index.html', **context)

            user_updated = User.update(username=form_mng.user_select.data, user_is_hidden=form_mng.user_is_hidden.data, user_is_active=form_mng.user_is_active.data, user_is_admin=form_mng.user_is_admin.data, user_is_banned=form_mng.user_is_banned.data, icon=filename)
            if not user_updated:
                context['error_mng'] = 'An error ocurren while updating user. Wait or contact the administrator.'
                return render_template('management/index.html', **context)

            context['success_mng'] = 'User successfully updated.'
            return render_template('management/index.html', **context)

        elif form_remove.validate():
            user:User = User.found(username=form_mng.user_select.data)
            if not bool(user):
                context['error_remove'] = 'User does not exist.'
                return render_template('management/index.html', **context)
            
            admin_validated = User.verify(username=current_user.username, password=form_remove.remove_password.data)
            if not admin_validated:
                context['error_remove'] = 'Invalid password.'
                return render_template('management/index.html', **context)
            
            if bool(user.team):
                team:Team = Team.found(teamname=user.team.teamname)
                if user.team.leader_id == user.id:
                    if len(team.members) > 1:
                        newleader:User = random.choice(team.members)
                        while newleader.id == user.id:
                            newleader:User = random.choice(team.members)
                        Team.update_leader(newleader=newleader, teamname=team.teamname)
                        Team.kickout_member(username=form_mng.user_select.data, teamname=user.team.teamname)
                    else: 
                        if not all([TeamChallengeLink.remove_challenge(teamname=user.team.teamname, challengename=challenge.name) for challenge in user.solved_challenges]): abort(400)
                        Team.remove(username=form_mng.user_select.data, teamname=team.teamname)
                else: Team.kickout_member(username=form_mng.user_select.data, teamname=user.team.teamname)

            if not all([UserChallengeLink.remove_challenge(username=form_mng.user_select.data, challengename=challenge.name) for challenge in user.solved_challenges]): abort(400)
            
            user_removed = User.remove(username=form_remove.user_select.data)
            if not user_removed:
                context['error_remove'] = 'An error ocurren while updating user. Wait or contact the administrator.'
                return render_template('management/index.html', **context)
            
            context['success_remove'] = 'User successfully removed.'
            return render_template('management/index.html', **context)

        else:
            form_name = request.form['form_name']
            if form_name == 'create':
                errors_dict = form_create.errors
                context['error_create'] = ', '.join(list(errors_dict.values())[0])
            elif form_name == 'mng':
                errors_dict = form_mng.errors
                context['error_mng'] = ', '.join(list(errors_dict.values())[0])
            elif form_name == 'remove':
                errors_dict = form_remove.errors
                context['error_remove'] = ', '.join(list(errors_dict.values())[0])
            
            return render_template('management/index.html', **context)

    return render_template('management/index.html', **context)

@bp.route('/team', methods=['GET', 'POST'])
@login_required
def team():

    if not current_user.user_is_admin: abort(401)

    form_create:Form = CreateTeam(formdata=request.form)
    form_mng:Form = ManageTeam(formdata=request.form, teams=sorted([team.teamname for team in Team.select()]))
    form_remove:Form = RemoveTeam(formdata=request.form, teams=sorted([team.teamname for team in Team.select()])) 

    context = {
        'title': 'Team Management',
        'form_create': form_create,
        'form_mng': form_mng,
        'form_remove': form_remove,
        'zeroadmin': current_user.user_is_admin,
        'error_create': '',
        'error_mng': '',
        'error_remove': '',
        'success_create': '',
        'success_mng': '',
        'success_remove': ''
    }

    if request.method == 'POST':

        if form_create.validate():

            leader:User = User.found(username=form_create.leader.data)
            if not leader:
                context['error_create'] = 'User does not exist.'
                return render_template('management/index.html', **context)

            if leader.user_is_hidden or not leader.user_is_active or leader.user_is_admin:
                context['error_create'] = 'User is hidden, ZeroAdmin or is not active.'
                return render_template('management/index.html', **context)

            if bool(leader.team):
                context['error_create'] = 'User is already a team member.'
                return render_template('management/index.html', **context)
            
            team:Team = Team.found(teamname=form_create.teamname.data)
            if bool(team):
                context['error_create'] = 'Team already exists.'
                return render_template('management/index.html', **context)

            team_added = Team.add_team(teamname=form_create.teamname.data, username=form_create.leader.data, password=form_create.password.data, hidden=form_create.team_is_hidden.data, active=form_create.team_is_active.data)
            if not team_added:
                context['error_create'] = 'An error ocurred while creating team. Wait or contact the administrator.'
                return render_template('management/index.html', **context)
        
            context['success_create'] = 'Successfully created.'
            return render_template('management/index.html', **context)

        elif form_mng.validate():
            team = Team.found(teamname=form_mng.team_select.data)
            if not team:
                context['error_mng'] = 'Team does not exist.'
                return render_template('management/index.html', **context)
            
            admin_validated = User.verify(username=current_user.username, password=form_mng.mng_password.data)
            if not admin_validated:
                context['error_mng'] = 'Invalid password.'
                return render_template('management/index.html', **context)

            team_updated = Team.update(teamname=form_mng.team_select.data, team_is_active=form_mng.team_is_active.data, team_is_hidden=form_mng.team_is_hidden.data)
            if not team_updated:
                context['error_mng'] = 'An error ocurred while updating team. Wait or contact the administrator.'
                return render_template('management/index.html', **context)
            
            context['success_mng'] = 'Team successfully updated.'
            return render_template('management/index.html', **context)

        elif form_remove.validate():
            team = Team.found(teamname=form_remove.team_select.data)
            if not team:
                context['error_remove'] = 'Team does not exist.'
                return render_template('management/index.html', **context)
            
            admin_validated = User.verify(username=current_user.username, password=form_remove.remove_password.data)
            if not admin_validated:
                context['error_remove'] = 'Invalid password.'
                return render_template('management/index.html', **context)
            
            user:User = User.select_by_id(id=team.leader_id)
            team:Team = Team.found(teamname=form_remove.team_select.data)
            
            if not all([TeamChallengeLink.remove_challenge(teamname=form_remove.team_select.data, challengename=challenge.name) for challenge in team.solved_challenges]):
                context['error_remove'] = 'An error ocurren while updating user. Check if all members are "Active", not "ZeroAdmin" and not "Hidden".'
                return render_template('management/index.html', **context)

            team_removed = Team.remove(teamname=form_remove.team_select.data, username=user.username)
            if not team_removed:
                context['error_remove'] = 'An error ocurren while updating user. Wait or contact the administrator.'
                return render_template('management/index.html', **context)
            
            context['success_remove'] = 'Team successfully removed.'
            return render_template('management/index.html', **context)

        else:
            form_name = request.form['form_name']
            if form_name == 'create':
                errors_dict = form_create.errors
                context['error_create'] = ', '.join(list(errors_dict.values())[0])
            elif form_name == 'mng':
                errors_dict = form_mng.errors
                context['error_mng'] = ', '.join(list(errors_dict.values())[0])
            elif form_name == 'remove':
                errors_dict = form_remove.errors
                context['error_mng'] = ', '.join(list(errors_dict.values())[0])
            
            return render_template('management/index.html', **context)

    return render_template('management/index.html', **context)

@bp.route('/challenge', methods=['GET', 'POST'])
@login_required
def challenge():

    if not current_user.user_is_admin: abort(401)

    form_create:Form = CreateChallenge(formdata=request.form)
    form_mng:Form = ManageChallenge(formdata=request.form, challenges=[challenge for challenge in Challenge.select()])
    form_remove:Form = RemoveChallenge(formdata=request.form, challenges=[challenge for challenge in Challenge.select()])

    context = {
        'title': 'Challenge Management',
        'form_create': form_create,
        'form_mng': form_mng,
        'form_remove': form_remove,
        'zeroadmin': current_user.user_is_admin,
        'error_create': '',
        'error_mng': '',
        'error_remove': '',
        'success_create': '',
        'success_mng': ''
    }

    if request.method == 'POST':

        if form_create.validate():
            challenge:Challenge = Challenge.found(name=form_create.challengename.data)
            if bool(challenge):
                context['error_create'] = 'Challenge already exists.'
                return render_template('management/index.html', **context)

            if not form_create.is_multiflag.data:
                flag = form_create.flag.data
            else:
                flag = None

            filename = None
            if 'file' in request.files:
                file = request.files['file']
                if file:
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    #filename = secure_filename(hashlib.sha1(str(f'{str(form_create.challengename.data)}_{str(file.filename)}').encode()).hexdigest() + '.zip')
                    filename = secure_filename(f'{str(form_create.challengename.data).lower().replace(" ", "_")}.zip')
                    if ext in ALLOWED_ZIP_EXTENSIONS and validate_zip(file.stream):
                        file.save(os.path.join(UPLOAD_FOLDER, UPLOAD_CHALLENGE_FOLDER, filename))
                    else:
                        context['error_create'] = 'Invalid ZIP format.'
                        return render_template('management/index.html', **context)

            challenge_added = Challenge.add_challenge(name=form_create.challengename.data, description=form_create.description.data, category=str(form_create.category.data).lower(), value=form_create.value.data, hidden=form_create.challenge_is_hidden.data, flag=flag, file=filename, url=form_create.url.data, is_multiflag=form_create.is_multiflag.data)

            if not challenge_added:
                context['error_create'] = 'An error ocurred while creating team. Wait or contact the administrator.'
                return render_template('management/index.html', **context)
            
            if form_create.is_multiflag.data:
                challenge:Challenge = Challenge.found(name=form_create.challengename.data)
                users:list[User] = User.select()
                for _ in users:
                    MultiFlag(challenge_id=challenge.id).add_flag()

            context['success_create'] = 'Successfully created.'
            return render_template('management/index.html', **context)

        elif form_mng.validate():
            challenge = Challenge.found(name=form_mng.challenge_select.data)
            if not challenge:
                context['error_mng'] = 'Challenge does not exist.'
                return render_template('management/index.html', **context)
            
            admin_validated = User.verify(username=current_user.username, password=form_mng.mng_password.data)
            if not admin_validated:
                context['error_mng'] = 'Invalid password.'
                return render_template('management/index.html', **context)

            challenge_updated = Challenge.update(name=form_mng.challenge_select.data, challenge_is_hidden=form_mng.challenge_is_hidden.data)
            if not challenge_updated:
                context['error_mng'] = 'An error ocurred while updating team. Wait or contact the administrator.'
                return render_template('management/index.html', **context)
            
            context['success_mng'] = 'Challenge successfully updated.'
            return render_template('management/index.html', **context)

        elif form_remove.validate():
            challenge:Challenge = Challenge.found(name=form_remove.challenge_select.data)
            if not challenge:
                context['error_remove'] = 'Challenge does not exist.'
                return render_template('management/index.html', **context)
            
            admin_validated = User.verify(username=current_user.username, password=form_remove.remove_password.data)
            if not admin_validated:
                context['error_remove'] = 'Invalid password.'
                return render_template('management/index.html', **context)
            
            # Exclusively in this order: first Users and then Teams.
            users:list[User] = challenge.solved_by_users
            if not all([UserChallengeLink.remove_challenge(username=user.username, challengename=form_remove.challenge_select.data) for user in users]): abort(400)
            teams:list[Team] = challenge.solved_by_teams
            if not all([TeamChallengeLink.remove_challenge(teamname=team.teamname, challengename=form_remove.challenge_select.data) for team in teams]): abort(400)

            multis:list[MultiFlag] = MultiFlag.select()
            for multi in multis:
                MultiFlag.remove_challenge(challenge_id=multi.challenge_id, user_id=multi.user_id)

            challenge_removed = Challenge.remove(name=form_remove.challenge_select.data)
            if not challenge_removed:
                context['error_remove'] = 'An error ocurred while updating team. Wait or contact the administrator.'
                return render_template('management/index.html', **context)
            
            context['success_remove'] = 'Challenge successfully removed.'
            return render_template('management/index.html', **context)

        else:
            form_name = request.form['form_name']
            if form_name == 'create':
                errors_dict = form_create.errors
                context['error_create'] = ', '.join(list(errors_dict.values())[0])
            elif form_name == 'mng':
                errors_dict = form_mng.errors
                context['error_mng'] = ', '.join(list(errors_dict.values())[0])
            elif form_name == 'remove':
                errors_dict = form_remove.errors
                context['error_remove'] = ', '.join(list(errors_dict.values())[0])
            
            return render_template('management/index.html', **context)

    return render_template('management/index.html', **context)

@bp.route('/ctf', methods=['GET', 'POST'])
@login_required
def ctf():

    if not current_user.user_is_admin: abort(401)

    ctfs:list[CTF] = CTF.select()
    ctf:CTF = ctfs[0]

    form_mng:Form = ManageLandingPage(formdata=request.form, ctf=ctf)
    form_social:Form = ManageSocial(formdata=request.form, ctf=ctf)

    #'sponsors': ctf.sponsors.split('::::::::')
    
    context = {
        'title': 'CTF Management',
        'form_mng': form_mng,
        'form_social': form_social,
        'zeroadmin': current_user.user_is_admin,
        'error_mng': '',
        'success_mng': '',
        'error_social': '',
        'success_social': '',
        'has_sponsors': True if len(ctf.sponsors.split('::::::::')) > 0 and ctf.sponsors.split('::::::::')[0] != '' else False,
    }

    if request.method == 'POST':

        if form_mng.validate():
            
            form_mng.ctf_description.data = request.form['ctf_description']

            if all([form_mng.ctf_name.data == '', form_mng.ctf_editon.data  == '', form_mng.ctf_description.data  == '', form_mng.ctf_link_one.data  == '', form_mng.ctf_link_one_href.data  == '', form_mng.ctf_link_two.data  == '', form_mng.ctf_link_two_href.data  == '']):
                context['error_mng'] = 'You cannot send an empty form.'
                return render_template('management/index.html', **context)

            ctf_updated = CTF.update(name=form_mng.ctf_name.data, edition=form_mng.ctf_editon.data, description=form_mng.ctf_description.data, link_one_name=form_mng.ctf_link_one.data, link_one_name_href=form_mng.ctf_link_one_href.data, link_two_name=form_mng.ctf_link_two.data, link_two_name_href=form_mng.ctf_link_two_href.data, ctf_active=form_mng.ctf_active.data)

            if not ctf_updated:
                context['error_mng'] = 'An error ocurren while updating CTF. Wait or contact the administrator.'
                return render_template('management/index.html', **context)

            context['success_mng'] = 'CTF successfully updated.'   
            return render_template('management/index.html', **context)
        
        elif form_social.validate():

            form_social.ctf_custom_description.data = request.form['ctf_custom_description']

            filenames = []
            if 'ctf_sponsors' in request.files:
                files:list = request.files.getlist('ctf_sponsors')
                for file in files:
                    if file:
                        filename = secure_filename(f'sponsor_{file.filename}'.lower())
                        filenames.append(filename)
                        saved = save_image(file=file, filename=filename, upload_folder=os.path.join(UPLOAD_FOLDER, UPLOAD_SPONSOR_FOLDER))
                        if not saved:
                            context['error_mng'] = 'Invalid image format.'
                            return render_template('management/index.html', **context)

            filenames = '::::::::'.join(filenames)

            ctf_updated = CTF.update(sponsors=filenames, telegram_group_link=form_social.telegram_group_link.data, discord_group_link=form_social.discord_group_link.data, custom_title=form_social.ctf_custom_title.data, custom_description=form_social.ctf_custom_description.data, custom_btn_name=form_social.ctf_custom_link.data, custom_btn_href=form_social.ctf_custom_link_href.data)

            if not ctf_updated:
                context['error_social'] = 'An error ocurren while updating CTF. Wait or contact the administrator.'
                return render_template('management/index.html', **context)
            
            context['success_social'] = 'CTF successfully updated.'   
            return render_template('management/index.html', **context)

        else:
            form_name = request.form['form_name']
            if form_name == 'mng':
                errors_dict = form_mng.errors
                context['error_mng'] = ', '.join(list(errors_dict.values())[0])

            return render_template('management/index.html', **context)

    return render_template('management/index.html', **context)

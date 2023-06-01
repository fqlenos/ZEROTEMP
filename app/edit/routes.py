from flask import render_template, request, redirect, url_for, abort
from flask_login import current_user, login_required
import html
import datetime

from flask import Blueprint
bp = Blueprint('edit', __name__, url_prefix='/edit')
from app.models.team import Team
from app.models.user import User
from app.models.challenge import Challenge
from app.extensions import cache
from wtforms import Form
import os
from werkzeug.utils import secure_filename

import config
from app.forms.forms import ManageChallenge
from app.models.flag import MultiFlag

basedir = os.path.abspath(os.path.dirname(__file__))
parentdir = os.path.abspath(os.path.join(basedir, os.pardir))

UPLOAD_FOLDER = config.Config.UPLOAD_FOLDER
UPLOAD_CHALLENGE_FOLDER = config.UPLOAD_CHALLENGE_FOLDER
ALLOWED_ZIP_EXTENSIONS = {'zip'}

def validate_zip(stream) -> bool:
    header = stream.read(4)
    if header == b'PK\x03\x04':
        # El archivo parece ser un archivo ZIP
        return True
    return False

@bp.route('/user/<string:user>', methods=['GET', 'POST'])
@cache.cached(timeout=5)
@login_required
def user(user:str):

    username = html.escape(user.strip())

    if any([not isinstance(username, str), username == '', username is None, not User.found(username=username)]): abort(404)
    if not current_user.user_is_admin:
        if username != current_user.username: abort(401)

    user:User = User.found(username=username)

    if username.endswith('s'): cusername = f"{username}'"
    else: cusername = f"{username}'s"

    if request.method == 'POST':
        form_id = request.form['form_id']
        if form_id == 'personal':

            email = html.escape(str(request.form['email'])) if request.form['email'] else ''
            name = html.escape(str(request.form['name'])) if request.form['name'] else ''
            surname = html.escape(str(request.form['surname'])) if request.form['surname'] else ''
            birthday = html.escape(str(request.form['birthday'])) if request.form['birthday'] else ''
            location = html.escape(str(request.form['location'])) if request.form['location'] else ''

            updated = User.update(
                username=username,
                email=email,
                name=name,
                surname=surname,
                birthday=birthday,
                location=location
                )
            
            if updated: return redirect(url_for('user.user_profile', username=username), code=303)
        
        elif form_id == 'social':
            ctftime = html.escape(str(request.form['ctftime'])) if request.form['ctftime'] else ''
            github = html.escape(str(request.form['github'])) if request.form['github'] else ''
            webpage = html.escape(str(request.form['webpage'])) if request.form['webpage'] else ''

            updated = User.update(
                username=username,
                ctftime=ctftime,
                github=github,
                webpage=webpage
            )

            if updated: return redirect(url_for('user.user_profile', username=username))

        elif form_id == 'updatepass':
            oldpassword = html.escape(str(request.form['oldpassword'])) if request.form['oldpassword'] else ''
            newpassword = html.escape(str(request.form['newpassword'])) if request.form['newpassword'] else ''
            renewpassword = html.escape(str(request.form['renewpassword'])) if request.form['renewpassword'] else ''

            verified = User.verify(username=username, password=oldpassword)

            if verified:
                if newpassword == renewpassword:
                    updated = User.passwdupdate(username=username, password=newpassword)
                    if updated: return redirect(url_for('user.user_profile', username=username), code=303)

    return render_template(
        'edit/index.html', 
        title=f'Edit {cusername} profile',
        user=True,
        team=False,
        email=user.email,
        name=user.name,
        surname=user.surname,
        birthday=user.birthday.strftime('%Y/%m/%d') if isinstance(user.birthday, datetime.datetime) else '',
        location=user.country,
        ctftime=user.ctftime,
        github=user.github,
        webpage=user.webpage,
        zeroadmin=current_user.user_is_admin
        )

@bp.route('/team/<string:team>', methods=['GET', 'POST'])
@cache.cached(timeout=5)
@login_required
def team(team:str):

    teamname = html.escape(team.strip())
    if any([not isinstance(teamname, str), teamname == '', teamname is None, not Team.found(teamname=teamname)]): abort(404)
    team:Team = Team.found(teamname=teamname)
    
    if not current_user.user_is_admin:
        if not bool(current_user.team): abort(404)
        if current_user.team.leader_id != team.leader_id: abort(403)

    if request.method == 'POST':
        form_id = request.form['form_id']
        if form_id == 'general':
            email = html.escape(str(request.form['email'])) if request.form['email'] else ''
            location = html.escape(str(request.form['location'])) if request.form['location'] else ''
            ctftime = html.escape(str(request.form['ctftime'])) if request.form['ctftime'] else ''
            github = html.escape(str(request.form['github'])) if request.form['github'] else ''
            webpage = html.escape(str(request.form['webpage'])) if request.form['webpage'] else ''

            updated = Team.update(
                teamname=teamname,
                email=email,
                location=location,
                ctftime=ctftime,
                github=github,
                webpage=webpage
                )

            if updated: return redirect(url_for('team.team_profile', team=teamname))

        elif form_id == 'updatepass':
            oldpassword = html.escape(str(request.form['oldpassword'])) if request.form['oldpassword'] else ''
            newpassword = html.escape(str(request.form['newpassword'])) if request.form['newpassword'] else ''
            renewpassword = html.escape(str(request.form['renewpassword'])) if request.form['renewpassword'] else ''

            verified = Team.verify(teamname=teamname, password=oldpassword)

            if verified:
                if newpassword == renewpassword:
                    updated = Team.passwdupdate(teamname=teamname, password=newpassword)
                    if updated: return redirect(url_for('team.team_profile', team=teamname))

    return render_template(
        'edit/index.html', 
        title=f'Edit {teamname}',
        user=False,
        team=True,
        teamname=team.teamname,
        location=team.country,
        github=team.github,
        ctftime=team.ctftime,
        webpage=team.webpage,
        email=team.email,
        zeroadmin=current_user.user_is_admin
        )

@bp.route('/challenge/<string:challenge>', methods=['GET', 'POST'])
@cache.cached(timeout=5)
@login_required
def challenge(challenge:str):

    challengename = html.escape(challenge.strip())
    if any([not isinstance(challenge, str), challengename == '', challengename is None, not Challenge.found(name=challengename)]): abort(404)
    challenge:Challenge = Challenge.found(name=challenge)
    
    if not current_user.user_is_admin: abort(403)
    
    form_mng:Form = ManageChallenge(formdata=request.form, challenge=challenge)

    context = {
        'title': 'Edit Challenge',
        'user': False,
        'team': False,
        'form_mng': form_mng,
        'zeroadmin': current_user.user_is_admin,
        'error_mng': '',
        'success_mng': ''
    }

    if request.method == 'POST':
        
        if form_mng.validate():

            form_mng.description.data = request.form['description']

            challenge = Challenge.found(name=form_mng.challengename.data)
            if challenge:
                if challenge.name != challengename:
                    context['error_mng'] = 'Challengename exists.'
                    return render_template('edit/index.html', **context)
            
            admin_validated = User.verify(username=current_user.username, password=form_mng.mng_password.data)
            if not admin_validated:
                context['error_mng'] = 'Invalid password.'
                return render_template('edit/index.html', **context)
            
            filename = None
            if 'file' in request.files:
                file = request.files['file']
                if file:
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = secure_filename(f'{str(form_mng.challengename.data).lower().replace(" ", "_")}.zip')
                    if ext in ALLOWED_ZIP_EXTENSIONS and validate_zip(file.stream):
                        file.save(os.path.join(UPLOAD_FOLDER, UPLOAD_CHALLENGE_FOLDER, filename))
                    else:
                        context['error_mng'] = 'Invalid ZIP format.'
                        return render_template('edit/index.html', **context)
            
            challenge_updated = Challenge.update(name=form_mng.challengename.data, challenge_is_hidden=form_mng.challenge_is_hidden.data, description=form_mng.description.data, category=form_mng.category.data, flag=form_mng.flag.data, is_multiflag=form_mng.is_multiflag.data, file=filename, url=form_mng.url.data)
            if not challenge_updated:
                context['error_mng'] = 'An error ocurred while updating team. Wait or contact the administrator.'
                return render_template('edit/index.html', **context)
            
            if form_mng.is_multiflag.data:
                challenge:Challenge = Challenge.found(name=form_mng.challengename.data)
                users:list[User] = User.select()
                for _ in users:
                    MultiFlag(challenge_id=challenge.id).add_flag()
            
            context['success_mng'] = 'Challenge successfully updated.'
            return render_template('edit/index.html', **context)

        else:
            print(form_mng.errors)
            errors_dict = form_mng.errors
            context['error_mng'] = ', '.join(list(errors_dict.values())[0])
    
    return render_template('edit/index.html', **context)
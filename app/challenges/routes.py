from flask_login import login_required, current_user
from flask import Blueprint, render_template, abort, request, redirect, url_for

import html

bp = Blueprint('challenge', __name__, url_prefix='/challenges')
from app.models.challenge import Challenge
from app.models.user import User
from app.models.team import Team
from app.models.user_challenge_link import UserChallengeLink
from app.models.flag import MultiFlag
from wtforms import Form
from app.forms.forms import SubmitFlag
from app.extensions import cache

@bp.route('/', methods=['GET', 'POST'])
@cache.cached(timeout=5)
@login_required
def index():

    error = ''
    challenges:list[Challenge] = Challenge.select()
    solves:dict = Challenge.get_solves_count_by_challenges() 
    categories = sorted(list(set([challenge.category for challenge in challenges])))

    if not current_user.user_is_admin:
        categories_challenges_hidden = sorted(list(set([challenge.category for challenge in challenges if challenge.challenge_is_hidden])))
        not_showing_categories = [c for c in categories_challenges_hidden if all([challenge.challenge_is_hidden for challenge in challenges if challenge.category == c])]
        [categories.remove(category) for category in not_showing_categories]

    team:Team = current_user.team
    solvers = {}
    if bool(team):
        for challenge in challenges:
            solvers[challenge.name]:list = [user for user in challenge.solved_by_users if user in team.members]
    else:
        for challenge in challenges:
            solvers[challenge.name]:list = [current_user] if challenge in current_user.solved_challenges else []

    ordered_challenges:list[Challenge] = []
    for category in categories:
        for challenge in challenges:
            if challenge in ordered_challenges: continue
            if challenge.category.lower() == category.lower(): ordered_challenges.append(challenge)

    form:Form = SubmitFlag(formdata=request.form)
    if request.method == 'POST':
        if form.validate():
            challenge_id = request.form['challenge']
            valid = UserChallengeLink(challenge_id=challenge_id, user_id=current_user.id).add_challenge(input_flag=form.flag.data)                            
            if not valid:
                challenge:Challenge = Challenge.select_by_id(id=challenge_id)
                if challenge.is_multiflag:
                    error = 'You have been banned for cheating!'
                else:
                    error = 'Incorrect flag.'
            else:
                return redirect(url_for('user.user_profile', username=current_user.username))
        else:
            errors_dict = form.errors
            error = ', '.join(list(errors_dict.values())[0])

    return render_template(
        'challenges/index.html',
        title='Challenges',
        challenges=ordered_challenges,
        categories=categories, 
        solves=solves,
        solvers=solvers,
        team=bool(team),
        zeroadmin=current_user.user_is_admin,
        form=form,
        error=error
        )

@bp.route('/<string:challengename>', methods=['GET', 'POST'])
@cache.cached(timeout=5)
@login_required
def challenge(challengename:str):
    
    error = ''
    name = html.escape(challengename.strip())
    if any([not isinstance(name, str), name == '', name is None, not Challenge.found(name=name)]): abort(404)
    challenge:Challenge = Challenge.found(name=name)
    if challenge.challenge_is_hidden and not current_user.user_is_admin: abort(404)
    solver_list:list[User] = challenge.solved_by_users

    challenges:list[Challenge] = Challenge.select()
    categories = sorted(list(set([challenge.category for challenge in challenges])))

    if not current_user.user_is_admin:
        categories_challenges_hidden = sorted(list(set([challenge.category for challenge in challenges if challenge.challenge_is_hidden])))
        not_showing_categories = [c for c in categories_challenges_hidden if all([challenge.challenge_is_hidden for challenge in challenges if challenge.category == c])]
        [categories.remove(category) for category in not_showing_categories]

    users:list[User] = sorted(challenge.solved_by_users, key=lambda user: user.score, reverse=True)
    positions:dict = {}
    for user in users: positions[user.username] = User.position(username=user.username) 

    team:Team = current_user.team
    solved = False
    if bool(team):
        if challenge in team.solved_challenges:
            solved = True
    else:
        if challenge in current_user.solved_challenges:
            solved = True
    form = None
    if not solved:
        form:Form = SubmitFlag(formdata=request.form)
        if request.method == 'POST':
            if form.validate():
                valid = UserChallengeLink(challenge_id=challenge.id, user_id=current_user.id).add_challenge(input_flag=form.flag.data)
                if not valid:
                    if challenge.is_multiflag:
                        flags:list[MultiFlag] = MultiFlag.select()
                        for flag in flags:
                            if form.flag.data == flag.flag:
                                if User.update(username=current_user.username, user_is_banned=True):
                                    return redirect(url_for('user.user_profile', username=current_user.username))
                        if error == '':
                            error = 'Incorrect flag.'
                    else:
                        error = 'Incorrect flag.'
                else:
                    return redirect(url_for('user.user_profile', username=current_user.username))
            else:
                errors_dict = form.errors
                error = ', '.join(list(errors_dict.values())[0])
    
    return render_template(
        'challenges/challenge.html',
        title=name,
        is_hidden=challenge.challenge_is_hidden,
        id=challenge.id,
        challengename=name,
        description=challenge.description,
        file=challenge.file,
        url=challenge.url,
        points=challenge.value,
        solvers=solver_list,
        zeroadmin=current_user.user_is_admin,
        users=users,
        positions=positions,
        form=form,
        error=error,
        solved=solved,
        user_is_banned=current_user.user_is_banned
        )
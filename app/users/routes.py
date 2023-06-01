from flask import render_template, abort, redirect, url_for
from flask_login import login_required, current_user, logout_user
import html
import random
import os

from flask import Blueprint
bp = Blueprint('user', __name__, url_prefix='/user')
from app.models.user import User
from app.models.team import Team
from app.models.challenge import Challenge
from app.models.user_challenge_link import UserChallengeLink, TeamChallengeLink
from app.extensions import cache

basedir = os.path.abspath(os.path.dirname(__file__))
parentdir = os.path.abspath(os.path.join(basedir, os.pardir))
UPLOAD_FOLDER = os.path.join(parentdir, 'uploads', 'icons')

@bp.route('/scoreboard')
@cache.cached(timeout=5)
def scoreboard():
    users:list[User] = User.select()
    if len(users) == 0: users = []
    users = sorted(users, key=lambda user: user.score, reverse=True)
    positions:dict = {}
    for user in users: positions[user.username] = User.position(username=user.username)
    if current_user.is_authenticated: zeroadmin = current_user.user_is_admin
    else: zeroadmin = False
    return render_template('users/scoreboard.html', title='User Scoreboard', users=users, positions=positions, zeroadmin=zeroadmin)

@bp.route('/<string:username>')
@cache.cached(timeout=5)
@login_required
def user_profile(username:str):
    username = html.escape(username.strip())
    if any([not isinstance(username, str), username == '', username is None, not User.found(username=username)]): abort(404)
    user:User = User.found(username=username)
    if (not user.user_is_active or user.user_is_hidden) and not current_user.id == user.id: abort(404)
    users_count:int = User.count()
    user_position:int = User.position(username=username)
    user_solves:dict = Challenge.get_solves_count_by_category(foruser=True, username=username)
    user_has_solves = True if any(user_solves.values()) else False
    user_average:dict = Challenge.get_users_average_solves_by_category(users=[user for user in User.select() if user.user_is_active and not user.user_is_hidden])
    teams_count:int = Team.count()
    team:Team = user.team
    has_team:bool = bool(team)
    if has_team:
        teamname = team.teamname
        team_solves:dict = Challenge.get_solves_count_by_category(foruser=False, teamname=teamname)
        team_average:dict = Challenge.get_teams_average_solves_by_category(teams=[team for team in Team.select() if team.team_is_active and not team.team_is_hidden])
        team_position:int = Team.position(teamname=teamname)
        team_score:int = team.score
    else: team_solves = team_average = teamname = team_position = team_score = None
    category_challenges = Challenge.get_challenges_count_by_category()

    is_owner = current_user.username == username

    challenges:list[Challenge] = Challenge.select()
    categories = sorted(list(set([challenge.category for challenge in challenges])))

    if not current_user.user_is_admin:
        categories_challenges_hidden = sorted(list(set([challenge.category for challenge in challenges if challenge.challenge_is_hidden])))
        not_showing_categories = [c for c in categories_challenges_hidden if all([challenge.challenge_is_hidden for challenge in challenges if challenge.category == c])]
        [categories.remove(category) for category in not_showing_categories]

    solved:list[Challenge] = []
    for challenge in challenges:
        if challenge in user.solved_challenges: solved.append(challenge) 
    ordered_challenges:list[Challenge] = []
    for category in categories:
        for challenge in solved:
            if challenge in ordered_challenges: continue
            if challenge.category.lower() == category.lower(): ordered_challenges.append(challenge)

    solvers = {}
    for challenge in ordered_challenges:
        solvers[challenge.name]:list = [user] if challenge in user.solved_challenges else []

    return render_template(
        'users/profile.html', 
        title=f'User profile: {username}',
        users_count=users_count, 
        user_position=user_position,
        username=user.username,
        name=user.name,
        surname=user.surname,
        icon=user.icon,
        email=user.email,
        birthday=user.birthday,
        country=user.country,
        created=user.created_at.strftime('%d %B %Y'),
        last_logged_in=user.last_logged_in.strftime('%d %B %Y'),
        last_flag=user.last_flag.strftime('%d %B %Y') if user.last_flag else '',
        user_score=user.score,
        ctftime=user.ctftime,
        github=user.github,
        webpage=user.webpage,
        is_owner=is_owner,
        user_has_solves = user_has_solves,
        user_solves=user_solves, 
        user_average=user_average,
        has_team=has_team,
        teamname=teamname,
        teams_count=teams_count,
        team_position = team_position,
        team_solves=team_solves,        
        team_average=team_average,
        team_score=team_score,
        category_challenges=category_challenges,
        zeroadmin=current_user.user_is_admin,
        solvers=solvers,
        challenges=ordered_challenges,
        user_is_banned=user.user_is_banned
        )

@bp.route('/remove/<string:username>', methods=['GET'])
@login_required
def remove(username:str):

    username = html.escape(str(username.strip()))

    if any([username == '', username is None, not User.found(username=username)]): return abort(404)
    if (current_user.username != username) and not current_user.user_is_admin: abort(401)

    user:User = User.found(username=username)

    if bool(user.team):
        team:Team = Team.found(teamname=user.team.teamname)
        if user.team.leader_id == user.id:
            if len(team.members) > 1:
                newleader:User = random.choice(team.members)
                while newleader.id == user.id:
                    newleader:User = random.choice(team.members)
                Team.update_leader(newleader=newleader, teamname=team.teamname)
            else:
                if len(user.solved_challenges) > 0:
                    if not all([TeamChallengeLink.remove_challenge(teamname=user.team.teamname, challengename=challenge.name) for challenge in user.solved_challenges]): abort(400)
                Team.remove(username=username, teamname=team.teamname)
        else: Team.kickout_member(username=username, teamname=user.team.teamname)
        
    else:
        if len(user.solved_challenges) > 0:
            if not all([UserChallengeLink.remove_challenge(username=username, challengename=challenge.name) for challenge in user.solved_challenges]): abort(400)

    user_removed = User.remove(username=username)
    if user_removed: redirect(url_for('main.logout'))
    return redirect(url_for('user.user_profile', username=username))
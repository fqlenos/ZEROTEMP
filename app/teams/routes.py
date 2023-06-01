from flask import render_template, request, redirect, url_for, abort
from flask_login import current_user, login_required
import html
import time
import random

from flask import Blueprint
bp = Blueprint('team', __name__, url_prefix='/team')
from app.models.team import Team
from app.models.challenge import Challenge
from app.models.user import User
from app.extensions import cache
from app.models.team_challenge_link import TeamChallengeLink

@bp.route('/scoreboard')
@cache.cached(timeout=5)
def scoreboard():
    teams:list[Team] = Team.select()
    if len(teams) == 0: teams = []
    teams = sorted(teams, key=lambda team: team.score, reverse=True)
    if current_user.is_authenticated: zeroadmin = current_user.user_is_admin
    else: zeroadmin = False
    return render_template('teams/scoreboard.html', title='Team Scoreboard', teams=teams, zeroadmin=zeroadmin)

@bp.route('/<string:team>')
@cache.cached(timeout=5)
@login_required
def team_profile(team:str):
    teamname = html.escape(team.strip())
    if any([not isinstance(teamname, str), teamname == '', teamname is None, not Team.found(teamname=teamname)]): abort(404)
    team:Team = Team.found(teamname=teamname)
    if not team.team_is_active or team.team_is_hidden: abort(404)
    teams_count:int = Team.count()
    team_position:int = Team.position(teamname=teamname)
    team_solves:dict = Challenge.get_solves_count_by_category(foruser=False, teamname=teamname)
    team_average:dict = Challenge.get_teams_average_solves_by_category(teams=Team.select())
    category_challenges = Challenge.get_challenges_count_by_category()

    leader_id = team.leader_id
    if bool(current_user.team): is_admin = team.leader_id == current_user.id
    else: is_admin = False

    challenges:list[Challenge] = Challenge.select()
    categories = sorted(list(set([challenge.category for challenge in challenges])))
    solved:list[Challenge] = []

    for challenge in challenges:
        if challenge in team.solved_challenges: solved.append(challenge) 
    ordered_challenges:list[Challenge] = []
    for category in categories:
        for challenge in solved:
            if challenge in ordered_challenges: continue
            if challenge.category.lower() == category.lower(): ordered_challenges.append(challenge)

    solvers = {}
    for challenge in ordered_challenges:
        solvers[challenge.name]:list = [user for user in challenge.solved_by_users if user in team.members]
    
    return render_template(
        'teams/profile.html', 
        title=f'Team profile: {teamname}',
        users_count=None, 
        user_position=None,
        username=None,
        user_has_solves = None,
        user_solves=None, 
        user_average=None,
        has_team=True,
        is_admin=is_admin,
        teamname=teamname,
        teams_count=teams_count,
        team_position = team_position,
        team_solves=team_solves,        
        team_average=team_average,
        category_challenges=category_challenges,
        email=team.email,
        ctftime=team.ctftime,
        webpage=team.webpage,
        github=team.github,
        country=team.country,
        team_score=team.score,
        members=team.members,
        me=current_user.username,
        leader_id=leader_id,
        zeroadmin=current_user.user_is_admin,
        challenges=ordered_challenges,
        solvers=solvers
        )

@bp.route('/join-create', methods=['GET', 'POST'])
@login_required
def join_create():
    if current_user.team is not None: return redirect(url_for('team.team_profile', team=current_user.teamname))
    if request.method == 'POST':
        form_id = request.form['form_id']

        if form_id == 'join':
            teamname = str(request.form['teamname'])
            password = str(request.form['password'])
            
            if any([teamname == '', password == '']):
                return render_template('teams/join_create.html', title='Join Team', error='Username/password cannot be empty.', join=True)

            verified = Team.verify(teamname=teamname, password=password)
            if not verified:
                return render_template('teams/join_create.html', title='Join Team', error='Incorrect teamname/password.', join=True)
            
            team_added = Team.add_member(teamname=teamname, username=current_user.username)
            if not team_added:
                return render_template('teams/join_create.html', title='Join Team', error='Try with a different teamname/password.', join=True)
            
            return redirect(url_for('team.team_profile', team=teamname))

        elif form_id == 'create':

            teamname = str(request.form['teamname'])
            password = str(request.form['password'])
            re_password = str(request.form['password2'])

            if any([teamname == '', password == '', re_password == '']): 
                return render_template('teams/join_create.html', title='Create Team', error='Teamname/password cannot be empty.', create=True)
            elif password != re_password: 
                return render_template('teams/join_create.html', title='Create Team', error='Passwords are not the same.', create=True)
            
            team_added = Team.add_team(teamname=teamname, username=current_user.username, password=password)
            if not team_added:
                return render_template('teams/join_create.html', title='Join Team', error='Try with a different teamname/password.', create=True)
            return redirect(url_for('team.team_profile', team=teamname))
    
    return render_template('teams/join_create.html', title='Join or Create Team', join=True)

@bp.route('/kickout/<string:teamname>/<string:username>', methods=['GET'])
@login_required
def kickout(teamname:str, username:str):
    
    teamname = html.escape(str(teamname.strip()))
    username = html.escape(str(username.strip()))

    if any([teamname == '', teamname is None, username == '', username is None, not Team.found(teamname=teamname), not User.found(username=username)]): return abort(404)
    
    user:User = User.found(username=username)
    if not bool(user.team): abort(404)
    team:Team = Team.found(teamname=teamname)
    if ((team.leader_id != current_user.id) or (team.id != user.team_id)) and not current_user.user_is_admin: abort(401)

    if len(team.solved_challenges) > 0:
        if not all([TeamChallengeLink.remove_challenge(teamname=teamname, challengename=challenge.name) for challenge in user.solved_challenges]): abort(400)
    
    if user.team.leader_id == user.id:
        if len(team.members) > 1:
            newleader:User = random.choice(team.members)
            while newleader.id == user.id:
                newleader:User = random.choice(team.members)
            Team.update_leader(newleader=newleader, teamname=team.teamname)
            Team.kickout_member(username=user.username, teamname=user.team.teamname)
        else:
            if len(team.solved_challenges) > 0:
                if not all([TeamChallengeLink.remove_challenge(teamname=user.team.teamname, challengename=challenge.name) for challenge in user.solved_challenges]): abort(400)
            Team.remove(username=user.username, teamname=team.teamname)
    else:
        Team.kickout_member(username=username, teamname=teamname)
        team:Team = Team.found(teamname=teamname)
        if len(team.members) == 0:
            removed = Team.remove(teamname=teamname, username=username)
            if not removed: return redirect(url_for('team.team_profile', team=teamname))
    
    time.sleep(2)
    return redirect(url_for('team.scoreboard', team=teamname))

@bp.route('/remove/<string:teamname>/<string:username>', methods=['GET'])
@login_required
def remove(teamname:str, username:str):

    teamname = html.escape(str(teamname.strip()))
    username = html.escape(str(username.strip()))

    if any([teamname == '', teamname is None, username == '', username is None, not Team.found(teamname=teamname), not User.found(username=username)]): return abort(404)
    if (current_user.username != username) and not current_user.user_is_admin: abort(401)

    team:Team = Team.found(teamname=teamname)
    if (team.leader_id != current_user.id) and not current_user.user_is_admin: abort(401)
    if not current_user.user_is_admin:
        user:User = User.found(username=username)
        if not bool(user.team): abort(404)
        if len(user.solved_challenges) > 0:
            if not all([TeamChallengeLink.remove_challenge(teamname=teamname, challengename=challenge.name) for challenge in user.solved_challenges]): abort(400)
        
    removed = Team.remove(teamname=teamname, username=username)
    if not removed: return redirect(url_for('team.team_profile', team=teamname))

    return redirect(url_for('team.scoreboard', team=teamname))
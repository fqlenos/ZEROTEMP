from flask import Flask, redirect, url_for, jsonify, send_from_directory
from flask_login import LoginManager, login_required
import os

import config
from .extensions import db, cache, limiter
from .models.user import User
from .models.ctf import CTF

login_manager = LoginManager()

def create_app(profile=config.Production):

    os.makedirs(os.path.join(config.Config.UPLOAD_FOLDER, config.UPLOAD_USER_FOLDER), exist_ok=True)
    os.makedirs(os.path.join(config.Config.UPLOAD_FOLDER, config.UPLOAD_SPONSOR_FOLDER), exist_ok=True)
    os.makedirs(os.path.join(config.Config.UPLOAD_FOLDER, config.UPLOAD_CHALLENGE_FOLDER), exist_ok=True)
    os.makedirs(os.path.join(config.Config.DOWNLOAD_FOLDER, config.DOWNLOAD_CTF_FOLDER), exist_ok=True)

    app = Flask(__name__, static_folder='static')
    app.config.from_object(profile)

    # Initialize Flask extensions
    db.init_app(app)
    cache.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    
    with app.app_context():
        if profile == config.Development:
            db.drop_all()
        db.create_all()
        CTF.add(name=config.CTFNAME)
        User.add_user(username='admin', password='admin', admin=True, hidden=True)

    # Loading users for LoginManager
    @login_manager.user_loader
    def load_user(user_id):
        #app.logger.debug(f"Loading user with ID {user_id}")
        user_found = User.found(username=user_id)
        if not user_found or not user_found.user_is_active:
            #app.logger.debug(f"User with ID {user_id} not found")
            return None
        return user_found
    
    # Redirect to login the unauthorized
    @login_manager.unauthorized_handler
    def unauthorized_handler():
        return redirect(url_for('main.login'))
    
    # Redirect to login the 404
    @app.errorhandler(404)
    def page_not_found(e):
        return redirect(url_for('main.login'))
    
    # Redirect to login the 500
    @app.errorhandler(500)
    def internal_server_error(e):
        return redirect(url_for('main.login'))
    
    # Handle 429 Too Many Requests
    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify({'Error': 'Too many requests per minute. Max 1 or 10 requests per second.'}), 429
    
    @app.route('/uploads/user/<path:filename>')
    def serve_user_img(filename):
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], config.UPLOAD_USER_FOLDER), filename)
    
    @app.route('/uploads/sponsor/<path:filename>')
    def serve_sponsor_img(filename):
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], config.UPLOAD_SPONSOR_FOLDER), filename)
    
    @app.route('/uploads/challenge/<path:filename>')
    def serve_challenge_file(filename):
        return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], config.UPLOAD_CHALLENGE_FOLDER), filename)
    
    from app.main.routes import bp as main_bp
    from app.challenges.routes import bp as challenge_bp
    from app.teams.routes import bp as teams_bp
    from app.users.routes import bp as users_bp
    from app.edit.routes import bp as edit_bp
    from app.api.routes import bp as api_bp
    from app.management.routes import bp as management_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(challenge_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(edit_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(management_bp)

    return app
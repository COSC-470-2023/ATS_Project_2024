from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, LoginManager, login_required, current_user
from .models import Users
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()

        if user:
            if user.password == password:
                flash('Login successful', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.configuration'))
            else:
                flash('error', category='error')
        else:
                flash('No user found', category='error')   


        # for user in users:
        #     print(user.username)
        #     if user.username == username:
        #         if user.password == password:
        #             flash('Login successful', category='success')
        #             login_user(user, remember=True)
        #             return redirec
        #         else:
        #             flash('error', category='error')
        #     else:
        #         flash('No user found', category='error')   

        # Check for matching username and password in DB
        
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/create-user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        first_name = request.form.get('first-name')
        last_name = request.form.get('last-name')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if password1 != password2:
            pass

    return render_template('create_user.html')
    


# from flask import Flask, render_template, request, url_for, redirect
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import login_user, logout_user, LoginManager, login_required, current_user, UserMixin
# from flask_bcrypt import Bcrypt
# from sqlalchemy import text

# import sys
# sys.path.insert(0, './database/processing')
# import connect as conn

# app = Flask(__name__)
# bcrypt = Bcrypt
# app.config['SECRET_KEY'] = 'secretkey'
# db = conn.connect()
# app.app_context().push()

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "login"

# @login_manager.user_loader
# def load_user(user_id):
#     return Authorized_users.query.get(int(user_id))

# @app.route('/login', methods = ['POST', 'GET'])
# def login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get("password")
        
#         user = Authorized_users.query.filter_by(username=username).first()

#         if user and user.password == password:
#             login_user(user)
#             return redirect(url_for("configuration"))
#         else: 
#             redirect(url_for("configuration"))
#     return render_template('index.html')

# @app.route('/configuration')
# @login_required
# def configuration():
#     return render_template('configuration.html')

# # @app.route('/logout')
# # @login_required
# # def logout():
# #     logout_user()
# #     return redirect(url_for())

# if __name__ == '__main__':
#     app.run(debug=True)
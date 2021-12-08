from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
import os

app = Flask(__name__)



app.secret_key = 'keyhere'
csrf = CSRFProtect(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "Database"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'harshata@email.com'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN') 

     
     
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'

app.config['UPLOAD_FOLDER'] = "Folder_path"
app.config['RECAPTCHA_PUBLIC_KEY']='key_here'
app.config['RECAPTCHA_PRIVATE_KEY']='key_here'



from main import routes
from main.models import *


@app.context_processor
def inject_permissions():
    return dict(Permission=Permission)



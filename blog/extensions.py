from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_moment import Moment
from flask_whooshee import Whooshee
from flask_redis import FlaskRedis


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
bootstrap = Bootstrap()
ckeditor  = CKEditor()
moment = Moment()
whooshee = Whooshee()
redis_store = FlaskRedis()


login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
# login_manager.login_message = ''

@login_manager.user_loader
def user_loader(user_id):
	from blog.models import Admin
	admin = Admin.query.filter_by(id=int(user_id)).first()
	return admin

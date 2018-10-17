import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URL
WIN = sys.platform.startswith('win')
if WIN:
	prefix = 'sqlite:///'
else:
	prefix = 'sqlite:////'



class BaseConfig(object):
	SECRET_KEY = os.getenv('SECRET_KEY', 'my secret key')

	DEBUG_TB_INTERCEPT_REDIRECTS = False

	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SQLALCHEMY_RECORD_QUERIES = True

	# MAIL_SERVER = os.getenv('MAIL_SERVER')
	# MAIL_PORT = 465
	# MAIL_USE_SSL = True
	# MAIL_USERNAME = os.getenv('MAIL_USERNAME')
	# MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
	# MAIL_DEFAULT_SENDER = ('Blog Admin', MAIL_USERNAME)

	# BLOG_EMAIL = os.getenv('BLOG_EMAIL')
	
	BLOG_POST_PER_PAGE = 5
	BLOG_MANAGE_POST_PER_PAGE = 15
	BLOG_COMMENT_PER_PAGE = 8
	BLOG_MANAGE_POST_PER_PAGE = 15



class DevelopmentConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data-dev.db')
	REDIS_URL = "redis://localhost:6379/0"


class ProductionConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))
	REDIS_URL = os.getenv('REDIS_URL', "redis://localhost:6379/0")
	
class TestingConfig(BaseConfig):
	Testing = True
	WTF_CSRF_ENABLED = False
	SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory'

config = {
	'development': DevelopmentConfig,
	'production': ProductionConfig,
	'testing': TestingConfig
}
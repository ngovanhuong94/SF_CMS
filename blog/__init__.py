import os
import click

from flask import Flask, render_template
from flask_login import current_user
from blog.blueprints.auth import auth_bp
from blog.blueprints.blog import blog_bp
from blog.blueprints.admin import admin_bp

from blog.extensions import db, migrate, csrf, bootstrap, login_manager, ckeditor, moment, whooshee, redis_store
from blog.models import Admin, Post, Comment, Tag, Category, Link
from blog.settings import config
from flask_wtf.csrf import CSRFError

def create_app(config_name=None):
	app = Flask(__name__)
	if config_name == None:
		config_name = os.getenv('FLASK_CONFIG', 'development')
	app.config.from_object(config[config_name])

	register_extensions(app)
	register_commands(app)
	register_context_processors(app)
	register_errors(app)
	register_blueprints(app)

	return app

def register_extensions(app):
	bootstrap.init_app(app)
	db.init_app(app)
	csrf.init_app(app)
	login_manager.init_app(app)
	migrate.init_app(app, db)
	ckeditor.init_app(app)
	moment.init_app(app)
	whooshee.init_app(app)
	redis_store.init_app(app)


def register_blueprints(app):
	app.register_blueprint(auth_bp, url_prefix='/auth')
	app.register_blueprint(blog_bp)
	app.register_blueprint(admin_bp, url_prefix='/admin')

def register_context_processors(app):
	@app.context_processor
	def make_template_context():
		admin = Admin.query.first()
		categories = Category.query.order_by(Category.id.desc()).all()
		tags = Tag.query.order_by(Tag.id.desc()).all()
		links = Link.query.order_by(Link.id.desc()).all()
		popular_ids = redis_store.zrange('posts', 0, -1, desc=True)[:3]
		post_ids = []
		for id in popular_ids:
			post_ids.append(int(id))

		popular_posts = Post.query.filter(Post.id.in_(post_ids)).all()

		if current_user.is_authenticated:
			unread_comments = Comment.query.filter_by(reviewed=False).count()
		else:
			unread_comments = None
		return dict(admin=admin, categories=categories, tags=tags, links=links, unread_comments=unread_comments, popular_posts=popular_posts)

def register_commands(app):
	@app.cli.command()
	@click.option('--username', prompt=True, help='The admin username to login')
	@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The pasword used to login')
	def init(username, password):
		"""Building the Blog for you"""
		click.echo('Initialize the database')
		db.create_all()

		admin = Admin.query.first()

		if admin:
			click.echo('The administrator already exists, updating...')
			admin.username = username
			admin.set_password(password)
		else:
			click.echo('Create the administrator ...')
			admin = Admin(
				username=username,
				blog_title='KeepSimple',
				blog_sub_title='You can add your description here',
				name='Huong',
				about='This is my blog'
			)
			admin.set_password(password)
			db.session.add(admin)
			db.session.commit()
			click.echo('Done')
	
	@app.cli.command()
	@click.option('--category', default=10, help='Quantity of categories, default is 10.')
	@click.option('--post', default=50, help='Quantity of categories, default is 10.')
	@click.option('--tag', default=10, help='Quantity of categories, default is 10.')
	@click.option('--comment', default=500, help='Quantity of categories, default is 10.')
	def forge(category, post, tag, comment):
		"""Generate fake data."""
		from blog.fakes import fake_admin, fake_posts, fake_categories, fake_tags, fake_links, fake_comments

		db.drop_all()
		db.create_all()

		click.echo('Generating the administrator...')
		fake_admin()

		click.echo('Generating the categories...')
		fake_categories()

		click.echo('Generating the tags...')
		fake_tags()

		click.echo('Generating the posts...')
		fake_posts()

		click.echo('Generating the comments...')
		fake_comments()

		click.echo('Generating the links...')
		fake_links()

		click.echo('Done.')


def register_errors(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400





	

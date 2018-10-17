from datetime import datetime
from blog.extensions import db, whooshee
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify
import sqlalchemy as sa
from random import choice
from hashlib import md5


tags_posts = db.Table(
		'tags',
		db.Column('tag_id', db.ForeignKey('tag.id')),
		db.Column('post_id', db.ForeignKey('post.id'))
	)

class Admin(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True)
	email = db.Column(db.String(60), unique=True)
	password_hash = db.Column(db.String(128))
	blog_title = db.Column(db.String(60))
	blog_sub_title = db.Column(db.String(100))
	name = db.Column(db.String(30))
	about = db.Column(db.Text)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def validate_password(self, password):
		return check_password_hash(self.password_hash, password)


class Category(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(40), unique=True)
	description = db.Column(db.String(300), default='')

	slug = db.Column(db.String(50), unique=True)

	posts = db.relationship('Post', back_populates='category')

	def delete(self):
		default_category = Category.query.first()
		posts = self.posts[:]
		for post in posts:
			post.category = default_category
		db.session.delete(self)
		db.session.commit()

	def __str__(self):
		return self.name

@sa.event.listens_for(Category, 'before_insert')
def init_category_slug(mapper, connection, target):
	if target.slug:
		return
	target.slug = slugify(target.name)

@whooshee.register_model('title', 'body')
class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100))
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)
	description = db.Column(db.Text, default='')
	body = db.Column(db.Text)
	can_comment = db.Column(db.Boolean, default=True)
	# image = db.Column(db.String(400))
	is_draft = db.Column(db.Boolean, default=False)
	slug = db.Column(db.String(110))

	category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

	tags = db.relationship('Tag', secondary=tags_posts, back_populates='posts')
	category = db.relationship('Category', back_populates='posts')
	comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')
	
	
	
	@property
	def url(self):
		return '/%d/%02d-%02d/%s' % (self.timestamp.year, self.timestamp.month, self.timestamp.day, self.slug)

	@property
	def previous(self):
		return Post.query.order_by(Post.id.desc()).filter(Post.id < self.id).first()
	
	@property
	def next(self):
		return Post.query.order_by(Post.id.asc()).filter(Post.id > self.id).first()

	@property
	def related_post(self):
		posts = Post.query.join(Post.tags).filter(
			Tag.id.in_([tag.id for tag in self.tags]),
			Post.id != self.id, ~Post.is_draft
			)
		if posts.count() > 0:
			return choice(posts.all())
			 
@sa.event.listens_for(Post, 'before_insert')
def init_post_slug(mapper, connection, target):
	if target.slug:
		return
	target.slug = slugify(target.title)


class Tag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(40), unique=True)
	description = db.Column(db.String(300), default='')
	slug = db.Column(db.String(50), unique=True)
	posts = db.relationship('Post', secondary=tags_posts, back_populates='tags')

	@property
	def heat(self):
		return self.posts.count()

	def __str__(self):
		return self.name

@sa.event.listens_for(Tag, 'before_insert')
def init_tag_slug(mapper, connection, target):
	if target.slug:
		return
	target.slug = slugify(target.name)

class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String(30))
	email = db.Column(db.String(254))
	site = db.Column(db.String(254))
	body = db.Column(db.Text)
	from_admin = db.Column(db.Boolean, default=False)
	reviewed = db.Column(db.Boolean, default=False)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

	post = db.relationship('Post', back_populates='comments')

	def avatar(self, size):
	    digest = md5(self.author.lower().encode('utf-8')).hexdigest()
	    return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
	        digest, size)


class Link(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30))
	url = db.Column(db.String(255))
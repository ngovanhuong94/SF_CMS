import random
from faker import Faker
from sqlalchemy.exc import IntegrityError

from blog import db
from blog.models import Admin, Comment, Category, Link, Tag, Post

faker = Faker()

def fake_admin():
	admin = Admin(
			username='admin',
			blog_title='KeepSimple',
			blog_sub_title='You can add your description here',
			name='Huong',
			about='This is my blog'
		)
	admin.set_password('123456')
	db.session.add(admin)
	db.session.commit()

def fake_categories(count=10):
	category = Category(name='Default')
	db.session.add(category)

	for i in range(count):
		category = Category(name=faker.word(), description=faker.text(200))
		db.session.add(category)
	db.session.commit()


def fake_tags(count=10):
	for i in range(count):
		tag = Tag(name=faker.word(), description=faker.text(200))
		db.session.add(tag)
	db.session.commit()

def fake_posts(count=50):
	for i in range(count):
		post = Post(
			title=faker.sentence(),
			description=faker.text(300),
			body=faker.text(2000),
			timestamp=faker.date_time_this_year(),
			category=Category.query.get(random.randint(1, Category.query.count()))
		)
		for j in range(random.randint(1, 5)):
			tag = Tag.query.get(random.randint(1, Tag.query.count()))
			if tag not in post.tags:
				post.tags.append(tag)

		db.session.add(post)
	db.session.commit()



def fake_comments(count=500):
	for i in range(count):
		comment = Comment(
			author=faker.name(),
			email=faker.email(),
			site=faker.url(),
			body=faker.sentence(),
			timestamp=faker.date_time_this_year(),
			reviewed=True,
			post=Post.query.get(random.randint(1, Post.query.count()))
			)
		db.session.add(comment)
	salt = int(count*0.2)

	for i in range(salt):
		#unreviewed comments
		comment = Comment(
			author=faker.name(),
			email=faker.email(),
			site=faker.url(),
			body=faker.sentence(),
			timestamp=faker.date_time_this_year(),
			reviewed=False,
			post=Post.query.get(random.randint(1, Post.query.count()))
		)
		db.session.add(comment)
		# from admin
		comment = Comment(
			author='Admin',
			email='Admin@example.com',
			site='example.com',
			body=faker.sentence(),
			from_admin=True,
			timestamp=faker.date_time_this_year(),
			reviewed=True,
			post=Post.query.get(random.randint(1, Post.query.count()))
		)

		db.session.add(comment)
	db.session.commit()

def fake_links():
    twitter = Link(name='Twitter', url='#')
    facebook = Link(name='Facebook', url='#')
    linkedin = Link(name='LinkedIn', url='#')
    google = Link(name='Google+', url='#')
    db.session.add_all([twitter, facebook, linkedin, google])
    db.session.commit()
	
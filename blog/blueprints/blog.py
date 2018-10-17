from flask import render_template, Blueprint, current_app, request, flash, url_for, redirect
from blog.models import Post, Category, Tag, Comment, Link
from blog.extensions import redis_store, db
from blog.utils import redirect_back
from flask_login import current_user
from datetime import datetime

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
	page = request.args.get('page', 1, type=int)
	per_page = current_app.config['BLOG_POST_PER_PAGE']
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page, False)
	posts = pagination.items
	next_url = url_for('blog.index', page=pagination.next_num) if pagination.has_next else None
	prev_url = url_for('blog.index', page=pagination.prev_num) if pagination.has_prev else None
	return render_template('blog/index.html', posts=posts, pagination=pagination, next_url=next_url, prev_url=prev_url)

@blog_bp.route('/post/<slug>', methods=['GET', 'POST'])
def single_post(slug):
	post = Post.query.filter_by(slug=slug).first_or_404()
	page = request.args.get('page', 1, type=int)
	per_page = current_app.config['BLOG_COMMENT_PER_PAGE']
	redis_store.zincrby('posts', post.id)
	views = redis_store.zscore('posts', post.id)
	pagination = Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.desc()).paginate(page, per_page)
	comments = pagination.items
	next_url = url_for('blog.single_post', slug=slug, page=pagination.next_num) if pagination.has_next else None
	prev_url = url_for('blog.single_post', slug=slug, page=pagination.prev_num) if pagination.has_prev else None
	if request.method == 'POST':
		if current_user.is_authenticated:
			if request.form['message'] != '':
				comment = Comment(
					author='Admin',
					email='Admin@example.com',
					site='example.com',
					body=request.form['message'],
					from_admin=True,
					reviewed=True,
					post=post
				)
				db.session.add(comment)
				db.session.commit()

				# flash('Comment published.', 'success')
				return redirect(url_for('blog.single_post', slug=slug))
		else:
			if request.form['message'] != '' and request.form['author'] != '':
				comment = Comment(
					author=request.form['author'],
					email=request.form['email'],
					site=request.form['site'],
					body=request.form['message'],
					reviewed=False,
					post=post
				)

				db.session.add(comment)
				db.session.commit()

				# flash('Thanks, your comment will be published after reviewed.', 'info')
				return redirect(url_for('blog.single_post', slug=slug))

	return render_template('blog/single_post.html', post=post, views=int(views), comments=comments, next_url=next_url, prev_url=prev_url, pagination=pagination)


@blog_bp.route('/category/<slug>')
def show_category(slug):
	category = Category.query.filter_by(slug=slug).first_or_404()
	page = request.args.get('page',1 ,type=int)
	per_page = current_app.config['BLOG_POST_PER_PAGE']
	pagination = Post.query.filter_by(category_id=category.id).order_by(Post.timestamp.desc()).paginate(page, per_page)
	posts = pagination.items
	next_url = url_for('blog.show_category', slug=slug, page=pagination.next_num) if pagination.has_next else None
	prev_url = url_for('blog.show_category', slug=slug, page=pagination.prev_num) if pagination.has_prev else None

	return render_template('blog/show_category.html', category=category, posts=posts, next_url=next_url, prev_url=prev_url)


@blog_bp.route('/tag/<slug>')
def show_tag(slug):
	tag = Tag.query.filter_by(slug=slug).first_or_404()
	page = request.args.get('page',1 ,type=int)
	per_page = current_app.config['BLOG_POST_PER_PAGE']
	ids = [post.id for post in tag.posts]
	pagination = Post.query.filter(Post.id.in_(ids)).paginate(page, per_page)
	posts = pagination.items

	next_url = url_for('blog.show_tag', slug=slug,page=pagination.next_num) if pagination.has_next else None
	prev_url = url_for('blog.show_tag', slug=slug,page=pagination.prev_num) if pagination.has_prev else None

	return render_template('blog/show_tag.html', tag=tag, posts=posts, next_url=next_url, prev_url=prev_url)


@blog_bp.route('/search')
def search():
	q = request.args.get('q', '')
	if q == '':
		flash('Enter key word about post')
		return redirect_back()
	page = request.args.get('page',1 ,type=int)
	per_page = current_app.config['BLOG_POST_PER_PAGE']
	pagination = Post.query.whooshee_search(q).order_by(Post.timestamp.desc()).paginate(page, per_page)
	posts = pagination.items
	next_url = url_for('blog.search', q=q, page=pagination.next_num) if pagination.has_next else None
	prev_url = url_for('blog.search', q=q, page=pagination.prev_num) if pagination.has_prev else None

	return render_template('blog/search.html', q=q, posts=posts, pagination=pagination,next_url=next_url, prev_url=prev_url)


@blog_bp.route('/about')
def about():
	return render_template('blog/about.html')
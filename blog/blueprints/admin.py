from flask import render_template, Blueprint, redirect, url_for, current_app, request, flash
from flask_login import login_required, current_user
from blog.forms import SettingForm, PostForm, CategoryForm, TagForm, LinkForm, get_redirect_target, is_safe_url
from blog.extensions import db
from blog.models import Post, Category, Tag, Comment, Link
from blog.utils import redirect_back

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
	form = SettingForm()
	if form.validate_on_submit():
		current_user.name = form.name.data
		current_user.blog_title = form.blog_title.data
		current_user.blog_sub_title = form.blog_sub_title.data
		current_user.about = form.about.data
		db.session.commit()
		flash('Setting updated.', 'success')
		return redirect(url_for('blog.index'))
	form.name.data = current_user.name
	form.blog_title.data = current_user.blog_title
	form.blog_sub_title.data = current_user.blog_sub_title
	form.about.data = current_user.about
	return render_template('admin/settings.html', form=form)

@admin_bp.route('/category/manage')
@login_required
def manage_category():
	return render_template('admin/manage_category.html')

@admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
	form = CategoryForm()
	if form.validate_on_submit():
		category = Category(name=form.name.data)
		db.session.add(category)
		db.session.commit()
		flash('Category created', 'success')
		return redirect('admin.manage_category')
	return render_template('admin/new_category.html', form=form)


@admin_bp.route('/category/<int:category_id>/edit')
@login_required
def edit_category(category_id):
	category = Category.query.get_or_404(category_id)
	if category.id == 1:
		flash('Cannot edit default category.', 'warning')
		return redirect(url_for('admin.manage_category'))
	form = CategoryForm()
	if form.validate_on_submit():
		category.name = form.name.data
		db.session.commit()
		flash('Category created', 'success')
		return redirect(url_for('admin.manage_category'))
	form.name.data = category.name
	return render_template('admin/edit_category.html', form=form)


@admin_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
	category = Category.query.get_or_404(category_id)
	if category.id == 1:
		flash('you cannot delete default category.', 'warning')
		return redirect(url_for('admin.manage_category'))
	db.session.delete(category)
	db.session.commit()
	flash('Category deleted.', 'success')
	return redirect(url_for('admin.manage_category'))

@admin_bp.route('/tag/manage')
@login_required
def manage_tag():
	return render_template('admin/manage_tag.html')

@admin_bp.route('/tag/new', methods=['GET', 'POST'])
@login_required
def new_tag():
	form = TagForm()
	if form.validate_on_submit():
		tag = Tag(name=form.name.data)
		db.session.add(tag)
		db.session.commit()
		flash('Tag created.', 'success')
		return redirect(url_for('admin.manage_tag'))
	return render_template('admin/new_tag.html', form=form)

@admin_bp.route('/tag/<int:tag_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_id):
	tag = Tag.query.get_or_404(tag_id)
	form = TagForm()
	if form.validate_on_submit():
		tag.name = form.name.data
		flash('Tag updated.', 'info')
		db.session.commit()
		return redirect(url_for('admin.manage_tag'))
	form.name.data = tag.name
	return render_template('admin/edit_tag.html', form=form)


@admin_bp.route('/tag/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(tag_id):
	tag = Tag.query.get_or_404(tag_id)
	db.session.delete(tag)
	db.session.commit()
	flash('Tag deleted.', 'success')
	return redirect(url_for('admin.manage_tag'))


@admin_bp.route('/post/manage')
@login_required
def manage_post():
	q = request.args.get('q')
	per_page = current_app.config['BLOG_MANAGE_POST_PER_PAGE']
	page = request.args.get('page', 1, type=int)
	if q == '' or q == None:
		pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page)
	else:
		pagination = Post.query.whooshee_search(q).order_by(Post.timestamp.desc()).paginate(page, per_page)
	
	
	posts = pagination.items
	return render_template('admin/manage_post.html', page=page, pagination=pagination, posts=posts, q=q)

@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		category = Category.query.filter_by(id=form.category.data).first()
		tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()

		post = Post(
			title=form.title.data,
			body=form.body.data,
			category=category,
			tags=tags,
			can_comment=form.can_comment.data,
			is_draft=form.is_draft.data,
			timestamp=form.publish.data
		)

		db.session.add(post)
		db.session.commit()
		flash('Post created.', 'success')
		return redirect(url_for('.manage_post'))
	return render_template('admin/new_post.html', form=form)

@admin_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
	post = Post.query.get_or_404(post_id)
	form = PostForm()
	if form.validate_on_submit():
		category = Category.query.filter_by(id=form.category.data).first()
		tags = Tag.query.filter(Tag.id.in_(form.tags.data)).all()
		post.title = form.title.data
		post.body = form.body.data
		post.category = category
		post.tags = tags
		post.can_comment = form.can_comment.data
		post.is_draft = form.is_draft.data
		post.timestamp = form.publish.data
		db.session.commit()
		flash('Post updated.', 'success')
		return redirect(url_for('admin.manage_post'))

	form.title.data = post.title
	form.body.data = post.body
	form.category.data = post.category.id
	form.tags.data = [tag.id for tag in post.tags]
	form.can_comment.data = post.can_comment
	form.is_draft.data = post.is_draft
	form.publish.data = post.timestamp

	return render_template('admin/edit_post.html', form=form)



@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	db.session.delete(post)
	db.session.commit()
	flash('Post deleted.', 'success')
	return redirect(url_for('admin.manage_post'))


@admin_bp.route('/link/manage')
@login_required
def manage_link():
	return render_template('admin/manage_link.html')

@admin_bp.route('/link/new', methods=['GET', 'POST'])
@login_required
def new_link():
	form = LinkForm()
	if form.validate_on_submit():
		link = Link(name=form.name.data, url=form.url.data)
		db.session.add(link)
		db.session.commit()
		flash('Link created.', 'success')
		return redirect(url_for('admin.manage_link'))
	return render_template('admin/new_link.html')

@admin_bp.route('/link/<int:link_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_link(link_id):
	link = Link.query.get_or_404(link_id)
	form = LinkForm()
	if form.validate_on_submit():
		link.name = form.name.data
		link.url = form.url.data
		db.session.commit()
		flash('Link updated')
		return redirect(url_for('admin.manage_link'))
	form.name.data = link.name
	form.url.data = link.url
	return render_template('admin/edit_link.html', form=form)


@admin_bp.route('/link/<int:link_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_link(link_id):
	link = Link.query.get_or_404(link_id)
	db.session.delete(link)
	db.session.commit()
	flash('Link deleted.', 'success')
	return redirect(url_for('admin.manage_link'))


@admin_bp.route('/comment/manage')
@login_required
def manage_comment():
	filter = request.args.get('filter', 'all')
	page = request.args.get('page', 1, type=int)
	per_page = current_app.config['BLOG_MANAGE_POST_PER_PAGE']

	if filter == 'all':
		query = Comment.query.order_by(Comment.timestamp.desc())
	if filter == 'unread':
		query = Comment.query.filter_by(reviewed=False).order_by(Comment.timestamp.desc())
	if filter == 'from_admin':
		query = Comment.query.filter_by(from_admin=True).order_by(Comment.timestamp.desc())


	pagination = query.paginate(page, per_page=per_page)
	comments = pagination.items
	return render_template('admin/manage_comment.html', pagination=pagination, filter=filter, comments=comments)


@admin_bp.route('/comment/<int:comment_id>/approve', methods=['POST'])
@login_required
def approve_comment(comment_id):
	comment = Comment.query.get_or_404(comment_id)
	comment.reviewed = True
	db.session.commit()
	flash('Comment approved.', 'info')
	return redirect_back()

@admin_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
	comment = Comment.query.get_or_404(comment_id)
	db.session.delete(comment)
	db.session.commit()
	flash('Comment deleted.', 'info')
	return redirect_back()





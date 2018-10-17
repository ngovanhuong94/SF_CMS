from datetime import datetime
from flask import request, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, HiddenField, SelectField, SelectMultipleField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin
from flask_ckeditor import CKEditorField
from blog.models import Post, Category, Tag, Link

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


class RedirectForm(FlaskForm):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))
        
class LoginForm(RedirectForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember me')
	submit = SubmitField('Log in')


class SettingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 70)])
    blog_title = StringField('Blog Title', validators=[DataRequired(), Length(1, 60)])
    blog_sub_title = StringField('Blog Sub Title', validators=[DataRequired(), Length(1, 100)])
    about = CKEditorField('About Page', validators=[DataRequired()])
    submit = SubmitField()


class PostForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired(), Length(1, 100)])
	category = SelectField('Category', coerce=int, default=1)
	tags = SelectMultipleField('Tags', coerce=int)
	description = TextAreaField('Description (will show on index page)')
	publish = DateTimeField('Publish Time', default=datetime.utcnow)
	is_draft = BooleanField('is draft')
	can_comment = BooleanField('allow comment')

	body = CKEditorField('Body', validators=[DataRequired()])
	submit = SubmitField()

	def __init__(self, *args, **kwargs):
		super(PostForm, self).__init__(*args, **kwargs)
		self.category.choices = [(category.id, category.name) for category in Category.query.order_by(Category.name).all()]
		self.tags.choices = [(tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()]

	
class CategoryForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired(), Length(1, 50)])
	description = TextAreaField('Description', validators=[DataRequired(), Length(1, 300)])

	submit = SubmitField()

	def validate_name(self, field):
		if Category.query.filter_by(name=field.data).first():
			raise ValidationError('Name is already in use.')

class TagForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired(), Length(1, 50)])
	description = TextAreaField('Description', validators=[DataRequired(), Length(1,300)])
	submit = SubmitField()

	def validate_name(self, field):
		if Category.query.filter_by(name=field.data).first():
			raise ValidationError('Name is already in use.')

class LinkForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
	url = StringField('URL', validators=[DataRequired(), Length(1, 255)])
	submit = SubmitField()

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import DataRequired, ValidationError, Email, Optional
from spell_checker.models import Users


class LoginForm(FlaskForm):
    username = StringField("Username", id="uname", validators=[DataRequired()])
    password = PasswordField("Password", id="pword", validators=[DataRequired()])
    two_factor = StringField("Two Factor", id="2fa", validators=[Optional()])

    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", id="uname", validators=[DataRequired()])
    password = PasswordField("Password", id="pword", validators=[DataRequired()])
    two_factor = StringField("Two Factor", id="2fa", validators=[Optional()])

    submit = SubmitField("Login")

    def validate(self):
        return Users.query.filter_by(username=self.username.data).one_or_none() is None


class SpellCheckForm(FlaskForm):
    input = StringField("Input", id="inputtext", validators=[DataRequired()])
    submit = SubmitField("Spell Check")


class SpellCheckQueryHistoryForm(FlaskForm):
    username = StringField("Username", id="userquery", validators=[DataRequired()])
    submit = SubmitField("Query User")


class AuthHistoryQueryForm(FlaskForm):
    username = StringField("Username", id="userid", validators=[DataRequired()])
    submit = SubmitField("Query User")


class LoginHistoryForm(FlaskForm):
    username = StringField("Username", id="userid", validators=[DataRequired()])
    submit = SubmitField("Query User")

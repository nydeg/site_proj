from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class JobsForm(FlaskForm):
    job = StringField('Работа', validators=[DataRequired()])
    team_leader = IntegerField('id', validators=[DataRequired()])
    work_size = IntegerField('hours', validators=[DataRequired()])
    collaborators = StringField('коллаборация', validators=[DataRequired()])
    is_finished = BooleanField('Статус', validators=[DataRequired()])

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange

class MedicineForm(FlaskForm):
    name = StringField('Medicine Name', validators=[DataRequired()])
    batch = StringField('Batch No', validators=[Optional()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    unit = StringField('Unit', validators=[Optional()])
    expiry_date = DateField('Expiry Date (YYYY-MM-DD)', validators=[Optional()], format='%Y-%m-%d')
    threshold = IntegerField('Low-stock Threshold', validators=[Optional(), NumberRange(min=0)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save')

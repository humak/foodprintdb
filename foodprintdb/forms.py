from wtforms import Form, StringField, PasswordField, validators, TextAreaField, ValidationError

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
        validators.Length(min=4, max=25),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

def update_check(min, max):
    def _check(form, field):
        error = "Must be between %d and %d characters long" % (min, max)
        if field.data != "":
            if len(field.data) > max or len(field.data) < min:
                raise ValidationError(error)

    return _check

class UpdateUser(Form):
    name = StringField('Name', [update_check(min=1, max=25)])
    username = StringField('Username')
    password = PasswordField('Password', [
        update_check(min=6, max=25),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

class RecordForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=50)])
    comment = TextAreaField('Comment(Optional)', [validators.Length(max=300)])

class ConsumptionForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=50)])
    meattype = StringField('Meat Type', [validators.Length(min=1, max=50)]) 
    portion = StringField('Portion', [validators.Length(min=1, max=50)])
    amount = StringField('Amount', [validators.Length(min=1, max=50)]) 

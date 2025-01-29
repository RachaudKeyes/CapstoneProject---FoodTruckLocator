from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, RadioField, DecimalRangeField, IntegerField, TimeField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, ValidationError


class ComplexPassword(object):
    """ Password must meet minimum complexity requirements: 
        - X number(s)
        - X uppercase/lowercase letter(s)
        - X special character(s) (! @ # $ % & * ?)
    """


    def __init__(self, min_num=-1, min_lower=-1, min_upper=-1, min_char=-1, message=None):
        self.min_num = min_num
        self.min_lower = min_lower
        self.min_upper = min_upper
        self.min_char = min_char
        if not message:
            message = f"Field must contain at least {min_num} number(s), {min_lower} lowercase letter(s), {min_upper} uppercase letter(s), {min_char} special character(s) (! @ # $ % & * ?) ."
        self.message = message

    def __call__(self, form, field):

        LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
        UPPERCASE = LOWERCASE.upper()
        NUMBERS = "0123456789"
        CHARS = "!@#$%?*&"

        pwd = field.data

        l_total = 0
        for l in LOWERCASE:
            count = pwd.count(l)
            l_total += count

        if l_total < self.min_lower:
            raise ValidationError(self.message)
        
        u_total = 0
        for u in UPPERCASE:
            count = pwd.count(u)
            u_total += count

        if u_total < self.min_upper:
            raise ValidationError(self.message)
        
        n_total = 0
        for n in NUMBERS:
            count = pwd.count(n)
            n_total += count

        if n_total < self.min_num:
            raise ValidationError(self.message)
        
        c_total = 0
        for c in CHARS:
            count = pwd.count(c)
            c_total += count
            
        if c_total < self.min_char:
            raise ValidationError(self.message)


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[Length(min=6, max=20)])
    
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(min=10, max=40)])
    
    password = PasswordField('Password', validators=[Length(min=6, max=20), ComplexPassword(min_num=1, min_char=1, min_lower=1, min_upper=1)])
    
    profile_image = StringField('(Optional) Profile Image URL', 
                                validators=[Optional()])
    
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=20)])

    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=20)])
    
    role = RadioField("Profile Type", 
                      choices=[('personal','Personal'),('business','Business')],
                      validators=[DataRequired()])
    

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[Length(min=6, max=20)])
    
    password = PasswordField('Password', validators=[Length(min=6, max=20)])


class TruckAddForm(FlaskForm):
    """Register Business/Truck form."""

    name = StringField('Food Truck Name', validators=[DataRequired(), Length(min=6, max=25)]) 
    
    email = StringField('Business E-mail', validators=[DataRequired(), Email(), Length(min=10, max=40)])

    phone_number = StringField('Business Phone Number (XXX) XXX-XXXX', validators=[DataRequired(), Length(min=13, max=20)])

    logo_image = StringField('Logo Image', validators=[Optional()])

    menu_image = StringField('Menu Image', validators=[DataRequired()])

    social_media_1 = StringField('(Optional) Facebook', validators=[Optional()])

    social_media_2 = StringField('(Optional) Instagram', validators=[Optional()])

    bio = TextAreaField('Tell us about your business and/or food truck.', validators=[Optional()])


class UserEditForm(FlaskForm):
    """Form for editing user."""

    username = StringField('Username', validators=[Length(min=6, max=20)])
    
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(min=10, max=40)])
    
    profile_image = StringField('(Optional) Profile Image URL', 
                                validators=[Optional()])
    
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=20)])

    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=20)])
    
    role = RadioField("Profile Type", 
                      choices=[('personal','Personal'),('business','Business')],
                      validators=[DataRequired()])
    
    password = PasswordField('Password', validators=[Length(min=6, max=20)])


class ChangePasswordForm(FlaskForm):
    """Form for logged in user to change password."""

    current_password = PasswordField('Current Password', validators=[Length(min=6, max=20)])
    new_password = PasswordField('New Password', validators=[Length(min=6, max=20), ComplexPassword(min_num=1, min_char=1, min_lower=1, min_upper=1)])
    new_password_confirm = PasswordField('Confirm New Password', validators=[Length(min=6, max=20)])


class TruckEditForm(FlaskForm):
    """Form for user/owner to edit truck details."""

    username = StringField('Username', validators=[Length(min=6, max=20)])

    name = StringField('Food Truck Name', validators=[DataRequired(), Length(min=6, max=25)]) 
    
    email = StringField('Business E-mail', validators=[DataRequired(), Length(min=10, max=40)])

    phone_number = StringField('Business Phone Number (XXX) XXX-XXXX', validators=[DataRequired(), Length(min=13, max=20)])

    logo_image = StringField('Logo Image', validators=[Optional()])

    menu_image = StringField('Menu Image', validators=[DataRequired()])

    social_media_1 = StringField('(Optional) Social Media', validators=[Optional()])

    social_media_2 = StringField('(Optional) Social Media', validators=[Optional()])

    bio = TextAreaField('Tell us about your business and/or food truck.', validators=[Optional()])

    password = PasswordField('Password', validators=[Length(min=6, max=20)])


class UserReviewForm(FlaskForm):
    """Form for a user to review a truck."""

    rating = DecimalRangeField(label='How would you rate us? (0 - poor, 5 - excellent)',
                               render_kw={"value": "0",
                                        "max": "5",
                                        "step": "0.5"
                                        }, 
                               validators=[NumberRange(min=0.0, max=5.0)],
                               default=0.0)

    review = TextAreaField('Review', validators=[Length(min=10)])

    image_1 = StringField('(Optional) Image URL', validators=[Optional()])
    image_2 = StringField('(Optional) Image URL', validators=[Optional()])
    image_3 = StringField('(Optional) Image URL', validators=[Optional()])
    image_4 = StringField('(Optional) Image URL', validators=[Optional()])


class UserReviewEditForm(FlaskForm):
    """Form for a user to edit a review of a truck."""

    rating = DecimalRangeField(label='How would you rate us? (0 - poor, 5 - excellent)',
                               render_kw={"value": "0",
                                        "max": "5",
                                        "step": "0.5"
                                        }, 
                               validators=[NumberRange(min=0.0, max=5.0)],
                               default=0.0)

    review = TextAreaField('Review', validators=[Length(min=10)])

    image_1 = StringField('(Optional) Image URL', validators=[Optional()])
    image_2 = StringField('(Optional) Image URL', validators=[Optional()])
    image_3 = StringField('(Optional) Image URL', validators=[Optional()])
    image_4 = StringField('(Optional) Image URL', validators=[Optional()])


class TruckLocationForm(FlaskForm):
    """Form for truck owner to update location and hours of operation."""

    open_time = TimeField('Open', validators=[Optional()])

    close_time = TimeField('Close', validators=[Optional()])

    location = StringField('Address', validators=[Optional()])
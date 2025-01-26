from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, RadioField, DecimalRangeField, IntegerField, TimeField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[Length(min=6)])
    
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    
    password = PasswordField('Password', validators=[Length(min=6)])
    
    profile_image = StringField('(Optional) Profile Image URL', 
                                validators=[Optional()])
    
    first_name = StringField("First Name", validators=[DataRequired()])

    last_name = StringField("Last Name", validators=[DataRequired()])
    
    role = RadioField("Profile Type", 
                      choices=[('personal','Personal'),('business','Business')],
                      validators=[DataRequired()])
    

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[Length(min=6)])
    
    password = PasswordField('Password', validators=[Length(min=6)])


class TruckAddForm(FlaskForm):
    """Register Business/Truck form."""

    name = StringField('Food Truck Name', validators=[DataRequired()]) 
    
    email = StringField('Business E-mail', validators=[DataRequired()])

    phone_number = StringField('Business Phone Number', validators=[DataRequired()])

    logo_image = StringField('Logo Image', validators=[Optional()])

    menu_image = StringField('Menu Image', validators=[DataRequired()])

    social_media_1 = StringField('(Optional) Facebook', validators=[Optional()])

    social_media_2 = StringField('(Optional) Instagram', validators=[Optional()])

    bio = TextAreaField('Tell us about your business and/or food truck.', validators=[Optional()])


class UserEditForm(FlaskForm):
    """Form for editing user."""

    username = StringField('Username', validators=[Length(min=6)])
    
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    
    profile_image = StringField('(Optional) Profile Image URL', 
                                validators=[Optional()])
    
    first_name = StringField("First Name", validators=[DataRequired()])

    last_name = StringField("Last Name", validators=[DataRequired()])
    
    role = RadioField("Profile Type", 
                      choices=[('personal','Personal'),('business','Business')],
                      validators=[DataRequired()])
    
    password = PasswordField('Password', validators=[Length(min=6)])


class ChangePasswordForm(FlaskForm):
    """Form for logged in user to change password."""

    current_password = PasswordField('Current Password', validators=[Length(min=6)])
    new_password = PasswordField('New Password', validators=[Length(min=6)])
    new_password_confirm = PasswordField('Confirm New Password', validators=[Length(min=6)])


class TruckEditForm(FlaskForm):
    """Form for user/owner to edit truck details."""

    username = StringField('Username', validators=[Length(min=6)])

    name = StringField('Food Truck Name', validators=[DataRequired()]) 
    
    email = StringField('Business E-mail', validators=[DataRequired()])

    phone_number = StringField('Business Phone Number', validators=[DataRequired()])

    logo_image = StringField('Logo Image', validators=[Optional()])

    menu_image = StringField('Menu Image', validators=[DataRequired()])

    social_media_1 = StringField('(Optional) Social Media', validators=[Optional()])

    social_media_2 = StringField('(Optional) Social Media', validators=[Optional()])

    bio = TextAreaField('Tell us about your business and/or food truck.', validators=[Optional()])

    password = PasswordField('Password', validators=[Length(min=6)])


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
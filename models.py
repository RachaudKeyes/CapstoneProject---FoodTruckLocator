"""SQLAlchemy models for Food Locator App."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import requests

bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """ Connect this database to provided Flask app."""

    with app.app_context():
        db.app = app
        db.init_app(app)


class Review(db.Model):
    """ User reviews about truck. """

    __tablename__ = "reviews"

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True
                    )
    
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete="cascade"),
                        nullable=False
                        )
        
    truck_id = db.Column(db.Integer,
                        db.ForeignKey('trucks.id', ondelete="cascade"),
                        nullable=False
                        )
    
    rating = db.Column(db.Float,
                       nullable=False)
    
    review = db.Column(db.Text,
                       nullable=False)

    image_1 = db.Column(db.Text)
    image_2 = db.Column(db.Text)
    image_3 = db.Column(db.Text)
    image_4 = db.Column(db.Text)
    

class Truck(db.Model):
    """ Truck model."""

    __tablename__ = "trucks"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True
                   )
    
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='cascade'),
                        nullable=False)
    
    name = db.Column(db.String(25),
                         nullable=False,
                         unique=True
                         )
    
    email = db.Column(db.String(40),
                      nullable=False,
                      unique=True
                      )
    
    
    logo_image = db.Column(db.Text,
                           default="/static/images/truck_default_img.jpg"
                           )
    
    menu_image = db.Column(db.Text,
                           nullable=False)
    
    phone_number = db.Column(db.String(20),
                            nullable=False)
    
    # schedule_id = db.Column(db.Integer,
    #                         db.ForeignKey('schedules.id', ondelete="cascade")
    #                         )
    
    open_time = db.Column(db.Time)          # can be nullable for closed

    close_time = db.Column(db.Time)
    
    location = db.Column(db.Text,
                         default="Closed")

    latitude = db.Column(db.String)        

    longitude = db.Column(db.String)       

    social_media_1 = db.Column(db.Text)

    social_media_2 = db.Column(db.Text)

    bio = db.Column(db.Text)

    # category_id = db.Column(db.Integer,
    #                         db.ForeignKey('categories.id', ondelete="cascade")
    #                         )
    
    reviews = db.relationship('Review', backref="trucks")

    @classmethod
    def request_coords(cls, API_BASE, key, location):
        """Return {lat, lng} from MapBox API for given location"""

        url = f"{API_BASE}.places/{location}.json?access_token={key}"

        response = requests.get(url)
        r = response.json()

        lng = r['features'][0]['geometry']['coordinates'][0]
        lat = r['features'][0]['geometry']['coordinates'][1]

        return {"lat": lat, "lng": lng}


class User(db.Model):
    """ User"""

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True
                   )

    username = db.Column(db.String(20),
                         nullable=False,
                         unique=True
                         )
    
    email = db.Column(db.String(40),
                      nullable=False,
                      unique=True
                      )
    
    first_name = db.Column(db.String(20),
                           nullable=False)
    
    last_name = db.Column(db.String(20),
                           nullable=False)
    
    password = db.Column(db.Text,
                         nullable=False
                         )
    
    profile_image = db.Column(db.Text,
                              default="/static/images/user_default_img.jpg"
                              )
    
    role = db.Column(db.Text,
                     nullable=False
                     )
    
    trucks = db.relationship('Truck')
    
    favorites = db.relationship('Truck', secondary="favorites")
    
    reviews = db.relationship('Review', backref="users")
    

    @property
    def full_name(self):
        """Return full name of user"""

        return f"{self.first_name} {self.last_name}"


    @classmethod
    def signup(cls, username, email, first_name, last_name, password, profile_image, role):
        """
        Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=hashed_pwd,
            profile_image=profile_image,
            role=role
        )

        db.session.add(user)
        return user
    
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    @classmethod
    def update_password(cls, username, new_password):
        """Updates user's password to new_password."""

        user = cls.query.filter_by(username=username).first()

        new_hashed_password = bcrypt.generate_password_hash(new_password).decode('UTF-8')
        user.password = new_hashed_password


class Favorite(db.Model):
    """ User's Favorites"""

    __tablename__ = "favorites"

    id = db.Column(db.Integer,
                    primary_key=True,
                    autoincrement=True
                    )

    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete="cascade")
                        )
        
    truck_id = db.Column(db.Integer,
                        db.ForeignKey('trucks.id', ondelete="cascade")
                        )
        
################################################################      
# Future Considerations:

# class Schedule(db.Model):
#     """Hours of operation for trucks"""

#     __tablename__ = "schedules"

#     id = db.Column(db.Integer,
#                     primary_key=True,
#                     autoincrement=True
#                     )
    
#     truck_id = db.Column(db.Integer,
#                          db.ForeignKey('trucks.id', 
#                                        name="schedules_truck_id_fkey", 
#                                        ondelete="cascade")
#                          )
    
#     day = db.Column(db.Integer,
#                     nullable=False
#                     )
    
#     open_time = db.Column(db.Time)

#     close_time = db.Column(db.Time)

#     location = db.Column(db.Text)

#     longitude = db.Column(db.Integer)

#     latitude = db.Column(db.Integer)


# class Category(db.Model):
#     """Truck cateogories"""

#     __tablename__ = "categories"

#     id = db.Column(db.Integer,
#                     primary_key=True,
#                     autoincrement=True
#                     )
    
#     name = db.Column(db.Text,
#                      nullable=False)

    

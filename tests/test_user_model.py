"""User model tests."""

# run these tests like:
#
#    python3 -m unittest tests/test_user_model.py

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///food_truck_test"

# Now we can import app

from app import app


class UserModelTestCase(TestCase):
    """Test User model."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("testp1", 
                         "emailp1@email.com",
                         "TestP",
                         "TestingP", 
                         "password",
                         None,
                         "personal"
                         )
        uid1 = 1111
        u1.id = uid1

        db.session.commit()

        u1 = User.query.get(uid1)

        self.u1 = u1
        self.uid1 = uid1

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            first_name="FirstName",
            last_name="LastName",
            role="personal"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no reviews, trucks, or favorites.
        self.assertEqual(len(u.reviews), 0)
        self.assertEqual(len(u.trucks), 0)
        self.assertEqual(len(u.favorites), 0)

    ####
    #
    # Signup Tests
    #
    ####

    def test_valid_signup(self):
        u_test = User.signup("testtesttest", 
                             "testtest@test.com", 
                             "Firstname",
                             "Lastname",
                             "password", 
                             None,
                             "personal")
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertEqual(u_test.email, "testtest@test.com")
        self.assertNotEqual(u_test.password, "password")
        self.assertEqual(u_test.first_name, "Firstname")
        self.assertEqual(u_test.last_name, "Lastname")
        self.assertNotEqual(u_test.profile_image, None)
        self.assertEqual(u_test.role, "personal")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup(None, 
                             "testtest@test.com", 
                             "Firstname",
                             "Lastname",
                             "password", 
                             None,
                             "personal")
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_username_not_unique_signup(self):
        invalid = User.signup(self.u1.username, 
                             "testtest@test.com", 
                             "Firstname",
                             "Lastname",
                             "password", 
                             None,
                             "personal")
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("testtesttest", 
                             None, 
                             "Firstname",
                             "Lastname",
                             "password", 
                             None,
                             "personal")
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_not_unique_signup(self):
        invalid = User.signup("testtesttest", 
                             self.u1.email, 
                             "Firstname",
                             "Lastname",
                             "password", 
                             None,
                             "personal")
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtesttest", 
                        "testtest@test.com", 
                        "Firstname",
                        "Lastname",
                        "", 
                        None,
                        "personal")

        with self.assertRaises(ValueError) as context:
            User.signup("testtesttest", 
                        "testtest@test.com", 
                        "Firstname",
                        "Lastname",
                        None, 
                        None,
                        "personal")
            
    def test_invalid_first_name_signup(self):
        invalid = User.signup("testtesttest", 
                        "testtest@test.com", 
                        None,
                        "Lastname",
                        "password", 
                        None,
                        "personal")
        uid = 157428
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

             
    def test_invalid_last_name_signup(self):
        invalid = User.signup("testtesttest", 
                              "testtest@test.com", 
                              "Firstname",
                              None,
                              "password", 
                              None,
                              "personal")
        uid = 132874
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    ####
    #
    # Authentication Tests
    #
    ####

    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))


  


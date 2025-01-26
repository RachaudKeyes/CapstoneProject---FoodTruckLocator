"""Review model tests."""

# run these tests like:
#
#    python3 -m unittest tests/test_review_model.py

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Truck, Review

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///food_truck_test"

# Now we can import app

from app import app

class ReviewModelTestCase(TestCase):
    """Test review model."""

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

        u2 = User.signup("testb2", 
                         "emailb2@email.com", 
                         "TestB",
                         "TestingB",
                         "password", 
                         None,
                         "business"
                         )
        uid2 = 2222
        u2.id = uid2

        t1 = Truck(
            user_id = uid2,
            name = "Testing Truck",
            email = "testingTruck@email.com",
            logo_image = None,
            menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
            phone_number = "123-456-7890"
            )
        
        tid1 = 3333
        t1.id = tid1

        u2.trucks.append(t1)

        r1 = Review(
            user_id = uid1,
            truck_id = tid1,
            rating = 4.5,
            review = "This is a sample review about food trucks."
            )
        
        rid1 = 2251
        r1.id = rid1
        
        u1.reviews.append(r1)

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)
        t1 = Truck.query.get(tid1)
        r1 = Review.query.get(rid1)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.t1 = t1
        self.tid1 = tid1

        self.r1 = r1
        self.rid1 = rid1

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_review_model(self):
        """Does the basic model work?"""

        # User should have 1 review
        # role - "business" cannot leave a review
        self.assertEqual(len(self.u1.reviews), 1)
        self.assertEqual(self.u1.reviews[0].rating, 4.5)

    
    def test_invalid_user_id(self):
        u_test = User.signup("testbusiness101", 
                            "testbusiness101@email.com", 
                            "First",
                            "Last",
                            "password", 
                            None,
                            "business"
                            )
        uidtest = 1123
        u_test.id = uidtest

        t_test = Truck(
                user_id = uidtest,
                name = "Another Truck",
                email = "anothertruck@email.com",
                logo_image = None,
                menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                phone_number = "032-165-8745"
                )
        tidtest = 3258
        t_test.id = tidtest

        r_test = Review(
                user_id = None,
                truck_id = tidtest,
                rating = 4.5,
                review = "Another sample review for a food truck."
        )
        ridtest = 8974
        r_test.id = ridtest

        db.session.add(r_test)
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_user_id_truck_owner(self):
        u_test = User.signup("testbusiness101", 
                            "testbusiness101@email.com", 
                            "First",
                            "Last",
                            "password", 
                            None,
                            "business"
                            )
        uidtest = 1123
        u_test.id = uidtest

        t_test = Truck(
                user_id = uidtest,
                name = "Another Truck",
                email = "anothertruck@email.com",
                logo_image = None,
                menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                phone_number = "032-165-8745"
                )
        tidtest = 3258
        t_test.id = tidtest

        r_test = Review(
                user_id = uidtest,
                truck_id = tidtest,
                rating = 4.5,
                review = "Another sample review for a food truck."
        )
        ridtest = 8974
        r_test.id = ridtest

        db.session.add(r_test)
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()        

    def test_invalid_truck_id(self):
        u_test = User.signup("testbusiness101", 
                            "testbusiness101@email.com", 
                            "First",
                            "Last",
                            "password", 
                            None,
                            "business"
                            )
        uidtest = 1123
        u_test.id = uidtest

        t_test = Truck(
                user_id = uidtest,
                name = "Another Truck",
                email = "anothertruck@email.com",
                logo_image = None,
                menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                phone_number = "032-165-8745"
                )
        tidtest = 3258
        t_test.id = tidtest

        r_test = Review(
                user_id = uidtest,
                truck_id = None,
                rating = 4.5,
                review = "Another sample review for a food truck."
                )
        ridtest = 8974
        r_test.id = ridtest

        db.session.add(r_test)
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_rating(self):
        u_test = User.signup("testbusiness101", 
                            "testbusiness101@email.com", 
                            "First",
                            "Last",
                            "password", 
                            None,
                            "business"
                            )
        uidtest = 1123
        u_test.id = uidtest

        t_test = Truck(
                user_id = uidtest,
                name = "Another Truck",
                email = "anothertruck@email.com",
                logo_image = None,
                menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                phone_number = "032-165-8745"
                )
        tidtest = 3258
        t_test.id = tidtest

        r_test = Review(
                user_id = uidtest,
                truck_id = tidtest,
                rating = None,
                review = "Another sample review for a food truck."
                )
        ridtest = 8974
        r_test.id = ridtest

        db.session.add(r_test)
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
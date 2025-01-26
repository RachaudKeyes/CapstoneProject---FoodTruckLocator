"""Truck model tests."""

# run these tests like:
#
#    python3 -m unittest tests/test_truck_model.py

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Truck, Favorite

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///food_truck_test"

# Now we can import app

from app import app, GEOCODE_API_BASE_URL, KEY

class TruckModelTestCase(TestCase):
    """Test truck model."""

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

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)
        t1 = Truck.query.get(tid1)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.t1 = t1
        self.tid1 = tid1

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_Truck_model(self):
        """Does basic model work?"""

        # User should have 1 truck
        # Only role - "business" can have a truck
        self.assertEqual(len(self.u2.trucks), 1)
        self.assertEqual(self.u2.trucks[0].name, "Testing Truck")

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
                user_id = None,
                name = "Another Truck 101",
                email = "anothertruck@email.com",
                logo_image = None,
                menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                phone_number = "032-165-8745"
                )
        
        db.session.add(t_test)
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_name_is_none(self):
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
                name = None,
                email = "anothertruck@email.com",
                logo_image = None,
                menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                phone_number = "032-165-8745"
                )
        
        db.session.add(t_test)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_name_is_not_unique(self):
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
                name = self.u2.trucks[0].name,
                email = "anothertruck@email.com",
                logo_image = None,
                menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                phone_number = "032-165-8745"
                )

        db.session.add(t_test)
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_is_none(self):
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
                name = "Another Truck 101",
                email = None,
                logo_image = None,
                menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                phone_number = "032-165-8745"
                )

        db.session.add(t_test)
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_is_not_unique(self):
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
                name = "Another Truck 101",
                email = self.u2.trucks[0].email,
                logo_image = None,
                menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                phone_number = "032-165-8745"
                )

        db.session.add(t_test)
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_menu_image(self):
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
                name = "Another Truck 101",
                email = "anothertruck@email.com",
                logo_image = None,
                menu_image = None,
                phone_number = "032-165-8745"
                )

        db.session.add(t_test)
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_phone_number(self):
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
                name = "Another Truck 101",
                email = "anothertruck@email.com",
                logo_image = None,
                menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                phone_number = None
                )

        db.session.add(t_test)
        
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()



    def test_truck_favorites(self):
        u_personal = User.signup("testpersonal", 
                         "testpersonal@email.com", 
                         "FirstName",
                         "LastName",
                         "password", 
                         None,
                         "personal"
                         )
        uidpersonal = 5541
        u_personal.id = uidpersonal

        u_business = User.signup("testbusiness", 
                         "testbusiness@email.com", 
                         "First",
                         "Last",
                         "password", 
                         None,
                         "business"
                         )
        uidbusiness = 4155
        u_business.id = uidbusiness

        test_truck = Truck(
                    user_id = uidbusiness,
                    name = "Another Truck",
                    email = "anothertruck@email.com",
                    logo_image = None,
                    menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                    phone_number = "032-165-8745"
                    )

        db.session.add_all([u_personal, u_business, test_truck])
        db.session.commit()

        # role - "business" cannot favorite their own truck.
        u_personal.favorites.append(test_truck)
        db.session.commit()

        f = Favorite.query.filter(Favorite.user_id == uidpersonal).all()
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0].truck_id, test_truck.id)

####
#
# Request Coords Test
#
####

    def test_valid_request_coords(self):
        u_test = User.signup(
                        "testingbusiness1", 
                        "testbusiness1@email.com", 
                        "FirstName1",
                        "LastName1",
                        "password", 
                        None,
                        "business"
                        )
        uidtest = 7785
        u_test.id = uidtest


        truck_test = Truck(
                    user_id = uidtest,
                    name = "Another Test Truck",
                    email = "anothertesttruck@email.com",
                    logo_image = None,
                    menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                    phone_number = "111-235-6541",
                    location = "2900 Learning Campus Dr, Bettendorf, IA 52722"
                    )
        tid = 5550
        truck_test.id = tid

        truck_test.latitude = truck_test.request_coords(GEOCODE_API_BASE_URL, KEY, truck_test.location)["lat"]
        truck_test.longitude = truck_test.request_coords(GEOCODE_API_BASE_URL, KEY, truck_test.location)["lng"]
        
        db.session.add_all([u_test, truck_test])
        db.session.commit()

        truck_test = Truck.query.get(tid)
      
        self.assertEqual(truck_test.latitude, "41.55241")
        self.assertEqual(truck_test.longitude, "-90.50253")

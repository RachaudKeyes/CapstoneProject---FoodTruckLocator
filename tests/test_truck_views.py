"""Truck View tests."""

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest private_tests/test_truck_views.py

import os
from unittest import TestCase

from models import db, Truck, User, Review
from bs4 import BeautifulSoup

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///food_truck_test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class TruckViewTestCase(TestCase):
    """Test views for trucks."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Truck.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup("test", 
                                    "email@email.com",
                                    "Test",
                                    "Testing", 
                                    "password",
                                    None,
                                    "personal"
                                    )
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

        self.u1 = User.signup("test1", 
                            "test1@email.com",
                            "Test1",
                            "Testing1", 
                            "password",
                            None,
                            "personal"
                            )
        self.u1_id = 778
        self.u1.id = self.u1_id

        self.u2 = User.signup("test2", 
                            "test2@email.com",
                            "Test2",
                            "Testing2", 
                            "password",
                            None,
                            "personal"
                            )
        self.u2_id = 884
        self.u2.id = self.u2_id

        self.ub1 = User.signup("testub1", 
                            "testub1@email.com",
                            "Testub1",
                            "Testingub1", 
                            "password",
                            None,
                            "business"
                            )
        self.ub1_id = 548
        self.ub1.id = self.ub1_id

        self.ub2 = User.signup("testub2", 
                            "testub2@email.com",
                            "Testub2",
                            "Testingub2", 
                            "password",
                            None,
                            "business"
                            )
        self.ub2_id = 967
        self.ub2.id = self.ub2_id

        self.ub3 = User.signup("testub3", 
                            "testub3@email.com",
                            "Testub3",
                            "Testingub3", 
                            "password",
                            None,
                            "business"
                            )
        self.ub3_id = 905
        self.ub3.id = self.ub3_id

        self.ub4 = User.signup("testub4", 
                            "testub4@email.com",
                            "Testub4",
                            "Testingub4", 
                            "password",
                            None,
                            "business"
                            )
        self.ub4_id = 445
        self.ub4.id = self.ub4_id

        self.truck1 = Truck(user_id = self.ub1_id,
                            name = "Testing Truck1",
                            email = "testingTruck1@email.com",
                            logo_image = None,
                            menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                            phone_number = "123-456-7890"
                            )
        self.truck1_id = 224
        self.truck1.id = self.truck1_id

        self.truck2 = Truck(user_id = self.ub2_id,
                            name = "Testing Truck2",
                            email = "testingTruck2@email.com",
                            logo_image = None,
                            menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                            phone_number = "251-874-7851"
                            )
        self.truck2_id = 822
        self.truck2.id = self.truck2_id

        self.truck3 = Truck(user_id = self.ub3_id,
                            name = "Different Foods",
                            email = "differentfoods@email.com",
                            logo_image = None,
                            menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                            phone_number = "581-879-8724"
                            )
        self.truck3_id = 936
        self.truck3.id = self.truck3_id

        self.truck4 = Truck(user_id = self.ub4_id,
                            name = "Odd Foods",
                            email = "oddfoods@email.com",
                            logo_image = None,
                            menu_image = "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                            phone_number = "581-879-8724"
                            )
        self.truck4_id = 348
        self.truck4.id = self.truck4_id

        self.review1 = Review(user_id = self.u1_id,
                              truck_id = self.truck1_id,
                              rating = 4.0,
                              review = "This is an AMAZING test truck review!"
                              )
        self.review1_id = 275
        self.review1.id = self.review1_id

        self.review2 = Review(user_id = self.u2_id,
                              truck_id = self.truck2_id,
                              rating = 1.5,
                              review = "This is a TERRIBLE test truck review!"
                              )
        self.review2_id = 559
        self.review2.id = self.review2_id

        self.review3 = Review(user_id = self.ub2_id,
                              truck_id = self.truck1_id,
                              rating = 3.0,
                              review = "This is an OK test truck review!"
                              )
        self.review3_id = 772
        self.review3.id = self.review3_id

        db.session.commit()

    def test_register_truck(self):
        """Can user add a truck?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.ub1.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
            resp = c.post("/truck_registration", data={"user_id" : f"{self.ub1_id}",
                                                        "name" : "Testing Truck1",
                                                        "email" : "testingTruck1@email.com",
                                                        "logo_image" : None,
                                                        "menu_image" : "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                                                        "phone_number" : "123-456-7890"}
                         )

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            truck = Truck.query.one()
            self.assertEqual(truck.name, "Testing Truck1")

    def test_register_no_session(self):
        with self.client as c:
            resp = c.post("/truck_registration", data={"user_id" : f"{self.ub1_id}",
                                                        "name" : "Testing Truck1",
                                                        "email" : "testingTruck1@email.com",
                                                        "logo_image" : None,
                                                        "menu_image" : "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                                                        "phone_number" : "123-456-7890"},
                                                        follow_redirects=True
                         )
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_register_invalid_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 99222224  # user does not exist

            resp = c.post("/truck_registration", data={"user_id" : f"{self.ub1_id}",
                                                        "name" : "Testing Truck1",
                                                        "email" : "testingTruck1@email.com",
                                                        "logo_image" : None,
                                                        "menu_image" : "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                                                        "phone_number" : "123-456-7890"},
                                                        follow_redirects=True
                         )
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_register_invalid_role(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id  

            resp = c.post("/truck_registration", data={"user_id" : f"{self.testuser_id}",
                                                        "name" : "Testing Truck1",
                                                        "email" : "testingTruck1@email.com",
                                                        "logo_image" : None,
                                                        "menu_image" : "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                                                        "phone_number" : "123-456-7890"},
                                                        follow_redirects=True
                         )
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_register_only_one_truck(self):
        t = self.truck1

        db.session.add(t)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.ub1.id  

            resp = c.post("/truck_registration", data={"user_id" : f"{self.ub1.id}",
                                                        "name" : "Bad Truck",
                                                        "email" : "badtruck@email.com",
                                                        "logo_image" : None,
                                                        "menu_image" : "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                                                        "phone_number" : "123-456-7890"},
                                                        follow_redirects=True
                         )

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access denied. Business profile already exists.", str(resp.data))

    def setup_trucks(self):
        truck1 = self.truck1
        truck2 = self.truck2
        truck3 = self.truck3
        truck4 = self.truck4

        db.session.add_all([truck1, truck2, truck3, truck4])
        db.session.commit()

    def test_search_trucks(self):
        self.setup_trucks()

        with self.client as c:
            resp = c.get("/trucks?q=Test")

            self.assertIn("Testing Truck1", str(resp.data))
            self.assertIn("Testing Truck2", str(resp.data))

            self.assertNotIn("Different Foods", str(resp.data))
            self.assertNotIn("Odd Foods", str(resp.data))

    def test_trucks_index(self):
        self.setup_trucks()

        with self.client as c:
            resp = c.get("/trucks")

            self.assertIn("Testing Truck1", str(resp.data))
            self.assertIn("Testing Truck2", str(resp.data))
            self.assertIn("Different Foods", str(resp.data))
            self.assertIn("Odd Foods", str(resp.data))

    def test_truck_show(self):

        t = self.truck1

        db.session.add(t)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            t = Truck.query.get(t.id)

            resp = c.get(f'/trucks/{t.id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Testing Truck1", str(resp.data))

    def test_invalid_truck_show(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get('/trucks/99999999')  # does not exist

            self.assertEqual(resp.status_code, 404)

    def setup_reviews(self):
        truck1 = self.truck1
        truck2 = self.truck2
        review1 = self.review1
        review2 = self.review2
        review3 = self.review3
        
        db.session.add_all([truck1, truck2, review1, review2, review3])

    def test_truck_list_reviews(self):
        self.setup_reviews()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/trucks/{self.truck1.id}/reviews')

            self.assertEqual(resp.status_code, 200)

            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "list-group-item"})

            # test for count of reviews
            self.assertEqual(len(found), 2)
            self.assertEqual(len(self.truck1.reviews), 2)
            self.assertIn("Testing Truck1 Reviews", str(resp.data))

    def test_invalid_truck_list_reviews(self):
        self.setup_reviews()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/trucks/99999999/reviews')   # does not exist

            self.assertEqual(resp.status_code, 404)

    def test_invalid_user_list_reviews(self):
        self.setup_reviews()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 999999    # does not exist

            resp = c.get(f'/trucks/{self.truck1.id}/reviews', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
    
    def test_truck_location(self):
        t = self.truck1

        db.session.add(t)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.ub1.id    
  
            truck = Truck.query.get(t.id)
            truck.location = "2900 Learning Campus Dr, Bettendorf, IA 52722"

            resp = c.post(f'/trucks/{truck.id}/location', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(truck.latitude, "41.55241")
            self.assertEqual(truck.longitude, "-90.50253")
            self.assertIn("Location successfully updated!", str(resp.data))
            self.assertIn("2900 Learning Campus Dr, Bettendorf, IA 52722", str(resp.data))

    def test_location_invalid_user(self):
        t = self.truck1

        db.session.add(t)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 999999    # does not exist

            truck = Truck.query.get(t.id)
            truck.location = "2900 Learning Campus Dr, Bettendorf, IA 52722"

            resp = c.post(f'/trucks/{truck.id}/location', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
    
    def test_location_invalid_truck(self):
        t = self.truck1

        db.session.add(t)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.ub1.id    
  
            truck = Truck.query.get(t.id)
            truck.location = "2900 Learning Campus Dr, Bettendorf, IA 52722"

            resp = c.post(f'/trucks/999999/location', follow_redirects=True) # does not exist

            self.assertEqual(resp.status_code, 404)

    def test_location_not_truck_owner(self):
        t = self.truck1

        db.session.add(t)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.ub2.id

            truck = Truck.query.get(t.id)
            truck.location = "2900 Learning Campus Dr, Bettendorf, IA 52722"

            resp = c.post(f'/trucks/{truck.id}/location', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_location_not_business_user(self):
        t = self.truck1

        db.session.add(t)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            truck = Truck.query.get(t.id)
            truck.location = "2900 Learning Campus Dr, Bettendorf, IA 52722"

            resp = c.post(f'/trucks/{truck.id}/location', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_edit_profile(self):
        # Will be same for editing any valid parts of form.
        t = self.truck1

        db.session.add(t)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.ub1.id
            if self.ub1.authenticate(self.ub1.username, self.ub1.password):
                resp = c.post(f"/trucks/profile", data={"user_id" : f"{self.ub1_id}",
                                                        "name" : "Edited Truck1",
                                                        "email" : "testingTruck1@email.com",
                                                        "logo_image" : None,
                                                        "menu_image" : "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                                                        "phone_number" : "123-456-7890"
                                                        },
                                                        follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Edited Truck1", str(resp.data))
                self.assertIn("Profile updated successfully!", str(resp.data))

    def test_edit_invalid_session(self):

        t = self.truck1

        db.session.add(t)
        db.session.commit()

        with self.client as c:
            if self.ub1.authenticate(self.ub1.username, self.ub1.password):
                resp = c.post(f"/trucks/profile", data={"user_id" : f"{self.ub1_id}",
                                                        "name" : "Edited Truck1",
                                                        "email" : "testingTruck1@email.com",
                                                        "logo_image" : None,
                                                        "menu_image" : "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                                                        "phone_number" : "123-456-7890"
                                                        },
                                                        follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Access unauthorized", str(resp.data))
                self.assertNotIn("Edited Truck1", str(resp.data))


    def test_edit_invalid_user_role(self):
        t = self.truck1

        db.session.add(t)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            if self.testuser.authenticate(self.testuser.username, self.testuser.password):
                resp = c.post(f"/trucks/profile", data={"user_id" : f"{self.testuser.id}",
                                                        "name" : "Edited Truck1",
                                                        "email" : "testingTruck1@email.com",
                                                        "logo_image" : None,
                                                        "menu_image" : "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                                                        "phone_number" : "123-456-7890"
                                                        },
                                                        follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Access unauthorized", str(resp.data))
                self.assertNotIn("Edited Truck1", str(resp.data))

    def test_edit_not_truck_owner(self):
        t = self.truck1

        db.session.add(t)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.ub2.id

            if self.ub2.authenticate(self.ub2.username, self.ub2.password):
                resp = c.post(f"/trucks/profile", data={"user_id" : f"{self.ub2.id}",
                                                        "name" : "Edited Truck1",
                                                        "email" : "testingTruck1@email.com",
                                                        "logo_image" : None,
                                                        "menu_image" : "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                                                        "phone_number" : "123-456-7890"
                                                        },
                                                        follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Access unauthorized", str(resp.data))
                self.assertNotIn("Edited Truck1", str(resp.data))

    def test_edit_name_not_unique(self):
        t = self.truck1
        t2 = self.truck2

        db.session.add(t, t2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.ub1.id

            if self.ub1.authenticate(self.ub1.username, self.ub1.password):
                resp = c.post(f"/trucks/profile", data={"user_id" : f"{self.ub1.id}",
                                                        "name" : "Testing Truck2",
                                                        "email" : "testingTruck1@email.com",
                                                        "logo_image" : None,
                                                        "menu_image" : "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                                                        "phone_number" : "123-456-7890"
                                                        },
                                                        follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("New name already taken", str(resp.data))
                self.assertNotIn("Testing Truck2", str(resp.data))

    def test_edit_invalid_password(self):
        t = self.truck1
        t2 = self.truck2

        db.session.add(t, t2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.ub1.id

            if self.ub1.authenticate(self.ub1.username, self.ub2.password):
                resp = c.post(f"/trucks/profile", data={"user_id" : f"{self.ub1.id}",
                                                        "name" : "Edited Truck1",
                                                        "email" : "testingTruck1@email.com",
                                                        "logo_image" : None,
                                                        "menu_image" : "https://img.freepik.com/free-vector/blank-menu_1308-31027.jpg",
                                                        "phone_number" : "123-456-7890"
                                                        },
                                                        follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Password Incorrect. Please try again.", str(resp.data))
                self.assertNotIn("Edited Truck1", str(resp.data))        






        






















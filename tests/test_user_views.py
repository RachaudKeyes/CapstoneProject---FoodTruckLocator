"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python3 -m unittest tests/test_user_views.py

import os
from unittest import TestCase

from models import db, Truck, User, Favorite, Review
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

class UserViewTestCase(TestCase):
    """Test views for users."""

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

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_user_show(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("Test Testing", str(resp.data))

    def setup_favorites(self):
        self.testuser.favorites.append(self.truck1)
        self.testuser.favorites.append(self.truck2)
        db.session.commit()

    def test_user_show_favorites(self):
        self.setup_favorites()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/favorites")

            self.assertEqual(resp.status_code, 200)

            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "list-group-item"})

            # test for count of favorites
            self.assertEqual(len(found), 2)
            self.assertEqual(len(self.testuser.favorites), 2)
            self.assertIn("2", str(resp.data))

            # test for header to indicate we are on the Favorites tab:
            self.assertIn("Favorites:", str(resp.data))


    def test_add_favorite(self):

        db.session.add(self.truck1)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            resp = c.post(f"/trucks/{self.truck1_id}/favorite", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            favorites = Favorite.query.filter(Favorite.truck_id == self.truck1_id).all()
            self.assertEqual(len(favorites), 1)
            self.assertEqual(favorites[0].user_id, self.u1_id)

    def test_remove_favorite(self):
        self.setup_favorites()

        t = Truck.query.filter(Truck.name == "Testing Truck1").one()
        self.assertIsNotNone(t)
        self.assertNotEqual(t.user_id, self.testuser_id)

        f = Favorite.query.filter(Favorite.user_id == self.testuser_id
                                  ).filter(Favorite.truck_id == t.id).one()
        
        # Now we are sure that testuser favorited truck named "Testing Truck1"
        self.assertIsNotNone(f)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(f"/trucks/{t.id}/favorite", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            favorites = Favorite.query.filter(Favorite.truck_id == t.id).all()
            # the like has been deleted
            self.assertEqual(len(favorites), 0)

    def test_unauthenticated_favorite(self):
        self.setup_favorites()

        t = Truck.query.filter(Truck.name == "Testing Truck1").one()
        self.assertIsNotNone(t)

        favorite_count = Favorite.query.count()

        with self.client as c:
            resp = c.post(f"/trucks/{t.id}/favorite", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            self.assertIn("Access unauthorized", str(resp.data))

            # The number of favorites has not changed since making the request
            self.assertEqual(favorite_count, Favorite.query.count())

    def test_unauthorized_favorite(self):
        ''' Truck owner cannot favorite their own truck. '''

        db.session.add(self.truck1)
        db.session.commit()

        t = Truck.query.filter(Truck.name == "Testing Truck1").one()
        self.assertIsNotNone(t)

        favorite_count = Favorite.query.count()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.ub1_id

            resp = c.post(f"/trucks/{t.id}/favorite", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            self.assertIn("Cannot favorite your own truck!", str(resp.data))

            # The number of favorites has not changed since making the request
            self.assertEqual(favorite_count, Favorite.query.count())
    
    def setup_reviews(self):
        truck1 = self.truck1
        truck2 = self.truck2

        r1 = Review(user_id = self.testuser_id,
                    truck_id = self.truck1_id,
                    rating = 4.5,
                    review = "This is an AMAZING test review!"
                    )
        
        r1_id = 275
        r1.id = r1_id
        
        r2 = Review(user_id = self.testuser_id,
                    truck_id = self.truck2_id,
                    rating = 1.0,
                    review = "This is a TERRIBLE test review!"
                    )
        r2_id = 559
        r2.id = r2_id

        db.session.add_all([truck1, truck2, r1, r2])
        db.session.commit()

    def test_users_show_reviews(self):
        self.setup_reviews()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/reviews")

            self.assertEqual(resp.status_code, 200)

            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "list-group-item"})

            # test for count of reviews
            self.assertEqual(len(found), 2)
            self.assertEqual(len(self.testuser.reviews), 2)
            self.assertIn("2", str(resp.data))

            # test for header to indicate we are on the Favorites tab:
            self.assertIn("Reviews:", str(resp.data))

    def test_users_delete_review(self):
        self.setup_reviews()

        # specific review queried and only one
        r = Review.query.filter(Review.rating == 1.0).one()

        self.assertIsNotNone(r)
        self.assertEqual(r.user_id, self.testuser_id)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/reviews/{r.id}/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            reviews = Review.query.filter(Review.rating == 1.0).all()

            # the review has been deleted
            self.assertEqual(len(reviews), 0)

    def test_unauthenticated_delete_review(self):
        self.setup_reviews()

        r = Review.query.filter(Review.rating == 1.0).one()
        self.assertIsNotNone(r)

        review_count = Review.query.count()

        with self.client as c:
            resp = c.get(f"/users/reviews/{r.id}/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn("Access unauthorized", str(resp.data))

            # The number of reviews has not changed since making the request
            self.assertEqual(review_count, Review.query.count())

    def test_unauthorized_delete_review(self):
        ''' Only the review author can delete review '''

        self.setup_reviews()

        r = Review.query.filter(Review.rating == 1.0).one()
        self.assertIsNotNone(r)

        review_count = Review.query.count()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id

            resp = c.get(f"/users/reviews/{r.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            self.assertIn("Not Authorized to delete this review!", str(resp.data))

            # The number of reviews has not changed since making the request
            self.assertEqual(review_count, Review.query.count())   

    def test_edit_profile(self):
        # Will be same for editing any valid parts of form.
        u = self.testuser

        db.session.add(u)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            if self.testuser.authenticate(self.testuser.username, self.testuser.password):
                resp = c.post(f"/users/profile", data={"id" : f"{self.testuser.id}",
                                                        "username" : "Edited Username",
                                                        "email" : "email@email.com",
                                                        "first_name" : "Test",
                                                        "last_name" : "Testing",
                                                        "profile_image" : "None",
                                                        "role" : "personal"
                                                        },
                                                        follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Edited Username", str(resp.data))
                self.assertIn("Profile updated successfully!", str(resp.data))

    def test_edit_profile_unauthorized(self):
        u = self.testuser

        db.session.add(u)
        db.session.commit()

        with self.client as c:
            if self.testuser.authenticate(self.testuser.username, self.testuser.password):
                resp = c.post(f"/users/profile", data={"id" : f"{self.testuser.id}",
                                                        "username" : "Edited Username",
                                                        "email" : "email@email.com",
                                                        "first_name" : "Test",
                                                        "last_name" : "Testing",
                                                        "profile_image" : "None",
                                                        "role" : "personal"
                                                        },
                                                        follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertNotIn("Edited Username", str(resp.data))
                self.assertIn("Access unauthorized.", str(resp.data))

    def test_edit_profile_username_taken(self):
        u = self.testuser

        db.session.add(u)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            if self.testuser.authenticate(self.testuser.username, self.testuser.password):
                resp = c.post(f"/users/profile", data={"id" : f"{self.testuser.id}",
                                                        "username" : "test1",
                                                        "email" : "email@email.com",
                                                        "first_name" : "Test",
                                                        "last_name" : "Testing",
                                                        "profile_image" : "None",
                                                        "role" : "personal"
                                                        },
                                                        follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertNotIn("test1", str(resp.data))
                self.assertIn("New username/email already taken", str(resp.data))

    def test_edit_profile_invalid_password(self):
        u = self.testuser

        db.session.add(u)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            if self.testuser.authenticate(self.testuser.username, self.u1.password):
                resp = c.post(f"/users/profile", data={"id" : f"{self.testuser.id}",
                                                        "username" : "Edited Username",
                                                        "email" : "email@email.com",
                                                        "first_name" : "Test",
                                                        "last_name" : "Testing",
                                                        "profile_image" : "None",
                                                        "role" : "personal"
                                                        },
                                                        follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertNotIn("EditedUsername", str(resp.data))
                self.assertIn("Password Incorrect. Please try again.", str(resp.data))

    def test_edit_review(self):
        self.setup_reviews()

        u = self.testuser

        db.session.add(u)
        db.session.commit()

        r = Review.query.filter(Review.rating == 1.0).one()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/users/reviews/{r.id}/edit", data={"user_id" : f"{self.testuser.id}",
                                                               "truck_id" : f"{r.truck_id}",
                                                               "rating" : "1.0",
                                                               "review" : "This is an OK test review!"
                                                               },
                                                               follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("This is an OK test review", str(resp.data))
            self.assertIn("Review updated!", str(resp.data))

    def test_edit_review_unauthorized(self):
        self.setup_reviews()

        u = self.testuser

        db.session.add(u)
        db.session.commit()

        r = Review.query.filter(Review.rating == 1.0).one()

        with self.client as c:

            resp = c.post(f"/users/reviews/{r.id}/edit", data={"user_id" : f"{self.testuser.id}",
                                                               "truck_id" : f"{r.truck_id}",
                                                               "rating" : "1.0",
                                                               "review" : "This is an OK test review!"
                                                               },
                                                               follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("This is an OK test review", str(resp.data))
            self.assertIn("Access unauthorized.", str(resp.data))

    def test_edit_review_not_creator(self):
        self.setup_reviews()

        u = self.u1

        db.session.add(u)
        db.session.commit()

        r = Review.query.filter(Review.rating == 1.0).one()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1.id

            resp = c.post(f"/users/reviews/{r.id}/edit", data={"user_id" : f"{self.u1.id}",
                                                               "truck_id" : f"{r.truck_id}",
                                                               "rating" : "1.0",
                                                               "review" : "This is an OK test review!"
                                                               },
                                                               follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("This is an OK test review", str(resp.data))
            self.assertIn("Access Unauthorized.", str(resp.data))
        
    def test_delete_user(self):

        # specific user has been queried and only one
        u = User.query.filter(User.username == "test").one()

        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.testuser_id)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post("/users/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            users = User.query.filter(User.username == "test").all()

            # the user has been deleted
            self.assertEqual(len(users), 0)

    def test_delete_user_unauthorized(self):

        # specific user has been queried and only one
        u = User.query.filter(User.username == "test").one()

        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.testuser_id)

        users_count = User.query.count()

        with self.client as c:
            resp = c.post("/users/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn("Access unauthorized", str(resp.data))

            # The number of users has not changed since making the request
            self.assertEqual(users_count, User.query.count())    

    def test_change_password(self):
        u = self.testuser

        db.session.add(u)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            if self.testuser.authenticate(self.testuser.username, self.testuser.password):
                resp = c.post(f"/users/change_password", data={"current_password" : f"{self.testuser.password}",
                                                               "new_password" : "password1",
                                                               "new_password_confirm" : "password1"},
                                                        follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Password updated.", str(resp.data))

    def test_change_password_unauthorized(self):
        u = self.testuser

        db.session.add(u)
        db.session.commit()

        with self.client as c:
            if self.testuser.authenticate(self.testuser.username, self.testuser.password):
                resp = c.post(f"/users/change_password", data={"current_password" : f"{self.testuser.password}",
                                                               "new_password" : "password1",
                                                               "new_password_confirm" : "password1"},
                                                        follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Access unauthorized.", str(resp.data))

    def test_change_password_unmatching_passwords(self):
        u = self.testuser

        db.session.add(u)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            if self.testuser.authenticate(self.testuser.username, self.testuser.password):
                resp = c.post(f"/users/change_password", data={"current_password" : f"{self.testuser.password}",
                                                               "new_password" : "password1",
                                                               "new_password_confirm" : "password2"},
                                                        follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Unable to update password", str(resp.data))

    def test_change_password_failed_auth(self):
        u = self.testuser

        db.session.add(u)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            if self.testuser.authenticate(self.testuser.username, "BadPassword"):
                resp = c.post(f"/users/change_password", data={"current_password" : f"{self.testuser.password}",
                                                               "new_password" : "password1",
                                                               "new_password_confirm" : "password1"},
                                                        follow_redirects=True)

                self.assertEqual(resp.status_code, 200)
                self.assertIn("Unable to update password. Current password does not match.", str(resp.data))


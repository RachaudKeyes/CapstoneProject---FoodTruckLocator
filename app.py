import os
from flask import Flask, render_template, request, flash, redirect, session, g
# from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

from forms import UserAddForm, LoginForm, TruckAddForm, UserEditForm, ChangePasswordForm, TruckEditForm, UserReviewForm, UserReviewEditForm, TruckLocationForm
from models import db, connect_db, User, Truck, Review

from secrets2 import API_SECRET_KEY

CURR_USER_KEY = "curr_user"
KEY = API_SECRET_KEY
GEOCODE_API_BASE_URL = "https://www.mapquestapi.com/geocoding/v1"
MAP_API_BASE_URL = "https://www.mapquestapi.com/staticmap/v5/map"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///food_truck'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# toolbar = DebugToolbarExtension(app)

app.app_context().push()
connect_db(app)
db.create_all()


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():   
        user = User.signup(                     
            username=form.username.data,
            password=form.password.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            profile_image=form.profile_image.data or User.profile_image.default.arg,
            role=form.role.data
            )

        # if username is not unique, return to signup form.
        try:    
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username already exists.')
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        # db.session.commit()
        do_login(user)

        # For business account
        if user.role == "business":
            return redirect("truck_registration")
        
        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)
    
    
@app.route('/truck_registration', methods=["GET", "POST"])
def register_truck():
    """
    Handle business/truck registration.
    Create Truck model, add to DB, 
    If form not valid, present form.

    If there already is a Truck with that Title: flash message
    and re-present form.
    """
    user = g.user

    # Check if user is logged-in
    if not user:
        flash("Access unauthorized", "danger")
        return redirect("/")
    
    if user.role != "business":
        flash("Access unauthorized", "danger")
        return redirect("/")
    
     # User can only have one business profile
    if len(user.trucks) == 1:
        flash("Access denied. Business profile already exists.", "danger")
        return redirect("/")

    form = TruckAddForm()

    if form.validate_on_submit():
        truck = Truck(
            name = form.name.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            logo_image=form.logo_image.data or Truck.logo_image.default.arg,
            menu_image=form.menu_image.data,
            social_media_1=form.social_media_1.data or None,
            social_media_2=form.social_media_2.data or None,
            bio=form.bio.data,
            user_id = user.id
        )

        user.trucks.append(truck)

        # if name is not unique, return to signup form.
        try:    
            db.session.commit()
        except IntegrityError:
            form.name.errors.append('Truck name already exists.')
            flash("Truck name already taken", 'danger')
            return render_template('trucks/signup.html', form=form)
        
        return redirect('/')
    
    else:    
        return render_template('trucks/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.first_name}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Goodbye!", "primary")
    return redirect("/login")


##############################################################################
# General user routes:

@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    return render_template('users/show.html', user=user)


@app.route('/users/<int:user_id>/favorites', methods=["GET"])
def users_show_favorites(user_id):
    """Show a list of favorited food trucks by current logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(user_id)

    return render_template('users/favorites.html', user=user, favorites=user.favorites)


@app.route('/trucks/<int:truck_id>/favorite', methods=["POST"])
def toggle_favorite(truck_id):
    """Toggle a favorited food truck for current logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    truck = Truck.query.get_or_404(truck_id)

    # Handle case, logged in user cannot like their own truck
    if truck.user_id == g.user.id:
        flash("Cannot favorite your own truck!", "danger")
        redired_url = request.referrer or "/"
        return redirect(redired_url)
    
    user_favorites = g.user.favorites

    if truck in user_favorites:
        # if the truck is contained in user's favorites --> remove truck --> outlined star
        g.user.favorites = [favorite for favorite in user_favorites if favorite != truck]
        flash("Truck successfully removed from favorites.", "success")
    else:
        # if the truck is not in the user's favorites --> add truck --> solid star
        g.user.favorites.append(truck)
        flash("Truck successfully added to favorites.", "success")

    db.session.commit()

    redired_url = request.referrer or "/"
    return redirect(redired_url)


@app.route('/trucks/<int:truck_id>/review', methods=["GET", "POST"])
def add_review(truck_id):
    """ Add a review for truck for logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    truck = Truck.query.get_or_404(truck_id)

    # Handle case, logged in user cannot review their own truck
    if truck.user_id == g.user.id:
        flash("Cannot review your own truck!", "danger")
        redired_url = request.referrer or "/"
        return redirect(redired_url)
    
    form = UserReviewForm()

    if form.validate_on_submit():
        review = Review(
            truck_id = truck_id,
            user_id = g.user.id,
            rating = form.rating.data,
            review = form.review.data,
            image_1 = form.image_1.data or None,
            image_2 = form.image_2.data or None,
            image_3 = form.image_3.data or None,
            image_4 = form.image_4.data or None,
        )

        g.user.reviews.append(review)
        db.session.commit()
        flash("Review successfully submitted!", "success")

        return redirect(f"/trucks/{truck_id}")
    
    return render_template('trucks/review.html', form=form, truck=truck, user=g.user)


@app.route('/users/<int:user_id>/reviews', methods=["GET"])
def users_show_reviews(user_id):
    """Show a list of food trucks reviewed by current logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(user_id)

    return render_template('users/reviews.html', user=user, reviews=user.reviews)


@app.route('/users/reviews/<int:review_id>/edit', methods=["GET", "POST"])
def edit_review(review_id):
        """Update review for logged in-user."""

        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")
    
        user = g.user
        reviewObj = Review.query.get_or_404(review_id)

        # Only creator can edit review
        if user.id != reviewObj.user_id:
            flash("Access Unauthorized.", "danger")

        form = UserReviewEditForm(obj=reviewObj)

        if form.validate_on_submit():
            reviewObj.rating = form.rating.data,
            reviewObj.review = form.review.data,
            reviewObj.image_1 = form.image_1.data or None,
            reviewObj.image_2 = form.image_2.data or None,
            reviewObj.image_3 = form.image_3.data or None,
            reviewObj.image_4 = form.image_4.data or None

            db.session.commit()
            flash("Review updated!", "success")
            return redirect(f"/users/{ g.user.id}/reviews")
        
        return render_template("/users/review_edit.html", user=user, review=reviewObj, form=form)


@app.route('/users/reviews/<int:review_id>/delete', methods=["GET"])
def delete_review(review_id):
    """Delete a logged-in user's specific review."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    review = Review.query.get_or_404(review_id)

    # Only the review's creator can delete review
    if review.user_id != g.user.id:
        flash("Not Authorized to delete this review!", "danger")
        redired_url = request.referrer or "/"
        return redirect(redired_url)

    flash("Review deleted", "warning")
    db.session.delete(review)
    db.session.commit()

    return redirect(f"/users/{ g.user.id }/reviews")


@app.route('/users/profile', methods=["GET", "POST"])
def edit_profile():
    """Update profile for current user."""

    # Check if user is logged-in
    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect("/")

    user = g.user
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username=form.username.data,
            user.email=form.email.data,
            user.first_name=form.first_name.data,
            user.last_name=form.last_name.data,
            user.profile_image=form.profile_image.data or User.profile_image.default.arg,
            user.role=form.role.data

            try:
                db.session.commit()
            except IntegrityError:
                flash("New username/email already taken", "danger")
                return redirect(f"/users/{user.id}")
            
            flash("Profile updated successfully!", "success")
            return redirect(f"/users/{user.id}")
        
        flash("Password Incorrect. Please try again.", "danger")
        
    return render_template('users/edit.html', form=form, user_id=user.id)


@app.route('/users/change_password', methods=["GET", "POST"])
def change_password():
    """Show form for logged-in user to change password. Update password if current password is correct."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user
    form = ChangePasswordForm()

    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        new_password_confirm = form.new_password_confirm.data

    # Check whether current password matches what user enters
        if User.authenticate(user.username, current_password):
            
            # New password and confirm new password fields must match
            if new_password == new_password_confirm:
                User.update_password(user.username, new_password)
                try:
                    db.session.commit()
                except IntegrityError:
                    flash("Unable to update password", "danger")
                    return redirect('/users/change_password.html', form=form)
                
                flash("Password updated.", "success")
                return redirect(f'/users/{user.id}')
            
            flash("Unable to update password. New password / Confirmed password do not match.", "danger")

        flash("Unable to update password. Current password does not match.", "danger")
    
    return render_template("users/change_password.html", form=form, user_id=user.id)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete logged-in user account."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# General truck routes:

@app.route('/trucks')
def list_trucks():
    """Page with listing of trucks.
    
    Can take a 'q' param in querystring to search by that truck.
    """

    search = request.args.get('q')

    if not search:
        trucks = Truck.query.all()
    else:
        trucks = Truck.query.filter(Truck.name.like(f"%{search}%")).all()

    return render_template('trucks/index.html', trucks=trucks, user=g.user)


@app.route('/trucks/<int:truck_id>', methods=["GET"])
def truck_show(truck_id):
    """Show a specified truck profile."""

    truck = Truck.query.get_or_404(truck_id)
    
    # average rating query
    t = text(f'SELECT AVG(rating) as average_rating FROM reviews WHERE truck_id = {truck_id}')
    average_rating = db.session.execute(t).first()[0]

    if truck.reviews:
        rounded = round(average_rating, 1)
    else:
        rounded = "None"

    reviews = (Review
            .query
            .filter(Review.truck_id == truck_id)
            .order_by(Review.id.desc())
            .limit(4)
            .all())

    return render_template('trucks/show.html', 
                           truck=truck, user=g.user, average_rating=rounded, reviews=reviews)


@app.route('/trucks/profile', methods=["GET", "POST"])
def truck_edit():
    """ Update truck profile for current user with role = "business".
        Only truck owner can edit profile.
    """

    # Check if user is logged-in and has role = "business"
    user = g.user

    if not user:
        flash("Access unauthorized", "danger")
        return redirect("/")
    
    if user.role != "business":
        flash("Access unauthorized", "danger")
        return redirect("/")
    
    truckObj = user.trucks[0]

    # Only truck owner can edit truck
    if truckObj.user_id != g.user.id:
        flash("Access unauthorized", "danger")
        return redirect('/')
    
    form = TruckEditForm(obj=truckObj)    # user can only have 1 truck per account

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            truckObj.name = form.name.data,
            truckObj.email=form.email.data,
            truckObj.phone_number=form.phone_number.data,
            truckObj.logo_image=form.logo_image.data or Truck.logo_image.default.arg,
            truckObj.menu_image=form.menu_image.data,
            truckObj.social_media_1=form.social_media_1.data or None,
            truckObj.social_media_2=form.social_media_2.data or None,
            truckObj.bio=form.bio.data

            try:
                db.session.commit()
            except IntegrityError:
                flash("New username/email already taken", "danger")
                return redirect(f"/users/{user.id}")
            
            flash("Profile updated successfully!", "success")
            return redirect(f"/users/{user.id}")
        
        flash("Password Incorrect. Please try again.", "danger")
        
    return render_template('trucks/edit.html', form=form, user_id=user.id)


@app.route('/trucks/<int:truck_id>/location', methods=["GET", "POST"])
def truck_location(truck_id):
    """Show and handle a form for logged in truck user to update location and business hours."""

    # Check if user is logged-in and has role = "business"
    user = g.user

    if not user:
        flash("Access unauthorized", "danger")
        return redirect("/")
    
    if user.role != "business":
        flash("Access unauthorized", "danger")
        return redirect("/")
    
    truck = Truck.query.get_or_404(truck_id)

    # Only truck owner can edit truck details
    if truck.user_id != g.user.id:
        flash("Access unauthorized", "danger")
        return redirect('/')

    form = TruckLocationForm(obj=truck)

    if form.validate_on_submit():
        truck.open_time = form.open_time.data,
        truck.close_time = form.close_time.data,
        truck.location = form.location.data
        
        if truck.location:
            truck.latitude = truck.request_coords(GEOCODE_API_BASE_URL, KEY, truck.location)["lat"]
            truck.longitude = truck.request_coords(GEOCODE_API_BASE_URL, KEY, truck.location)["lng"]

        db.session.commit()
        flash("Location successfully updated!", "success")
        return redirect(f"/trucks/{truck_id}")
    
    return render_template('trucks/location.html', form=form, truck=truck, user=user)
    

@app.route('/trucks/<int:truck_id>/reviews', methods=["GET"])
def truck_list_reviews(truck_id):
    """Show a list of all reviews for a specified truck for logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    truck = Truck.query.get_or_404(truck_id)

    reviews = (Review
               .query
               .filter(Review.truck_id == truck_id)
               .order_by(Review.id.desc())
               .limit(50)
               .all())

    return render_template('trucks/reviews.html', reviews=reviews, user=g.user, truck=truck)


##############################################################################
# Homepage and error pages

@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no map or trucks
    - logged in: map populated with registered trucks and list below
    """

    size = "750,650"
    center = "41.520251,-90.540287"
    marker = "via-md-b92ce3"
    locations = ""
    rounded = []

    if g.user:
        # Retrieve truck locations from database. Add to LOCATIONS string.
        trucks = Truck.query.all()
        for truck in trucks:
            locations += f"{truck.latitude},{truck.longitude}||"

            # average rating query
            t = text(f'SELECT AVG(rating) as average_rating FROM reviews WHERE truck_id = {truck.id}')
            average_rating = db.session.execute(t).first()[0]

            if truck.reviews:
                rounded.append(round(average_rating, 1))
            else:
                rounded.append("None")

        url = f"{MAP_API_BASE_URL}?key={KEY}&locations={locations}&size={size}&center={center}&defaultMarker={marker}&zoom=12"

        return render_template('home.html', url=url, trucks=trucks, average_rating=rounded)

    else:
        return render_template('home-anon.html')
    

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return render_template('404.html'), 404

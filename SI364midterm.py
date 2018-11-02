## Bradley Scharf
## SI 364 - Fall 2018
## Midterm

###############################
####### SETUP (OVERALL) #######
###############################

# Import statements
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import Required, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.datastructures import MultiDict
import os
import requests
import json

## App setup code
app = Flask(__name__)
app.debug = True

## All app.config values
app.config['SECRET_KEY'] = 'hard to guess string from si364'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://Bradley_Scharf@localhost/SI364Midterm"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## App constants
API_KEY = "BPkzEWvcbWBgJMUSm95p3aEOPuPjmBRVcHSq0xhjsLgUZP5LfC0ukb9sW-ty5cS7OsXbjs-8XhHWr46mlRgvo6rFU22DZRSNkr4sYkckTnYsdcPhCAPw9peKxoPXW3Yx"
API_HOST = "https://api.yelp.com/"
DELIVERY_SEARCH = "v3/transactions/delivery/search"
BUSINESS_SEARCH = "v3/businesses/search"
BUSINESS = "restaurant"
headers = {'Authorization': f'Bearer {API_KEY}'}
SEARCH_LIMIT = 3

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)

###################
###### FORMS ######
###################

class IndexForm(FlaskForm):
    user = StringField("Username:",validators=[Required(), Length(min=0, max=64)])
    location = StringField("Please enter your location by georgraphic area or zipcode",validators=[Required(), Length(min=0, max=64)])
    submit = SubmitField("Submit")

class ReviewForm(FlaskForm):
    id = StringField("id:", validators=[Required()])
    name = StringField("Name:", validators=[Required()])
    user = StringField("Username:",validators=[Required(), Length(min=0, max=64)])
    review = TextAreaField("Review:", render_kw={"rows": 11, "cols": 70})
    submit = SubmitField("Submit")

##################
##### MODELS #####
##################

class Login(db.Model):
    __tablename__ = "login"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64))
    location = db.Column(db.String(64))
    def __repr__(self):
        return "{} (ID: {})".format(self.user, self.id)

class Delivery(db.Model):
    __tablename__ = "delivery"
    restaurant_id = db.Column(db.String(100), primary_key=True)
    restaurant_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))

class HotAndNew(db.Model):
    __tablename__ = "hotandnew"
    restaurant_id = db.Column(db.String(100), primary_key=True)
    restaurant_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))

class Review(db.Model):
    __tablename__ = "review"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64))
    restaurant_id = db.Column(db.String(100))
    restaurant_name = db.Column(db.String(100))
    review = db.Column(db.String(7000))

#######################
###### VIEW FXNS ######
#######################

@app.route('/')
def index():
    form = IndexForm()
    if request.args:
        return redirect(url_for('all_logins'))
    return render_template("index.html", form=form)

@app.route('/home', methods=['GET'])
def home():
    response = {}
    if request.args.get("location") == None or request.args.get("location") == "":
        return redirect(url_for('index'))
    if request.args: #args used for get
        location = request.args.get('location')
        user = request.args.get('user')
        login = Login.query.filter_by(user=user).first()
        if not login:
            login = Login(user=user, location=location)
            db.session.add(login)
            db.session.commit()

        params = {'location': request.args.get('location'),
            'limit': SEARCH_LIMIT,
            'sort_by': 'rating',
            'term': BUSINESS
        }
        url = API_HOST + BUSINESS_SEARCH
        response = requests.get(url, headers=headers, params=params).json()
    return render_template("home.html", data=response['businesses'], location=location)

@app.route('/delivery')
def delivery():
    if request.args.get("location") == None or request.args.get("location") == "":
        return redirect(url_for('index'))
    if request.args:
        location = request.args.get('location')
        params = {'location': location}
        url = API_HOST + DELIVERY_SEARCH
        response = requests.get(url, headers=headers, params=params).json()
        for business in response["businesses"]:
            delivery = Delivery.query.filter_by(restaurant_id=business["id"]).first()
            if not delivery:
                delivery = Delivery(restaurant_id=business["id"], restaurant_name=business["name"], phone=business['display_phone'])
                db.session.add(delivery)
                db.session.commit()
    return render_template("delivery.html", data=response["businesses"], location=location)

@app.route('/hotandnew')
def hotandnew():
    if request.args.get("location") == None or request.args.get("location") == "":
        return redirect(url_for('index'))
    if request.args:
        location = request.args.get('location')
        params = {'location': request.args.get('location'),
            'limit': 10,
            'sort_by': 'rating',
            'term': BUSINESS,
            'attributes': 'hot_and_new'
        }
        url = API_HOST + BUSINESS_SEARCH
        response = requests.get(url, headers=headers, params=params).json()
        for business in response["businesses"]:
            hot = HotAndNew.query.filter_by(restaurant_id=business["id"]).first()
            if not hot:
                hot = HotAndNew(restaurant_id=business["id"], restaurant_name=business["name"], phone=business['display_phone'])
                db.session.add(hot)
                db.session.commit()
    return render_template("hotandnew.html", data=response["businesses"], location=location)

@app.route('/review', methods=['GET', 'POST'])
def review():
    if request.args.get("location") == None or request.args.get("location") == "":
        return redirect(url_for('index'))
    autofill = {'id': request.args.get('id'), 'name': request.args.get('name')}
    form = ReviewForm(formdata=MultiDict(autofill))
    location = request.args.get("location")
    if request.method=="POST":
        id = request.form.get("id")
        name = request.form.get("name")
        user = request.form.get("user")
        review = request.form.get("review")

        review_obj = Review.query.filter_by(user=user, restaurant_id=id).first()
        all_reviews = Review.query.filter_by(user=user)
        if not review_obj:
            review_obj = Review(user=user, restaurant_id=id, restaurant_name=name, review=review)
            db.session.add(review_obj)
            db.session.commit()
            return render_template("review_read.html", location=location, id=id, name=name, user=user, review=review, all=all_reviews)
        return render_template("review_read.html", location=location, id=id, name=name, user=user, review=review, all=all_reviews, review_exist="True")
    return render_template("review.html", location=location, form=form, data=autofill)

@app.route('/all_logins')
def all_logins():
    if request.args.get("location") == None or request.args.get("location") == "":
        return redirect(url_for('index'))
    results = Login.query.all()
    return render_template("all_logins.html", results=results, location=request.args.get("location"))

@app.route('/all_reviews')
def all_reviews():
    if request.args.get("location") == None or request.args.get("location") == "":
        return redirect(url_for('index'))
    results = Review.query.all()
    return render_template("all_review.html", results=results, location=request.args.get("location"))

@app.route('/all_deliveries')
def all_deliveries():
    if request.args.get("location") == None or request.args.get("location") == "":
        return redirect(url_for('index'))
    results = Delivery.query.all()
    return render_template("all_deliveries.html", results=results, location=request.args.get("location"))

@app.route('/all_hotandnew')
def all_hotandnew():
    if request.args.get("location") == None or request.args.get("location") == "":
        return redirect(url_for('index'))
    results = HotAndNew.query.all()
    return render_template("all_hotandnew.html", results=results, location=request.args.get("location"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 400

## Code to run the application...
if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    app.run(use_reloader=True, debug=True) # The usual

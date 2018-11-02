# Bradley Scharf SI364 - Fall 2018 Midterm
## Restaurant Yelp Application

This application allows users to enter any location, and find:
*The top three restaurants in the area
+++Write a review to one of these restaurants (click name to write review)
*View nearby restaurants that deliver in the area (can click directly on link under Navigation)
*View the top Hot and New restaurants in the area (can click directly on link under Navigation)

The application also allows users to view all logins, reviews done, and all deliveries and hot and new restaurants that have been viewed by the application.

* http://localhost:5000/ -> index.html
* http://localhost:5000/home -> home.html
* http://localhost:5000/review -> review_read.html, review.html
* http://localhost:5000/delivery -> delivery.html
* http://localhost:5000/hotandnew -> hotandnew.html
* http://localhost:5000/all_logins -> all_logins.html
* http://localhost:5000/all_reviews -> all_review.html
* http://localhost:5000/all_deliveries -> all_deliveries.html
* http://localhost:5000/all_hotandnew -> all_hotandnew.html

Sources:

StackOverflow:
*MultiDict for autofilling the form in review.html
*Passing boolean variable to render_template as String
*TextAreaField to create a large input space for the user
*Python string formatting using f and {} for the API_KEY

Yelp.com/Developers:
*API Documentation for business search and delivery search

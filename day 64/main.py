from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new-books-collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    year = db.Column(db.Integer(), unique=False, nullable=False)
    description = db.Column(db.String(120), unique=False, nullable=False)
    rating = db.Column(db.Float(10), unique=False, nullable=True)
    ranking = db.Column(db.Integer(), unique=False, nullable=True)
    review = db.Column(db.String(10), unique=False, nullable=True)
    img_url = db.Column(db.String(240), unique=True, nullable=False)

    def __repr__(self):
        return f"<Movie {self.title}>"

db.create_all()

class EditForm(FlaskForm):
    rating = StringField('Your rating out of 10 e.g 7.5', validators=[DataRequired()])
    review = StringField('Your review', validators=[DataRequired()])
    submit = SubmitField('Done')

class AddForm(FlaskForm):
    add = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add movie')

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )

# db.session.add(new_movie)
# db.session.commit()

@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    
    return render_template("index.html", movies=all_movies)

@app.route("/edit", methods=["GET", "POST"])
def edit():
    form = EditForm()
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()

        return redirect(url_for ('home') )
    return render_template('edit.html', form=form, movie=movie)

@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for ('home'))

@app.route("/add", methods=['GET', "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        name = form.add.data
        response = requests.get(f"https://api.themoviedb.org/3/search/movie", params={"api_key": f"{API_KEY}", "query": {name}})
        list = response.json()['results']
        return render_template('select.html', movies=list)
    return render_template('add.html', form=form)

@app.route("/find")
def find_movie():
    movie_api_id = request.args.get('id')
    print(movie_api_id)
    if movie_api_id:
        response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_api_id}?api_key={API_KEY}&language=en-US")
        result = response.json()
        new_movie = Movie(
            title = result["title"],
            description = result["overview"],
            year = result["release_date"].split('-')[0],
            img_url = f"https://image.tmdb.org/t/p/w500{result['poster_path']}"
            )

        db.session.add(new_movie)
        db.session.commit()

        return redirect(url_for('edit', id=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True)



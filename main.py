from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
URL="https://api.themoviedb.org/3/search/movie?"
API_KEY="5c355f369cc0e881c3169c020008cbe2"
class login_form(FlaskForm):
    rating=StringField(label='Your rating out of 10 e.g 7.5')
    review=StringField(label='Your review.')
    submit=SubmitField(label='Done')
class addFilm(FlaskForm):
    title = StringField(label='Title of the movie?')
    submit=SubmitField(label='Add movie')


app = Flask(__name__)
with app.app_context():
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books.db"
    # Optional: But it will silence the deprecation warning in the console.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)

    class Movie(db.Model):
        id=db.Column(db.Integer, primary_key=True)
        title=db.Column(db.String(1000), unique=False,nullable=False)
        year=db.Column(db.Integer,unique=False,nullable=True)
        description=db.Column(db.String(10000), nullable=True)
        rating= db.Column(db.Float, nullable=True)
        ranking= db.Column(db.Integer, nullable=True)
        review=db.Column(db.String(1000), nullable=True)
        img_url=db.Column(db.String(1000), nullable=True)

    db.create_all()
    # new_movie=Movie(
    # title="Phone Booth",
    # year=2002,
    # description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    # rating=7.3,
    # ranking=10,
    # review="My favourite character was the caller.",
    # img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    # )
    # db.session.add(new_movie)
    # db.session.commit()
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


@app.route("/")
def home():
    all_movies=db.session.query(Movie).order_by(Movie.rating.desc()).all()
    for movies in all_movies:
        movies.ranking =all_movies.index(movies)+1
    db.session.commit()
    return render_template("index.html",movies=all_movies)

@app.route("/edit",methods=['GET','POST'])
def edit():
    movie_id = request.args.get('id')
    movie_to_update = Movie.query.get(movie_id)
    if login_form().validate_on_submit():
        movie_to_update.rating = float(login_form().rating.data)
        movie_to_update.review = login_form().review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html",movie=movie_to_update,form=login_form())
@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))
@app.route("/select_film",methods=['GET','POST'])
def search():
    if addFilm().validate_on_submit():
        lis_of_movies = []
        movie_to_search=addFilm().title.data
        print(movie_to_search)
        results=requests.get(URL+'api_key='+API_KEY+'&query='+movie_to_search+'&pages=3').json()
        print(results)
        for movies in results['results']:
            movie_info ={}
            movie_info['title'] = movies["title"]
            movie_info['description'] = movies['overview']
            movie_info['image'] = 'https://image.tmdb.org/t/p/w500' + str(movies['poster_path'])
            try:
                if '-' in movies['release_date']:
                    movie_info['date'] = movies["release_date"]
                else:
                    movie_info['date']="Unknown"
            except KeyError:
                movie_info['date'] = "Unknown"
            lis_of_movies.append(movie_info)
        return render_template('select.html',search_results=lis_of_movies)
    return render_template('add.html',form=addFilm())
@app.route('/add')
def add():
    new_movie= Movie(
        title=request.args.get('movie_title'),
        description=request.args.get('movie_description'),
        img_url=request.args.get('movie_image'),
        year=000 if request.args.get('movie_year') =='Unknown' else request.args.get('movie_year')[:4],
        rating=float(0.0),
        ranking=0,
        review=''
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit',id=new_movie.id))
if __name__ == '__main__':
    app.run(debug=True)

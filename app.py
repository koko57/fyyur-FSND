import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from mock_data import *

# App Config

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Models

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


# Filters

def format_datetime(value, format='medium'):
    date = value
    if type(value) != datetime:
        date = dateutil.parser.parse(value)
        print(type(date))
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime


# Controllers

@app.route('/')
def index():
    return render_template('pages/home.html')

#  Venues

@app.route('/venues')
def venues():
    places = Venue.query.with_entities(Venue.city, Venue.state).distinct()

    areas = [{'city': place[0], 'state': place[1]} for place in places]

    for p in areas:
        p['venues'] = Venue.query.filter(Venue.city == p['city']).all()

    return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term= request.form['search_term']
    searched_venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))

    response={
      "count": searched_venues.count(),
      "data": searched_venues
    }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    shows = Show.query.filter(Show.venue_id == venue_id).all()

    for show in shows:
      setattr(show, 'artist_name', show.artist.name)

    upcoming_shows = list(filter(lambda x: x.start_time > datetime.now(), shows))
    past_shows = list(filter(lambda x: x.start_time < datetime.now(), shows))

    setattr(venue, 'upcoming_shows', upcoming_shows)
    setattr(venue, 'upcoming_shows_count', len(upcoming_shows))
    setattr(venue, 'past_shows', past_shows)
    setattr(venue, 'past_shows_count', len(past_shows))
    return render_template('pages/show_venue.html', venue=venue)

#  Create Venue

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False

    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    facebook_link = request.form['facebook_link']
    genres = request.form.getlist('genres')
    image_link = request.form['image_link']
    website = request.form['website']
    seeking_talent = bool(request.form['seeking_talent'])
    seeking_description = request.form['seeking_description']

    try:
        new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
        db.session.add(new_venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + name + ' could not be listed.')
    else:
        flash('Venue ' + name + ' was successfully listed!')

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    try:
        db.session.delete(venue)
        db.session.commit()
        flash('Venue was successfully deleted!')
        return render_template('pages/home.html')
    except:
        error = True
        db.session.rollback()
        flash('An error occurred. Venue could not be deleted.')
    finally:
        db.session.close()

    return None

#  Artists

@app.route('/artists')
def artists():
    all_artists = Artist.query.all()
    return render_template('pages/artists.html', artists=all_artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form['search_term']
    searched_artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))

    response={
      "count": searched_artists.count(),
      "data": searched_artists
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    shows = Show.query.filter(Show.artist_id == artist_id).all()

    for show in shows:
      setattr(show, 'venue_name', show.venue.name)

    upcoming_shows = list(filter(lambda x: x.start_time > datetime.now(), shows))
    past_shows = list(filter(lambda x: x.start_time < datetime.now(), shows))

    setattr(artist, 'upcoming_shows', upcoming_shows)
    setattr(artist, 'upcoming_shows_count', len(upcoming_shows))
    setattr(artist, 'past_shows', past_shows)
    setattr(artist, 'past_shows_count', len(past_shows))

    return render_template('pages/show_artist.html', artist=artist)

#  Update

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).first()

    form.state.process_data(artist.state)
    form.genres.process_data(artist.genres)
    form.seeking_venue.process_data(artist.seeking_venue)
    form.seeking_description.process_data(artist.seeking_description)
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    name = request.form['name']

    artist.name = name
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    artist.website = request.form['website']
    artist.seeking_venue = bool(request.form['seeking_venue'])
    artist.seeking_description = request.form['seeking_description']

    error = False

    try:
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + name + ' could not be edited.')
    else:
        flash('Artist ' + name + ' was successfully edited!')

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).first()

    form.state.process_data(venue.state)
    form.genres.process_data(venue.genres)
    form.seeking_talent.process_data(venue.seeking_talent)
    form.seeking_description.process_data(venue.seeking_description)

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()

    name = request.form['name']

    venue.name = name
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.website = request.form['website']
    venue.seeking_talent = bool(request.form['seeking_talent'])
    venue.seeking_description = request.form['seeking_description']

    error = False
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue ' + name + ' could not be edited.')
    else:
        flash('Venue ' + name + ' was successfully edited!')

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
    error = False

    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    image_link = request.form['image_link']
    website = request.form['website']
    seeking_venue = bool(request.form['seeking_venue'])
    seeking_description = request.form['seeking_description']

    try:
        new_artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)
        db.session.add(new_artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist ' + name + ' could not be listed.')
    else:
        flash('Artist ' + name + ' was successfully listed!')

    return render_template('pages/home.html')

#  Shows

@app.route('/shows')
def shows():
    all_shows = Show.query.all()

    for show in all_shows:
        setattr(show, 'artist_name', show.artist.name)
        setattr(show, 'artist_image_link', show.artist.image_link)
        setattr(show, 'venue_name', show.venue.name)


    return render_template('pages/shows.html', shows=all_shows)

@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    error=False
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    try:
        new_show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(new_show)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show could not be listed.')
    else:
        flash('Show was successfully listed!')

    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')


# Launch.


# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

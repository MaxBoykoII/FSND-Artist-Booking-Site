#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

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
from itertools import groupby
from sqlalchemy.sql import func
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

Show = db.Table('Show',
                db.Column(
                    'artist_id',
                    db.Integer,
                    db.ForeignKey('Artist.id'),
                    primary_key=True),
                db.Column(
                    'venue_id',
                    db.Integer,
                    db.ForeignKey('Venue.id'),
                    primary_key=True),
                db.Column('start_time', db.DateTime, nullable=False))


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(500))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(2500))
    artists = db.relationship(
        'Artist',
        secondary=Show,
        backref=db.backref('Venue', lazy=True))

    @property
    def genres_list(self):
        genres = self.genres.split(',') if self.genres != None else []

        return genres

    @property
    def past_shows(self):
        show_data = self.__shows(Show.c.start_time < datetime.now())

        return show_data

    @property
    def upcoming_shows(self):
        show_data = self.__shows(Show.c.start_time >= datetime.now())

        return show_data

    def __shows(self, start_time_filter):
        results = db.session.query(
            Show.c.artist_id,
            Artist.name.label('artist_name'),
            Artist.image_link.label('artist_image_link'),
            func.to_char(Show.c.start_time,
                         'YYYY HH:MM:SS').label('start_time')
        ) \
            .filter(Show.c.venue_id == self.id) \
            .filter(start_time_filter) \
            .join(Artist, Artist.id == Show.c.artist_id) \
            .all()

        show_data = [r._asdict() for r in results]

        return show_data

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    venues = db.relationship(
        'Venue',
        secondary=Show,
        backref=db.backref('Artist', lazy=True))

    @property
    def genre_list(self):
        genres = self.genres.split(',') if self.genres != None else []

        return genres

    @property
    def past_shows(self):
        show_data = self.__shows(Show.c.start_time < datetime.now())

        return show_data

    @property
    def upcoming_shows(self):
        show_data = self.__shows(Show.c.start_time >= datetime.now())

        return show_data

    def __shows(self, start_time_filter):
        results = db.session.query(
            Show.c.venue_id,
            Venue.name.label('venue_name'),
            Venue.image_link.label('venue_image_link'),
            func.to_char(
                Show.c.start_time,
                'YYYY HH:MM:SS').label('start_time')
        ) \
            .filter(Show.c.artist_id == self.id) \
            .filter(start_time_filter) \
            .join(Venue, Venue.id == Show.c.venue_id) \
            .all()

        show_data = [r._asdict() for r in results]

        return show_data

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models,
#  and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    venue_query = db.session.query(Venue).order_by(
        Venue.city,
        Venue.state).all()

    groups = [
        (*key, list([{'id': v.id, 'name': v.name, 'num_upcomming_shows': 0} for v in venues])) for
        key, venues in groupby(venue_query, key=lambda v: (v.city, v.state))]

    data = [{'city': g[0], 'state': g[1], 'venues': g[2]} for g in groups]
    """
    data = [{
        "city": "San Francisco",
        "state": "CA",
        "venues": [{
            "id": 1,
            "name": "The Musical Hop",
            "num_upcoming_shows": 0,
        }, {
            "id": 3,
            "name": "Park Square Live Music & Coffee",
            "num_upcoming_shows": 1,
        }]
    }, {
        "city": "New York",
        "state": "NY",
        "venues": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }] """
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
    past_shows = venue.past_shows
    upcoming_shows = venue.upcoming_shows

    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres_list,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        venue = Venue(
            name=request.form.get('name'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            address=request.form.get('address'),
            phone=request.form.get('phone'),
            facebook_link=request.form.get('facebook_link'),
            image_link=request.form.get('image_link'),
            website=request.form.get('website'),
            seeking_description=request.form.get('seeking_description'),
            seeking_talent=True if request.form.get('seeking_talent') == 'y' else False)

        db.session.add(venue)
        db.session.commit()

        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except Exception as err:
        print(err)
        error = True
        db.session.rollback()

        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')

    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = db.session.query(Artist.id, Artist.name).all()

    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    artist = db.session.query(Artist).filter(Artist.id == artist_id).first()
    past_shows = artist.past_shows
    upcoming_shows = artist.upcoming_shows

    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genre_list,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': 'https://www.gunsnpetalsband.com',
        'facebook_link': artist.facebook_link,
        'seeking_venue': True,
        'seeking_description': "Looking for shows to perform at in the San Francisco Bay Area!",
        'image_link': artist.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    results = db.session.query(
        Show.c.venue_id,
        Show.c.artist_id,
        Venue.name.label('venue_name'),
        Artist.name.label('artist_name'),
        Artist.image_link.label('artist_image_link'),
        func.to_char(Show.c.start_time, 'YYYY HH:MM:SS').label('start_time')
    ).join(Venue, Venue.id == Show.c.venue_id) \
        .join(Artist, Artist.id == Show.c.artist_id) \
        .all()

    data = [r._asdict() for r in results]

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

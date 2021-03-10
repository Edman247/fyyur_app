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
from flask_migrate import Migrate
from models import app, db, Venue, Artist, Show
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
db.init_app(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
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

    #implement list of venues per city
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    #query for real data to replace mock data
    venues = Venue.query.all()
    data_returned = []
    areas = Venue.query.distinct(Venue.id, Venue.city, Venue.state)
    for area in areas:
        location = {}
        location['city'] = area.city
        location['state'] = area.state
        location['venues'] = []
        for venue_data in Venue.query.filter_by(city = location['city'], state = location['state']).all():
            shows = Show.query.filter(Show.venue_id ==venue_data.id, Show.start_time > datetime.today()).all()
            venues_data = {
                'id': venue_data.id,
                'name': venue_data.name,
                'num_upcoming_shows': len(shows)
            }
            location['venues'].append(venues_data)
        if location not in data_returned:
            data_returned.append(location)
    print(data_returned)
    return render_template('pages/venues.html', areas=data_returned);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term=(request.form.get('search_term'))
    search_term = "%{}%".format(search_term)
    venues = Venue.query.filter(Venue.name.ilike(search_term)).all()
    response={
        'count': len(venues),
        'data': [{
          'id': venue.id,
          'name': venue.name,
        } for venue in venues]
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    join_query = (db.session.query(Artist, Show).join(Show, Show.artist_id == Artist.id).join(Venue, Show.venue_id == venue_id))
    past_shows= join_query.filter(Show.start_time < datetime.today()).all()
    upcoming_shows = join_query.filter(Show.start_time > datetime.today()).all()

    venue = Venue.query.filter_by(id=venue_id).first_or_404()

    all_venues = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genre,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': [{
            "artist_id" : artist.id,
            "artist_name" : artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
            } for artist, show in past_shows],
        'upcoming_shows': [{
            "artist_id" : artist.id,
            "artist_name" : artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
            } for artist, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    return render_template('pages/show_venue.html', venue=all_venues)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        venue_form_data = VenueForm(request.form)
        new_venue = Venue(
            name= venue_form_data.name.data,
            city= venue_form_data.city.data,
            state= venue_form_data.state.data,
            address = venue_form_data.address.data,
            genre= venue_form_data.genres.data,
            phone= venue_form_data.phone.data,
            facebook_link= venue_form_data.facebook_link.data,
            image_link = venue_form_data.image_link.data,
            website = venue_form_data.website.data,
            seeking_talent = bool(venue_form_data.seeking_talent.data),
            seeking_description = venue_form_data.seeking_description.data
        )
        db.session.add(new_venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/delete', methods=['DELETE', 'POST'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    confirm_delete = request.form.get('confirm_delete')
    venue = Venue.query.get(venue_id)
    print(venue.name == confirm_delete)
    try:
        if (venue.name == confirm_delete):
            Venue.query.filter_by(id=venue_id).delete()
            db.session.commit()
            flash('Venue was successfully deleted!')
        else:
            flash('An error occurred. Venue could not be listed.')
    except:
        db.session.rollback()
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
    data_returned = []
    query = Artist.query.all()
    for x in query:
        artist = {}
        artist['id'] = x.id
        artist['name'] = x.name
        artist['genres'] = x.genres
        data_returned.append(artist)
    print(data_returned)
    return render_template('pages/artists.html', artists=data_returned)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term=(request.form.get('search_term'))
    search_term = "%{}%".format(search_term)
    print(search_term)
    artists = Artist.query.filter(Artist.name.ilike(search_term)).all()
    for artist in artists:
        print(artist)
    response={
        'count': len(artists),
        'data': [{
          'id': artist.id,
          'name': artist.name,
        } for artist in artists]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  join_query = (db.session.query(Venue, Show).join(Show, Show.venue_id == Venue.id).join(Artist, Show.artist_id == artist_id))
  past_shows= join_query.filter(Show.start_time < datetime.today()).all()
  upcoming_shows = join_query.filter(Show.start_time > datetime.today()).all()

  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  #for r in join_query:
  #    join_objects ={}
  #    join_objects['venue_id'] = r.Venue.id

  all_artists = {
      'id': artist.id,
      'name': artist.name,
      'genres': artist.genres,
      'city': artist.city,
      'state': artist.state,
      'phone': artist.phone,
      'website': artist.website,
      'facebook_link': artist.facebook_link,
      'seeking_talent': artist.seeking_venue,
      'seeking_description': artist.seeking_description,
      'image_link': artist.image_link,
      'past_shows': [{
          "venue_id" : venue.id,
          "venue_name" : venue.name,
          "venue_image_link": venue.image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
          } for venue, show in past_shows],
      'upcoming_shows': [{
          "venue_id" : venue.id,
          "venue_name" : venue.name,
          "venue_image_link": venue.image_link,
          "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
          } for venue, show in upcoming_shows],
      'past_shows_count': len(past_shows),
      'upcoming_shows_count': len(upcoming_shows)
  }

  print(all_artists)
  return render_template('pages/show_artist.html', artist=all_artists)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist_data = Artist.query.get(artist_id)
    artist={
    "id": artist_data.id,
    "name": artist_data.name,
    "genres": artist_data.genres,
    "city": artist_data.city,
    "state": artist_data.state,
    "phone": artist_data.phone,
    "website": artist_data.website,
    "facebook_link": artist_data.facebook_link,
    "seeking_venue": artist_data.seeking_venue,
    "seeking_description": artist_data.seeking_description,
    "image_link": artist_data.image_link
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    artist_edit_form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)
    edited_artist = Artist(
      name = artist_edit_form.name.data,
      city = artist_edit_form.city.data,
      state = artist_edit_form.state.data,
      genres= artist_edit_form.genres.data,
      phone= artist_edit_form.phone.data,
      facebook_link= artist_edit_form.facebook_link.data,
      image_link = artist_edit_form.image_link.data,
      website = artist_edit_form.website.data,
      seeking_venue = bool(artist_edit_form.seeking_venue.data),
      seeking_description = artist_edit_form.seeking_description.data
    )
    try:
        artist.name = edited_artist.name
        artist.city = edited_artist.city
        artist.state = edited_artist.state
        artist.genres = edited_artist.genres
        artist.phone = edited_artist.phone
        artist.facebook_link = edited_artist.facebook_link
        artist.image_link = edited_artist.image_link
        artist.website = edited_artist.website
        artist.seeking_venue = edited_artist.seeking_venue
        artist.seeking_description = edited_artist.seeking_description
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))

#-------------------------DONE------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue_values = Venue.query.get(venue_id)
  form = VenueForm()
  venue={
    "id": venue_values.id,
    "name": venue_values.name,
    "genres": venue_values.genre,
    "address": venue_values.address,
    "city": venue_values.city,
    "state": venue_values.state,
    "phone": venue_values.phone,
    "website": venue_values.website,
    "facebook_link": venue_values.facebook_link,
    "seeking_talent": venue_values.seeking_talent,
    "seeking_description": venue_values.seeking_description,
    "image_link": venue_values.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

#-------------------------DONE------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue_edit_form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    edited_venue = Venue(
        name = venue_edit_form.name.data,
        city = venue_edit_form.city.data,
        state = venue_edit_form.state.data,
        address = venue_edit_form.address.data,
        genre= venue_edit_form.genres.data,
        phone= venue_edit_form.phone.data,
        facebook_link= venue_edit_form.facebook_link.data,
        image_link = venue_edit_form.image_link.data,
        website = venue_edit_form.website.data,
        seeking_talent = bool(venue_edit_form.seeking_talent.data),
        seeking_description = venue_edit_form.seeking_description.data
    )
    try:
        venue.name = edited_venue.name
        venue.city = edited_venue.city
        venue.state = edited_venue.state
        venue.address = edited_venue.address
        venue.genre = edited_venue.genre
        venue.phone = edited_venue.phone
        venue.facebook_link = edited_venue.facebook_link
        venue.image_link = edited_venue.image_link
        venue.website = edited_venue.website
        venue.seeking_talent = edited_venue.seeking_talent
        venue.seeking_description = edited_venue.seeking_description
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

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
    new_artist_form = ArtistForm(request.form)
    try:
        new_artist = Artist(
                name = new_artist_form.name.data,
                city = new_artist_form.city.data,
                state = new_artist_form.state.data,
                phone = new_artist_form.phone.data,
                genres = new_artist_form.genres.data,
                facebook_link = new_artist_form.facebook_link.data,
                image_link = new_artist_form.image_link.data,
                website = new_artist_form.website.data,
                seeking_venue = bool(new_artist_form.seeking_venue.data),
                seeking_description = new_artist_form.seeking_description.data

        )
        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed')
    finally:
        db.session.close()

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., .')
    return render_template('pages/home.html')

@app.route('/artists/<int:artist_id>/delete', methods=['POST'])
def delete_artist(artist_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    confirm_delete = request.form.get('confirm_delete')
    artist = Artist.query.get(artist_id)
    print(artist.name == confirm_delete)
    try:
        if (artist.name == confirm_delete):
            Artist.query.filter_by(id=artist_id).delete()
            db.session.commit()
            flash('Artist was successfully deleted!')
        else:
            flash('An error occurred. Artist could not be deleted.')
    except:
        db.session.rollback()
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data_returned = []
    shows = Show.query.all()
    for show in shows:
        show_data = {}
        for venue in Venue.query.filter(Venue.id == show.venue_id):
            show_data['venue_id'] = venue.id
            show_data['venue_name'] = venue.name
        for artist in Artist.query.filter(Artist.id == show.artist_id):
            show_data['artist_id'] = artist.id
            show_data['artist_name'] = artist.name
            show_data['artist_image_link'] = artist.image_link
        show_data['start_time'] = show.start_time.strftime("%m/%d/%Y, %H:%M")
        data_returned.append(show_data)
    print(data_returned)

    return render_template('pages/shows.html', shows=data_returned)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)
    existing_show = Show.query.filter_by(artist_id=form.artist_id.data, venue_id=form.venue_id.data, start_time=form.start_time.data).first()
    try:
        if existing_show is None:
            new_show = Show(
            artist_id = form.artist_id.data,
            venue_id = form.venue_id.data,
            start_time = form.start_time.data
            )
            db.session.add(new_show)
            db.session.commit()
            flash('Show was successfully listed!')
        else:
            flash('An error occurred. Show could not be listed.')
    except:
        db.session.rollback()
    finally:
        db.session.close()
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success

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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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

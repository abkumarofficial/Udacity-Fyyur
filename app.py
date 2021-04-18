#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask,
  render_template,
  request,
  Response,
  flash,
  redirect,
  url_for, abort,
  jsonify
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from datetime import datetime
from forms import *
from operator import itemgetter
from flask_migrate import Migrate
import re
from models import db, Venue, Artist, Show, Genre
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)
db.init_app(app)
# connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  # getting all data from Venues Table
  venues = Venue.query.all()
  if len(venues) == 0:
    flash('There are no Venues :(, add some Venue data')
    return redirect(url_for('index'))
  cities_and_states = set()
  for venue in venues:
    cities_and_states.add( (venue.city, venue.state) )  # Add tuple, we are using set so that duplicate values wont be added in it. So our pair of City and states would be unique in Set.
  cities_and_states = list(cities_and_states)
  cities_and_states.sort(key=itemgetter(1,0))     # Sorts on second column first (state), then by city.
  now = datetime.now()

  for location in cities_and_states:
      # For this location, see if there are any venues there
      venues_list = []
      for venue in venues:
          if (venue.city == location[0]) and (venue.state == location[1]):

              # If we've got a venue to add, check how many upcoming shows it has
              venue_shows = Show.query.filter_by(venue_id=venue.id).all()
              num_upcoming = 0
              for show in venue_shows:
                  if show.start_time > now:
                      num_upcoming += 1

              venues_list.append({
                  "id": venue.id,
                  "name": venue.name,
                  "num_upcoming_shows": num_upcoming
              })
      data = []
      data.append({
          "city": location[0],
          "state": location[1],
          "venues": venues_list
      })
  return render_template('pages/venues.html', areas=data)


# resource for below pattern match : https://stackoverflow.com/questions/20363836/postgresql-ilike-query-with-sqlalchemy
@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term =  request.form.get('search_term', '').strip()
  regEx = '%' + search_term + '%'
  # filtering out the searched text
  venues = Venue.query.filter(Venue.name.ilike(regEx)).all()
  # print(venues)
  # storing current time , so that we can have a list of upcoming and past shows based on the time and date of the show
  current_time = datetime.now()
  shows_data = []
  all_shows = Show.query.all()
  for venue in venues:
    all_shows = Show.query.filter_by(venue_id=venue.id).all()
    upcomingShow = 0
    for show in all_shows:
      if show.start_time > current_time:
        upcomingShow += 1
    shows_data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": upcomingShow
    })
  response = {
    "count": len(venues),
    "data": shows_data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # venue = Venue.query.get(venue_id)
  venue = Venue.query.first_or_404(venue_id)
  genre_list = []
  # genre has to be sent as a list in the Object
  for genre in venue.genres:
    genre_list.append(genre.name)
  
  current_time = datetime.now()
  past_shows = []
  no_of_past_shows = 0
  upcoming_shows = []
  no_of_upcoming_shows = 0

  for show in venue.shows:
    # artist = Artist.query.get(show.artist_id)
    if show.start_time < current_time:
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name":  show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
      })
      no_of_past_shows += 1
    if show.start_time > current_time:
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name":  show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
      })
      no_of_upcoming_shows += 1
  
  data = {
    "id": venue_id,
    "name": venue.name,
    "genres": genre_list,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "past_shows_count": no_of_past_shows,
    "upcoming_shows": upcoming_shows,
    "upcoming_shows_count": no_of_upcoming_shows
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
  print ('Entered')
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data
  address = form.address.data.strip()
  phone = form.phone.data
  phone = re.sub('\D', '', phone)
  genres = form.genres.data
  seeking_talent = form.seeking_talent.data
  seeking_description = form.seeking_description.data.strip()
  image_link = form.image_link.data.strip()
  website = form.website.data.strip()
  facebook_link = form.facebook_link.data.strip()

  insertedGenres = Venue.query.all()

  if not form.validate():
    flash( form.errors )
    return redirect(url_for('create_venue_submission'))
  else:
    error_in_insert = False

    # Insert form data into DB
    try:
        # creates the new venue with all fields but not genre yet
        new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, \
            seeking_talent=seeking_talent, seeking_description=seeking_description, image_link=image_link, \
            website=website, facebook_link=facebook_link)
        foundElement = False
        for genre in genres:
          found_genre = Genre.query.filter_by(name=genre).one_or_none()
          if found_genre:
              # if found a genre, append it to the list
              new_venue.genres.append(found_genre)

          else:
              # found_genre was None. It's not created yet, so create it
              new_genre = Genre(name=genre)
              db.session.add(new_genre)
              new_venue.genres.append(new_genre)  # Create a new Genre item and append it
        db.session.add(new_venue)
        db.session.commit()
    except Exception as e:
      flash(f'Exception "{e}" in create_venue_submission()')
      error_in_insert = True
      db.session.rollback()
    finally:
        db.session.close()

    if not error_in_insert:
        # on successful db insert, flash success
        flash('Venue was successfully Added!')
        return redirect(url_for('index'))
    else:
        flash('An error occurred. Venue  could not be Added.')
        # return redirect(url_for('create_venue_submission'))
        abort(500)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # first getting the venue from venues table
  venue = Venue.query.get(venue_id)
  status = False
  try:
    db.session.delete(venue)
    db.session.commit()
    status = True
  except:
    status = False
  if status:
    flash('Successfully deleted the Venue')
  else:
    flash('Deletion Failed, Please try again!')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  if len(artists) == 0:
    flash('There are no Artists :(, add some Artist data')
    return redirect(url_for('index'))
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  # lets stripm the search string before use
  search_term = request.form.get('search_term', '').strip()
  # using ilike to match pattern
  artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  for artist in artists:
    shows = Show.query.filter_by(artist_id=artist.id).all()
    upcoming_shows = 0
    for show in shows:
      if show.start_time > datetime.now():
        upcoming_shows += 1
  searched_artists = []
  searched_artists.append({ 
    "id": artist.id,
    "name": artist.name,
    "num_upcoming_shows": upcoming_shows
  })

  response={
    "count": len(artists),
    "data": searched_artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # using get function to retrieve the artist
  artist = Artist.query.get(artist_id)
  genre_list = []
  # genre list has to be sent as List
  for genre in artist.genres:
    genre_list.append(genre.name)

  current_time = datetime.now()
  past_shows = []
  no_of_past_shows = 0
  upcoming_shows = []
  no_of_upcoming_shows = 0

  # below set of instructions is to fetch the information about the past and upcoming shows 
  for show in artist.shows:
    # found_venue = Venue.query.get(show.venue_id)
    if show.start_time > current_time:
      upcoming_shows.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
      })
      no_of_upcoming_shows += 1
    if show.start_time < current_time:
      past_shows.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
      })
      no_of_past_shows += 1
  # puuting everything in data now
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": genre_list,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": no_of_past_shows,
    "upcoming_shows_count": no_of_upcoming_shows
  }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if not artist:
    flash('Unable to load!')
    return redirect(url_for('index'))
  else:
    # this is to populate the form fields with the Object Data
    form = ArtistForm(obj=artist)
  # genres = Artist.query.get(artist_id)
  genres_list = []
  for genre in artist.genres:
    genres_list.append(genre.name)
  artist = {
    "id": artist_id,
    "name": artist.name,
    "genres": genres_list,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  # getting data from form data 
  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data
  phone = form.phone.data
  genres = form.genres.data
  seeking_venue = form.seeking_venue.data
  seeking_description = form.seeking_description.data.strip()
  image_link = form.image_link.data.strip()
  website_link = form.website_link.data.strip()
  facebook_link = form.facebook_link.data.strip()
  # Insert form data into DB
  try:
    # First get the existing artist object
    artist = Artist.query.get(artist_id)
    # artist = Artist.query.filter_by(id=artist_id).one_or_none()

    # Update fields
    artist.name = name
    artist.city = city
    artist.state = state
    # artist.address = address
    artist.phone = phone

    artist.seeking_venue = seeking_venue
    artist.seeking_description = seeking_description
    artist.image_link = image_link
    artist.website_link = website_link
    artist.facebook_link = facebook_link
    # deleting the genres , to update it again with the new values
    artist.genres = []
    # Basically what we are doing in the below code is, from new Genre list, we are checking if they are inn the Genre table, if not, we are creating them , and subsequently adding them to the Artist Object
    for genre in genres:
        genre_found = Genre.query.filter_by(name=genre).one_or_none()
        if genre_found:
            artist.genres.append(genre_found)
        else:
            # creating new Genre , if it does not exist
            new_genre = Genre(name=genre)
            db.session.add(new_genre)
            artist.genres.append(new_genre)  # Create a new Genre item and append it

    # Attempt to save everything
    db.session.commit()
  except:
      error_occured = True
      db.session.rollback()
  finally:
      db.session.close()

  if not error_occured:
      # on successful db update, flash success
      flash('Artist Details have been updated Successfully')
      return redirect(url_for('show_artist', artist_id=artist_id))
  else:
      flash('Updation Failed, please try Again')

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # form = VenueForm()
  venue = Venue.query.get(venue_id)
  genre_list = []
  for genre in venue.genres:
    genre_list.append(genre.name)
  form = VenueForm(obj=venue)
  venue = {
    "id": venue_id,
    "name": venue.name,
    "genres": genre_list,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()
  print ('genres', form.genres.data)
  try:
      venue = Venue.query.get(venue_id)
      # Update fields
      venue.name = form.name.data.strip()
      venue.city = form.city.data.strip()
      venue.state = form.state.data
      venue.address = form.address.data.strip()
      venue.phone = form.phone.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data.strip()
      venue.image_link = form.image_link.data.strip()
      venue.website = form.website.data.strip()
      venue.facebook_link = form.facebook_link.data.strip()
      foundElement = False

      error_occured = False
      genres = form.genres.data
      venue.genres = []
      # db.session.add(venue)
      # db.session.commit()
      i = 0
      for genre in genres:
        genre_found = Genre.query.filter_by(name=genre).one_or_none()

        if genre_found:
          venue.genres.append(genre_found)
        else:
          new_genre = Genre(name=genre)
          db.session.add(new_genre)
          venue.genres.append(new_genre)
      db.session.add(venue)
      db.session.commit()
  except:
      error_occured = True
      db.session.rollback()
  finally:
      db.session.close()
  if not error_occured:
    flash('Venue has been added successfully ')
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
      flash('Error in submitting data')
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
  form = ArtistForm()
  print ('form.genres.data', form.genres.data)
  # getting data from Form
  name = form.name.data.strip()
  city = form.city.data.strip()
  state = form.state.data
  phone = form.phone.data
  # removing anything from the string that is not a number
  phone = re.sub('\D', '', phone)
  genres = form.genres.data
  # seeking_venue = True if form.seeking_venue.data == 'Yes' else False
  seeking_venue = form.seeking_venue.data
  seeking_description = form.seeking_description.data.strip()
  image_link = form.image_link.data.strip()
  website_link = form.website_link.data.strip()
  facebook_link = form.facebook_link.data.strip()
  # getting Artist Genres
  insertedGenres = Genre.query.all()

  error_occured = False
  # Insert form data into DB
  try:
    # creating new Artist
    new_artist = Artist(name=name, city=city, state=state, phone=phone, seeking_venue=seeking_venue, seeking_description=seeking_description, image_link=image_link, website_link=website_link, facebook_link=facebook_link)
    foundElement = False # Createing a variable to check if the Genre is already present in the Genre Table
    # Basically what we are doing in the below code is, from new Genre list, we are checking if they are inn the Genre table, if not, we are creating them , and subsequently adding them to the Artist Object
    for genre in genres:
      genre_found = Genre.query.filter_by(name=genre).one_or_none()
      if genre_found:
          # if found a genre, append it to the list
          new_artist.genres.append(genre_found)

      else:
          # genre_found was None. It's not created yet, so create it
          new_genre = Genre(name=genre)
          db.session.add(new_genre)
          new_artist.genres.append(new_genre)  # Create a new Genre item and append it
    db.session.add(new_artist)
    db.session.commit()
  except:
      error_occured = True
      db.session.rollback()
  finally:
      db.session.close()

  if not error_occured:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return redirect(url_for('index'))
  else:
      flash('An error occurred. Artist ' + name + ' could not be listed.')
      print("Error in create_artist_submission()")
      abort(500)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  try:
    data = []
    for show in shows:
      artist = show.artist
      venue = show.venue
      data.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)
      })
  except:
    flash('Something went Wrong')
    return redirect(url_for('index'))
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm()

  artist_id = form.artist_id.data.strip()
  venue_id = form.venue_id.data.strip()
  start_time = form.start_time.data

  error_found = False
  
  try:
      new_show = Show(start_time=start_time, artist_id=artist_id, venue_id=venue_id)
      db.session.add(new_show)
      db.session.commit()
  except:
      error_found = True
      print(f'Error "{e}" , please try Again')
      db.session.rollback()
  finally:
      db.session.close()

  if error_found:
      flash('Error Occured')
  else:
      flash('Show was successfully Created, Have Fun')
  
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

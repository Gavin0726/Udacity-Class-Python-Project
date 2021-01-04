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
from flask_wtf import CsrfProtect


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
csrf = CsrfProtect()
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
csrf.init_app(app)
migrate = Migrate(app,db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Show(db.Model):
    __tablename__ = 'show'
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
    artist_id = db.Column( db.Integer, db.ForeignKey('artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime,primary_key=True)
    artist = db.relationship("Artist", back_populates="show_artist")
    venue = db.relationship("Venue", back_populates="show_venue")


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.String(10))
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    show_venue = db.relationship('Show',back_populates="venue")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(10))
    seeking_description = db.Column(db.String(500))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    show_artist = db.relationship('Show', back_populates="artist")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value
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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
 
  datavenues=[]
  results  = Venue.query.with_entities(Venue.city,Venue.state).distinct().all()
  
  for result in results:
    venues=[]
    venuelists = Venue.query.filter_by(city=result.city,state=result.state)
    
    for venuelist in venuelists:
      venueresults = Show.query.filter_by(venue_id=venuelist.id).all()
      num_upcoming_shows = len(venueresults)
      
      venues.append({"id":venuelist.id,"name":venuelist.name,"num_upcoming_shows":num_upcoming_shows})

    datavenues.append({"city":result.city,"state":result.state,"venues":venues})
 

 
  return render_template('pages/venues.html', areas=datavenues)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  searchname = request.form.get('search_term', '')
  search = "%{}%".format(searchname)


  data=[]
  results = Venue.query.filter(Venue.name.ilike(search)).all()
  count = len(results)
  
  for result in results:
    
    data.append({"id":result.id,"name":result.name})

  response = {"count":count,"data":data}
  

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  genres=[]
  for genresitem in venue.genres.split(","):
     
     genres.append(genresitem)
  
  past_shows=[]
  results = Show.query.filter(Show.start_time < datetime.now()).all()
  if len(results) > 0:
    for result in results:
      if result.venue_id == venue_id:
        past_show={
          "artist_id": result.artist.id,
          "artist_name": result.artist.name,
          "artist_image_link": result.artist.image_link,
          "start_time": result.start_time
        }
        past_shows.append(past_show)
  upcoming_shows=[]
  results = Show.query.filter(Show.start_time > datetime.now()).all()
  if len(results) > 0:
    for result in results:
      if result.venue_id == venue_id:
        upcoming_show={
          "artist_id": result.artist.id,
          "artist_name": result.artist.name,
          "artist_image_link": result.artist.image_link,
          "start_time": result.start_time
        }
        upcoming_shows.append(upcoming_show)
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows":past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
 
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = None
  form = VenueForm(request.form)
  
  if form.validate():
    try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      address = form.address.data
      phone = form.phone.data
      image_link = form.image_link.data
      seeking_talent = form.seeking_talent.data
      seeking_description = form.seeking_description.data
      website = form.website.data
      genres = ','.join(form.genres.data)
      facebook_link = form.facebook_link.data

      record = Venue(name=name, city=city, 
                    state=state,address=address, 
                    phone=phone,genres=genres,
                    image_link = image_link,
                    seeking_talent = seeking_talent,
                    seeking_description = seeking_description,
                    website = website,
                    facebook_link=facebook_link)      
      db.session.add(record)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      error = True
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
    return render_template('forms/new_venue.html', form=form)
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')
  
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = Artist.query.all()
 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  searchname = request.form.get('search_term', '')
  search = "%{}%".format(searchname)

  data = Artist.query.filter(Artist.name.ilike(search)).all()
  count = len(data)
  
  response = {"count":count,"data":data}

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  genres=[]
  for genresitem in artist.genres.split(","):
   
     genres.append(genresitem)
  
  past_shows=[]
  results = Show.query.filter(Show.start_time < datetime.now()).all()
  if len(results) > 0:
    for result in results:
      if result.artist_id == artist_id:
        past_show={
          "venue_id": result.venue_id,
          "venue_name": result.venue.name,
          "venue_image_link": result.venue.image_link,
          "start_time": result.start_time
        }
        past_shows.append(past_show)
  upcoming_shows=[]

  results = Show.query.filter(Show.start_time > datetime.now()).all()
  if len(results) > 0:
    for result in results:
      if result.artist_id == artist_id:
        upcoming_show={
          "venue_id": result.venue_id,
          "venue_name": result.venue.name,
          "venue_image_link": result.venue.image_link,
          "start_time": result.start_time
        }
        upcoming_shows.append(upcoming_show)


  data={
    "id": artist.id,
    "name": artist.name,
    "genres": genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows":past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }
  
  
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  genres=[]
  for genresitem in artist.genres.split(","):
     
     genres.append(genresitem)
  
  artist.genres=genres
  form = ArtistForm(obj=artist)
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form)
  
  if form.validate():
    try:
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.image_link = form.image_link.data
      artist.genres = ",".join(form.genres.data) 
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      artist.website = form.website.data
      artist.facebook_link = form.facebook_link.data

      db.session.commit()
      
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
    return render_template('forms/edit_venue.html', form=form,artist=artist)
    
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/<artist_id>/delete', methods=['GET'])
def delete_artist(artist_id):

  try:
    Artist.query.filter_by(id=artist_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  venue = Venue.query.get(venue_id)
  genres=[]
  for genresitem in venue.genres.split(","):
     
     genres.append(genresitem)
  
  venue.genres=genres
  form = VenueForm(obj=venue)
 
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  
  if form.validate():
    try:
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.image_link = form.image_link.data
      venue.genres = ",".join(form.genres.data)
      
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      venue.website = form.website.data
      venue.facebook_link = form.facebook_link.data

      db.session.commit()
      
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
    return render_template('forms/edit_venue.html', form=form,venue=venue)

  return redirect(url_for('show_venue', venue_id=venue_id))
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  
  if form.validate():
    try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      phone = form.phone.data
      image_link = form.image_link.data
      seeking_venue = form.seeking_venue.data
      seeking_description = form.seeking_description.data
      website = form.website.data
      genres = ','.join(form.genres.data)
      facebook_link = form.facebook_link.data

      record = Artist(name=name, city=city, 
                    state=state, 
                    phone=phone,genres=genres,
                    image_link = image_link,
                    seeking_venue = seeking_venue,
                    seeking_description = seeking_description,
                    website = website,
                    facebook_link=facebook_link)      
      db.session.add(record)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
  else:
    return render_template('forms/new_artist.html', form=form)
  
  return render_template('pages/home.html')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  showdata = Show.query.all()
  data = []

  for dataitem in showdata:

  # genres=[]
  # for genresitem in artist.genres.split(","):
   
  #    genres.append(genresitem)
  
    
    subdata={
      "venue_id": dataitem.venue_id,
      "venue_name": dataitem.venue.name,
      "artist_id": dataitem.artist_id,
      "artist_name": dataitem.artist.name,
      "artist_image_link": dataitem.artist.image_link,
      "start_time": dataitem.start_time
    }
    data.append(subdata)
    
  
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
  form = ShowForm(request.form)
  
  if form.validate():
    try:
      artist_id = form.artist_id.data
      venue_id = form.venue_id.data
      start_time = form.start_time.data

      v = Venue.query.get(venue_id)
      a = Artist.query.get(artist_id)
      s = Show(venue_id=1, artist_id=1, start_time=start_time)
      
      v.show_venue.append(s)
      a.show_artist.append(s)
      
      
      db.session.add_all([v,a])
      db.session.commit()

      flash('Show was successfully listed!')
    except:
      
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
    finally:
      db.session.close()
  else:
    return render_template('forms/new_artist.html', form=form)
  
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

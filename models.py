from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# Creating a genre Class, this will be the child class for both Venue and Artist
# there will be a many to many relation b/w (genre and artist)  and (genre and venue)
db = SQLAlchemy()
class Genre(db.Model):
    __tablename__ = 'Genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

# Genre Model and Artist Model has many to many relationship
artist_genre_relation = db.Table('artist_genre_relation',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)

# Genre Model and Venue Model has many to many relationship
venue_genre_relation = db.Table('venue_genre_relation',
    db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
    db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # below statement is to create a m2m relation with Genre
    genres = db.relationship('Genre', secondary=venue_genre_relation, backref=db.backref('venues'))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    # below line is to create a one to many relation with Show modal
    shows = db.relationship('Show', backref='venue', lazy=True)    # Can reference show.venue (as well as venue.shows)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # A many to many relation needs to be created with artist and genre, same as Venue and genre
    genres = db.relationship('Genre', secondary=artist_genre_relation, backref=db.backref('artists'))
    image_link = db.Column(db.String(900))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    website_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    # just like for Venue, below statement is to create a one to many relatiuon with Show
    shows = db.relationship('Show', backref='artist', lazy=True)
    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

# Creating show Class for Show page in the UI, all the fields have been created by reviewing the UI
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    def __repr__(self):
        return f'<Show {self.id} artistID={self.artist_id} venueID={self.venue_id}>'
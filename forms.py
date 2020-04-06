from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired, AnyOf, URL, Length
from choices import *


class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), AnyOf(states_list)],
        choices=states
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), AnyOf(genres_list)],
        choices=genres
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website = StringField(
        'website', validators=[URL()]
    )
    seeking_talent = SelectField(
        'seeking_talent',
        choices=[('', 'No'), ('True', 'Yes')]
    )
    seeking_description = TextAreaField(
        'seeking_description', validators=[Length(max=500)]
    )

class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(), AnyOf(states_list)],
        choices=states
    )
    phone = StringField(
        'phone', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), AnyOf(genres_list)],
        choices=genres
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website = StringField(
        'website', validators=[URL()]
    )
    seeking_venue = SelectField(
        'seeking_venue',
        choices=[('', 'No'), ('True', 'Yes')]
    )
    seeking_description = TextAreaField(
        'seeking_description', validators=[Length(max=500)]
    )
    

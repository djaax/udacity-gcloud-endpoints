"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()

    @property
    def wins(self):
        return len(Score.query(Score.user == self.key).fetch())

    def to_form(self):
        """Returns a UserForm representation of the user"""
        return UserForm(
            name=self.name,
            email=self.email,
            wins=self.wins)


class Game(ndb.Model):
    """Game object"""
    game_over = ndb.BooleanProperty(required=True, default=False)
    marks = ndb.StringProperty(required=True, default='000000000')
    user = ndb.KeyProperty(required=True, kind='User')
    cancelled = ndb.BooleanProperty(required=False)
    history = ndb.PickleProperty(required=False, default=[('000000000', 'Start')])

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game"""
        game = Game(user=user,
                    game_over=False)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.game_over = self.game_over
        form.cancelled = self.cancelled
        form.message = message
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        if won is True:
            self.history.append('You win!')
        else:
            self.history.append('You lose!')

        self.game_over = True
        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won)
        score.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name,
            won=self.won,
            date=str(self.date))


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)
    cancelled = messages.BooleanField(6, required=False)

class GameForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)


class UserForm(messages.Message):
    """UserForm for outbound user information"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    wins = messages.IntegerField(3)

class UserForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(UserForm, 1, repeated=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    mark = messages.IntegerField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

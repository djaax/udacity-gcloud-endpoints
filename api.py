# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import StringMessage, \
    NewGameForm, \
    GameForm, \
    GameForms, \
    UserForm, \
    UserForms, \
    MakeMoveForm, \
    ScoreForms

from utils import get_by_urlsafe

from random import randint

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
CANCEL_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='tic_tac_toe', version='v1')
class TicTacToeApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        try:
            game = Game.new_game(user.key)
        except ValueError:
            raise endpoints.BadRequestException('Error')

        return game.to_form('Good luck playing Tic Tac Toe!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.game_over:
              raise endpoints.ForbiddenException('Illegal action: Game is already over.')
            else:
              return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over! Marks: %s' % game.marks)

        if type(request.mark) is not int or request.mark not in range(9):
          return game.to_form('This move is illegal. Please choose a field from 0 to 8')

        marks = list(game.marks)

        if marks[request.mark] != '0':
          return game.to_form('This field is already marked %s' % marks[request.mark])

        # Field is not free, user marks X
        marks[request.mark] = 'X'        
        game.marks = ''.join(marks)
        game.history.append((game.marks, 'X marks field %s' % request.mark))
        game.put()

        def check_win(XO):
          if (marks[0] == XO and marks[1] == XO and marks[2] == XO) or \
            (marks[3] == XO and marks[4] == XO and marks[5] == XO) or \
            (marks[6] == XO and marks[7] == XO and marks[8] == XO) or \
            (marks[0] == XO and marks[4] == XO and marks[8] == XO) or \
            (marks[0] == XO and marks[3] == XO and marks[6] == XO) or \
            (marks[1] == XO and marks[4] == XO and marks[7] == XO) or \
            (marks[2] == XO and marks[5] == XO and marks[8] == XO):
            return True
          else:
            return False

        def check_tie():
          if (marks[0]=='X' or marks[0]=='O') and \
            (marks[1]=='X' or marks[1]=='O') and \
            (marks[2]=='X' or marks[2]=='O') and \
            (marks[3]=='X' or marks[3]=='O') and \
            (marks[4]=='X' or marks[4]=='O') and \
            (marks[5]=='X' or marks[5]=='O') and \
            (marks[6]=='X' or marks[6]=='O') and \
            (marks[7]=='X' or marks[7]=='O') and \
            (marks[8]=='X' or marks[8]=='O'):
            return True
          else:
            return False

        # Check for win
        if check_win('X'):
          game.end_game(True)
          return game.to_form('You Win %s!' % game.marks)

        # If every field is marked -> End game (tie)
        if check_tie is True:
          game.end_game(False)
          return game.to_form("It's a Tie %s!" % game.marks)

        # Computer marks
        ai_mark = randint(0,8)
        def computer_random_move(field):
          if ( marks[field] != '0' ):
            ai_mark = randint(0,8)
            return computer_random_move(ai_mark)
          marks[field] = 'O'
        computer_random_move(ai_mark)
        game.marks = ''.join(marks)
        game.history.append((game.marks, 'O marks field %s' % ai_mark))
        game.put()

        # Check for lose
        if check_win('O'):
          game.end_game(False)
          return game.to_form('You Lose %s!' % game.marks)

        return game.to_form(game.marks)


    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
      """Returns all of a User's active games"""
      user = User.query(User.name == request.user_name).get()
      if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')

      games = Game.query(
        Game.user == user.key,
        Game.game_over == False,
        Game.cancelled != True)

      return GameForms(items=[
        game.to_form('Marks: %s' % game.marks) for game in games])

    
    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}/cancel',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
      '''This endpoint allows users to cancel a game in progress. '''
      game = get_by_urlsafe(request.urlsafe_game_key, Game)
      if game.game_over == True:
        raise endpoints.NotFoundException(
                    'This game is already completed')

      game.cancelled = True
      game.put()

      return game.to_form('cancelled')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
      '''Return the history of a game'''
      game = get_by_urlsafe(request.urlsafe_game_key, Game)
      return game.to_form(str(game.history))

    @endpoints.method(response_message=UserForms,
                      path='users/ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
      '''Returns all players ranked by performance'''
      users = User.query()
      users = sorted(users, key=lambda x: x.wins, reverse=True)
      return UserForms(items=[user.to_form() for user in users])


api = endpoints.api_server([TicTacToeApi])

# Udacity Design a Game: Tic Tac Toe

## Section 0: Intro
This API is built with python running on the Google Cloud Platform, powered by API Endpoints. The API is designed for a game of tic tac toe against an AI.

## Section 1: Setup environment:
1. Install the Google Cloud SDK for your environment. A install guide can be found [here](https://cloud.google.com/sdk/docs/quickstarts)
2. Install the SDK for App Engine for Python. You can find an install guide [here](https://cloud.google.com/sdk/docs/)

## Section 2: Install and run
Clone or download this project. Open a terminal and navigate to its path. Using ```dev_appserver.py .```you can run the app.

## Section 3: Usage
Open a browser and navigate to ```localhost:8080/_ah/api/explorer``` (default settings).
Note: If you see the API Explorer window but no API listed, you may have to launch your browser in dev mode. For Chrome on Mac use the following command ```/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --user-data-dir=test --allow-running-insecure-content```

## Section 4: Description
The board is represented as a string, e.g. X00OX0OOX. It comprises 9 fields, every 3 fields is a row:

| X | 0 | 0 |
|---|---|---|
| O | X | 0 |
| O | O | X |

In this example, player X (user) wins with marks on postion 1, 5, and 9

## Section 5: Play!
Launch the API Explorer (```localhost:8080/_ah/api/explorer```) and click the tic_tac_toe API. You'll find a list of endpoints which you can use.

1. Create a user (tic_tac_toe.create_user) and memorize the user name.
2. Create a game (tic_tac_toe.new_game) with the user_name from step 1 and copy the games key from the response.
3. Make a move (tic_tac_toe.make_move) with the game key copied in step 2. Mark the numeric field which you want to mark as an X. The AI will make a move immediately and returns the marks in the response (see message attribute). Example: If you want to mark the field in the middle of the board (horizontally and vertically) with an X, mark field with index 5. To mark the upper right corner field, mark field with index 3 and so on.

## Section 6: Files Included
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity definitions and their helpful functions.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

## Section 7: Endpoints Included
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, min, max, attempts
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Min must be less than
    max. Also adds a task to a task queue to update the average moves remaining
    for active games.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Accepts a 'guess' and returns the updated state of the game.
    If this causes a game to end, a corresponding Score entity will be created.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

 - **get_user_games**
    - Path: 'games/user/{user_name}'
    - Method: GET,
    - Parameters: user_name
    - Returns GameForms.
    - Description: Returns all of a User's active games

 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}/cancel'
    - Method: GET,
    - Parameters: urlsafe_game_key
    - Returns GameForm.
    - Description: This endpoint allows users to cancel a game in progress.

 - **get_game_history**
    - Path: 'game/{urlsafe_game_key}/history'
    - Method: GET,
    - Parameters: urlsafe_game_key
    - Returns GameForm.
    - Description: Return the history of a game

 - **get_user_rankings**
    - Path: 'users/ranking'
    - Method: GET,
    - Parameters: none
    - Returns UserForms.
    - Description: Returns all players ranked by performance

## Section 7: Models Included
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
## Section 8: Forms Included
 - **GameForm**
    - Representation of a Game's state (urlsafe_key,
    game_over flag, message, user_name, cancelled).
-  **GameForms**
    - Multiple GameForm container.
 - **NewGameForm**
    - Used to create a new game (user_name)
 - **MakeMoveForm**
    - Inbound make move form (guess).
 - **UserForm**
    - Representation of a User (name, email, wins).
 - **UserForms**
    - Multiple UserForm container.
 - **ScoreForm**
    - Representation of a completed game's Score (user_name,
    date, won flag).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **StringMessage**
    - General purpose String container.
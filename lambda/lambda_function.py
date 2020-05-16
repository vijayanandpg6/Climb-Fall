# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import requests
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from random import randrange
from ask_sdk_model import Response
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


repeat_text = "Repeat"
gameName = "Climb Fall"
alexaOP_introduction = "Welcome to, " + gameName + " game. In the 13th century, the snakes and ladders game was invented, where the players climb when they reach the ladder, and fall when they reach the snake. This will not be your usual snake and ladder game, and can be played by only two players. After each player rolls a die, you will be asked a quiz with four options. If you tell the correct answer, you will get an option to roll another die. By rolling this die, you get a chance either to increase your position, or reduce your opponents position, whichever you choose. Sounds fun? "
alexaOP_rules = ""

# Game States
INITIALIZE = "INITIALIZE"
START = "START"
PLAYERTURNS = "PLAYERTURNS"
GAMEOVER = "GAMEOVER"  

# Player States
ROLLDIEANDQUESTION = "ROLLDIEANDQUESTION"
VALIDATEANSWER = "VALIDATEANSWER"
INCREASE = "INCREASE"
REDUCE = "REDUCE"

# sound effects
alexaOP_hammer = "<audio src=\"soundbank://soundlibrary/chairs/seats_stools/seats_stools_06\"/>"
alexaOP_scifiZapElectric = "<audio src=\"soundbank://soundlibrary/scifi/amzn_sfx_scifi_zap_electric_02\"/>"
alexaOP_gameshowOutro = "<audio src=\"soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_intro_01\"/>"
alexaOP_wrongAnswer = "<audio src=\"soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_negative_response_01\"/>"
alexaOP_correctAnswer = "<audio src=\"soundbank://soundlibrary/ui/gameshow/amzn_ui_sfx_gameshow_positive_response_01\"/>"
alexaOP_applauce = "<audio src=\"soundbank://soundlibrary/human/amzn_sfx_crowd_applause_01\"/>"
alexaOP_walk = "<audio src=\"soundbank://soundlibrary/human/amzn_sfx_human_walking_01\"/>"
alexaOP_snake = "<audio src=\"soundbank://soundlibrary/scifi/amzn_sfx_scifi_air_escaping_01\"/>"
alexaOP_roll = "<audio src=\"soundbank://soundlibrary/toys_games/board_games/board_games_07\"/>"

class GameState(Enum):
    Intialize = 1
    Start = 2
    PlayerTurns = 3
    GameOver = 4

class PlayerState(Enum):
    RollDieAndQuestion = 1
    ValidateAnswer = 2

# currentPlayer = 0
snakes = {
    8: 4,
    18: 1,
    26: 10,
    39: 5,
    51: 6,
    54: 36,
    56: 1,
    60: 23,
    75: 28,
    83: 45,
    85: 59,
    90: 48,
    92: 25,
    97: 87,
    99: 63
}

ladders = {
    3: 20,
    6: 14,
    11: 28,
    15: 34,
    17: 74,
    22: 37,
    38: 59,
    49: 67,
    57: 76,
    61: 78,
    73: 86,
    81: 98,
    88: 91
}


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attr = handler_input.attributes_manager.session_attributes
        attr["GameState"] = "INITIALIZE"
        attr["PlayerState"] = "ROLLDIEANDQUESTION"
        attr["PreviousQuestion"] = ""
        attr["Options"] = []
        attr["CorrectOption"] = ""
        attr["CorrectOptionID"] = ""
        attr["CurrentPlayer"] = 1
        attr["Player1"] = 0
        attr["Player2"] = 0
        attr["SecondDie"] = 0
        speak_output = alexaOP_gameshowOutro + alexaOP_introduction + alexaOP_rules + alexaOP_startGame
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class  PlayGameIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PlayGameIntent")(handler_input)
        
    def handle(self, handler_input):
        attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        
        # Configurable values
        numberOfPlayers = 2 #slots['NumberOfPlayers']
        difficulty = 2 # slots['Difficulty']
        
        speak_output = "Okay"
        #speak_output += str(slots['QuizResponse'])
        
        if(attr.get("GameState") == "INITIALIZE"):
            attr["GameState"] = "PLAYERTURNS"
            # board construct logic
            speak_output = "Let me construct the board for you. " + alexaOP_scifiZapElectric + "We are now ready to start the game. " + alexaOP_gameshowOutro
		if(attr.get("GameState") == "PLAYERTURNS"):
            currentPlayer = attr.get("CurrentPlayer")
            if(attr.get("PlayerState") == "INCREASE"):
                cplayer = attr["CurrentPlayer"] + 1
                if(cplayer > 2):
                    cplayer = 1
                player = "Player" + str(cplayer)
                attr[player] += attr["SecondDie"]
                attr["PlayerState"] = "ROLLDIEANDQUESTION"
                if attr[player] in snakes:
                    final_value = snakes.get(attr[player])
                    attr[player] -= final_value
                    speak_output += "Oh no! There is a snake. " + player + " falling down to position " + str(attr[player]) + ". " + alexaOP_snake
                    
                if attr[player] in ladders:
                    final_value = ladders.get(attr[player])
                    attr[player] += final_value
                    speak_output +=  "Yay! There is a ladder. " + player + " climbing up to position " + str(attr[player]) + ". " + alexaOP_walk
                if(attr.get("Player1") >= MAXVALUE):
                    speak_output += "Player 1 wins. Congratulations. " + alexaOP_applauce + "Thank you for playing this game."
                    attr["GameState"] = "INITIALIZE"
                    attr["PlayerState"] = "ROLLDIEANDQUESTION"
                    return (
                        handler_input.response_builder
                            .speak(speak_output)
                            .response
                    )
			if(attr.get("Player2") >= MAXVALUE):
                    speak_output += "Player 2 wins. Congratulations. " + alexaOP_applauce + "Thank you for playing this game."
                    attr["GameState"] = "INITIALIZE"
                    attr["PlayerState"] = "ROLLDIEANDQUESTION"
                    return (
                        handler_input.response_builder
                            .speak(speak_output)
                            .response
                    )
                speak_output += " Now, Player 1 at position " + str(attr["Player1"]) + " and Player 2 at position " + str(attr["Player2"])  + ". "
			elif(attr.get("PlayerState") == "REDUCE"):
                player = "Player" + str(currentPlayer)
                attr[player] -= attr["SecondDie"]
                if(attr.get(player) < 0):
                    attr[player] = 0
                attr["PlayerState"] = "ROLLDIEANDQUESTION"
                if attr[player] in snakes:
                    final_value = snakes.get(attr[player])
                    attr[player] -= final_value
                    speak_output += "Oh no! There is a snake. " + player + " falling down to position " + str(attr[player]) + ". " + alexaOP_snake
                    
                if attr[player] in ladders:
                    final_value = ladders.get(attr[player])
                    attr[player] += final_value
                    speak_output += "Yay! There is a ladder. " + player + " climbing up to position " + str(attr[player]) + ". " + alexaOP_walk
                if(attr.get("Player1") >= MAXVALUE):
                    speak_output += "Player 1 wins. Congratulations. " + alexaOP_applauce + "Thank you for playing this game."
                    attr["GameState"] = "INITIALIZE"
                    attr["PlayerState"] = "ROLLDIEANDQUESTION"
                    return (
                        handler_input.response_builder
                            .speak(speak_output)
                            .response
                    )
                if(attr.get("Player2") >= MAXVALUE):
                    speak_output += "Player 2 wins. Congratulations. " + alexaOP_applauce + "Thank you for playing this game."
                    attr["GameState"] = "INITIALIZE"
                    attr["PlayerState"] = "ROLLDIEANDQUESTION"
                    return (
                        handler_input.response_builder
                            .speak(speak_output)
                            .response
                    )
                speak_output += " Now, Player 1 at position " + str(attr["Player1"]) + " and Player 2 at position " + str(attr["Player2"])  + ". "
			if(attr.get("PlayerState") == "VALIDATEANSWER"):
                # 3. validate user's VALIDATEANSWER
                currentAnswer = str(slots['QuizResponse'].value)
                answerOption = ""
                if(str(attr.get("CorrectOptionID")) == currentAnswer):
                #if(attr.get("CorrectOption").lower() == currentAnswer.lower()):
                    secondDie = random.randint(1, 6)
                    attr["SecondDie"] = secondDie
                    speak_output = alexaOP_correctAnswer + "Yay! Your answer is correct. Rolling your second die." + alexaOP_roll + " You hit a " + str(secondDie) + ". "
                    if(attr.get("Player1") >= MAXVALUE):
                        speak_output += "Player 1 wins. Congratulations. " + alexaOP_applauce + "Thank you for playing this game."
                        attr["GameState"] = "INITIALIZE"
                        attr["PlayerState"] = "ROLLDIEANDQUESTION"
                        return (
                            handler_input.response_builder
                                .speak(speak_output)
                                .response
                        )
						if(attr.get("Player2") >= MAXVALUE):
                        speak_output += "Player 2 wins. Congratulations. " + alexaOP_applauce + "Thank you for playing this game."
                        attr["GameState"] = "INITIALIZE"
                        attr["PlayerState"] = "ROLLDIEANDQUESTION"
                        return (
                            handler_input.response_builder
                                .speak(speak_output)
                                .response
                        )
                    speak_output += "You have two options. You can either increase your score or reduce your opponents score. Do you want to, increase? or reduce?"
                    return (
                        handler_input.response_builder
                            .speak(speak_output)
                            .ask(speak_output)
                            .response
                    )
                    # 4. Roll another die options
                else:
                    if(attr.get("CorrectOptionID") == 1):
                        answerOption = "one"
                    elif(attr.get("CorrectOptionID") == 2):
                        answerOption = "two"
                    elif(attr.get("CorrectOptionID") == 3):
                        answerOption = "three"
                    elif(attr.get("CorrectOptionID") == 4):
                        answerOption = "four"
                    speak_output = alexaOP_wrongAnswer + "Uh Oh! Wrong answer. Correct answer is Option " + answerOption + ", " + attr.get("CorrectOption") + " . "
                speak_output += " Player 1 at position " + str(attr["Player1"]) + " and Player 2 at position " + str(attr["Player2"])  + ". "
                attr["PlayerState"] = "ROLLDIEANDQUESTION"
			if(attr.get("PlayerState") == "ROLLDIEANDQUESTION"):
                # 1. Roll first die
                speak_output += "Player " + str(currentPlayer) + "'s turn. " + "Rolling your first die. " + alexaOP_roll
                firstDie = random.randint(1, 6)
                speak_output += "You hit a " + str(firstDie) + ". "
                # 2. ask question and display options
                attr["CurrentPlayer"] =  attr["CurrentPlayer"] + 1
                if(attr.get("CurrentPlayer") > 2):
                    attr["CurrentPlayer"] = 1
                player = "Player" + str(currentPlayer)
                attr[player] += firstDie
				if(attr.get("Player2") >= MAXVALUE):
                        speak_output += "Player 2 wins. Congratulations. " + alexaOP_applauce + "Thank you for playing this game."
                        attr["GameState"] = "INITIALIZE"
                        attr["PlayerState"] = "ROLLDIEANDQUESTION"
                        return (
                            handler_input.response_builder
                                .speak(speak_output)
                                .response
                        )
                    speak_output += "You have two options. You can either increase your score or reduce your opponents score. Do you want to, increase? or reduce?"
                    return (
                        handler_input.response_builder
                            .speak(speak_output)
                            .ask(speak_output)
                            .response
                
                #Todo: quiz logic here....................  difficulty - 1,2,3
                game_difficulty = {1:"easy", 2:"medium" , 3:"hard"}
                
				#attr["PreviousQuestion"] = "whats your name?"
                #attr["Options"] = ["Bhu", "George", "Einstein", "Albert"]
                question_with_options = "Question. " + attr["PreviousQuestion"] + " Option one, " + attr["Options"][0] +",  Option two, "+ attr["Options"][1]+",  Option three, "+ attr["Options"][2]+",  Option four, "+ attr["Options"][3] + ". Is it, option one, option two, option three, or option four?"
                speak_output += question_with_options
                attr["PlayerState"] = "VALIDATEANSWER"
                
                    
        # api-endpoint 
                URL = "https://opentdb.com/api.php?amount=1"

                #attr["PreviousQuestion"] = "whats your name?"
                #attr["Options"] = ["Bhu", "George", "Einstein", "Albert"]
                question_with_options = "Question. " + attr["PreviousQuestion"] + " Option one, " + attr["Options"][0] +",  Option two, "+ attr["Options"][1]+",  Option three, "+ attr["Options"][2]+",  Option four, "+ attr["Options"][3] + ". Is it, option one, option two, option three, or option four?"
                speak_output += question_with_options
                attr["PlayerState"] = "VALIDATEANSWER"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class IncreaseIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("IncreaseIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attrib = handler_input.attributes_manager.session_attributes
        attrib["PlayerState"] = "INCREASE"
        return PlayGameIntentHandler().handle(handler_input)

class ReduceIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ReduceIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        attrib = handler_input.attributes_manager.session_attributes
        attrib["PlayerState"] = "REDUCE"
        return PlayGameIntentHandler().handle(handler_input)

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IncreaseIntentHandler())
sb.add_request_handler(ReduceIntentHandler())
#sb.add_request_handler(OptionsIntentHandler())
sb.add_request_handler(PlayGameIntentHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()

# Built using Alexa Skills Kit SDK for Python.
# Song Match by Yash Goenka
# Built an Alexa skill which lets users learn the song by their favorite musician that best matches their life.
# Currently works for the Artists: Adele, David Bowie, Kanye West, Madonna

import random
import logging
import ask_sdk_core.utils as ask_utils
import json

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


#Utility functions
def get_random_yes_no_question():
    """Return exit question for YES/NO answering."""
    # type: () -> str
    questions = [
        "Would you like to get another Song Match with a different artist?",
        "Can I help you get a Song Match for a different artist?",
        "Do you want to try it for another artist?"]
    return random.choice(questions)

def get_random_goodbye():
    """Return random goodbye message."""
    # type: () -> str
    goodbyes = ["OK.  Goodbye!", "Have a great day!", "Come back again soon!"]
    return random.choice(goodbyes)

def get_random_speechcon():
    """Return speechcon"""
    SPEECHCONS = ['hmm','awesome','ah']
    text = ("<say-as interpret-as='interjection'>{} !"
            "</say-as><break strength='strong'/>")
    return text.format(random.choice(SPEECHCONS))

def get_excited(phrase):
    """Return excited ssml"""
    text = ("<speak><amazon:emotion name='excited' intensity='high'>{}</amazon:emotion></speak>")
    return text.format(phrase)

def get_medium_excited(phrase):
    """Return excited ssml"""
    text = ("<speak><amazon:emotion name='excited' intensity='medium'>{}</amazon:emotion></speak>")
    return text.format(phrase)


#Skill Handlers
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch Requests.
    User starts the skill with the invocation name
    The handler requests from the users the name of thier favorite artis
    
    User says: Alexa, open Song Match.
    
    Alexa says: Welcome to Song Match! I can help you understand which song by
            your favorite artist best matches your life. Please tell me 
            the name of your favorite artist.
    
    User says: David Bowie
    """
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speech = "Welcome to Song Match! I can help you understand which song by your favorite artist best matches your life. Please tell me the name of your favorite artist."
        
        reprompt = "My favorite artist is Kanye West. Who is yours?"
        
        handler_input.response_builder.speak(get_excited(speech)).ask(get_excited(reprompt))
        return handler_input.response_builder.response


class CaptureArtistIntentHandler(AbstractRequestHandler):
    """Handler for CaptureArtistIntent.
    Captures name of artist with slot type AMAZON.Musician
    Alexa asks first questions
    """
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CaptureArtistIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        session_attr = handler_input.attributes_manager.session_attributes
        artist = session_attr["artist"] = slots["artist"].value
        questionNum_list = session_attr["questionNum_list"] = ARTISTS.get(artist)
        speak_output = ("So you like {artist}. That's awesome! Now. Answer the next three questions "
                        "so that we can figure out which song of theirs best matches your life. Here's "
                        "your first question. {q1}".format(artist=artist, q1=QUESTIONS.get(questionNum_list[0])))
        return (
            handler_input.response_builder
                .speak(get_medium_excited(speak_output))
                .ask("{q1}".format(q1=QUESTIONS.get(questionNum_list[0])))
                .response
        )

class AnswerOneIntentHandler(AbstractRequestHandler):
    """
    Picks up first aswer and asks second question.
    """
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AnswerOneIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        session_attr["answerOne"] = slots["answerOne"].value
        questionNum_list = session_attr["questionNum_list"]
        speak_output = ("<say-as interpret-as='interjection'>{sc}!</say-as><break strength='strong'/>"
                        " Next question. {q2}".format(sc=random.choice(SPEECHCONS), q2=QUESTIONS.get(questionNum_list[1])))
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("{q2}".format(q2=QUESTIONS.get(questionNum_list[1])))
                .response
        )

class AnswerTwoIntentHandler(AbstractRequestHandler):
    """
    Picks up second aswer and asks third question.
    """
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AnswerTwoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        session_attr["answerTwo"] = slots["answerTwo"].value
        questionNum_list = session_attr["questionNum_list"]
        speak_output = ("Great! Next question. {q3}".format(q3=QUESTIONS.get(questionNum_list[2])))
        return (
            handler_input.response_builder
                .speak(get_medium_excited(speak_output))
                .ask("{q3}".format(q3=QUESTIONS.get(questionNum_list[2])))
                .response
        )

class AnswerThreeIntentHandler(AbstractRequestHandler):
    """
    Picks up second aswer.
    Figures out and says the uninque song match.
    Asks if we want to try again with another artist
    """
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AnswerThreeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        session_attr = handler_input.attributes_manager.session_attributes
        slots = handler_input.request_envelope.request.intent.slots
        artist = session_attr["artist"]
        songList = SONGS.get(artist)
        answerThree = session_attr["answerThree"] = slots["answerThree"].value
        answerTwo = session_attr["answerTwo"]
        answerOne = session_attr["answerOne"]
        test2 = ANSWERS.get(1)[0][0]
        
        songNum = -1
        if answerOne in ANSWERS.get(1)[0]:
            if answerTwo in ANSWERS.get(2)[0]:
                if answerThree in ANSWERS.get(3)[0]:
                    songNum = 0
                else:
                    songNum = 1
            else:
                if answerThree in ANSWERS.get(3)[0]:
                    songNum = 2
                else:
                    songNum = 3
        else:
            if answerTwo in ANSWERS.get(2)[0]:
                if answerThree in ANSWERS.get(3)[0]:
                    songNum = 4
                else:
                    songNum = 5
            else:
                if answerThree in ANSWERS.get(3)[0]:
                    songNum = 6
                else:
                    songNum = 7
                    
        speak_output = "Based on your answers, your {artist} Song Match is {song}. {yesno}".format(artist=artist, song= songList[songNum], yesno= get_random_yes_no_question())
        return (
            handler_input.response_builder
                .speak(get_excited(speak_output))
                .ask(get_random_yes_no_question())
                .response
        )

class YesHandler(AbstractRequestHandler):
    """If the user says Yes, they want to do the song match again
    with another artist
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In YesHandler")
        #return LaunchRequestHandler.handle(handler_input)
        return  LaunchRequestHandler.handle(handler_input)


class NoHandler(AbstractRequestHandler):
    """If the user says No, then alexa says bye and the skill should be exited."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In NoHandler")

        return handler_input.response_builder.speak(
            get_random_goodbye()).set_should_end_session(True).response


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

        # Any cleanup logic goes here.

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

#Data

QUESTIONS = {
    1 : "Do you wet your toothbrush before or after putting toothpaste?",
    2 : "When you were a kid, were you extroverted or introverted?",
    3 : "If you could colonize a planet out of Mars or Jupiter, which one would it be?",
    4 : "Which social media platform do you use more? Facebook or Instagram?",
    5 : "For your cheat meal, what would you prefer? Burger or Pizza?",
    6 : "What do you think of flat earthers? Crazy or brilliant?",
    7 : "Robots vs Humans. Who would win?",
    8 : "Would you rather go to the beach or to a hill for a vacation?",
    9 : "What do you like more for breakfast, pancakes or waffles?"
}

ANSWERS = {
    1 : [['before','extroverted','crazy'],['after','introverted','brilliant']],
    2 : [['Mars', 'robots','beach'],['Jupiter', 'humans','hill']],
    3 : [['Facebook','burger','pancakes'],['Instagram','pizza','waffles']],
}

ARTISTS = {"Adele" : [1,8,4], "David bowie":[2,3,5], "Kanye west": [6,7,9], "Madonna": [1,7,4]}

SONGS = {
    "Adele" : ["Someone Like You","Rumour Has It","Skyfall","Chasing Pavements","Set Fire to the Rain","Rolling in the Deep","Hello","Hometown Glory"],
    "David bowie" : ["Rebel Rebel","Life on Mars?","Station to Station","Starman","Young Americans","Sound and Vision","Heroes","Ashes to Ashes"], 
    "Kanye west" : ["Heartless","Stronger","Devil in a New Dress","Gold Digger","Jesus Walks","Runaway","Waves","Touch the Sky"], 
    "Madonna" : ["Like a Virgin","Borderline","Live to Tell","Like a Prayer","Open Your Heart","Express Yourself","Burning Up","Material Girl"]}

SPEECHCONS = ['hmm','awesome','ah']



# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CaptureArtistIntentHandler())
sb.add_request_handler(AnswerOneIntentHandler())
sb.add_request_handler(AnswerTwoIntentHandler())
sb.add_request_handler(AnswerThreeIntentHandler())

sb.add_request_handler(YesHandler())
sb.add_request_handler(NoHandler())

sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
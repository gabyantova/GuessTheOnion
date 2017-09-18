
import json
import requests
import time
import unidecode
from random import randint


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }



current_correct_answer = ""

# --------------- Functions that control the skill's behavior ------------------



def get_headlines(type_of_onion):
    user_pass_dict = {'user' : 'LetsReadAlexa',
		      'passwd': 'helloalexa21',
                      'api_type': 'json'}
    sess = requests.Session()
    sess.headers.update({'User-Agent': 'I am testing Alexa: Sentdex'})
    sess.post('https://www.reddit.com/api/login', data = user_pass_dict)
    time.sleep(3)
    url = 'https://reddit.com/r/' + type_of_onion + '/.json?limit=10'
    html = sess.get(url)
    data = json.loads(html.content.decode('utf-8'))
    titles = [unidecode.unidecode(listing['data']['title']) for listing in data['data']['children']]
    return titles


def get_random_headline():
    random = randint(0,1)
    if (random == 0):
        subreddit = "The Onion"
        headlinearray = get_headlines('theonion')
        randomheadline = headlinearray[randint(0,len(headlinearray)-1)]

    else:
        subreddit = "Not The Onion"
        headlinearray = get_headlines('nottheonion')
        randomheadline = headlinearray[randint(0,len(headlinearray)-1)]
    
    return {"subreddit": subreddit, "headline": randomheadline}


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome!"
    welcome_msg = "Welcome to the 'Guess the onion' online game. " \
                    "I will read you a headline from either the subreddit 'The Onion', or 'Not the onion', and you have to guess if it's a real headline or not. " \
                    "For example, if you think the headline is made up, say 'The Onion'. Otherwise, say 'Not'. To get your first headline, say 'Give me a headline'. "
    


    speech_output = welcome_msg
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = None
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_response(intent, session):

    session_attributes = {}
    card_title = "Response feedback: "


    if 'Answer' in intent['slots']:
        answer = intent['slots']['Answer']['value']
        #current_correct_answer = "The Onion"#session['attributes']['correct_subreddit']
        #session_attributes = {"answer": answer}
        if session.get('attributes', {}) and "correct_subreddit" in session.get('attributes', {}):
            current_correct_answer = session['attributes']['correct_subreddit']
            if answer.lower() == current_correct_answer.lower() or current_correct_answer.lower().split(" ")[0] == answer.lower():
                speech_output = "You are correct. To continue playing, please say 'Give me a headline'."
            else:
                speech_output = "Sorry, you are incorrect. To continue playing, please say 'Give me a headline'."
            reprompt_text = "Please say 'Give me a headline if you would like to continue playing. Otherwise say 'stop'. "
        else:
            speech_output = "Please say 'Give me a headline', to receive a question. "
            reprompt_text = "I'm sorry. Please request a new headline by saying 'Give me a headline'. "
    else:
        speech_output = "I didn't understand your answer. " 
        reprompt_text = "Sorry, I didn't understand your response. Please say 'The onion' if you think that was a real article, or say 'Not', if you think it was made up. "

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))



def give_me_a_headline(intent, session):

    current_correct_answer = "The Onion"

    session_attributes = {}
    card_title = "Here is your headline: "

    randomheadlinedict = get_random_headline()
    headline = randomheadlinedict["headline"]
    subreddit = randomheadlinedict["subreddit"]
    question = headline + "... Is that 'The onion' or 'Not'?"
    session_attributes = {"correct_subreddit" : subreddit, "user_answer": None}

    current_correct_answer = subreddit

    speech_output = question
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "If you think the headline is real, say 'The Onion'. Otherwise, say 'Not'."
    should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Goodbye!"
    speech_output = "Thank you for playing 'Guess the onion'! " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "answerQuestionIntent":
        return handle_response(intent, session)
    elif intent_name == "giveMeAHeadlineIntent":
        return give_me_a_headline(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])




import os
import openai
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
from flask import Flask, request
import time
from dotenv import load_dotenv

load_dotenv()

# Set your API keys
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)

MAX_RETRIES = 3

def get_ai_response(user_query):
    try:
        response = client.chat.completions.create(  # Correct method for chat models
            model="gpt-3.5-turbo",  # Ensure you're using a chat model
            messages=[
                {"role": "system", "content":
                    "You are an AI assistant for a logistics company. "
                    "You handle customer queries about shipment tracking, delivery status, "
                    "pickup scheduling, and general logistics support. "
                    "Support the user with whatever queries they are asking."
                 },
                {"role": "user", "content": user_query}
            ],
            max_tokens=150,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error with AI: {e}")
        return "I'm sorry, I couldn't process your request."

def process_user_input(recognized_text, retry_count=0):
    try:

        prompt = f"User has asked for assistance. They said: '{recognized_text}'. Please provide a clear and specific response to help the user with their request."
        ai_response = get_ai_response(prompt)

        return ai_response

    except Exception as e:
        print(f"Error in process_user_input: {e}")
        if retry_count < MAX_RETRIES:
            print(f"Retrying... Attempt {retry_count + 1}/{MAX_RETRIES}")
            time.sleep(2)
            return process_user_input(recognized_text, retry_count + 1)
        else:
            return "Sorry, I'm having trouble processing your request."

def handle_ivr_call(mobile_number):
    try:
        call = twilio_client.calls.create(
            to=mobile_number,
            from_=TWILIO_PHONE_NUMBER,
            url="http://localhost:5000/ivr"
        )
        print(f"Call initiated to {mobile_number}")
    except Exception as e:
        print(f"Error initiating call: {e}")

app = Flask(__name__)

@app.route("/trigger_ivr", methods=["POST"])
def trigger_ivr():

    mobile_number = request.json.get("mobileNumber")
    if not mobile_number:
        return "mobileNumber is required", 400

    handle_ivr_call(mobile_number)
    return "IVR call initiated successfully", 200

@app.route("/ivr", methods=["POST"])
def ivr():
    response = VoiceResponse()
    response.say("Hello! How can I assist you today?", voice="alice", language="en-US")

    gather = Gather(input="speech", action="/process_audio", timeout=5, speech_timeout="auto")
    response.append(gather)
    return str(response)

@app.route("/process_audio", methods=["POST"])
def process_audio():
    recognized_text = request.form.get("SpeechResult")

    if recognized_text:
        ai_response = get_ai_response(recognized_text)
    else:
        ai_response = "I couldn't hear you clearly. Could you please repeat?"

    response = VoiceResponse()

    # Ensure Twilio reads the full response by breaking it into parts
    sentences = ai_response.split(". ")  # Split sentences for better pacing
    for sentence in sentences:
        response.say(sentence, voice="alice", language="en-US")
        response.pause(length=1)  # Add a 1-second pause after each sentence

    # Add a Gather input to continue the conversation
    gather = response.gather(input="speech", action="/process_audio", timeout=5, speech_timeout="auto")
    response.append(gather)

    return str(response)


@app.route("/ping", methods=["GET"])
def ping():
    return "WORKING!", 200

if __name__ == "__main__":
    app.run(debug=True)


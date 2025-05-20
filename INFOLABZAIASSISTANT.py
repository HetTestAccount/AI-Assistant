# import os
# import json
# import base64
# import asyncio
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import websockets
# from fastapi import FastAPI, WebSocket, Request
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.websockets import WebSocketDisconnect
# from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
# from dotenv import load_dotenv
# import requests
# from datetime import datetime
# from pymongo import MongoClient
# from bson import ObjectId

# load_dotenv()

# app = FastAPI()

# # Configuration
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# SMS_KEY = os.getenv('SMS_KEY')
# PORT = int(os.getenv('PORT', 5000))
# SMS_URL = "https://www.fast2sms.com/dev/bulkV2"
# EMAIL_HOST = os.getenv('EMAIL_HOST')
# EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
# EMAIL_USER = os.getenv('EMAIL_USER')
# EMAIL_PASS = os.getenv('EMAIL_PASS')
# MONGO_URI = os.getenv('MONGO_URI', "")

# # MongoDB Setup
# client = MongoClient(MONGO_URI)
# db = client.infolabz
# internships_collection = db.internship_applications

# # Current date and time
# current_datetime = datetime.now()
# current_date = current_datetime.strftime("%d-%m-%Y")
# current_time = current_datetime.strftime("%I:%M %p")

# SYSTEM_MESSAGE = f"""
# I am Infolabz Assistant, the virtual guide for INFOLABZ I.T. SERVICES PVT. LTD.'s AICTE-approved internship program.

# Key Information:
# - Internship Domains:
#   1. Web Development (React, Django)
#   2. Mobile App Development (Flutter, Android)
#   3. Custom Software Solutions
#   4. IoT Development
#   5. UI/UX Design
#   6. Data Science & Machine Learning

# Application Requirements:
# - Must be enrolled in BCA/MCA/Diploma/Degree program
# - Basic programming knowledge preferred
# - Duration options: 3 or 6 months

# Required Details:
# 1. Full Name
# 2. Contact Information (Phone/Email)
# 3. Educational Institution
# 4. Current Year/Semester
# 5. Preferred Internship Domain
# 6. Technical Skills
# 7. Preferred Start Date

# Process Flow:
# 1. Eligibility verification
# 2. Domain selection guidance
# 3. Application collection
# 4. Screening call scheduling
# 5. Final confirmation

# Current Date: {current_date}
# Current Time: {current_time}

# Behavior Guidelines:
# 1. Always verify educational status first
# 2. Explain AICTE benefits clearly
# 3. Provide real project examples when discussing domains
# 4. Be encouraging but realistic about expectations
# 5. For technical queries, reference our actual tech stack
# 6. Maintain professional yet student-friendly tone
# """
# VOICE = 'alloy'
# LOG_EVENT_TYPES = [
#     'error', 'response.content.done', 'rate_limits.updated',
#     'response.done', 'input_audio_buffer.committed',
#     'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
#     'session.created'
# ]
# SHOW_TIMING_MATH = False

# @app.get("/", response_class=JSONResponse)
# async def index_page():
#     return {"message": "INFOLABZ Internship Assistant is running"}

# @app.api_route("/incoming-call", methods=["GET", "POST"])
# async def handle_incoming_call(request: Request):
#     """Handle incoming internship inquiry calls"""
#     response = VoiceResponse()
#     response.say("Thank you for calling INFOLABZ.", voice=VOICE)
#     response.pause(length=1)
#     response.say("I'm your virtual assistant for our AICTE approved internship program.", voice=VOICE)
#     response.pause(length=1)
#     response.say("Please tell me how I can help you today.", voice=VOICE)
    
#     host = "ai-assistant-vftu.onrender.com"  
#     connect = Connect()
#     connect.stream(url=f'wss://{host}/media-stream')
#     response.append(connect)
#     return HTMLResponse(content=str(response), media_type="application/xml")

# @app.websocket("/media-stream")
# async def handle_media_stream(websocket: WebSocket):
#     """Handle WebSocket connection for internship inquiries"""
#     await websocket.accept()
    
#     async with websockets.connect(
#         'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
#         extra_headers={
#             "Authorization": f"Bearer {OPENAI_API_KEY}",
#             "OpenAI-Beta": "realtime=v1"
#         }
#     ) as openai_ws:
#         await initialize_session(openai_ws)

#         # Connection state
#         stream_sid = None
#         latest_media_timestamp = 0
#         last_assistant_item = None
#         mark_queue = []
#         response_start_timestamp_twilio = None
        
#         async def receive_from_twilio():
#             """Receive audio from Twilio and send to OpenAI"""
#             nonlocal stream_sid, latest_media_timestamp
#             try:
#                 async for message in websocket.iter_text():
#                     data = json.loads(message)
#                     if data['event'] == 'media' and openai_ws.open:
#                         latest_media_timestamp = int(data['media']['timestamp'])
#                         audio_append = {
#                             "type": "input_audio_buffer.append",
#                             "audio": data['media']['payload']
#                         }
#                         await openai_ws.send(json.dumps(audio_append))
#                     elif data['event'] == 'start':
#                         stream_sid = data['start']['streamSid']
#                         print(f"New internship inquiry session started: {stream_sid}")
#                     elif data['event'] == 'mark':
#                         if mark_queue:
#                             mark_queue.pop(0)
#             except WebSocketDisconnect:
#                 print("Client disconnected")
#                 if openai_ws.open:
#                     await openai_ws.close()

#         async def send_to_twilio():
#             """Receive responses from OpenAI and send to Twilio"""
#             nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
#             try:
#                 async for openai_message in openai_ws:
#                     response = json.loads(openai_message)
                    
#                     if response.get('type') == 'response.audio.delta' and 'delta' in response:
#                         audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
#                         audio_delta = {
#                             "event": "media",
#                             "streamSid": stream_sid,
#                             "media": {
#                                 "payload": audio_payload
#                             }
#                         }
#                         await websocket.send_json(audio_delta)

#                         if response_start_timestamp_twilio is None:
#                             response_start_timestamp_twilio = latest_media_timestamp

#                         if response.get('item_id'):
#                             last_assistant_item = response['item_id']

#                         await send_mark(websocket, stream_sid)

#                     # Handle when user starts speaking
#                     if response.get('type') == 'input_audio_buffer.speech_started':
#                         print("User started speaking - handling possible interruption")
#                         if last_assistant_item and response_start_timestamp_twilio is not None:
#                             elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
#                             if SHOW_TIMING_MATH:
#                                 print(f"Truncating response after {elapsed_time}ms")

#                             truncate_event = {
#                                 "type": "conversation.item.truncate",
#                                 "item_id": last_assistant_item,
#                                 "content_index": 0,
#                                 "audio_end_ms": elapsed_time
#                             }
#                             await openai_ws.send(json.dumps(truncate_event))

#                             await websocket.send_json({
#                                 "event": "clear",
#                                 "streamSid": stream_sid
#                             })

#                             mark_queue.clear()
#                             last_assistant_item = None
#                             response_start_timestamp_twilio = None

#                     # Handle application completion
#                     if response.get('type') == 'conversation.item.completed' and 'application_data' in response.get('metadata', {}):
#                         app_data = response['metadata']['application_data']
#                         await process_application(app_data)

#             except Exception as e:
#                 print(f"Error in send_to_twilio: {str(e)}")

#         async def send_mark(connection, stream_sid):
#             """Send mark event to Twilio"""
#             if stream_sid:
#                 mark_event = {
#                     "event": "mark",
#                     "streamSid": stream_sid,
#                     "mark": {"name": "responsePart"}
#                 }
#                 await connection.send_json(mark_event)
#                 mark_queue.append('responsePart')


#         async def process_application(app_data):
#             """Process completed internship application with DB storage and email"""
#             try:
#             # Store in MongoDB
#                 application_id = await store_application(app_data)
                
#                 # Send confirmation SMS
#                 sms_response = await send_internship_confirmation(
#                     phone=app_data['phone'],
#                     domain=app_data['domain']
#                 )
                
#                 # Send confirmation email
#                 email_response = await send_confirmation_email(
#                     email=app_data['email'],
#                     name=app_data['name'],
#                     domain=app_data['domain'],
#                     application_id=str(application_id))
                
#                 print(f"Application processed: {application_id}")
#                 print(f"SMS sent: {sms_response}")
#                 print(f"Email sent: {email_response}")
            
#             except Exception as e:
#                 print(f"Error processing application: {str(e)}")


#         async def store_application(app_data: dict) -> ObjectId:
#             """Store application in MongoDB"""
#             application = {
#                 "name": app_data.get('name'),
#                 "phone": app_data.get('phone'),
#                 "email": app_data.get('email'),
#                 "institution": app_data.get('institution'),
#                 "current_year": app_data.get('current_year'),
#                 "domain": app_data.get('domain'),
#                 "skills": app_data.get('skills', []),
#                 "duration": app_data.get('duration'),
#                 "start_date": app_data.get('start_date'),
#                 "application_date": datetime.now(),
#                 "status": "pending",
#                 "notes": "Awaiting screening call"
#             }
#             result = internships_collection.insert_one(application)
#             return result.inserted_id

#         async def send_confirmation_email(email: str, name: str, domain: str, application_id: str) -> bool:
#             """Send email confirmation to applicant"""
#             try:
#                 message = MIMEMultipart()
#                 message['From'] = EMAIL_USER
#                 message['To'] = email
#                 message['Subject'] = "INFOLABZ Internship Application Confirmation"
                
#                 body = f"""
#                 <html>
#                     <body>
#                         <h2>Dear {name},</h2>
#                         <p>Thank you for applying to the INFOLABZ I.T. SERVICES PVT. LTD. internship program!</p>
                        
#                         <h3>Application Details:</h3>
#                         <ul>
#                             <li><strong>Application ID:</strong> {application_id}</li>
#                             <li><strong>Domain:</strong> {domain}</li>
#                             <li><strong>Status:</strong> Under Review</li>
#                         </ul>
                        
#                         <h3>Next Steps:</h3>
#                         <ol>
#                             <li>Our team will review your application</li>
#                             <li>You'll receive a call for screening within 3 working days</li>
#                             <li>Technical assessment (if required for your domain)</li>
#                             <li>Final confirmation and onboarding</li>
#                         </ol>
                        
#                         <p>For any queries, please contact <a href="mailto:internship@infolabz.com">internship@infolabz.com</a></p>
                        
#                         <p>Best regards,<br>
#                         INFOLABZ Internship Team<br>
#                         <em>AICTE Approved Program</em></p>
#                     </body>
#                 </html>
#                 """
                
#                 message.attach(MIMEText(body, 'html'))
                
#                 with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
#                     server.starttls()
#                     server.login(EMAIL_USER, EMAIL_PASS)
#                     server.send_message(message)
                
#                 return True
#             except Exception as e:
#                 print(f"Error sending email: {str(e)}")
#                 return False
        

#     await asyncio.gather(receive_from_twilio(), send_to_twilio())

# async def initialize_session(openai_ws):
#     """Initialize OpenAI session with internship-specific settings"""
#     session_update = {
#         "type": "session.update",
#         "session": {
#             "turn_detection": {"type": "server_vad"},
#             "input_audio_format": "g711_ulaw",
#             "output_audio_format": "g711_ulaw",
#             "voice": VOICE,
#             "instructions": SYSTEM_MESSAGE,
#             "modalities": ["text", "audio"],
#             "temperature": 0.7,
#             "metadata": {
#                 "company": "INFOLABZ I.T. SERVICES PVT. LTD.",
#                 "program_type": "AICTE Approved Internship"
#             }
#         }
#     }
#     await openai_ws.send(json.dumps(session_update))

# async def send_internship_confirmation(phone: str, domain: str):
#     """Send SMS confirmation for internship application"""
#     msg = f"""INFOLABZ Internship Application Received!
# Domain: {domain}
# Status: Under Review
# Next Steps: Review your application, you'll receive a call within 3 days
# Contact: internship@infolabz.com
# (AICTE Approved Program)"""
    
#     querystring = {
#         "authorization": SMS_KEY,
#         "message": msg,
#         "language": "english",
#         "route": "q",
#         "numbers": phone
#     }
#     headers = {'cache-control': "no-cache"}
#     response = requests.get(SMS_URL, headers=headers, params=querystring)
#     return response.json()

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=PORT)
#     # uvicorn.run(app)









###########  INFOLABZ AI ASSISTANT WORKING CODE [without sms,email,googlesheet,wp]   ###########

import os
import json
import base64
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream, Record
from dotenv import load_dotenv
from datetime import datetime
import threading
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.message import EmailMessage
from pymongo import MongoClient
from datetime import datetime

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PORT = int(os.getenv('PORT', 5050))

# # Current date and time
current_datetime = datetime.now()
current_date = current_datetime.strftime("%d-%m-%Y")
current_time = current_datetime.strftime("%I:%M %p")

SYSTEM_MESSAGE = f"""
I am infolabz Assistant, the virtual guide for INFOLABZ I.T. SERVICES PVT. LTD.'s AICTE-approved internship program.

Key Information:
- Internship Domains:
  1. Web Development (React, Django)
  2. Mobile App Development (Flutter, Android)
  3. Custom Software Solutions
  4. IoT Development
  5. UI/UX Design
  6. Data Science & Machine Learning

Application Requirements:
- Must be enrolled in BCA/MCA/Diploma/Degree program
- Basic programming knowledge preferred
- Duration options: 3 or 6 months

Required Details:
1. Full Name
2. Contact Information (Phone/Email)
3. Educational Institution
4. Current Year/Semester
5. Preferred Internship Domain
6. Technical Skills
7. Preferred Start Date

Process Flow:
1. Eligibility Verification :-
    Check if the user meets the basic eligibility criteria for the internship (e.g., student status, availability, etc.).

2. Domain Selection Guidance :- 
    Help the user choose the most relevant domain based on their interest and skillset (e.g., Web Dev, AI, IoT, etc.).

3. Application Collection :-
    Collect all essential information from the user required details.

4. User Detail Verification
Cross-verify the submitted details for completeness and accuracy (e.g., format checks, required fields, duplicates if needed).

5. Final Confirmation Message
    Once verified, send a confirmation message :
        "You have successfully registered/enquired for the internship at Infolabz with the following details. One of our team members will contact you shortly to guide you through the next steps."

Current Date: {current_date}
Current Time: {current_time}

Behavior Guidelines:
1. Always verify educational status first
2. Explain AICTE benefits clearly
3. Provide real project examples when discussing domains
4. Be encouraging but realistic about expectations
5. For technical queries, reference our actual tech stack
6. Maintain professional yet student-friendly tone
"""

VOICE = 'alloy'
# VOICE = 'Polly.Raveena'
LOG_EVENT_TYPES = [
    'error', 'response.content.done', 'rate_limits.updated',
    'response.done', 'input_audio_buffer.committed',
    'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
    'conversation.item.retrived','conversation.item.input_audio_transcription.completed',
    'session.created'
]
SHOW_TIMING_MATH = False

app = FastAPI()

if not OPENAI_API_KEY:
    raise ValueError('Missing the OpenAI API key. Please set it in the .env file.')

@app.get("/", response_class=JSONResponse)
async def index_page():
    return {"message": "Twilio Media Stream Server is running!"}

@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    # Get caller's number from the request
    caller_number = request
    
    # Log or use this number
    print(f"Incoming call from: {caller_number}")

    """Handle incoming call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()
    # <Say> punctuation to improve text-to-speech flow
    response.say("Please wait while we connect your call to the A. I. voice assistant, powered by infolabz",language='en-IN')
    response.pause(length=1)
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f'wss://{host}/media-stream')
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")

@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""
    print("Client connected")
    await websocket.accept()

    async with websockets.connect(
        # 'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
        'wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17',
        extra_headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
    ) as openai_ws:
        await initialize_session(openai_ws)

        # Connection specific state
        stream_sid = None
        latest_media_timestamp = 0
        last_assistant_item = None
        mark_queue = []
        response_start_timestamp_twilio = None
        conversation_transcript = ""
        
        async def receive_from_twilio():
            """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
            nonlocal stream_sid, latest_media_timestamp
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data['event'] == 'media' and openai_ws.open:
                        latest_media_timestamp = int(data['media']['timestamp'])
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data['media']['payload']
                        }
                        await openai_ws.send(json.dumps(audio_append))
                    elif data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        print(f"Incoming stream has started {stream_sid}")
                        response_start_timestamp_twilio = None
                        latest_media_timestamp = 0
                        last_assistant_item = None
                    elif data['event'] == 'mark':
                        if mark_queue:
                            mark_queue.pop(0)
            except WebSocketDisconnect:
                print("Client disconnected.")
                if openai_ws.open:
                    await openai_ws.close()

        async def send_to_twilio():
            """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
            nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio, conversation_transcript
            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)
                    print("All responses: ",response)
                    if response['type'] in LOG_EVENT_TYPES:
                        print(f"Received event: {response['type']}", response)
                    if response.get('type') == 'conversation.item.input_audio_transcription.completed':
                        print("[USER SAID IN RESPONSE TEXT AFTER COMPLETION OF AUDIO]:", response)
                        user_text = response['transcript']
                        print("[USER SAID]:", user_text)
                        conversation_transcript += f"[USER SAID]: {user_text}\n"
                    # if response.get('type') == 'conversation.item.retrived':
                    #     user_text = response['item']['content'][0]['transcript']
                    #     print("[USER SAID IN RESPONSE]:", response)
                    #     print("[USER SAID]:", user_text)
                    #     conversation_transcript += f"[USER SAID]: {user_text}\n"
                    if response.get('type') == 'response.audio_transcript.delta':
                        bot_text = response['delta']
                        print("[BOT SAID WORD BY WORD]:", bot_text)
                    try:
                        if response.get('type') == 'response.done':
                            print("Conversation finished. Processing user data...")
                            print("Response Done: ",response['response']['output'][0]['content'][0]['transcript'])
                            bot_text2 = response['response']['output'][0]['content'][0]['transcript']
                            print("[BOT SAID]:", bot_text2)
                            process_user_conversation(conversation_transcript)
                    except Exception as e:
                        print("Respons.Done error on line 560:",e)
                    if response.get('type') == 'response.audio.delta' and 'delta' in response:
                        audio_payload = base64.b64encode(base64.b64decode(response['delta'])).decode('utf-8')
                        audio_delta = {
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {
                                "payload": audio_payload
                            }
                        }
                        await websocket.send_json(audio_delta)

                        if response_start_timestamp_twilio is None:
                            response_start_timestamp_twilio = latest_media_timestamp
                            if SHOW_TIMING_MATH:
                                print(f"Setting start timestamp for new response: {response_start_timestamp_twilio}ms")

                        # Update last_assistant_item safely
                        if response.get('item_id'):
                            last_assistant_item = response['item_id']

                        await send_mark(websocket, stream_sid)

                    # Trigger an interruption. Your use case might work better using `input_audio_buffer.speech_stopped`, or combining the two.
                    if response.get('type') == 'input_audio_buffer.speech_started':
                        print("Speech started detected.")
                        if last_assistant_item:
                            print(f"Interrupting response with id: {last_assistant_item}")
                            await handle_speech_started_event()
            except Exception as e:
                print(f"Error in send_to_twilio: {e}")

        async def handle_speech_started_event():
            """Handle interruption when the caller's speech starts."""
            nonlocal response_start_timestamp_twilio, last_assistant_item
            print("Handling speech started event.")
            if mark_queue and response_start_timestamp_twilio is not None:
                elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
                if SHOW_TIMING_MATH:
                    print(f"Calculating elapsed time for truncation: {latest_media_timestamp} - {response_start_timestamp_twilio} = {elapsed_time}ms")

                if last_assistant_item:
                    if SHOW_TIMING_MATH:
                        print(f"Truncating item with ID: {last_assistant_item}, Truncated at: {elapsed_time}ms")

                    truncate_event = {
                        "type": "conversation.item.truncate",
                        "item_id": last_assistant_item,
                        "content_index": 0,
                        "audio_end_ms": elapsed_time
                    }
                    await openai_ws.send(json.dumps(truncate_event))

                await websocket.send_json({
                    "event": "clear",
                    "streamSid": stream_sid
                })

                mark_queue.clear()
                last_assistant_item = None
                response_start_timestamp_twilio = None

        async def send_mark(connection, stream_sid):
            if stream_sid:
                mark_event = {
                    "event": "mark",
                    "streamSid": stream_sid,
                    "mark": {"name": "responsePart"}
                }
                await connection.send_json(mark_event)
                mark_queue.append('responsePart')

        await asyncio.gather(receive_from_twilio(), send_to_twilio())

async def send_initial_conversation_item(openai_ws):
    """Send initial conversation item if AI talks first."""
    initial_conversation_item = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Hi there! 👋 I'm your friendly assistant from INFOLABZ. I can help you explore internship opportunities. Feel free to ask me anything — I'm here to help!"
                }
            ]
        }
    }
    await openai_ws.send(json.dumps(initial_conversation_item))
    await openai_ws.send(json.dumps({"type": "response.create"}))

# def extract_user_info(messages):
#     full_text = " ".join(re.findall(r'\[USER SAID\]: (.+)', messages, re.IGNORECASE))
#     name_match = re.search(r'my name is ([\w\s]+)', full_text, re.IGNORECASE)
#     email_match = re.search(r'[\w\.-]+@[\w\.-]+', full_text)
#     phone_match = re.search(r'(\+?\d[\d\s]{8,}\d)', full_text)

#     name = name_match.group(1).strip().title() if name_match else "Not Provided"
#     email = email_match.group(0) if email_match else "Not Provided"
#     phone = phone_match.group(1).replace(" ", "") if phone_match else "Not Provided"

#     return {
#         "name": name,
#         "email": email,
#         "phone": phone,
#         "message": full_text,
#         "raw_text": messages,
#         "timestamp": datetime.utcnow()
#     }

def spoken_to_email(text):
    text = text.lower()
    text = text.replace(" at the rate ", "@").replace(" dot ", ".").replace(" dash ", "-").replace(" underscore ", "_").replace(" ", "")
    text = re.sub(r'(?<=\w)-(?=\w)', '', text)  # remove unnecessary hyphens between characters
    return re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)

def normalize_phone(text):
    text = text.lower()
    digit_words = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        "plus": "+"
    }

    tokens = text.split()
    digits = []
    for token in tokens:
        if token.isdigit():
            digits.append(token)
        elif token in digit_words:
            digits.append(digit_words[token])
        elif re.match(r'\+?\d+', token):
            digits.append(token)

    phone = ''.join(digits)
    return phone if len(phone) >= 10 else None

def extract_user_info(messages):
    full_text = " ".join(re.findall(r'\[USER SAID\]: (.+)', messages, re.IGNORECASE)).lower()

    # Name
    name_match = re.search(r'my (full )?name is ([a-z\s]+)', full_text)
    name = name_match.group(2).strip().title() if name_match else "Not Provided"

    # Email (spoken-like and normal)
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', full_text)
    if not email_match:
        spoken_email = spoken_to_email(full_text)
        email = spoken_email.group(0) if spoken_email else "Not Provided"
    else:
        email = email_match.group(0)

    # Phone number
    phone_match = re.search(r'(\+?\d[\d\s]{12,}\d)', full_text)
    if phone_match:
        phone = phone_match.group(1).replace(" ", "")
    else:
        phone = normalize_phone(full_text)
        phone = phone if phone else "Not Provided"

    # Institution
    institution_match = re.search(r'(college|university) name is ([a-z\s]+)', full_text)
    institution = institution_match.group(2).strip().title() if institution_match else "Not Provided"

    # Current year / semester
    year_match = re.search(r'(in my|currently in|i am in) (\d+)(st|nd|rd|th)? (year|semester)', full_text)
    current_year = year_match.group(2) + " " + year_match.group(4) if year_match else "Not Provided"

    # Domain
    domain_match = re.search(r'internship.*?(in|for) ([\w\s]+)', full_text)
    domain = domain_match.group(2).strip().title() if domain_match else "Not Provided"

    # Skills
    skills_match = re.search(r'(skills|experience) (of|in|with) ([\w\s,]+)', full_text)
    skills = skills_match.group(3).strip().title() if skills_match else "Not Provided"

    # Duration
    duration_match = re.search(r'(internship|position|training) (duration|for) (\d+ ?(weeks?|months?|days?))', full_text)
    duration = duration_match.group(3).strip() if duration_match else "Not Provided"

    # Start Date
    start_date_match = re.search(r'start (from|on|in)? (next term|[a-zA-Z]+\s?\d{0,4})', full_text)
    start_date = start_date_match.group(2).strip().title() if start_date_match else "Not Provided"

    return {
        "Name": name,
        "Phone": phone,
        "Email": email,
        "Institution": institution,
        "Current_year": current_year,
        "Domain": domain,
        "Skills": skills,
        "Duration": duration,
        "Start_date": start_date,
        "Raw_Message": full_text,
        "Timestamp": datetime.utcnow().isoformat()
    }

# def background_tasks(user_data):
#     try:
#         # Google Sheets
#         scope = [
#             "https://spreadsheets.google.com/feeds",
#             "https://www.googleapis.com/auth/spreadsheets",
#             "https://www.googleapis.com/auth/drive.file",
#             "https://www.googleapis.com/auth/drive"
#         ]

#         credentials_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
#         credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
#         gs_client = gspread.authorize(credentials)
#         sheet = gs_client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
#         worksheet = sheet.worksheet("Test")
#         # creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
#         # sheet_client = gspread.authorize(creds)
#         # sheet = sheet_client.open("Internship Applications").sheet1
#         worksheet.append_row([user_data['name'], user_data['email'], user_data['phone'], user_data['message']])
#         print("[+] Saved to Google Sheets")

#         # Twilio
#         twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
#         twilio_client.messages.create(
#             body=f"Hi {user_data['name']}, we've received your application. Thanks!",
#             from_=os.getenv("TWILIO_PHONE_NUMBER"),
#             to=user_data['phone']
#         )
#         twilio_client.messages.create(
#             body=f"""Hello {user_data['name']},

# # Thank you for applying for the internship at Infolabz!

# # 📞 Phone: {user_data['phone']}
# # 📧 Email: {user_data['email']}
# # 🏫 Institution: {user_data['institution']}
# # 🎯 Domain: {user_data['domain']}
# # ⏳ Duration: {user_data['duration']}
# # 📅 Preferred Start Date: {user_data['start_date']}

# # ✅ We have received your details successfully. Our team will contact you in a few days with the next steps.

# # Best regards,  
# # Infolabz Team""",
#             from_=os.getenv("TWILIO_WHATSAPP_FROM"),
#             to=f"whatsapp:{user_data['phone']}"
#         )
#         print("[+] Twilio messages sent")

#         # Email
#         # msg = MIMEText(f"""Hi {user_data['name']},\n\nThanks for applying. We'll get back to you shortly.\n\nMessage:\n{user_data['message']}""")
#         # msg['Subject'] = "Internship Application Received"
#         # msg['From'] = os.getenv("EMAIL_USER")
#         # msg['To'] = user_data['email']
        
#         message_email = f"""Hello {user_data['name']},

# # Thank you for applying for the internship at Infolabz!

# # 📞 Phone: {user_data['phone']}
# # 📧 Email: {user_data['email']}
# # 🏫 Institution: {user_data['institution']}
# # 🎯 Domain: {user_data['domain']}
# # ⏳ Duration: {user_data['duration']}
# # 📅 Preferred Start Date: {user_data['start_date']}

# # ✅ We have received your details successfully. Our team will contact you in a few days with the next steps.

# # Best regards,  
# # Infolabz Team"""
#         email = EmailMessage()
#         email["From"] = os.getenv("EMAIL_USER")
#         email["To"] = user_data["email"]
#         email["Subject"] = "Internship Application - Infolabz"
#         email.set_content(message_email)
#         with smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT"))) as server:
#             server.starttls()
#             server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
#             server.send_message(email)
#         print("[+] Email sent")

#         # MongoDB
#         mongo_client = MongoClient(os.getenv("MONGO_URI"))
#         db = mongo_client["infolabz"]
#         db["conversations"].insert_one(user_data)
#         print("[+] MongoDB insert done")

#     except Exception as e:
#         print("[-] Error in background task:", str(e))

def background_tasks(user_data):
    try:
        required_fields = ['name', 'email', 'phone', 'institution', 'domain', 'duration', 'start_date']
        for field in required_fields:
            if field not in user_data or not user_data[field] or user_data[field] == "Not Provided":
                raise ValueError(f"Missing required field: {field}")

        # Step 1: Save to Google Sheets
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        gs_client = gspread.authorize(credentials)
        sheet = gs_client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
        worksheet = sheet.worksheet("Test")
        worksheet.append_row([
            user_data['name'],
            user_data['email'],
            user_data['phone'],
            user_data.get('message', ''),
            user_data['institution'],
            user_data['domain'],
            user_data['duration'],
            user_data['start_date']
        ])
        print("[+] Google Sheet updated")

        # Step 2: Send SMS & WhatsApp via Twilio
        twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        phone_number = user_data['phone']

        message_body = f"Hi {user_data['name']}, we have received your internship application at Infolabz. Our team will contact you shortly."

        twilio_client.messages.create(
            body=message_body,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=phone_number
        )

        whatsapp_body = f"""Hello {user_data['name']},

                                        ✅ You have successfully registered/enquired for the internship at Infolabz with the following details:

                                        📞 Phone: {user_data['phone']}
                                        📧 Email: {user_data['email']}
                                        🏫 Institution: {user_data['institution']}
                                        🎯 Domain: {user_data['domain']}
                                        ⏳ Duration: {user_data['duration']}
                                        📅 Preferred Start Date: {user_data['start_date']}

                                        One of our team members will contact you shortly regarding the next steps.

                                        Regards,  
                                        Infolabz Team"""

        twilio_client.messages.create(
            body=whatsapp_body,
            from_=os.getenv("TWILIO_WHATSAPP_FROM"),
            to=f"whatsapp:{phone_number}"
        )
        print("[+] Twilio messages sent")

        # Step 3: Send Email
        email = EmailMessage()
        email["From"] = os.getenv("EMAIL_USER")
        email["To"] = user_data["email"]
        email["Subject"] = "Internship Application Received - Infolabz"
        email.set_content(whatsapp_body)

        with smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
            server.send_message(email)
        print("[+] Email sent")

        # Step 4: Store in MongoDB
        mongo_client = MongoClient(os.getenv("MONGO_URI"))
        db = mongo_client["infolabz"]
        db["conversations"].insert_one(user_data)
        print("[+] MongoDB insert complete")

    except Exception as e:
        print("[-] Background task error:", str(e))

def process_user_conversation(convo_text):
    user_data = extract_user_info(convo_text)
    threading.Thread(target=background_tasks, args=(user_data,)).start()
    return f"Thanks {user_data['name']}! Your application is being processed."

async def initialize_session(openai_ws):
    """Control initial session with OpenAI."""
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "input_audio_transcription": {"model": "whisper-1"},
            "voice": VOICE,
            "instructions": SYSTEM_MESSAGE +  "\nYou must detect and respond in the language the user speaks. Supported: English, Hindi, Gujarati, Tamil, Telugu, Marathi, Bengali.",
            "modalities": ["text", "audio"],
            "temperature": 0.9,
        }
    }
    print('Sending session update:', json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))

    # Uncomment the next line to have the AI speak first
    # await send_initial_conversation_item(openai_ws)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)



####### Working Code Ends #######













# import os
# import json
# import base64
# import asyncio
# import websockets
# from fastapi import FastAPI, WebSocket, Request
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.websockets import WebSocketDisconnect
# from twilio.twiml.voice_response import VoiceResponse, Connect
# from dotenv import load_dotenv
# from datetime import datetime
# from pymongo import MongoClient
# from oauth2client.service_account import ServiceAccountCredentials
# import gspread
# from twilio.rest import Client as TwilioClient
# import smtplib
# from email.message import EmailMessage
# import re

# load_dotenv()

# # Configuration
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# PORT = int(os.getenv('PORT', 5050))

# # MongoDB
# mongo_client = MongoClient(os.getenv("MONGO_URI"))
# db = mongo_client["infolabz"]
# conversation_collection = db["conversations"]
# user_collection = db["user_details"]

# # Google Sheets
# scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# credentials_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
# credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
# gs_client = gspread.authorize(credentials)
# sheet = gs_client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
# worksheet = sheet.worksheet("Test")

# # Twilio
# twilio_client = TwilioClient(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

# # Email
# EMAIL_USER = os.getenv("EMAIL_USER")
# EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

# # Timestamps
# current_datetime = datetime.now()
# current_date = current_datetime.strftime("%d-%m-%Y")
# current_time = current_datetime.strftime("%I:%M %p")

# SYSTEM_MESSAGE = f"""
# I am infolabz Assistant, the virtual guide for INFOLABZ I.T. SERVICES PVT. LTD.'s AICTE-approved internship program.

# Key Information:
# - Internship Domains:
#   1. Web Development (React, Django)
#   2. Mobile App Development (Flutter, Android)
#   3. Custom Software Solutions
#   4. IoT Development
#   5. UI/UX Design
#   6. Data Science & Machine Learning

# Application Requirements:
# - Must be enrolled in BCA/MCA/Diploma/Degree program
# - Basic programming knowledge preferred
# - Duration options: 3 or 6 months

# Required Details:
# 1. Full Name
# 2. Contact Information (Phone/Email)
# 3. Educational Institution
# 4. Current Year/Semester
# 5. Preferred Internship Domain
# 6. Technical Skills
# 7. Preferred Start Date

# Process Flow:
# 1. Eligibility verification
# 2. Domain selection guidance
# 3. Application collection
# 4. Verify the users details 
# 5. Final confirmation

# Current Date: {current_date}
# Current Time: {current_time}
# """


# # SYSTEM_MESSAGE = f"""
# # I am infolabz Assistant, the virtual guide for INFOLABZ I.T. SERVICES PVT. LTD.'s AICTE-approved internship program.

# # Key Information:
# # - Internship Domains:
# #   1. Web Development (React, Django)
# #   2. Mobile App Development (Flutter, Android)
# #   3. Custom Software Solutions
# #   4. IoT Development
# #   5. UI/UX Design
# #   6. Data Science & Machine Learning

# # Application Requirements:
# # - Must be enrolled in BCA/MCA/Diploma/Degree program
# # - Basic programming knowledge preferred
# # - Duration options: 3 or 6 months

# # Required Details (to be collected upon eligibility confirmation):
# # 1. Full Name
# # 2. Contact Information (Phone/Email)
# # 3. Educational Institution
# # 4. Current Year/Semester
# # 5. Preferred Internship Domain
# # 6. Technical Skills
# # 7. Preferred Start Date

# # Process Flow:
# # 1. Eligibility verification
# # 2. Domain selection guidance
# # 3. If eligible and interested, collect required details
# # 4. Show collected details back to the user for confirmation:
# # 5. Final confirmation of the details and Team will contact you soon regarding the next steps.

# # Current Date: {current_date}
# # Current Time: {current_time}
# # """

# VOICE = 'alloy'
# LOG_EVENT_TYPES = [
#     'error', 'response.content.done', 'rate_limits.updated',
#     'response.done', 'input_audio_buffer.committed', 'conversation.item.retrived','conversation.item.input_audio_transcription.completed',
#     'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
#     'session.created'
# ]
# SHOW_TIMING_MATH = False

# app = FastAPI()

# @app.get("/", response_class=JSONResponse)
# async def index_page():
#     return {"message": "INFOLABZ Twilio AI Assistant is running."}

# @app.api_route("/incoming-call", methods=["GET", "POST"])
# async def handle_incoming_call(request: Request):
#     response = VoiceResponse()
#     response.say("Please wait while we connect your call to the AI voice assistant.", language='en-IN')
#     host = request.url.hostname
#     connect = Connect()
#     connect.stream(url=f'wss://{host}/media-stream')
#     response.append(connect)
#     return HTMLResponse(content=str(response), media_type="application/xml")

# @app.websocket("/media-stream")
# async def handle_media_stream(websocket: WebSocket):
#     await websocket.accept()
#     print("Client connected.")

#     async with websockets.connect(
#         'wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17',
#         extra_headers={
#             "Authorization": f"Bearer {OPENAI_API_KEY}",
#             "OpenAI-Beta": "realtime=v1"
#         }
#     ) as openai_ws:
#         await initialize_session(openai_ws)

#         stream_sid = None
#         latest_media_timestamp = 0
#         last_assistant_item = None
#         mark_queue = []
#         response_start_timestamp_twilio = None

#         collected_data = {
#             "name": None, "phone": None, "email": None,
#             "institution": None, "semester": None,
#             "domain": None, "skills": None,
#             "start_date": None, "duration": None
#         }
#         submitted = False

#         def all_fields_filled(data):
#             return all(data.values())

#         async def process_user_message(text):
#             print("Inside the process user message function")
#             nonlocal submitted
#             text_lower = text.lower()
#             print("The data received from the bot: ",text_lower)
#             # if "name is" in text_lower:
#             #     collected_data["name"] = text.split("is")[-1].strip()
#             # elif "email" in text_lower:
#             #     collected_data["email"] = text.split()[-1].strip()
#             # elif "phone" in text_lower or "contact" in text_lower:
#             #     collected_data["phone"] = ''.join(filter(str.isdigit, text))
#             # elif "institution" in text_lower or "college" in text_lower:
#             #     collected_data["institution"] = text.split()[-1].strip()
#             # elif "semester" in text_lower or "year" in text_lower:
#             #     collected_data["semester"] = text.split()[-1].strip()
#             # elif "domain" in text_lower:
#             #     collected_data["domain"] = text.split("domain")[-1].strip()
#             # elif "skill" in text_lower:
#             #     collected_data["skills"] = text.split("skill")[-1].strip()
#             # elif "start date" in text_lower or "from" in text_lower:
#             #     collected_data["start_date"] = text.split()[-1].strip()
#             # elif "month" in text_lower or "duration" in text_lower:
#             #     collected_data["duration"] = text.split()[0].strip()
#             # Name
#             match = re.search(r"(my name is|i am)\s+([a-zA-Z ]+)", text_lower)
#             if match:
#                 collected_data["name"] = match.group(2).strip()

#             # Email
#             match = re.search(r"[\w\.-]+@[\w\.-]+", text)
#             if match:
#                 collected_data["email"] = match.group(0).strip()

#             # Phone
#             match = re.search(r"\b\d{10}\b", text)
#             if match:
#                 collected_data["phone"] = match.group(0).strip()

#             # Institution
#             if "institution" in text_lower or "college" in text_lower:
#                 collected_data["institution"] = text.split()[-1].strip()

#             # Semester
#             match = re.search(r"(semester|year)\s+(\w+)", text_lower)
#             if match:
#                 collected_data["semester"] = match.group(2).strip()

#             # Domain
#             if "domain" in text_lower:
#                 collected_data["domain"] = text.split("domain")[-1].strip()

#             # Skills
#             if "skill" in text_lower:
#                 collected_data["skills"] = text.split("skill")[-1].strip()

#             # Start Date
#             match = re.search(r"(start date|from)\s+(\w+)", text_lower)
#             if match:
#                 collected_data["start_date"] = match.group(2).strip()

#             # Duration
#             match = re.search(r"(duration|month)\s+(\w+)", text_lower)
#             if match:
#                 collected_data["duration"] = match.group(2).strip()

#             if all_fields_filled(collected_data) and not submitted:
#                 print("🔥 Final Data to Submit:", collected_data)
#                 await handle_user_submission(collected_data)
#                 submitted = True

#         async def receive_from_twilio():
#             nonlocal stream_sid, latest_media_timestamp
#             try:
#                 async for message in websocket.iter_text():
#                     data = json.loads(message)
#                     if data['event'] == 'media' and openai_ws.open:
#                         latest_media_timestamp = int(data['media']['timestamp'])
#                         await openai_ws.send(json.dumps({
#                             "type": "input_audio_buffer.append",
#                             "audio": data['media']['payload']
#                         }))
#                     elif data['event'] == 'start':
#                         stream_sid = data['start']['streamSid']
#                     elif data['event'] == 'mark':
#                         if mark_queue: mark_queue.pop(0)
#             except WebSocketDisconnect:
#                 print("Client disconnected.")
#                 if openai_ws.open:
#                     await openai_ws.close()

#         async def send_to_twilio():
#             nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
#             try:
#                 async for openai_message in openai_ws:
#                     response = json.loads(openai_message)
#                     print("Bot Response: ", response)
#                     if response['type'] in LOG_EVENT_TYPES:
#                         print(f"Received event: {response['type']}", response)
#                     if response.get('type') == 'response.audio.delta' and 'delta' in response:
#                         await websocket.send_json({
#                             "event": "media",
#                             "streamSid": stream_sid,
#                             "media": {"payload": base64.b64encode(base64.b64decode(response['delta'])).decode()}
#                         })
#                         if response.get("item_id"): last_assistant_item = response["item_id"]
#                         if response_start_timestamp_twilio is None:
#                             response_start_timestamp_twilio = latest_media_timestamp
#                         await send_mark(websocket, stream_sid)
#                     if response.get('type') == 'conversation.item.input_audio_transcription.completed':
#                                 print("[USER SAID IN RESPONSE TEXT AFTER COMPLETION OF AUDIO]:", response)
#                                 user_text = response['transcript']
#                                 print("[USER SAID]:", user_text)
#                                 try:
#                                     asyncio.create_task(save_conversation_to_db(stream_sid, f"[USER SAID]: {user_text}"))
#                                 except Exception as e:
#                                     print("Save Conversation Error: ",e)
#                                 try:
#                                     asyncio.create_task(process_user_message(user_text))
#                                 except Exception as e:
#                                     print("Process User Message Error: ",e)
#                     if response.get('type') == 'conversation.item.retrived':
#                                 user_text = response['item']['content'][0]['transcript']
#                                 print("[USER SAID IN RESPONSE]:", response)
#                                 print("[USER SAID]:", user_text)
#                                 try:    
#                                     asyncio.create_task(save_conversation_to_db(stream_sid, f"[USER SAID]: {user_text}"))
#                                 except Exception as e:
#                                     print("User Response Error on line 990: ",e)
#                                 try:
#                                     asyncio.create_task(process_user_message(user_text))
#                                 except Exception as e:
#                                     print("User Response Error on line 994: ",e)
#                     if response.get('type') == 'response.audio_transcript.delta':
#                                 bot_text = response['delta']
#                                 print("[BOT SAID WORD BY WORD]:", bot_text)
#                     if response.get('type') == 'response.done':
#                                 print("Response Done: ",response)
#                                 bot_text1 = response['output'][0]['content'][0]['transcript']
#                                 bot_text2 = response['response']['output'][0]['content'][0]['transcript']
#                                 print("[BOT SAID WHOLE TEXT 1]:", bot_text1)
#                                 print("[BOT SAID WHOLE TEXT 2]:", bot_text2)
#                                 try:
#                                     asyncio.create_task(save_conversation_to_db(stream_sid, f"[BOT SAID]: {bot_text2}"))
#                                 except Exception as e:
#                                     print("Bot resposne  Error on line 1008: ",e)
#                     if response.get("type") == "input_audio_buffer.speech_started":
#                         await handle_speech_started_event()
#             except Exception as e:
#                 print("Error:", e)

#         async def handle_speech_started_event():
#             nonlocal response_start_timestamp_twilio, last_assistant_item
#             if last_assistant_item and response_start_timestamp_twilio:
#                 await openai_ws.send(json.dumps({
#                     "type": "conversation.item.truncate",
#                     "item_id": last_assistant_item,
#                     "content_index": 0,
#                     "audio_end_ms": latest_media_timestamp - response_start_timestamp_twilio
#                 }))
#                 await websocket.send_json({"event": "clear", "streamSid": stream_sid})
#                 mark_queue.clear()
#                 last_assistant_item = None
#                 response_start_timestamp_twilio = None

#         async def send_mark(connection, stream_sid):
#             await connection.send_json({
#                 "event": "mark",
#                 "streamSid": stream_sid,
#                 "mark": {"name": "responsePart"}
#             })
#             mark_queue.append("responsePart")

#         await asyncio.gather(receive_from_twilio(), send_to_twilio())

# # Helper Functions
# async def save_conversation_to_db(user_id, message):
#     conversation_collection.insert_one({
#         "user_id": user_id,
#         "message": message,
#         "timestamp": datetime.now()
#     })

# async def save_user_to_google_sheet(data):
#     worksheet.append_row([
#         data["name"],
#         data["phone"],
#         data["email"],
#         data["institution"],
#         data["semester"],
#         data["domain"],
#         data["skills"],
#         data["start_date"]
#     ])

# async def notify_user(data):
#     message = f"""Hello {data['name']},

# Thank you for applying for the internship at Infolabz!

# 📞 Phone: {data['phone']}
# 📧 Email: {data['email']}
# 🏫 Institution: {data['institution']}
# 🎯 Domain: {data['domain']}
# ⏳ Duration: {data['duration']}
# 📅 Preferred Start Date: {data['start_date']}

# ✅ We have received your details successfully. Our team will contact you in a few days with the next steps.

# Best regards,  
# Infolabz Team"""

#     twilio_client.messages.create(
#         from_=os.getenv("TWILIO_WHATSAPP_FROM"),
#         to=f'whatsapp:{data["phone"]}',
#         body=message
#     )

#     twilio_client.messages.create(
#         from_=os.getenv("TWILIO_PHONE_NUMBER"),
#         to=data["phone"],
#         body="Thanks for applying for the internship at Infolabz! We have received your details successfully."
#     )

#     email = EmailMessage()
#     email["From"] = EMAIL_USER
#     email["To"] = data["email"]
#     email["Subject"] = "Internship Application - Infolabz"
#     email.set_content(message)

#     with smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT"))) as server:
#         server.starttls()
#         server.login(EMAIL_USER, EMAIL_PASSWORD)
#         server.send_message(email)

# async def handle_user_submission(user_data):
#     user_collection.insert_one(user_data)
#     await save_user_to_google_sheet(user_data)
#     await notify_user(user_data)

# async def initialize_session(openai_ws):
#     await openai_ws.send(json.dumps({
#         "type": "session.update",
#         "session": {
#             "turn_detection": {"type": "server_vad"},
#             "input_audio_format": "g711_ulaw",
#             "output_audio_format": "g711_ulaw",
#             "input_audio_transcription": {"model": "whisper-1"},
#             "voice": VOICE,
#             "instructions": SYSTEM_MESSAGE + "\nYou must detect and respond in the language the user speaks. Supported: English, Hindi, Gujarati, Tamil, Telugu, Marathi, Bengali.",
#             "modalities": ["text", "audio"],
#             "temperature": 0.8,
#         }
#     }))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=PORT)

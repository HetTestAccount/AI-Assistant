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

# import os
# import json
# import base64
# import asyncio
# import websockets
# from fastapi import FastAPI, WebSocket, Request
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.websockets import WebSocketDisconnect
# from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
# from dotenv import load_dotenv
# from datetime import datetime

# load_dotenv()

# # Configuration
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# PORT = int(os.getenv('PORT', 5050))

# # # Current date and time
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
# # VOICE = 'Polly.Raveena'
# LOG_EVENT_TYPES = [
#     'error', 'response.content.done', 'rate_limits.updated',
#     'response.done', 'input_audio_buffer.committed',
#     'input_audio_buffer.speech_stopped', 'input_audio_buffer.speech_started',
#     'session.created'
# ]
# SHOW_TIMING_MATH = False

# app = FastAPI()

# if not OPENAI_API_KEY:
#     raise ValueError('Missing the OpenAI API key. Please set it in the .env file.')

# @app.get("/", response_class=JSONResponse)
# async def index_page():
#     return {"message": "Twilio Media Stream Server is running!"}

# @app.api_route("/incoming-call", methods=["GET", "POST"])
# async def handle_incoming_call(request: Request):
#     """Handle incoming call and return TwiML response to connect to Media Stream."""
#     response = VoiceResponse()
#     # <Say> punctuation to improve text-to-speech flow
#     response.say("Please wait while we connect your call to the A. I. voice assistant, powered by infolabz",language='en-IN')
#     response.pause(length=1)
#     host = request.url.hostname
#     connect = Connect()
#     connect.stream(url=f'wss://{host}/media-stream')
#     response.append(connect)
#     return HTMLResponse(content=str(response), media_type="application/xml")

# @app.websocket("/media-stream")
# async def handle_media_stream(websocket: WebSocket):
#     """Handle WebSocket connections between Twilio and OpenAI."""
#     print("Client connected")
#     await websocket.accept()

#     async with websockets.connect(
#         'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
#         extra_headers={
#             "Authorization": f"Bearer {OPENAI_API_KEY}",
#             "OpenAI-Beta": "realtime=v1"
#         }
#     ) as openai_ws:
#         await initialize_session(openai_ws)

#         # Connection specific state
#         stream_sid = None
#         latest_media_timestamp = 0
#         last_assistant_item = None
#         mark_queue = []
#         response_start_timestamp_twilio = None
        
#         async def receive_from_twilio():
#             """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
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
#                         print(f"Incoming stream has started {stream_sid}")
#                         response_start_timestamp_twilio = None
#                         latest_media_timestamp = 0
#                         last_assistant_item = None
#                     elif data['event'] == 'mark':
#                         if mark_queue:
#                             mark_queue.pop(0)
#             except WebSocketDisconnect:
#                 print("Client disconnected.")
#                 if openai_ws.open:
#                     await openai_ws.close()

#         async def send_to_twilio():
#             """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
#             nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
#             try:
#                 async for openai_message in openai_ws:
#                     response = json.loads(openai_message)
#                     if response['type'] in LOG_EVENT_TYPES:
#                         print(f"Received event: {response['type']}", response)

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
#                             if SHOW_TIMING_MATH:
#                                 print(f"Setting start timestamp for new response: {response_start_timestamp_twilio}ms")

#                         # Update last_assistant_item safely
#                         if response.get('item_id'):
#                             last_assistant_item = response['item_id']

#                         await send_mark(websocket, stream_sid)

#                     # Trigger an interruption. Your use case might work better using `input_audio_buffer.speech_stopped`, or combining the two.
#                     if response.get('type') == 'input_audio_buffer.speech_started':
#                         print("Speech started detected.")
#                         if last_assistant_item:
#                             print(f"Interrupting response with id: {last_assistant_item}")
#                             await handle_speech_started_event()
#             except Exception as e:
#                 print(f"Error in send_to_twilio: {e}")

#         async def handle_speech_started_event():
#             """Handle interruption when the caller's speech starts."""
#             nonlocal response_start_timestamp_twilio, last_assistant_item
#             print("Handling speech started event.")
#             if mark_queue and response_start_timestamp_twilio is not None:
#                 elapsed_time = latest_media_timestamp - response_start_timestamp_twilio
#                 if SHOW_TIMING_MATH:
#                     print(f"Calculating elapsed time for truncation: {latest_media_timestamp} - {response_start_timestamp_twilio} = {elapsed_time}ms")

#                 if last_assistant_item:
#                     if SHOW_TIMING_MATH:
#                         print(f"Truncating item with ID: {last_assistant_item}, Truncated at: {elapsed_time}ms")

#                     truncate_event = {
#                         "type": "conversation.item.truncate",
#                         "item_id": last_assistant_item,
#                         "content_index": 0,
#                         "audio_end_ms": elapsed_time
#                     }
#                     await openai_ws.send(json.dumps(truncate_event))

#                 await websocket.send_json({
#                     "event": "clear",
#                     "streamSid": stream_sid
#                 })

#                 mark_queue.clear()
#                 last_assistant_item = None
#                 response_start_timestamp_twilio = None

#         async def send_mark(connection, stream_sid):
#             if stream_sid:
#                 mark_event = {
#                     "event": "mark",
#                     "streamSid": stream_sid,
#                     "mark": {"name": "responsePart"}
#                 }
#                 await connection.send_json(mark_event)
#                 mark_queue.append('responsePart')

#         await asyncio.gather(receive_from_twilio(), send_to_twilio())

# async def send_initial_conversation_item(openai_ws):
#     """Send initial conversation item if AI talks first."""
#     initial_conversation_item = {
#         "type": "conversation.item.create",
#         "item": {
#             "type": "message",
#             "role": "user",
#             "content": [
#                 {
#                     "type": "input_text",
#                     "text": "Hi there! 👋 I'm your friendly assistant from INFOLABZ. I can help you explore internship opportunities. Feel free to ask me anything — I'm here to help!"
#                 }
#             ]
#         }
#     }
#     await openai_ws.send(json.dumps(initial_conversation_item))
#     await openai_ws.send(json.dumps({"type": "response.create"}))


# async def initialize_session(openai_ws):
#     """Control initial session with OpenAI."""
#     session_update = {
#         "type": "session.update",
#         "session": {
#             "turn_detection": {"type": "server_vad"},
#             "input_audio_format": "g711_ulaw",
#             "output_audio_format": "g711_ulaw",
#             "voice": VOICE,
#             "instructions": SYSTEM_MESSAGE +  "\nYou must detect and respond in the language the user speaks. Supported: English, Hindi, Gujarati, Tamil, Telugu, Marathi, Bengali.",
#             "modalities": ["text", "audio"],
#             "temperature": 0.9,
#         }
#     }
#     print('Sending session update:', json.dumps(session_update))
#     await openai_ws.send(json.dumps(session_update))

#     # Uncomment the next line to have the AI speak first
#     # await send_initial_conversation_item(openai_ws)

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=PORT)





####### Working Code Ends #######














import os
import json
import base64
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import VoiceResponse, Connect, Say, Stream
from dotenv import load_dotenv
from datetime import datetime
# ====== ADDITIONAL IMPORTS AND SETUP ======
from pymongo import MongoClient
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from twilio.rest import Client as TwilioClient
import smtplib
from email.message import EmailMessage

load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PORT = int(os.getenv('PORT', 5050))


# ADDITIONAL CONFIGURATION
# MongoDB Setup
mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client["infolabz"]
conversation_collection = db["conversations"]
user_collection = db["user_details"]

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
# credentials = ServiceAccountCredentials.from_json_keyfile_name("extreme-lattice-459811-a1-031fbed6004a.json", scope)
credentials_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
gs_client = gspread.authorize(credentials)
sheet = gs_client.open_by_key(os.getenv("GOOGLE_SHEET_ID"))
worksheet = sheet.worksheet("Test") 

# Twilio Setup
twilio_client = TwilioClient(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

# Email Setup
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

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
1. Eligibility verification
2. Domain selection guidance
3. Application collection
4. Screening call scheduling
5. Final confirmation

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
        'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01',
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
        
        collected_data = {
            "name": None,
            "phone": None,
            "email": None,
            "institution": None,
            "semester": None,
            "domain": None,
            "skills": None,
            "start_date": None,
            "duration": None
        }
        submitted = False

        def all_fields_filled(data_dict):
            return all(data_dict.values())

        async def process_user_message(text):
            nonlocal submitted
            # Naive field extraction logic (replace with regex or NLP for accuracy)
            text_lower = text.lower()
            if "name is" in text_lower:
                collected_data["name"] = text.split("is")[-1].strip()
            elif "email" in text_lower:
                collected_data["email"] = text.split()[-1].strip()
            elif "phone" in text_lower or "contact" in text_lower:
                collected_data["phone"] = ''.join(filter(str.isdigit, text))
            elif "institution" in text_lower or "college" in text_lower:
                collected_data["institution"] = text.split()[-1].strip()
            elif "semester" in text_lower or "year" in text_lower:
                collected_data["semester"] = text.split()[-1].strip()
            elif "domain" in text_lower:
                collected_data["domain"] = text.split("domain")[-1].strip()
            elif "skill" in text_lower:
                collected_data["skills"] = text.split("skill")[-1].strip()
            elif "start date" in text_lower or "from" in text_lower:
                collected_data["start_date"] = text.split()[-1].strip()
            elif "month" in text_lower or "duration" in text_lower:
                collected_data["duration"] = text.split()[0].strip()

            if all_fields_filled(collected_data) and not submitted:
                handle_user_submission(collected_data)
                submitted = True

        async def receive_from_twilio():
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
                    elif data['event'] == 'user-message':
                        user_text = data['user-message']['text']
                        await process_user_message(user_text)
                        await save_conversation_to_db(stream_sid, user_text)
            except WebSocketDisconnect:
                print("Client disconnected.")
                if openai_ws.open:
                    await openai_ws.close()


        async def send_to_twilio():
                    """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
                    nonlocal stream_sid, last_assistant_item, response_start_timestamp_twilio
                    try:
                        async for openai_message in openai_ws:
                            response = json.loads(openai_message)
                            if response['type'] in LOG_EVENT_TYPES:
                                print(f"Received event: {response['type']}", response)

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


async def initialize_session(openai_ws):
    """Control initial session with OpenAI."""
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
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

# ====== FUNCTIONALITY ======

async def save_conversation_to_db(user_id, message):
    conversation_collection.insert_one({
        "user_id": user_id,
        "message": message,
        "timestamp": datetime.now()
    })

def save_user_to_google_sheet(data):
    worksheet.append_row([
        data["name"],
        f'{data["phone"]} / {data["email"]}',
        data["institution"],
        data["semester"],
        data["domain"],
        data["skills"],
        data["start_date"]
    ])

def notify_user(data):
    message = f"""Hello {data['name']},

Thank you for applying for the internship at Infolabz!

📞 Phone: {data['phone']}
📧 Email: {data['email']}
🏫 Institution: {data['institution']}
🎯 Domain: {data['domain']}
⏳ Duration: {data['duration']}
📅 Preferred Start Date: {data['start_date']}

✅ We have received your details successfully. Our team will contact you in a few days with the next steps.

Best regards,  
Infolabz Team"""

    # WhatsApp via Twilio
    twilio_client.messages.create(
        from_=os.getenv("TWILIO_WHATSAPP_FROM"),
        to=f'whatsapp:{data["phone"]}',
        body=message
    )

    #SMS
    twilio_client.messages.create(
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        to=data["phone"],
        body="Thanks for applying for the internship at Infolabz! We have received your details successfully. Our team will contact you in a few days with the next steps. Best regards, Infolabz Team"
    )

    # Email
    email = EmailMessage()
    email["From"] = EMAIL_USER
    email["To"] = data["email"]
    email["Subject"] = "Internship Application - Infolabz"
    email.set_content(message)

    with smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT"))) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(email)

def handle_user_submission(user_data):
    user_collection.insert_one(user_data)
    save_user_to_google_sheet(user_data)
    notify_user(user_data)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
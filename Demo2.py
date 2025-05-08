from twilio.rest import Client

client = Client("")

call = client.calls.create(
    from_="+19786345597",
    to="+16309233541",
    url="http://demo.twilio.com/docs/voice.xml",
)

print(call.sid)
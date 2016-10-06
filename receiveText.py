from flask import Flask, request, redirect
import twilio.twiml
import random

app = Flask(__name__)
possible_response = ["What did you say to me little bitch?", "Get Out", "You're dead to me", "Bye Felicia", "Just fuck me up fam"]

@app.route("/", methods=['GET', 'POST'])
def respond_to_call():
	resp = twilio.twiml.Response()
	randomNum = random.random()
	index = int(randomNum*5)

	resp.message(possible_response[index])
	return str(resp)

if __name__ == "__main__":
	app.run(debug=True)
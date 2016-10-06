from flask import Flask, request, redirect
import twilio.twiml

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def respond_to_call():
	print("got something")
	resp = twilio.twiml.Response()
	resp.message("Hi Matt")
	return str(resp)

if __name__ == "__main__":
	app.run(debug=True)
from flask import Flask, request, redirect
import twilio.twiml
import random
import requests
import re
from firebase import firebase

app = Flask(__name__)
LOCATION_URL = "https://webservices.telus.com/TerminalLocationService/services/TerminalLocation"
SMS_URL= "https://webservices.telus.com/SendSmsService/services/SendSms"
HEADER_TYPE = {'content-type': 'text/xml'}
VERIFY_PATH = "certificates/telus-eng.crt"
CERT_PATH = "certificates/TELUS-TELUS_UofT_01.crt"
KEY_PATH = "certificates/TELUS-TELUS_UofT_01.key"
NUMBER = "16042199584"
CITY_TO_CONTACT = {}
DSN = 'https://telushackathon1.firebaseio.com/'
database = firebase.FirebaseApplication(DSN)

@app.route("/", methods=['GET', 'POST'])

def respond_to_call():
	resp = twilio.twiml.Response()

	resp_list = resp.split('@' ,1)
	issue = resp_list[0]
	location = resp_list[1]

	city = get_location_telus(NUMBER)
	send_to_db(city, issue, location)

	reply = "Thank you for using CityInformer! Your message will be passed along to the city of " + city + . Please don't forget to send a description of your issue followed by an @ sign, then the relevant address Ex: \'excessive litter @College and Spadina\'"

	#send_message_telus(NUMBER, reply)

	resp.message(reply)
	return str(resp)

def get_location_telus(number):

	body = """ <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
								 xmlns:loc="http://www.csapi.org/schema/parlayx/terminal_location/v2_3 /local">
			        <soapenv:Header/>
			        <soapenv:Body>
			            <loc:getLocation>
			                <loc:address>tel:""" + number + """</loc:address>
			                <loc:requestedAccuracy>5000</loc:requestedAccuracy>
			                <loc:acceptableAccuracy>5000</loc:acceptableAccuracy>
			            </loc:getLocation>
			        </soapenv:Body>
		    	</soapenv:Envelope>"""

	response = requests.post(
				LOCATION_URL,
				data = body,
				headers = HEADER_TYPE,
	            verify = VERIFY_PATH,
	            cert = ( CERT_PATH, KEY_PATH )
			)

	latitude = -1
	longitude = -1
	latRex = re.compile(r'<latitude>(.*?)</latitude>',re.S|re.M)
	match = latRex.match(str(response))
	if match:
		latitude = match.groups()[0].strip()
	longRex = re.compile(r'<longitude>(.*?)</longitude>',re.S|re.M)
	match = longRex.match(str(response))
	if match:
		longitude = match.groups()[0].strip()

	if longitude != -1 and latitude != -1:
		return get_city(longitude, latitude)
	else:
		return get_city(longitude, latitude)

	return "toronto"

def send_message_telus(number, message):

	body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
	 		   					xmlns:loc="http://www.csapi.org/schema/parlayx/sms/send/v2_3/local">
		        <soapenv:Header/>
		        <soapenv:Body>
		            <loc:sendSms>
		                <!--1 or more repetitions:-->
		                <loc:addresses>tel:""" + number + """</loc:addresses>
		                <loc:senderName></loc:senderName>
		                <loc:message>+""" + message + """+</loc:message>
		                <!-- Optional -->
		                <loc:receiptRequest>
		                    <endpoint>https://webservices.telus.com/SendSmsService/services/SendSms</endpoint>
		                    <interfaceName>SmsNotification</interfaceName>
		                    <correlator>1010</correlator>
		                </loc:receiptRequest>
		            </loc:sendSms>
		        </soapenv:Body>
		    </soapenv:Envelope>"""

	response = requests.post(
				SMS_URL,
				data = body,
				headers = HEADER_TYPE,
	            verify = VERIFY_PATH,
	            cert = ( CERT_PATH, KEY_PATH )
			)

def get_city(lat, long):
	# initial url with API key replaced:
    	# https://maps.googleapis.com/maps/api/geocode/json?latlng=40.714224,-73.961452&key=AIzaSyBAVg_8QI088vxNgXNwO7hAdpu2zVxF6lM
    
	city_url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(lat) + ',' + str(long) + '&result_type=locality&key=AIzaSyBAVg_8QI088vxNgXNwO7hAdpu2zVxF6lM'
	resp = requests.get(city_url)
	resp = resp.json()
    	if resp.status == "OK":
    		return resp.results[0].address_components[0].long_name
	else:
		return 'error'

def send_to_db(city, issue, location):
	cityURL = '/cities/%s' %city
	result = database.post(cityURL, {"issue": issue, "location": location})
	print result

if __name__ == "__main__":
	#send_to_db("toronto","garbage","in a place")
	app.run(debug=True)

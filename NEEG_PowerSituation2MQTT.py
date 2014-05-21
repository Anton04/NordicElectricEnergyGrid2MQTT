#!/usr/bin/python

import sys,os 
import ConfigParser
import mosquitto
import json
import requests
import time

class NEEG_DataCollector(mosquitto.Mosquitto):
	def __init__(self,ip = "localhost", port = 1883, clientId = "NEEG2MQTT", user = "driver", password = "1234", prefix = "ElectricGridData", device = "/dev/ttyUSB0"):

		mosquitto.Mosquitto.__init__(self,clientId)

		self.prefix = prefix
		self.ip = ip
    		self.port = port
    		self.clientId = clientId
		self.user = user
    		self.password = password
    		
    		if user != None:
    			self.username_pw_set(user,password)

		self.will_set( topic =  "system/" + self.prefix, payload="Offline", qos=1, retain=True)
    		print "Connecting"
    		self.connect(ip,keepalive=10)
    		self.subscribe(self.prefix + "/#", 0)
    		self.on_connect = self.mqtt_on_connect
    		self.on_message = self.mqtt_on_message
    		self.publish(topic = "system/"+ self.prefix, payload="Online", qos=1, retain=True)
    		
    		self.lastupdate = 0
    		self.lasttimestamp = 0
    		self.updateperiod = 120
    		self.oldvalues = {}
    		self.running = True

		#thread.start_new_thread(self.ControlLoop,())	
		self.loop_start()

	def RunCollection(self):
		while(self.running):
			
			#Mark the time
			now = time.time()
			
			#Get data
			r = requests.get('http://driftsdata.statnett.no/restapi/ProductionConsumption/GetLatestDetailedOverview')
			

			#If we failed retry in a while
			if r.status_code != 200:
				print "Failed to get data from Nordic Electric Energy grid"
				time.sleep(30)
				continue
			
			self.lastupdate = now

			data = r.json()
			
			self.TranslateAndTransmitt(data)
			
			nextUpdate = self.lastupdate + self.updateperiod
			
			timeToNext = nextUpdate - time.time()
			
			if timeToNext > 0:
				time.sleep(timeToNext)
	
		return 
			
	def TranslateAndTransmitt(self,data):
		timestamp = data['MeasuredAt']
		
		#If this is old data ignore it. 
		if timestamp == self.lasttimestamp:
			return

		self.lasttimestamp = timestamp
		
		datadic = {}
		
		for category in data:
    			if type(data[category]) == type([]):
        			for item in data[category]:
        				#Abort if junk
            				if item[u'value'] == None or item[u'value'] == "" or item[u'titleTranslationId'] == None:
                				continue
            				topic = prefix + "/" + category + "/" +item[u'titleTranslationId']
            				value = item[u'value'].replace(u"\xa0","")
		
					#Has this topic existed before			
					if topic in self.oldvalues:
						#If yes do we have a new value?
						if self.oldvalues[topic] == value:
							#Same value ignore
							continue
					
					#Update 
					update = json.dumps({"time":timestamp,"value":value})
					self.publish(topic,update)
					
					#Save new value
					self.oldvalues[topic] = value
					
		return 

if __name__ == '__main__':


	#Where am I 
	path = os.path.abspath(os.path.dirname(sys.argv[0]))

	#Load config file... 	

	try:
		ConfigFile = sys.argv[1]
	except:
		ConfigFile = path + "/Plugwise2MQTT.cfg"

	try:
		f = open(ConfigFile,"r")
		f.close()
	except:
		try:
			ConfigFile = path + "/Plugwise2MQTT.cfg"
			f = open(ConfigFile,"r")
                	f.close()
		except:
			print "Please provide a valid config file! By argument or as default Plugwise2MQTT.cfg file."
			exit(1)
	config = ConfigParser.RawConfigParser(allow_no_value=True)
	config.read(ConfigFile)


	#Load basic config. 
	ip = config.get("MQTTServer","Address")
	port = config.get("MQTTServer","Port")
	user = config.get("MQTTServer","User")
	password = config.get("MQTTServer","Password")
	prefix = config.get("MQTTServer","Prefix")

	

	
	

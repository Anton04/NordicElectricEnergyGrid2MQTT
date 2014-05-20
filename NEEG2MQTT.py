#!/usr/bin/python

import urllib
import json
from time import sleep,time,mktime,strptime,strftime,localtime






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
	Name = config.get("PlugwiseOptions","Name")
	ip = config.get("MQTTServer","Address")
	port = config.get("MQTTServer","Port")
	user = config.get("MQTTServer","User")
	password = config.get("MQTTServer","Password")
	prefix = config.get("MQTTServer","Prefix")



	
	

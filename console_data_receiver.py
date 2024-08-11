#!/usr/bin/env python3

import rospy
import time
import os
import json
import argparse
from std_msgs.msg import Int32MultiArray
from webrtc_telemetry.msg import ConsoleCmd


class ConsoleDataReceiver(object):

	def __init__(self, PORT, with_NS_flag):

		rospy.init_node('console_data_receiver_node', anonymous=True)
		# self.console_cmd_pub = rospy.Publisher("/console_cmd", ConsoleCmd, queue_size=10)
		self.console_cmd_msg = ConsoleCmd()

		self.console_port = str(PORT)
		self.with_NS_flag = with_NS_flag

		if self.with_NS_flag:
			topic_name = "/robot" + "1" + "/console_cmd"
		else:
			topic_name = "/console_cmd"

		## This prepublish is required one time before, otherwise the first publish wouldn't be sent on loop
		console_cmd_pub = rospy.Publisher(topic_name, ConsoleCmd, queue_size=10)
		console_cmd_pub.publish(self.console_cmd_msg)
		print("pre-published")
		print(self.console_cmd_msg)

		self.loop()
		rospy.spin()

	def read_socat(self, term):
		read = term.readline().decode()
		return read

	def loop(self):

		rate = rospy.Rate(10)
		while not rospy.is_shutdown():
			# try:
			with open(self.console_port, "rb") as term:
				
				str_buffer = self.read_socat(term)
				# print(str_buffer)
				dec = json.loads(str_buffer)
				print(dec)
				for i in dec.items():
					if i[0] == "id":
						if dec["id"] is not None:
							self.console_cmd_msg.id.data = int(dec["id"])
					elif i[0] == "cmd":
						if dec["cmd"]["mode"] is not None:
							self.console_cmd_msg.mode.data = dec["cmd"]["mode"]
					elif i[0] == "mission":
						if dec["mission"] is not None:
							self.console_cmd_msg.mission.data = dec["mission"]

				if self.with_NS_flag:
					topic_name = "/robot" + str(dec["ID"]) + "/console_cmd"
				else:
					topic_name = "/console_cmd"

				
				console_cmd_pub = rospy.Publisher(topic_name, ConsoleCmd, queue_size=10)
				console_cmd_pub.publish(self.console_cmd_msg)
				print(self.console_cmd_msg)

				## clear data after published
				self.console_cmd_msg = ConsoleCmd()

			# except KeyboardInterrupt:
			# 		quit()
			# except Exception as e:
			# 	print("From console data receiver loop")
			# 	print(e)
			# 	print("Failed to parse")
			# 	pass	

			rate.sleep()



if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='console-data-receiver')
	parser.add_argument('--console_port',
						help="This is a second port generated by 1st_socat.sh")
	parser.add_argument('--with_ns',
						help="0 is without namespace as /console_cmd, 1 is with namespace as /robotX/console_cmd")

	args = parser.parse_args()
	CONSOLE_PORT = args.console_port
	with_ns = args.with_ns

	if CONSOLE_PORT is None:
		print("Error: please specify console port")
		quit()

	if with_ns is not None:
		if int(with_ns) == 0:
			with_ns_flag = False
		elif int(witn_ns) == 1:
			with_ns_flag = True
		else:
			print("Please specify --with_ns just only 0 or 1")
			quit()
	else:
		with_ns_flag = False

	print("Start console data receiver")
	cdr = ConsoleDataReceiver(CONSOLE_PORT, with_ns_flag)

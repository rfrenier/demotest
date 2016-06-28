
import os
import sys
import getopt
import commands
import time
import boto.cloudformation
import boto

#Define arguement variables
def main():
	app = ""
	nvtype = ""
	env = ""
	ver = ""
	dnsuser = ""
	dnspass = ""
	owner = ""
	email = ""


	print 'Number of arguments:', len(sys.argv), 'arguments.'
	print 'Argument List:', str(sys.argv)

	# Define globals
	helpmessage = "demoEC2.py --app <Application> --type <EnvironmentType> --env <ChefEnvironment> --ver <Version> --dnsuser <techopsapiuser> --dnspass <techopsapipassword> --owner <eid> --email <owneremail>"
	knifefile = "/opt/chef/developer12/developer/knife.rb"
	
	# Check if less than 8 parameters were passed
	if len(sys.argv) < 8:
		print helpmessage
		sys.exit(2)


	# Grab parameters and populate variables
	try:
		opts, args = getopt.getopt(sys.argv[1:],"ha:t:n:v:u:p:o:e:",["app=","type=","env=","ver=","dnsuser=","dnspass=","owner=","email="])
	except getopt.GetoptError: 
		print helpmessage
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print helpmessage
			sys.exit(2)
		elif opt in ("-a", "--app"):
			app = arg
		elif opt in ("-t", "--type"):
			nvtype = arg
		elif opt in ("-n", "--env"):
			env = arg
		elif opt in ("-v", "--ver"):
			ver = arg
		elif opt in ("-u", "--dnsuser"):
			dnsuser = arg
		elif opt in ("-p", "--dnspass"):
			dnspass = arg
		elif opt in ("-o", "--owner"):
			owner = arg
		elif opt in ("-e", "--email"):
			email = arg
		else:
			print helpmessage
			sys.exit(2)



	# If any of the variables were blank, echo help and quit
	#if (app == '') or (nvtype == '') or (env == '') or (ver == '') or (dnsuser == '') or (dnspass == '') or (owner == '') or (email == ''):
	#	print helpmessage
	#	sys.exit(2)

	# Define stackname
	stackname = app 
	#+ "-" + nvtype + "-" + env + "-" + ver + "-" + time.strftime("%H%M%S")

 	# Set S3 Template URL
	s3template = "https://s3.amazonaws.com/rf-cf-fidelity/web-cf.json"

 	# Run CFN command
	cfnconn = boto.cloudformation.connect_to_region(region)
	print "\nCreating stack...\n"
	cfnoutput = cfnconn.create_stack(stackname, template_url=s3template)
	if "arn:aws:cloudformation:" not in cfnoutput:
		print "Stack create failed."
		sys.exit(2)
	else:
		print "Output:\n" + cfnoutput
                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                



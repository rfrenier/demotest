
import os
import sys
import getopt
import commands
import time
import boto.cloudformation
import boto

def main():
	# Define arguement variables
	app = ""
	nvtype = ""
	env = ""
	ver = ""
	dnsuser = ""
	dnspass = ""
	owner = ""
	email = ""

	# Define globals
	helpmessage = "demo-deploy.py --app <Application> --type <EnvironmentType> --env <ChefEnvironment> --ver <Version> --dnsuser <techopsapiuser> --dnspass <techopsapipassword> --owner <eid> --email <owneremail>"
	knifefile = "/opt/chef/developer12/developer/knife.rb"
	
	# Check if less than 8 parameters were passed
	#if len(sys.argv) < 8:
	#	print helpmessage
	#	sys.exit(2)

	# Grab parameters and populate variables
	try:
		opts, args = getopt.getopt(sys.argv[1:],"ha:t:n:v:",["app=","type=","env=","ver="])
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
		else:
			print helpmessage
			sys.exit(2)

	# If any of the variables were blank, echo help and quit
	#if (app == '') or (nvtype == '') or (env == '') or (ver == '') or (dnsuser == '') or (dnspass == '') or (owner == '') or (email == ''):
	#	print helpmessage
	#	sys.exit(2)

	# Define stackname
	stackname = app + "-" + nvtype
	#+ "-" + nvtype + "-" + env + "-" + ver + "-" + time.strftime("%H%M%S")

	
	# Pull Chef Environment default_attributes --- changing this line to just read App
	chefpull = "/usr/bin/knife environment show -a default_attributes " + app 
	
	#+ "_" + nvtype + "_" + env + "_" + ver + " -c " + knifefile + " | sed 1,2d"
	#print "\nPulling chef environment:\n" + chefpull
	defattrib = commands.getoutput(chefpull)
	#print "\nOutput:\n" + defattrib
	diction = dict(item.strip().split(":") for item in defattrib.splitlines())
	region = diction["region"].strip()
	
	# Build CFN parameters
	cfecho = ""
	cfnparams = diction["cfn_inputs"].strip().split(",")

	print diction



	for detail in diction["echo2cfdetails"].strip().split(","):
		cfecho = cfecho + "echo " + detail + " >> /tmp/cf_details.txt;"
	paramslist = []
	
	
####################################	
	for param in cfnparams:
		if "TemplateURI" in param:
			paramslist.append((param,'https://' + diction[param].strip()))
		elif "echo2cfdetails" in param:
			paramslist.append((param,cfecho))
		else:
			paramslist.append((param,diction[param].strip()))
	#paramslist.append(('OwnerEID',owner))
	#paramslist.append(('OwnerEmail',email))
	#paramslist.append(('ApplicationName',app))
	#paramslist.append(('Environment',nvtype))
	#dnscname = app + env + ver
	#dnscname = dnscname.lower()
	#dnscname = dnscname.replace(".","-")
	#dnscname = dnscname + ".kdc.capitalone.com"
	#paramslist.append(('WebELBCNAMEFQDN',dnscname))
	print "\nParameters Contents:\n"
	print paramslist
##################################
	
	# Set S3 Template URL
	s3template = "https://" + diction["WebELBTemplateURI"].strip()
	
 	# Run CFN command
	cfnconn = boto.cloudformation.connect_to_region(region)
	print "\nCreating stack...\n"
	cfnoutput = cfnconn.create_stack(stackname, template_url=s3template, parameters=paramslist)
	if "arn:aws:cloudformation:" not in cfnoutput:
		print "Stack create failed."
		sys.exit(2)
	else:
		print "Output:\n" + cfnoutput
		
	# Wait for Stack to finish
	stacks = cfnconn.describe_stacks(stackname)
	stack = stacks[0]
	lcv = 0
	print "\nWaiting for stack to complete..."
	while "CREATE_COMPLETE" not in stack.stack_status:
		lcv += 1
		if "ROLLBACK" in stack.stack_status:
			print "\nStack is being rolled back. Check the cloudformation events for your stack to troubleshoot: " + stackname
			sys.exit(2)
		if lcv > 60:
			print "\nStack did not complete."
			print "Sending cfn delete: \n"
			cfnconn.delete_stack(stackname)
			sys.exit(2)
		time.sleep(10)
		stacks = cfnconn.describe_stacks(stackname)
		stack = stacks[0]
	print "Stack complete.\n"
        
if __name__ == "__main__":
	main()                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                



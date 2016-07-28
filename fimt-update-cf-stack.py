"""
  Script Name:  capone-aws-cfn-udpate.py
  Purpose:  This script is used to take several inputs and execute 
  			cloudformation after referencing chef.
"""
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
	stackname = ""

	# Define globals
	helpmessage = "capone-aws-cfn-update.py --app <Application> --type <EnvironmentType> --env <ChefEnvironment> --ver <Version> --dnsuser <techopsapiuser> --dnspass <techopsapipassword> --owner <eid> --email <owneremail> --stackname <aws-cfn-stackname>"
	knifefile = "/opt/chef/developer12/developer/knife.rb"
	
	# Check if less than 9 parameters were passed
	#if len(sys.argv) < 9:
	#	print helpmessage
	#	sys.exit(2)

	# Grab parameters and populate variables
	try:
		opts, args = getopt.getopt(sys.argv[1:],"ha:t:n:v:o:e:",["app=","type=","env=","ver=","owner=","email="])
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
		elif opt in ("-o", "--owner"):
			owner = arg
		elif opt in ("-e", "--email"):
			email = arg
		elif opt in ("-s", "--stackname"):
			stackname = arg
		else:
			print helpmessage
			sys.exit(2)

	# If any of the variables were blank, echo help and quit
	#if (app == '') or (nvtype == '') or (env == '') or (ver == '') or (dnsuser == '') or (dnspass == '') or (owner == '') or (email == '') or (stackname == ''):
	#	print helpmessage
	#	sys.exit(2)

	# Pull Chef Environment default_attributes
	chefpull = "/usr/bin/knife environment show -a default_attributes " + app + "_" + nvtype + "_" + env + "_" + ver + " -c " + knifefile + " | sed 1,2d"
	print "\nPulling chef environment:\n" + chefpull
	defattrib = commands.getoutput(chefpull)
	print "\nOutput:\n" + defattrib
	diction = dict(item.strip().split(":") for item in defattrib.splitlines())
	region = diction["region"].strip()

	# Build CFN parameters
	cfecho = ""
	cfnparams = diction["cfn_inputs"].strip().split(",")
	for detail in diction["echo2cfdetails"].strip().split(","):
		cfecho = cfecho + "echo " + detail + " >> /tmp/cf_details.txt;"
	paramslist = []
	for param in cfnparams:
		if "TemplateURI" in param:
			paramslist.append((param,'https://' + diction[param].strip()))
		elif "echo2cfdetails" in param:
			paramslist.append((param,cfecho))
		else:
			paramslist.append((param,diction[param].strip()))
	paramslist.append(('OwnerEID',owner))
	paramslist.append(('OwnerEmail',email))
	paramslist.append(('ApplicationName',app))
	paramslist.append(('Environment',nvtype))
	dnscname = app + env + ver
	dnscname = dnscname.lower()
	dnscname = dnscname.replace(".","-")
	dnscname = dnscname + ".kdc.capitalone.com"
	paramslist.append(('WebELBCNAMEFQDN',dnscname))
	print "\nParameters Contents:\n"
	print paramslist

	# Set S3 Template URL
	s3template = "https://" + diction["ParentTemplateS3File"].strip()

	# Run CFN command
	cfnconn = boto.cloudformation.connect_to_region(region)
	print "\nUpdating stack...\n"
	cfnoutput = cfnconn.update_stack(stackname, template_url=s3template, parameters=paramslist)
	if "arn:aws:cloudformation:" not in cfnoutput:
		print "Stack udpate failed."
		sys.exit(2)
	else:
		print "Output:\n" + cfnoutput

	# Wait for Stack to finish
	stacks = cfnconn.describe_stacks(stackname)
	stack = stacks[0]
	lcv = 0
	print "\nWaiting for stack to update..."
	while "UPDATE_COMPLETE" not in stack.stack_status:
		lcv += 1
		if "ROLLBACK" in stack.stack_status:
			print "\nStack is being rolled back. Check the cloudformation events for your stack to troubleshoot: " + stackname
			sys.exit(2)
		if lcv > 90:
			print "\nStack did not update."
			print "Sending cfn update cancel: \n"
			cfnconn.cancel_update_stack(stackname)
			sys.exit(2)
		time.sleep(10)
		stacks = cfnconn.describe_stacks(stackname)
		stack = stacks[0]
	print "Stack update complete.\n"

	# Get ELB Names
	webelbname = ""
	appelbname = ""
	stacks = cfnconn.describe_stacks(stackname)
	stack = stacks[0]
	for output in stack.outputs:
		if output.key == "WebELBName":
			webelbname = output.value
		elif output.key == "AppELBName":
			appelbname = output.value

	# Get starting IPs of instances
	appinstanceip = ""
	webinstanceip = ""
	elbconn = boto.connect_elb(region)
	ec2conn = boto.ec2.connect_to_region(region)
	load_balancer = elbconn.get_all_load_balancers(appelbname)[0]
	instance_ids = [ instance.id for instance in load_balancer.instances ]
	reservations = ec2conn.get_all_instances(instance_ids)
	instance_addresses = [ i.private_ip_address for r in reservations for i in r.instances ]
	appinstanceip = "*\t\t"
	for instanceip in instance_addresses:
		appinstanceip = appinstanceip + instanceip + "  "
	load_balancer = elbconn.get_all_load_balancers(webelbname)[0]
	instance_ids = [ instance.id for instance in load_balancer.instances ]
	reservations = ec2conn.get_all_instances(instance_ids)
	instance_addresses = [ i.private_ip_address for r in reservations for i in r.instances ]
	webinstanceip = "*\t\t"
	for instanceip in instance_addresses:
		webinstanceip = webinstanceip + instanceip + "  "

	# Get ELB Endpoints
	webelbendpoint = ""
	appelbendpoint = ""
	stacks = cfnconn.describe_stacks(stackname)
	stack = stacks[0]
	for output in stack.outputs:
		if output.key == "WebELBURL":
			webelbendpoint = output.value
		elif output.key == "AppELBURL":
			appelbendpoint = output.value

	# Print out summary
	print "******************************************************************************************"
	print "*\tStack Name: " + stackname
	print "*"
	print "*\t" + app + " Web Info:"
	print "*\tWeb ELB: " + webelbendpoint
	print "*\tWeb Chef Roles: " + diction["WebChefRoles"].strip()
	print "*\tStarting Web Instance IPs:"
	print webinstanceip
	print "*"
	print "*\t" + app + " App Info:"
	print "*\tApp ELB: " + appelbendpoint
	print "*\tApp Chef Roles: " + diction["AppChefRoles"].strip()
	print "*\tStarting App Instance IPs:"
	print appinstanceip
	print "******************************************************************************************"

if __name__ == "__main__":
	main()

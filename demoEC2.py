
import boto
import boto.cloudformation

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




	# Build CFN parameters
	cfecho = ""
	cfnparams = ""
	#diction["cfn_inputs"].strip().split(",")
	#for detail in diction["echo2cfdetails"].strip().split(","):
	#	cfecho = cfecho + "echo " + detail + " >> /tmp/cf_details.txt;"
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





# Define stackname
stackname = app 

 # Set S3 Template URL
s3template = "https://s3.amazonaws.com/rf-cf-fidelity/web-cf.json"

 # Run CFN command
cfnconn = boto.cloudformation.connect_to_region("us-east-1")
print "\nCreating stack...\n"
cfnoutput = cfnconn.create_stack(stackname, template_url=s3template)
if "arn:aws:cloudformation:" not in cfnoutput:
	print "Stack create failed."
	sys.exit(2)
else:
	print "Output:\n" + cfnoutput
                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                



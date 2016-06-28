
import boto
import boto.cloudformation


 # Set S3 Template URL
s3template = "https://s3.amazonaws.com/rf-cf-fidelity/web-cf.json"

 # Run CFN command
cfnconn = boto.cloudformation.connect_to_region("us-east-1")
print "\nCreating stack...\n"
cfnoutput = cfnconn.create_stack("rf-test02", template_url=s3template)
if "arn:aws:cloudformation:" not in cfnoutput:
	print "Stack create failed."
	sys.exit(2)
else:
	print "Output:\n" + cfnoutput
                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                     
                



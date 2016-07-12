"""
  Script Name:  capone-aws-cfn-delete.py
  Purpose:  This script is used to take several inputs and delete 
            a stack + clean up DNS.
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
    stackname = ""
    region = ""
    dnsuser = ""
    dnspass = ""

    # Define globals
    #helpmessage = "capone-aws-cfn-delete.py --region <region> --stackname <stackname> --dnsuser <techopsapiuser> --dnspass <techopsapipassword>"
    helpmessage = "capone-aws-cfn-delete.py --region <region> --stackname <stackname>"
    
    # Check if less than 4 parameters were passed
    if len(sys.argv) < 4:
        print helpmessage
        sys.exit(2)

    # Grab parameters and populate variables
    try:
        #opts, args = getopt.getopt(sys.argv[1:],"hr:s:u:p:",["region=","stackname=","dnsuser=","dnspass="])
        opts, args = getopt.getopt(sys.argv[1:],"hr:s:u:p:",["region=","stackname="])
    except getopt.GetoptError:
        print helpmessage
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print helpmessage
            sys.exit(2)
        elif opt in ("-r", "--region"):
            region = arg
        elif opt in ("-s", "--stackname"):
            stackname = arg
        #elif opt in ("-u", "--dnsuser"):
        #    dnsuser = arg
        #elif opt in ("-p", "--dnspass"):
        #    dnspass = arg
        else:
            print helpmessage
            sys.exit(2)

    # If any of the variables were blank, echo help and quit
    #if (region == '') or (stackname == '') or (dnsuser == '') or (dnspass == ''):
    if (region == '') or (stackname == ''):
        print helpmessage
        sys.exit(2)

#    # Get cname if exists in stack and determine if dns deletion is required
#    updatedns = "false"
#    dnscname = ""
#    webelb = commands.getoutput("/usr/local/bin/aws --region " + region + " cloudformation describe-stacks --stack-name " + stackname + " | grep OutputValue | grep WebELB | awk -F ':' '{print $2'} | tr -d ' \"'")
#    if ".kdc.capitalone.com" in commands.getoutput("/usr/local/bin/aws --region " + region + " cloudformation describe-stacks --stack-name " + stackname + " | grep OutputValue | grep kdc.capitalone.com | awk -F ':' '{print $2'} | tr -d ' \"'"):
#        dnscname = commands.getoutput("/usr/local/bin/aws --region " + region + " cloudformation describe-stacks --stack-name " + stackname + " | grep OutputValue | grep kdc.capitalone.com | awk -F ':' '{print $2'} | tr -d ' \"'")
#        if webelb in commands.getoutput("host " + dnscname):
#            print dnscname + " is pointing to " + webelb 
#            print commands.getoutput("host " + dnscname)
#            updatedns = "true"
#        else:
#            print "CNAME found in stack is not pointing to the web ELB so we are not going to delete."

    # Delete stack
    cfnconn = boto.cloudformation.connect_to_region(region)
    print "Sending CFN Delete...\n"
    cfnoutput = cfnconn.delete_stack(stackname)
    print cfnoutput

    # Make sure stack is in DELETE phase.  If not, exit with error.
    stacks = cfnconn.describe_stacks(stackname)
    stack = stacks[0]
    if "DELETE" not in stack.stack_status:
        print "Stack failed to enter DELETE status.  Assume that the delete command to AWS failed."
        sys.exit(2)

    # Wait for stack to delete
    stackfound = "false"
    stacks = cfnconn.describe_stacks()
    for stack in stacks:
        if stackname in stack.stack_name:
            stackfound = "true"
    if stackfound == "false":
        print "Stack " + stackname + " has been deleted."
        sys.exit(0)
    lcv = 0
    print "\nWaiting for stack to delete..."
    while stackfound == "true":
        lcv += 1
        stackfound = "false"
        stacks = cfnconn.describe_stacks()
        for stack in stacks:
            if stackname in stack.stack_name:
                stackfound = "true"
        if lcv > 60:
            print "\nStack did not delete."
            sys.exit(2)
        time.sleep(10)
    print "\nStack " + stackname + " has been deleted."

#    cnamedelete = "curl -i -X DELETE -H \"Content-Type:application/json\" --proxy proxy.kdc.capitalone.com:8099 --digest --user \"" + dnsuser + ":" + dnspass + "\" 'http://techopsapi.kdc.capitalone.com/technology-operations/infrastructure/networking/cname?cname=" + dnscname + "'"

#    # Delete cname if set to "true"
#    if updatedns == "true":
#        print "\n\nDeleting cname " + dnscname + "..."
#        print "Output:\n" + commands.getoutput(cnamedelete)

if __name__ == "__main__":
    main()

import boto3, sys, argparse, csv, re, string
from pathlib import Path
from boto3.session import Session
from botocore.exceptions import ClientError, ProfileNotFound

regions = Session().get_available_regions('ec2') # gets the availability zones that can be used by the SDK, from the SDK
home = str(Path.home()) # gets the running user's home dir. This should work across operating systems..
profiles = []
contents = ""
parser = argparse.ArgumentParser(description='perform aws reconnaissance via api scraping')
parser.add_argument("-a","--authfile", help="specify either 'credentials' or 'config' file for authentication, both located in ~/.aws/")
parser.add_argument("-e", "--external", action="store_true", help="use to only extract information about objects that are internet-facing/publicly accessible. without this flag, only internal, privately addressed resources will be returned")
parser.add_argument("-o", "--output", help="use --output <file.csv> to write to a csv file. without this, default output is to stdout")
parser.add_argument("-lb", "--loadbalancers", action="store_true", help="use this flag to pull dns names from classic and application load balancers")
parser.add_argument("-v", "--verbose", action="store_true", help="use this flag to output profile, region, and service blurbs to stdout as script iterates")
parser.add_argument("-p", "--profile", nargs='+', help=("specify a profile (or multiple) to use. defaults to all profiles found in selected authentication file"))
args = parser.parse_args()

def pull_elb (sesh): # Elastic Load Balancers
	client = sesh.client('elb')
	response = client.describe_load_balancers()
	for item in response["LoadBalancerDescriptions"]:
		dns = item["DNSName"]
		if args.external:
			if "internal" not in dns:
				output(writer,dns)
		else:
			if "internal" in dns:
				output(writer,dns)

def pull_alb (sesh): # Application Load Balancers
	client = sesh.client('elbv2')
	response = client.describe_load_balancers()
	for item in response["LoadBalancers"]:
		dns = item["DNSName"]
		if args.external:
			if "internal" not in dns:
				output(writer,dns)
		else:
			if "internal" in dns:
				output(writer,dns)

def pull_eip (sesh): # External Elastic IP Addresses
	client = sesh.client('ec2')
	response = client.describe_addresses()
	for item in response["Addresses"]:
		pub = item["PublicIp"]
		output(writer,pub)

def pull_pip (sesh): # Internal EC2 IP Addresses
	client = sesh.client('ec2')
	response = client.describe_instances()
	for reserv in response["Reservations"]:
		for instance in reserv["Instances"]:
			ec2r = sesh.resource('ec2')
			inst = ec2r.Instance(instance["InstanceId"])
			priv = inst.private_ip_address
			output(writer,priv)

def output (writer,item): # write the values returned by the "pull_*() queries"
	if args.output:
		writer.writerow({'Target': item})
	else:
		print(item)

def extractProfiles(home, args, profiles, contents): # parses the authentication file specified, gets list of all profiles in said file
	cf = open(home+"/.aws/"+args.authfile,"r")
	if cf.mode == 'r': contents = cf.read(); cf.close()
	if args.authfile == "config":
		if "default" in contents: profiles.append("default")
		for i in re.findall("(?:profile).*\w",contents): profiles.append(i.split(' ')[1])
	elif args.authfile == "credentials":
		for i in re.findall("\[([a-zA-Z0-9-\s]+)\]",contents): profiles.append(i)

if args.profile and args.authfile: # check for redundant arguments
	print("\nif you're specifying profiles, you don't need to include an authentication file. only specify an authentication file if you want this script to extract all of the profiles contained in said file, and loop through them. if you use a profile, its name will be passed to the SDK which will find the corresponding access keys in whatever auth file the profile was defined in\n")
	exit()

if args.profile: # if profiles are explictly passed to the script, use those
	for i in args.profile:
		profiles.append(i)
else: # if not, use all the profiles found in the authentication file specified
	try:
		extractProfiles(home, args, profiles, contents)
	except FileNotFoundError:
		print("specified file not found. it might not exist, or you misspelt. specify either 'config' or 'credentials'")
		exit()
	except PermissionError:
		print("you don't have permission to access",args.authfile)
		exit()
	except TypeError:
		print("specify an authentication file")
		exit()

if args.output: # sets up the output file, if that option has been used
	of = open(args.output,"w",newline='')
	writer = csv.DictWriter(of, fieldnames=['Target'])
else:
	writer = ""

for acct in profiles:
	for az in regions:
		if args.verbose: print("\nprofile:",acct,"-- region:",az)
		try:
			sesh = boto3.session.Session(region_name = az, profile_name = acct)
		except ProfileNotFound:
			print("invalid profile:",acct,"\ndouble check what profiles exist in your authentication files")
			exit()
		try:
			if args.loadbalancers:
				if args.verbose: print("elastic load balancers ----")
				pull_elb(sesh)
				if args.verbose: print("application load balancers ----")
				pull_alb(sesh)
			else:
				if args.external:
					if args.verbose: print("elastic IPs ----")
					pull_eip(sesh)
				else:
					if args.verbose: print("ec2 private IPs ----")
					pull_pip(sesh)
		except ClientError as err:
			if ("InvalidClientTokenId" in str(err)) or ("AuthFailure" in str(err)):
				print("authentication failure")
				pass
			else:
				print(err)
				pass
import boto3, sys, argparse, csv, re, string
from pathlib import Path
from boto3.session import Session
from botocore.exceptions import ClientError

regions = Session().get_available_regions('ecs')
home = str(Path.home())
profiles = []
contents = ""
parser = argparse.ArgumentParser(description='perform aws reconnaissance via api scraping')
parser.add_argument("credsfile", help="specify whether to use keys found in the 'credentials' or 'config' file, both located in ~/.aws/")
parser.add_argument("-p", "--public", action="store_true", help="use to only extract information about objects that are internet-facing/publicly accessible. without this flag, only internal, privately addressed resources will be returned")
parser.add_argument("-o", "--output", help="use --output <file.csv> to write to a csv file. without this, default output is to stdout")
parser.add_argument("-lb", "--loadbalancers", action="store_true", help="use this flag to pull dns names from classic and application load balancers")
parser.add_argument("-v", "--verbose", action="store_true", help="use this flag to output profile, region, and service blurbs to stdout as script iterates")
args = parser.parse_args()

def pull_elb (sesh): # Elastic Load Balancers
	client = sesh.client('elb')
	response = client.describe_load_balancers()
	for item in response["LoadBalancerDescriptions"]:
		dns = item["DNSName"]
		if args.public:
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
		if args.public:
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

def output (writer,item):
	if args.output:
		writer.writerow({'Target': item})
	else:
		print(item)

def extractProfiles(home, args, profiles, contents):
	cf = open(home+"/.aws/"+args.credsfile,"r")
	if cf.mode == 'r': contents = cf.read(); cf.close()
	if args.credsfile == "config":
		if "default" in contents: profiles.append("default")
		for i in re.findall("(?:profile).*\w",contents): profiles.append(i.split(' ')[1])
	if args.credsfile == "credentials":
		for i in re.findall("\[([a-zA-Z0-9-\s]+)\]",contents): profiles.append(i)

try:
	extractProfiles(home, args, profiles, contents)
except FileNotFoundError:
	print("specified file not found. it might not exist, or you misspelt. specify either 'config' or 'credentials'")
	exit()
except PermissionError:
	print("you don't have permission to access",args.credsfile)
	exit()

if args.output:
	of = open(args.output,"w",newline='')
	writer = csv.DictWriter(of, fieldnames=['Target'])
else:
	writer = ""

for acct in profiles:
	for az in regions:
		if args.verbose: print("\nprofile:",acct,"-- region:",az)
		sesh = boto3.session.Session(region_name = az, profile_name = acct)
		try:
			if args.loadbalancers:
				if args.verbose: print("elastic load balancers ----")
				pull_elb(sesh)
				if args.verbose: print("application load balancers ----")
				pull_alb(sesh)
			else:
				if args.public:
					if args.verbose: print("elastic IPs ----")
					pull_eip(sesh)
				else:
					if args.verbose: print("ec2 private IPs ----")
					pull_pip(sesh)
		except ClientError as err:
			if ("InvalidClientTokenId" in str(err)) or ("AuthFailure" in str(err)):
				print("invalid credentials")
				pass
			else:
				print(err)
				pass
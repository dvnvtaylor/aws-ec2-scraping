import boto3
import sys
import argparse
import csv

regions=["us-east-1","us-east-2","us-west-1","us-west-2", "ca-central-1","ap-south-1","ap-northeast-2","ap-southeast-1", "ap-southeast-2","ap-northeast-1","eu-central-1","eu-west-1","eu-west-2","sa-east-1"]
profiles=['prod','qa']

parser = argparse.ArgumentParser(description='perform aws reconnaissance via api scraping')
parser.add_argument("-p", "--public", action="store_true", help="use to only extract information about objects that are internet-facing/publicly accessible. without this flag, only internal, privately addressed resources will be returned")
args = parser.parse_args()

def pull_elb (sesh): # Elastic Load Balancers
	client = sesh.client('elb')
	response = client.describe_load_balancers()
	for item in response["LoadBalancerDescriptions"]:
		dns = item["DNSName"]
		if args.public:
			if "internal" not in dns:
				print(dns)
		else:
			if "internal" in dns:
				print(dns)

def pull_alb (sesh): # Application Load Balancers
	client = sesh.client('elbv2')
	response = client.describe_load_balancers()
	for item in response["LoadBalancers"]:
		dns = item["DNSName"]
		if args.public:
			if "internal" not in dns:
				print(dns)
		else:
			if "internal" in dns:
				print(dns)

def pull_eip (sesh): # External Elastic IP Addresses
	client = sesh.client('ec2')
	response = client.describe_addresses()
	for item in response["Addresses"]:
		pub = item["PublicIp"]
		print(pub)

def pull_pip (sesh): # Internal EC2 IP Addresses
	client = sesh.client('ec2')
	response = client.describe_instances()
	for reserv in response["Reservations"]:
		for instance in reserv["Instances"]:
			ec2r = sesh.resource('ec2')
			inst = ec2r.Instance(instance["InstanceId"])
			priv = inst.private_ip_address
			print(priv)


for acct in profiles:
	for az in regions:
		sesh = boto3.session.Session(region_name = az, profile_name = acct)
		pull_elb(sesh)
		pull_alb(sesh)
		if args.public:
			pull_eip(sesh)
		else:
			pull_pip(sesh)

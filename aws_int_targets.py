import boto3

regions=["us-east-1","us-east-2","us-west-1","us-west-2", "ca-central-1","ap-south-1","ap-northeast-2","ap-southeast-1", "ap-southeast-2","ap-northeast-1","eu-central-1","eu-west-1","eu-west-2","sa-east-1"]
profiles=['prod','qa']

def pull_elb (sesh): # Internal Elastic Load Balancers
	client = sesh.client('elb')
	response = client.describe_load_balancers()
	for item in response["LoadBalancerDescriptions"]:
		dns = item["DNSName"]
		if "internal" in dns:
			print(dns)

def pull_alb (sesh): # Internal Application Load Balancers
	client = sesh.client('elbv2')
	response = client.describe_load_balancers()
	for item in response["LoadBalancers"]:
		dns = item["DNSName"]
		if "internal" in dns:
			print(dns)

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
		pull_pip(sesh)

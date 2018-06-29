# AWS Infrastructure Recon
This script is essentially a wrapper for boto3 (Python SDK), to interface with the AWS API. I threw together the initial functionality to quickly create a list of all servers in my organization to pipe into our vulnerability scanner. Now I'm maintaining it to become more fluent in Python, and to hopefully provide a useful reconnaissance tool for pen-testing engagements. 

### Internal (privately addressed) targets:*
- Private EC2 IP addresses
- [Internal Classic Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-internal-load-balancers.html#internal-public-dns-name)
- [Internal Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)

### Public (internet-facing) targets:
- Elastic IP Addresses
- [External Classic Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-internet-facing-load-balancers.html)
- [External Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)

These require a certain amount of access [(AWS access credentials)](https://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html). A compromised workstation or server would supply these, given the keys are stored in plaintext in the filesystem.

#### To do:
- Include option for extracting EC2 tags
- Include option for extracting built-in EC2 information (AMI ID, VPC ID, attached security groups) 
- Create module for pulling useful IAM information
- Create module for pulling useful S3 information
- Create module for pulling useful EKS/ECS information
- Outline usage information here

## Requirements
- [Python3](https://www.python.org/downloads/)
- [AWS SDK for Python (Boto3)](https://aws.amazon.com/sdk-for-python/)


&ast;**_all internal load balancers (of either type) have the word "internal" in their given DNS name_**

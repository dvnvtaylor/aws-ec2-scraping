# AWS Infrastructure Recon
The purpose of these scripts are to scrape an AWS infrastructure to determine an attack surface for a pen-test. They will loop through all availability zones, and multiple accounts if supplied. By default, only IP addresses and DNS records are extracted. The targetted systems are as follows:

### Internal (privately addressed) targets:*
- EC2 IP addresses
- [Internal Classic Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-internal-load-balancers.html#internal-public-dns-name)
- [Internal Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)

### External (internet-facing) targets:
- Elastic IP Addresses
- [External Classic Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/elb-internet-facing-load-balancers.html)
- [External Application Load Balancers](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)

These require a certain amount of access [(AWS access credentials)](https://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html). A compromised workstation or server would supply these, given the keys are stored in plaintext in the filesystem.

#### Next Steps:
- Allow toggling of extraction of more data from the targets (ex: name, tags, etc)

## Requirements
- [Python3](https://www.python.org/downloads/)
- [AWS SDK for Python (Boto3)](https://aws.amazon.com/sdk-for-python/)


&ast;**_all internal load balancers (of either type) have the word "internal" in their given DNS name_**

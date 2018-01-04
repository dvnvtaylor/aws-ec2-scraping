# aws-scraping
Scripts to quickly scrape an AWS environment for information gathering purposes.

These assume you have access to AWS account credentials, and will loop through however many are available. Edit the intial profile variables accordingly. The examples used are 'prod' and 'qa' accounts. All regions will be parsed as well.

These credentials are stored in plain text, read about that here: https://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html

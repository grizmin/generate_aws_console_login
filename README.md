# generate_aws_console_login

### This tool will generate AWS console using only API access (API Key and Key Secret).  

| :zap:  Once created, AWS console login link will be active for the given amount of time and *ANYONE* can use it to access AWS console without *ANY* authentication.   |
|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

### Usage:
```
Usage:
    generate_console_url.py [options] [--] <account_id> [--tags=TAGS]...

    generate_console_url.py -h | --help

Options:
    -p PROFILE, --profile PROFILE            aws profile to use.
    
    -r ROLE, --role ROLE                     role name to assume [default: Admin]

    -u --username USERNAME                   username to append in session name [default: AssumeRoleUser]

    -t --tags TAGS                           Tags to add as PrincipalTags to the session.
    
    --timeout TIMEOUT                        Session Timeout in seconds [default: 3600]

    --browser                                Open link in browser

    -d --verbose                             Print condition

    -v --version                             show version

Example:
   python generate_console_url.py --profile MyAuthProfileName -r IAMRoleICanAssume -t team:bolt --timeout 900

Additional information: https://aws.amazon.com/blogs/security/how-to-enable-cross-account-access-to-the-aws-management-console/
```

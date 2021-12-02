"""
This tool will create a AWS Console login session using any role, that you have permissions to assume.

WARNING: Once generated the console login link will be active for the chosen duration time and _ANYONE_ with the link can use it to log in without _ANY_ authentication.

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
   python generate_console_url.py --profile MyAuthProfileName -r IAMRoleICanAssume -t team:bolt --timeout 900 --browser

Additional information: https://aws.amazon.com/blogs/security/how-to-enable-cross-account-access-to-the-aws-management-console/

"""
import urllib
import json
import sys
import os
import webbrowser
from docopt import docopt # 'pip install docopt'
import requests  # 'pip install requests'
import boto3  # AWS SDK for Python (Boto3) 'pip install boto3'


VERSION = '0.0.12'
__AUTHOR__ = 'grizmin@gmail.com'

def main():
    
    arg = docopt(__doc__, version=f'generate_console_url v{VERSION}')
    verbose = arg['--verbose']
    profle_name = arg['--profile']
    account_id = arg['<account_id>']
    role_name = arg['--role']
    user_name = arg['--username']
    tags = arg['--tags']
    session_timeout = arg['--timeout']
    
    # Step 1: Authenticate
    if not profle_name:
        print("No profile name specified. Falling back to environment variables.")
        my_session = boto3.Session(
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            aws_session_token=os.environ['AWS_SESSION_TOKEN']
        )
    else: 
        my_session = boto3.session.Session(profile_name=profle_name)

    # Step 2: Assume the desired role
    sts_connection = my_session.client('sts')

    assumed_role_object = sts_connection.assume_role(
        RoleArn=f"arn:aws:iam::{account_id}:role/{role_name}",
        RoleSessionName=f"{user_name}",
        Tags=[{'Key':k, 'Value':v} for (k,v) in [a.split(":") for a in tags]]
    )

    # Step 3: Format resulting temporary credentials into JSON
    url_credentials = {}
    url_credentials['sessionId'] = assumed_role_object.get(
        'Credentials').get('AccessKeyId')
    url_credentials['sessionKey'] = assumed_role_object.get(
        'Credentials').get('SecretAccessKey')
    url_credentials['sessionToken'] = assumed_role_object.get(
        'Credentials').get('SessionToken')
    json_string_with_temp_credentials = json.dumps(url_credentials)

    # Step 4. Make request to AWS federation endpoint to get sign-in token. Construct the parameter string with
    # the sign-in action request, a 60 minutes session duration, and the JSON document with temporary credentials
    # as parameters.
    def quote_plus_function(s):
        return urllib.parse.quote_plus(s)
    request_parameters = "?Action=getSigninToken"
    request_parameters += f"&DurationSeconds={session_timeout}"
    request_parameters += "&Session=" + \
        quote_plus_function(json_string_with_temp_credentials)
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters
    r = requests.get(request_url)
     # Returns a JSON document with a single element named SigninToken.
    signin_token = json.loads(r.text)

    # Step 5: Create URL where users can use the sign-in token to sign in to
    # the console. This URL must be used within 60 minutes (by default) after the sign-in token was issued.
    request_parameters = "?Action=login"
    request_parameters += "&Issuer=cb-sbu.io"
    request_parameters += "&Destination=" + \
        quote_plus_function("https://console.aws.amazon.com/")
    request_parameters += "&SigninToken=" + signin_token["SigninToken"]
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters

    # Send final URL to stdout
    print(request_url)
    # Open Browser
    if arg['--browser']:
        webbrowser.open(request_url)

if __name__ == "__main__":
    main()

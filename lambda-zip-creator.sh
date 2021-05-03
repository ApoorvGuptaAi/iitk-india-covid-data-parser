#/bin/bash
# Based on https://docs.aws.amazon.com/pinpoint/latest/developerguide/tutorials-importing-data-create-python-package.html
# and https://towardsdatascience.com/serverless-covid-19-data-scraper-with-python-and-aws-lambda-d6789a551b78

set -e
set -x

PYTHON_BINARY=python3.7  # Change for your machine, ensure this refers to a python3.x binary to match the lambda function environment.

$PYTHON_BINARY -m pip install requests beautifulsoup4 -t upload/
cp *.py upload/
pushd upload/
zip -r ../lambda.zip requests bs4 chardet lambda_function.py certifi idna backports urllib3 soupsieve *.py
popd

#/bin/bash
# Based on https://docs.aws.amazon.com/pinpoint/latest/developerguide/tutorials-importing-data-create-python-package.html
# Might have an easier approach based on https://towardsdatascience.com/serverless-covid-19-data-scraper-with-python-and-aws-lambda-d6789a551b78
PYTHON_BINARY=python3.7  #Change for your machine.
python -m pip install virtualenv
python -m virtualenv venv
source venv/bin/activate
python -m pip install requests beautifulsoup4
deactivate
pushd venv/lib/python3.7/site-packages
cp ../../../../*.py .
zip -r lambda.zip requests bs4 chardet lambda_function.py certifi idna backports urllib3 soupsieve *.py
popd
mv venv/lib/python3.7/site-packages/lambda.zip .


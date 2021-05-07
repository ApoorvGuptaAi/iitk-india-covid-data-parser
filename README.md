# iitk-india-covid-data-parser

Parse websites and return a list of hospital dataclases.
Written to a database.

## Update 

 * Run "./lambda-zip-creator.sh" to create a new lambda.zip.

 * Follow instructions from [AWS](https://docs.aws.amazon.com/pinpoint/latest/developerguide/tutorials-importing-data-lambda-function-input-split.html) to  update the [data_scraper lambda](https://ap-south-1.console.aws.amazon.com/lambda/home?region=ap-south-1#/functions/) from the zip.

## Code
Main entrypoint: lambda_function.py

## Deps
Requires environment variables:
* INDIA_COVID_HOST
* INDIA_COVID_AUTH_HEADER

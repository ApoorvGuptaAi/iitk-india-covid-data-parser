# iitk-india-covid-data-parser

Parse websites and return a list of hospital dataclases.
Written to a database.

## Code

Main entrypoint: lambda_function.py

### Deps
Requires environment variables:
* INDIA_COVID_HOST
* INDIA_COVID_AUTH_HEADER

## Deployment

### Deploy with SAM template + AWS CLI
1. Make sure you have AWS CLI set up and configured properly 
    - Install the AWS command line interface: <https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html>
    - Configure your CLI, <https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html>
        - use command `aws configure` and follow the prompts to enter your info
            - you may need to create your key ID and secret access key in the AWS console
2. Build the app with `sam build`
3. Deploy the app with `sam deploy --guided --profile <<INSERT AWS PROFILE NAME HERE>> --region ap-south-1`
4. Crack open a beer n chill

### Update - with the Lambda zip

 * Run "./lambda-zip-creator.sh" to create a new lambda.zip.

 * Follow instructions from [AWS](https://docs.aws.amazon.com/pinpoint/latest/developerguide/tutorials-importing-data-lambda-function-input-split.html) to  update the [data_scraper lambda](https://ap-south-1.console.aws.amazon.com/lambda/home?region=ap-south-1#/functions/) from the zip.

### Monitor

* AWS: https://ap-south-1.console.aws.amazon.com/lambda/home?region=ap-south-1#/functions/data_scraper?newFunction=true&tab=monitoring
* DB updates: https://charts.mongodb.com/charts-iitk-covid-help-jmykt/public/dashboards/609180fc-1094-48ee-8ed1-9b2f131c4f3f


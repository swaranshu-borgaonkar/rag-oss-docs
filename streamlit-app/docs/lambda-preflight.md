# lambda-preflight README

This tool enables developers to validate AWS Lambda handlers locally by checking IAM permissions against real execution role policies before deployment.

## Key Features

The tool performs "local IAM linting" by pulling an execution role's actual policies and evaluating boto3 calls against them. It allows you to find the missing s3:PutObject on your laptop, not in a CloudWatch log after a failed deploy.

The runtime component includes schema-accurate event fixtures for various AWS services (API Gateway v1/v2, SQS, SNS, S3, EventBridge, DynamoDB Streams) and faithful invocation semantics including context reproduction and timeout enforcement.

## Differentiation

Unlike standard local-lambda runners, lambda-preflight uniquely offers IAM permission linting against your real role — a capability absent from comparable tools. The solution handles explicit-deny logic, wildcards, resource matching, and permission boundaries, while flagging scenarios it cannot faithfully evaluate via a CannotEvaluate result.

## Limitations

The tool addresses shape, contract, runtime semantics, and identity-permission classes of failures. However, it cannot reproduce cloud-only realities like concurrency limits, SCPs, or resource-based policies. It is a pre-flight linter, not a parity guarantee.

## Installation & Licensing

Installation via pip install "lambda-preflight[aws]" with MIT licensing.

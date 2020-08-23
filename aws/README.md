# Amazon Web Services

## Overview

[Amazon Web Services](https://aws.amazon.com) (AWS) is a cloud computing
platform which provides a plethora of computing services such as servers,
storage, databases, messaging and queuing systems, etc. Here, we describe the
most important services as far as data engineers are concerned, and explain how
to interact with them using the console, the command line interface or the
Python SDK (Software Development Kit)
[boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html).

AWS documentation is exhaustive and usually well explained, so we will often
point the reader to official resources, and focus on providing a path to learn
how to use AWS.

## Getting started

If you do not have an AWS account, create one [here](https://aws.amazon.com/console).

Create a user with administrator permissions that you will use to build AWS resources by following these [instructions](https://docs.aws.amazon.com/mediapackage/latest/ug/setting-up-create-iam-user.html).

Install the AWS command-line interface by running `pip install aws-cli` and configure it according to the [documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

## IAM

IAM is Identity and Access Management.

We describe IAM main features and how to interact with them in [iam.md](iam.md).

## S3

S3 is Simple Storage Service.

We describe S3 main features and how to interact with them in [s3.md](s3.md).

## Other learning resources

[This page](https://expeditedsecurity.com/aws-in-plain-english/) describes many
of AWS services in layman's terms.

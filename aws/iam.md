# IAM

## Introduction

AWS Identity and Access Management (IAM) is a service which allows you to
manage users and their access to an AWS account in a centralized way. It
provides granular permissions (what user, what resources, what conditions,
etc), identity federation (you can let your users authenticate to your
applications with the Google or Facebook credentials, for example),
multi-factor authentication (MFA), and other useful features.

IAM is a *global* service, meaning that once you create IAM resources they
can be used in any AWS region.

## Users

IAM allows you to manages *users* of your account. Users can be created for
physical persons, or for applications (a so-called *service user*).

A user has permanent credentials to AWS and she uses these credentials to directly
interact with AWS. These credentials include AWS access keys for programmatic
access (e.g. using the AWS command line interface), a password for console
login, or an MFA device.

## Groups

A *group* is simply a collection of users. You can manage user permissions easily through group memberships.

## Roles

*Roles* are entities that define a set of permissions to access AWS resources. Contrary to users, roles do not have credentials and cannot access resources by themselves. You let users, applications, or AWS services (such as EC2) assume roles to give specific permissions.

## Policies

*Policies* manage access permissions for users, groups, roles, and other AWS
resources. A policy contains a *policy document* that defines permissions
using the JSON format. To assign permissions using a policy, you create a
policy and *attach* it to users, groups, or roles.

## Read the docs

You should have a look at the [FAQ](https://aws.amazon.com/iam/faqs) to get a
high level view of AWS IAM. For more details, please go to the [user
guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html).

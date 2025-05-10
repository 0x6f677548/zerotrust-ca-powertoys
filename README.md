# Conditional Access PowerToys (CA-PowerToys)

[![PyPI - Version](https://img.shields.io/pypi/v/ca-pwt.svg)](https://pypi.org/project/ca-pwt)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ca-pwt.svg)](https://pypi.org/project/ca-pwt)
[![GitHub - Lint](https://go.hugobatista.com/gh/zerotrust-ca-powertoys/actions/workflows/lint.yml/badge.svg)](https://go.hugobatista.com/gh/zerotrust-ca-powertoys/actions/workflows/lint.yml)
[![GitHub - Test](https://go.hugobatista.com/gh/zerotrust-ca-powertoys/actions/workflows/test.yml/badge.svg)](https://go.hugobatista.com/gh/zerotrust-ca-powertoys/actions/workflows/test.yml)

CA-PowerToys is a set of tools to help you manage Conditional Access policies in your tenant. It is a command line tool that can be used to export and import Conditional Access policies and associated groups, facilitating the editing of the policies in a human readable format. This is particular useful if you are implementing a Policy-as-Code approach, eventually using a Git repository to store your policies and a CI/CD pipeline (like Azure DevOps) to import them into your tenant.
![Overview](https://go.hugobatista.com/ghraw/zerotrust-ca-powertoys/main/docs/images/ca-powertoys-overview-architecture.png)

## Why ?
There are several tools to manage Conditional Access policies, such as Graph PowerShell, Microsoft Graph API, Azure AD PowerShell and even M365DSC. Unfortunately, none of these tools can be used to export Conditional Access policies in a **format that can be human readable and editable**, and then **import them back to another tenant**. This is where CA-PowerToys can help you, with several commands that can be chained to export, clean up, replace guids with attributes, and import Conditional Access policies and groups. 


## Features

CA-PowerToys can be used to:
- **Get an access token** to be used in subsequent commands or to be used in other tools, such as Graph PowerShell, using a desired client_id (useful if Graph PowerShell or other tools are blocked in the target tenant)
- **Export/Import Conditional Access policies** to/from a file
- **Export groups** that are used in Conditional Access policies to a file
- **Clean up Conditional Access policies and Groups files**, removing attributes that are read-only or not allowed in the import process
- **Replace guids with attributes in Conditional Access policies (and vice-versa)**, making it "human readable" and editable. For example, replace the `id` attribute with the `displayName` attribute in a list of excluded groups in a Conditional Access policy
- **Throttle the number of requests** to the Graph API, to avoid hitting the rate limits

### Human readable format Policies
One of the key features of CA-PowerToys is the ability to export CA Policies in a human readable format, where guids are replaced with attributes. This is particularly useful if you are implementing a Policy-as-Code approach, eventually using a Git repository to store your policies and a CI/CD pipeline (like Azure DevOps) to import them into your tenant.
![Human readable format Policies](https://go.hugobatista.com/ghraw/zerotrust-ca-powertoys/main/docs/images/human-readable-policies1.png)


## Zero Trust Sample Policies
A set of sample policies can be found in the [Zero Trust Conditional Access Policies](https://go.hugobatista.com/gh/zerotrust-ca-policies) repository. These policies are based on the samples available at https://github.com/microsoft/ConditionalAccessforZeroTrustResources and the [recommended guidelines](https://docs.microsoft.com/en-us/azure/architecture/guide/security/conditional-access-zero-trust?msclkid=d1768a34ceda11ec9b6c8f244f8d05bd) and can be used as a starting point to implement a Zero Trust strategy in your organization.

## Installation
CA-PowerToys is a command line tool that can be used in Windows, Linux, and MacOS. It is written in Python and can be used as a module or as a standalone tool, as long as you have Python >3.7 installed (or Docker).

### pip
To install it, you can use pip:
```console
> pip install ca-pwt
> ca-pwt --help
```

### From source code
You can also install it from the source code:
```console
> git clone https://go.hugobatista.com/gh/zerotrust-ca-powertoys.git
> cd ca-powertoys
> pip install .
> ca-pwt --help
```
### Docker
Alternatively, you can use the Docker image:
```console
> docker pull ghcr.io/0x6f677548/zerotrust-ca-powertoys:latest
> docker run -it --rm ghcr.io/0x6f677548/zerotrust-ca-powertoys --help
```

## Usage
All available commands and options can be seen by using the `--help` option.
```console
> ca-pwt --help
```

To get help on a specific command, use the `--help` option with the command name. For example, to get help on the `export-policies` command, use the following command:
```console
> ca-pwt export-policies --help
```

CA-PowerToys is based on [Click](https://github.com/pallets/click/), taking advantage of its features, such as chaining commands and options. As an example, several commands can be chained to achieve a specific goal, such as exporting policies, cleaning them up for import, replacing guids with attributes, and importing them back to the tenant. Further examples are provided below.

### Usage Examples

#### Obtaining an access token 

There are several ways to obtain an access token. The easiest is to use `acquire-token` in chain with other commands and login interactively. In the example below, the token obtained will be injected in the subsequent command to export the policies. 

```console
> ca-pwt acquire-token export-policies --output_file policies.json
```
```
Exporting conditional access policies...
Obtaining policies from tenant...
Writing policies to file policies.json...
```
##### Store it in a variable to be used in subsequent commands
You can also obtain an access token and store it in a variable to be used in subsequent commands. In this case, you need to instruct the command to output the token using the `--output_token` option. 

(pwsh)
```console
> $token = (ca-pwt acquire-token --output_token)
> ca-pwt --access_token $token export-policies --output_file policies.json
```
(bash)
```console
> token = $(ca-pwt acquire-token --output_token)
> ca-pwt --access_token $token export-policies --output_file policies.json
```
```
Exporting conditional access policies...
Obtaining policies from tenant...
Writing policies to file policies.json...
```
If you are in an endpoint where you can't use the interactive login, you can use `acquire-token` command with `--client_id` and `--client_secret` options, or, alternatively, using device flow, through the `--device_code` option. 
```console
> $token = (ca-pwt acquire-token --device_code --output_token)
To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code 123456789 to authenticate.
```

##### Using the tool in a CI/CD pipeline
If you are using the tool in a CI/CD pipeline, CA-PowerToys supports authentication through a service principal, using the `--client_id` and `--client_secret` options. In this case, you need to instruct the command to output the token using the `--output_token` option. You should also use the `--tenant_id` option to specify the tenant where the service principal was created.
```console
> $token = (ca-pwt acquire-token --client_id $client_id --client_secret $client_secret --tenant_id $tenant_id --output_token)
> ca-pwt --access_token $token import-policies --input_file policies.json --duplicate_action overwrite
```


#### Exporting policies
    
```console
> ca-pwt --access_token $token export-policies --output_file policies.json
```
```
Exporting conditional access policies...
Obtaining policies from tenant...
Writing policies to file policies.json...
```

You can also define oData filters to export only a subset of the policies. In the example below, we export only the policies that have the word "Global" in the DisplayName. 

```console
> ca-pwt --access_token $token export-policies --output_file policies.json --filter "startswith(displayName,'Global')"
```
```
Exporting conditional access policies...
Obtaining policies from tenant...
Writing policies to file policies.json...
```

#### Exporting all Policies and associated Groups

```console
> ca-pwt --access_token $token export-policies --output_file policies.json export-policy-groups --output_file groups.json
```
```
Exporting ca policies...
Output file: policies.json
Exporting groups found in CA policies...
Input file: policies.json; Output file: groups.json; Lookup cache file: None
```

#### Exporting all Policies and associated Groups, replace guids with human-readable attributes in the policies file and make the file ready for import

```console
> ca-pwt --access_token $token export-policies --output_file policies.json cleanup-policies replace-guids-with-attrs export-policy-groups --output_file groups.json cleanup-groups
```
```
Exporting ca policies...
Output file: policies.json
Cleaning up CA policies for import...
Input file: policies.json; Output file: policies.json
Replacing guids with attributes in CA policies...
Input file: policies.json; Output file: policies.json
Exporting groups found in CA policies...
Input file: policies.json; Output file: groups.json
Cleaning up groups for import...
Input file: groups.json; Output file: groups.json
```
#### Importing groups and policies

```console
> ca-pwt --access_token $token import-groups --input_file groups.json import-policies --input_file .\policies-humanreadable.json
```
```
Importing groups...
Input file: groups.json
Successfully created groups:
97d90185-6aef-4b84-9051-ed92c3b023a1: CA-Test-Group
Importing CA policies...
Input file: policies-humanreadable.json; Lookup cache file:
Successfully created policies:
896d7a7f-8300-4537-8d39-287b25f7259c: CA-Test-Policy
```

#### Using CA-PowerToys to export policies and import them using Graph PowerShell

You can use CA-PowerToys to export policies in a compatible format with Graph PowerShell. This is useful if you want to export policies from one tenant and import them into another tenant and use Graph PowerShell to import them (you can also use CA-PowerToys to import them, using the `import-policies` command).

This example chains the `export-policies` and `cleanup-policies` commands to export the policies and clean them up for import. The output is stored in the policies.json file. Then we read the policies from the file and import them using the New-MgIdentityConditionalAccessPolicy command. 

```console
> ca-pwt --access_token $token export-policies --output_file policies.json cleanup-policies
```
```
Exporting conditional access policies...
Obtaining policies from tenant...
Writing policies to file policies.json...
Cleaning up conditional access policies for import...
Reading policies from file policies.json...
Cleaning up policies...
Writing policies to file policies.json...
```
```powershell
>  $policy = Get-Content -Path .\policies.json | ConvertFrom-Json -AsHashtable
>  $policy.count
2
>  New-MgIdentityConditionalAccessPolicy -BodyParameter $policy[0]
```
```

Id                                   CreatedDateTime     Description DisplayName
--                                   ---------------     ----------- -----------
7b385aec-569a-470a-980b-8624bfa6332c 14/10/2023 07:52:54             CA001-Global-BaseProtection-All…
```
Note: In the above example, a token was previously obtained using the `acquire-token` and stored in the `$token` variable.

## FAQ
### If I prefer to create a service principal to execute CA-PowerToys, what permissions are needed?
It depends on the commands you may need to run. Please keep in mind that by creating a SP with some of these permissions, this will allow anyone with the SP credentials to change CA policies and add groups to your tenant. **Make sure you understand the implications of doing it.**
In a very controlled lab environment, and to run all the available commands, you may create a SP with the following permissions:
![image](https://go.hugobatista.com/gh/zerotrust-ca-powertoys/assets/64972114/d3b887b0-388d-42d8-b352-0c08608874dc)

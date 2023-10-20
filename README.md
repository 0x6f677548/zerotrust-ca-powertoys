# Conditional Access PowerToys (CA-PowerToys)
CA-PowerToys is a set of tools to help you manage Conditional Access policies in your tenant. It is a command line tool that can be used to export, import, and clean up Conditional Access policies. It can also be used to export groups that are used in Conditional Access policies and import them into another tenant.

# Capabilities
CA-PowerToys can be used to:
- **Get an access token** to be used in subsequent commands or to be used in other tools, such as Graph PowerShell, using a desired client_id (useful if Graph PowerShell or other tools are blocked in the target tenant)
- **Export/Import Conditional Access policies** to/from a file
- **Export groups** that are used in Conditional Access policies to a file
- **Clean up Conditional Access policies for import**, removing keys that are not allowed in the import process
- **Replace keys by values in Conditional Access policies**, for example, replace the Id of a group by its name
- **Clean up groups for import**, removing keys that are not allowed in the import process

# Why ?
There are several tools to manage Conditional Access policies, such as Graph PowerShell, Microsoft Graph API, Azure AD PowerShell and even M365DSC. Unfortunately, none of these tools can be used to export Conditional Access policies in a format that can be human readable and editable, and then import them back to another tenant. This is where CA-PowerToys can help you, with several commands that can be chained to export, clean up, replace keys by values, and import Conditional Access policies and groups.  

Here are a couple of examples of how CA-PowerToys can help you:
- Export Conditional Access policies from one tenant and import them into another tenant using Graph PowerShell
- Export Conditional Access policies and groups from one tenant and store them in a Git repository. Then, use a CI/CD pipeline to import them into another tenant using Graph PowerShell or CA-PowerToys


# Installation

# Usage
CA-PowerToys is a command line tool that can be used in Windows, Linux, and MacOS. It is written in Python and can be used as a module or as a standalone tool. Since it uses Click, it is self-documented and you can use the `--help` option to get help on the commands and options.
```cmd
> python -m src.ca_pwt --help
```

To get help on a specific command, use the `--help` option with the command name. For example, to get help on the `export-policies` command, use the following command:
```cmd
> python -m src.ca_pwt export-policies --help
```

## Usage Examples

### Obtaining an access token 

There are several ways to obtain an access token. The easiest is to use `get-access-token` in chain with other commands and login interactively. In the example below, the token obtained will be injected in the subsequent command to export the policies. 

```cmd
> python -m src.ca_pwt get-access-token export-policies --output_file policies.json
```
```
Exporting conditional access policies...
Obtaining policies from tenant...
Writing policies to file policies.json...
```
#### Store it in a variable to be used in subsequent commands
You can also obtain an access token and store it in a variable to be used in subsequent commands. In this case, you need to instruct the command to output the token using the `--output_token` option. 
   
```cmd
> $token = (python -m src.ca_pwt get-access-token --output_token)
> python -m src.ca_pwt --access_token $token export-policies --output_file policies.json
```
```
Exporting conditional access policies...
Obtaining policies from tenant...
Writing policies to file policies.json...
```
If you are in an endpoint where you can't use the interactive login, you can use `get-access-token` command with `--client_id` and `--client_secret` options, or, alternatively, using device flow, through the `--device_code` option. 
```cmd
> $token = (python -m src.ca_pwt get-access-token --device_code --output_token)
To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code 123456789 to authenticate.
```

### Exporting policies
    
```cmd
> python -m src.ca_pwt --access_token $token export-policies --output_file policies.json
```
```
Exporting conditional access policies...
Obtaining policies from tenant...
Writing policies to file policies.json...
```

You can also define oData filters to export only a subset of the policies. In the example below, we export only the policies that have the word "Global" in the DisplayName. 

```cmd
> python -m src.ca_pwt --access_token $token export-policies --output_file policies.json --filter "startswith(displayName,'Global')"
```
```
Exporting conditional access policies...
Obtaining policies from tenant...
Writing policies to file policies.json...
```

### Exporting all Policies and associated Groups, replace keys with values in the policies file and cleanup for import
    
```
> python -m src.ca_pwt --access_token $token export-policies --output_file policies.json cleanup-policies replace-keys-by-values export-groups --output_file groups.json cleanup-groups
```
```
Exporting ca policies...
Output file: policies.json
Cleaning up CA policies for import...
Input file: policies.json; Output file: policies.json
Replacing keys by values in CA policies...
Input file: policies.json; Output file: policies.json
Exporting groups found in CA policies...
Input file: policies.json; Output file: groups.json
Cleaning up groups for import...
Input file: groups.json; Output file: groups.json
```

### Using CA-PowerToys to export policies and import them using Graph PowerShell

You can use CA-PowerToys to export policies in a compatible format with Graph PowerShell. This is useful if you want to export policies from one tenant and import them into another tenant and use Graph PowerShell to import them (you can also use CA-PowerToys to import them, using the `import-policies` command).

This example chains the `export-policies` and `cleanup-policies` commands to export the policies and clean them up for import. The output is stored in the policies.json file. Then we read the policies from the file and import them using the New-MgIdentityConditionalAccessPolicy command. 

```powershell
> python -m src.ca_pwt --access_token $token export-policies --output_file policies.json cleanup-policies
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
Note: In the above example, a token was previously obtained using the `get-access-token` and stored in the `$token` variable.

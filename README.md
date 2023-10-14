# EntraID-Tools

## Usage Examples

### Obtaining an access token 

and store it in a variable to be used in subsequent commands

There are several ways to obtain an access token. The easiest is to use `get-access-token` in chain with other commands and login interactively. In the example below, the token obtained will be injected in the subsequent command to export the policies. 

```cmd
> python . get-access-token ca-export --output_file policies.json
Exporting conditional access policies...
Obtaining policies from tenant...
Writing policies to file policies.json...
```

You can also obtain an access token and store it in a variable to be used in subsequent commands. In this case, you need to instruct the command to output the token using the `--output_token` option. 
   
```cmd
> $token = (python . get-access-token --output_token)
> python . --access_token $token ca-export --output_file policies.json
Exporting conditional access policies...
Obtaining policies from tenant...
Writing policies to file policies.json...
```
If you are in an endpoint where you can't use the interactive login, you can use `get-access-token` command with `--client_id` and `--client_secret` options, or, alternatively, using device flow, through the `--device_code` option. 
```cmd
> $token = (python . get-access-token --device_code --output_token)
To sign in, use a web browser to open the page https://microsoft.com/devicelogin and enter the code 123456789 to authenticate.
```


### Using EntraID-Tools to export policies and import them using Graph PowerShell

You can use EntraID-Tools to export policies in a compatible format with Graph PowerShell. This is useful if you want to export policies from one tenant and import them into another tenant. 

This example chains the ca-export and ca-cleanup-for-import commands to export the policies and clean them up for import. The output is stored in the policies.json file. Then we read the policies from the file and import them using the New-MgIdentityConditionalAccessPolicy command. 

```powershell
> python . --access_token $token ca-export --output_file policies.json ca-cleanup-for-import
Exporting conditional access policies...
Obtaining policies from tenant...
Writing policies to file policies.json...
Cleaning up conditional access policies for import...
Reading policies from file policies.json...
Cleaning up policies...
Writing policies to file policies.json...
>  $policy = Get-Content -Path .\policies.json | ConvertFrom-Json -AsHashtable
>  $policy.count
2
>  New-MgIdentityConditionalAccessPolicy -BodyParameter $policy[0]

Id                                   CreatedDateTime     Description DisplayName
--                                   ---------------     ----------- -----------
7b385aec-569a-470a-980b-8624bfa6332c 14/10/2023 07:52:54             CA001-Global-BaseProtection-All…
```

Note: In the above example, a token was previously obtained using the get-access-token and stored in the $token variable.
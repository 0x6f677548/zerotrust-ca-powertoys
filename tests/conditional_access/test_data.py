policies: dict = [
    {
        "id": "88ef8435-6ab4-42c5-8e8d-e5dc2d1d66a9",
        "displayName": "TEST-POLICY",
        "createdDateTime": "2023-08-17T23:13:20.9225868Z",
        "modifiedDateTime": "2023-10-10T13:35:17.0858965Z",
        "state": "disabled",
        "conditions": {
            "userRiskLevels": [],
            "signInRiskLevels": [],
            "clientAppTypes": ["all"],
            "servicePrincipalRiskLevels": [],
            "applications": {
                "includeApplications": ["All"],
                "excludeApplications": [],
                "includeUserActions": [],
                "includeAuthenticationContextClassReferences": [],
            },
            "users": {
                "includeUsers": ["All"],
                "excludeUsers": [],
                "includeGroups": [],
                "excludeGroups": [
                    "9ae4a47f-c5e0-4d45-9948-8122a9b4e223",
                    "9cd8fcf0-8e52-4197-84fb-4d6a7e652c8e",
                    "d6660988-6fbb-44d8-8a36-5a21cf112a3b",
                    "d2118482-ca23-4d10-bb9d-9f42feba81e0",
                    "50eff093-29c4-4157-830f-5dba69e311f8",
                    "3e9053c7-8578-45ea-bc88-8ff343b5b32d",
                    "289d62fc-bd54-42c4-93f7-cd90f7652eef",
                    "70e962c3-5653-4359-b568-8316aa47d2ef",
                    "c04acbbf-53e5-4fbb-bf21-a607253d37a3",
                    "47eec19a-ec26-4e26-9924-a538d2c33e9d",
                ],
                "includeRoles": [],
                "excludeRoles": [],
            },
            "platforms": {"includePlatforms": ["all"], "excludePlatforms": []},
        },
        "grantControls": {
            "operator": "OR",
            "builtInControls": ["block"],
            "customAuthenticationFactors": [],
            "termsOfUse": [],
            "authenticationStrength@odata.context": "https://graph.microsoft.com/v1.0/$metadata#identity/conditionalAccess/policies('88ef8435-6ab4-42c5-8e8d-e5dc2d1d66a9')/grantControls/authenticationStrength/$entity",
        },
    }
]

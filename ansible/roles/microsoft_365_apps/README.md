# microsoft_365_apps

Installs Microsoft 365 Apps for enterprise with Microsoft's
[Office Deployment Tool](https://learn.microsoft.com/en-us/microsoft-365-apps/deploy/overview-office-deployment-tool).
The role verifies the ODT publisher signature, generates a non-secret
configuration, installs from the Microsoft CDN, and validates Click-to-Run
registration.

The default installation is 64-bit `O365ProPlusRetail`, English (`en-us`),
on the Monthly Enterprise Channel. An already matching installation is left
unchanged. If another MSI or Click-to-Run Office product is present, validation
stops before mutation.

## Variables

- `microsoft_365_apps_enabled` (default `true`)
- `microsoft_365_apps_product_id` (fixed to `O365ProPlusRetail`)
- `microsoft_365_apps_edition` (fixed to `64`)
- `microsoft_365_apps_channel` (`Current`, `MonthlyEnterprise`,
  `SemiAnnualEnterprise`, or `SemiAnnualEnterprisePreview`)
- `microsoft_365_apps_language` (default `en-us`)
- `microsoft_365_apps_odt_url` (Microsoft Office CDN)

Run installation with Internet access. For optional Office tests, the operator
assigns a qualifying user license, signs in, and activates Office after deployment.

# hybrid_identity_host_prep

Prepares the deterministic local software prerequisites for the compact
Microsoft Entra Connect Sync server.

The role:

- installs the Windows .NET Framework feature and handles its required reboot;
- explicitly enables TLS 1.2 for Schannel and .NET, rebooting when changed;
- allows signed PowerShell scripts when the effective policy is `Restricted`;
- optionally stages an operator-downloaded `AzureADConnect.msi` from the
  protected controller directory and verifies its Microsoft signature.

The operator owns current Connect support and capacity choices, the Connect
custom wizard, and MDI commissioning. Connect custom setup supplies SQL
LocalDB and its supporting components.

## Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `hybrid_identity_host_prep_enabled` | `true` | Apply local software preparation |
| `hybrid_identity_host_prep_connect_installer_controller_path` | Protected Source-sibling path | Optional operator-supplied MSI |
| `hybrid_identity_host_prep_connect_installer_guest_path` | `C:\ludus\AzureADConnect.msi` | Verified guest staging path |

An absent MSI is a visible skip rather than a local deployment failure.

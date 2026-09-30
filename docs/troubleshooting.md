# Troubleshooting

## DC01 has no MDE telemetry after onboarding

Use the Microsoft-provided identity reset for the SENSE Event 406 authentication
failure observed after onboarding. This creates a new MDE identity for DC01.

1. Download the Windows Server offboarding package from Defender **Settings >
   Endpoints > Device management > Offboarding**.
2. In **Azure Arc > Machines > DC01 > Extensions**, remove `MDE.Windows`.
   On DC01, run the offboarding script as administrator. In elevated PowerShell,
   confirm `Sense` reports **Stopped** before clearing its identity:

   ```powershell
   Get-Service Sense
   ```

3. Download [PsExec](https://learn.microsoft.com/en-us/sysinternals/downloads/psexec)
   on DC01. Open Command Prompt as administrator in its directory and start a
   SYSTEM shell:

   ```cmd
   PsExec.exe -s cmd.exe
   ```

4. In that SYSTEM shell, clear the Cyber-directory files and these three MDE
   registry values. The deletion uses the full directory path:

   ```cmd
   del "C:\ProgramData\Microsoft\Windows Defender Advanced Threat Protection\Cyber\*.*" /f /s /q
   REG DELETE "HKLM\SOFTWARE\Microsoft\Windows Advanced Threat Protection" /v senseGuid /f
   REG DELETE "HKLM\SOFTWARE\Microsoft\Windows Advanced Threat Protection" /v 7DC0B629-D7F6-4DB3-9BF7-64D5AAF50F1A /f
   REG DELETE "HKLM\SOFTWARE\Microsoft\Windows Advanced Threat Protection\48A68F11-7A16-4180-B32C-7F974C7BD783" /v 7DC0B629-D7F6-4DB3-9BF7-64D5AAF50F1A /f
   exit
   ```

5. Reboot DC01 and keep it online. With Defender for Servers Plan 1 and Endpoint
   protection enabled, allow Defender for Cloud to redeploy `MDE.Windows`.
6. Confirm the extension is installed, `Sense` is Running, and DC01 has recent
   **Timeline** activity in Defender **Assets > Devices**. Resume the runbook.

## DC01 is missing from MDI v3

1. Keep Testing Mode off and complete Windows updates and reboots:

   ```bash
   ludus -r <RANGE_ID> testing update -n mde_targets
   ```

2. Confirm recent MDE Timeline activity on DC01. The required cumulative update
   is July 2026 or later.
3. Allow time for discovery, then activate DC01 in **Defender > Settings >
   Identities > On-premises > Sensor management**.
4. Complete the auditing/action-account settings in your runbook and wait for
   DC01 to become **Healthy**. DC01 is the first v3 sensor in the range.

## CA01 or SYNC01 is missing from MDI v3

1. Complete Windows updates and reboots on the server, using your runbook's
   `testing update -n mde_targets` command.
2. Confirm recent MDE Timeline activity and a **Healthy** DC01 v3 sensor.
3. Give discovery ample time: SYNC01 took until the next day in a successful
   deployment. CA01 and SYNC01 can appear later than DC01.
4. When the server appears in **Sensor management**, activate it.

## Defender combines identities from repeated lab deployments

Repeatedly deploying a new AD forest with the same domain name, usernames, and
UPNs can leave historical domains and accounts in the Defender tenant. Defender
can aggregate accounts from different forest instances into one `StrongId`
account set. Destroying the range does not immediately remove this cloud identity
history.

Symptoms can include:

- duplicate domain or identity search results with different SIDs;
- an identity summary showing an old SID while the current SID appears under
  **Observed in organization > Accounts**;
- a current account missing from a Defender selector, such as **User automation
  exclusions**; or
- individual `StrongId` accounts being unavailable for manual unlinking.

1. Compare the domain SID and account SID to identify the current deployment.
2. If Defender aggregated the current account with historical accounts, create a
   uniquely named AD account for any testing or portal action that must target
   the current deployment.

## I get no PRT after signing in

1. Complete Entra Connect setup in your runbook. In Entra **Entra ID > Users**
   and **Devices**, confirm the user and workstation have synchronized.
2. Sign in to Windows with that user's verified UPN and current AD password.
   Fully sign out, then sign back in. Disconnecting RDP keeps the old session open.
3. In the user's non-elevated session, run `dsregcmd /status`. Confirm
   `DomainJoined : YES`, `AzureAdJoined : YES`, and `AzureAdPrt : YES`.

<details>
<summary>Deeper hybrid-join verification</summary>

- Check the [tenant ID and domain](#i-forgot-to-set-the-tenant-id-and-domain-in-the-range-configuration).
- On DC01, run `Get-ADComputer WKS01 -Properties userCertificate` to inspect the
  registration certificate; use WKS02 for the other Complete workstation.
- In **Task Scheduler**, run **Microsoft\Windows\Workplace Join > Automatic-Device-Join** on the
  workstation for another registration attempt. Inspect **User Device
  Registration > Admin** events for a failed attempt.
- On SYNC01, `Start-ADSyncSyncCycle -PolicyType Initial` requests another full
  sync cycle. The workstation's certificate and Devices OU selection govern
  device export.
- Compare local `DeviceId` with the Entra record's **Device ID** to distinguish
  same-named devices. For `error_missing_device`, retry registration after export.

See [Microsoft's hybrid-join verification guidance](https://learn.microsoft.com/en-us/entra/identity/devices/how-to-hybrid-join-verify).

</details>

## I forgot to copy the onboarding files to the Ludus host

1. Place the missing file in the protected directory: use
   [Arc script setup](getting-started.md#stage-the-arc-script), or WKS02 setup
   in [Client MDE](labs/client-mde.md#stage-wks02-onboarding),
   [Standard](labs/standard.md#stage-wks02-onboarding), or
   [Complete](labs/complete.md#stage-wks02-onboarding).
2. Rerun the onboarding role for the affected VM, using its `vm_name` from the
   range configuration. For Arc servers:

   ```bash
   ludus -r <RANGE_ID> range deploy -t user-defined-roles \
     -l <SERVER_VM_NAME> --only-roles 5tuk0v.azure_arc_onboard
   ```

   For WKS02 client MDE:

   ```bash
   ludus -r <RANGE_ID> range deploy -t user-defined-roles \
     -l <WKS02_VM_NAME> --only-roles 5tuk0v.mde_client_onboard
   ```

3. Resume your runbook's cloud commissioning after the role succeeds.

## I forgot to set the sign-in domain in the range configuration

`hybrid_identity_upn_suffix` sets the domain after `@` in the test users' UPNs.

1. Copy a verified domain from **Entra ID > Domain names**.
2. Run `ludus -r <RANGE_ID> range config edit` and set
   `hybrid_identity_upn_suffix` under DC01's `role_vars`.
3. On the deployed DC01, add that domain in **Active Directory Domains and
   Trusts > Properties > Alternative UPN suffixes**. In **Active Directory
   Users and Computers > EntraSync > Users**, set each test user's suffix under
   **Properties > Account**.
4. Continue Connect setup in your runbook. For an already synchronized user,
   allow the next sync and use the UPN shown in Entra to sign in.

## I forgot to set the tenant ID and domain in the range configuration

These values tell the workstation which Entra tenant to register with.

1. Copy the GUID from **Entra ID > Overview > Properties > Tenant ID** and a
   verified domain from **Entra ID > Domain names**.
2. Run `ludus -r <RANGE_ID> range config edit` and set `hybrid_join_tenant_id`
   and `hybrid_join_tenant_name` under WKS01's `role_vars`; also set WKS02's
   values for Complete.
3. Apply those same values to the deployed workstation in elevated PowerShell:

   ```powershell
   $discoveryPath = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CDJ\AAD'
   New-Item -Path $discoveryPath -Force | Out-Null
   New-ItemProperty -Path $discoveryPath -Name TenantId -Value '<tenant-guid>' -PropertyType String -Force | Out-Null
   New-ItemProperty -Path $discoveryPath -Name TenantName -Value '<verified-domain>' -PropertyType String -Force | Out-Null
   ```

4. Resume your runbook's workstation sign-in and PRT check.

## I forgot to copy the Entra Connect installer before deployment

On SYNC01, open [Entra admin center](https://entra.microsoft.com) and select
**Microsoft Entra Connect > Get started > Manage**. Download the latest
`AzureADConnect.msi`, run it as administrator, and follow your runbook's Connect
wizard settings.

## Testing Mode will not stop and Proxmox shows an EFI certificate warning

Proxmox shows this warning for the VM's EFI disk. An older snapshot can restore
previous EFI state. Enroll updated certificates on the affected Windows 11 VM:

1. Shut down the affected VM.
2. Select **Hardware > EFI disk > Disk Action > Enroll Updated Certificates**.
3. Start the VM, then retry stopping Testing Mode:

   ```bash
   ludus -r <RANGE_ID> testing stop
   ```

4. Enroll updated certificates on the restored VM before starting Testing Mode
   again, so the next snapshot includes the updated EFI state.

For BitLocker-protected disks, suspend protection before enrollment and resume
it after boot.

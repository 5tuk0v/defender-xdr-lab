# Hybrid join

> Current version: **0.2.2** · Last tested version: **0.2.0**.

The 0.2.0 run demonstrated WKS01 hybrid join and a synchronized user's PRT.
MDI health was not rechecked in that run.

This scenario combines Entra Connect Sync, Password Hash Sync (PHS), targeted
Microsoft Entra hybrid join, and Primary Refresh Token (PRT) sign-in.

Since 0.2.0, DC01 gained Server 2022 ASR Audit and the diagnostic-only state
report was removed. `complete` 0.1.3 exercised the shared DC01 role path; this
blueprint version has not been deployed.

## What it builds

See [host configuration](../host-configuration.md#hybrid-join) for
automated settings and purpose.

| Host | Resources | Purpose |
| --- | --- | --- |
| DC01 | 2 vCPU, 6 GB RAM | `defender.test` domain controller and scoped users and groups, ASR Audit |
| SYNC01 | 2 vCPU, 6 GB RAM | Entra Connect Sync, PHS, and Defender services |
| WKS01 | 2 vCPU, 4 GB RAM | Windows 11 25H2, Microsoft 365 Apps, targeted hybrid join |

WKS01 is the client without MDE. Office sign-in is an optional SSO exercise.

## 1. Preparation

Complete [common preparation](../getting-started.md), then prepare the items below.

- Confirm `win2022-server-x64-template` and
  `win11-25h2-x64-enterprise-template` are available. Use the stock Windows 11
  25H2 non-TPM template.
- Reserve 2 vCPU and 6 GB RAM for each server and 2 vCPU and 4 GB RAM for
  WKS01 (6 vCPU and 16 GB total), plus router, host, template-storage, and
  snapshot capacity.
- Use Entra Connect Sync 2.5.79.0 or later. See Microsoft's
  [minimum-version notice](https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/security-updates-pks).

### Collect tenant values

1. In Entra **Entra ID > Domain names**, copy a verified sign-in domain for
   `hybrid_identity_upn_suffix`. The listed `onmicrosoft.com` domain is suitable.
2. Copy the GUID from **Entra ID > Overview > Properties > Tenant ID** for
   `hybrid_join_tenant_id`. Use an exact verified domain from **Domain names**
   for `hybrid_join_tenant_name`.

Use `ludus_ssh_target` and `protected_dir` from common preparation for the
file-transfer and installation commands below.

### Stage the Connect installer

In [Entra admin center](https://entra.microsoft.com), open **Microsoft Entra
Connect > Get started > Manage** and download the latest `AzureADConnect.msi`.

1. Transfer the MSI from the download machine:

   ```bash
   connect_msi='/absolute/path/to/AzureADConnect.msi'
   scp -- "$connect_msi" "${ludus_ssh_target}:/tmp/AzureADConnect.msi"
   ```

2. On the Ludus host, install it in the same protected directory:

   ```bash
   sudo install -o ludus -g ludus -m 600 /tmp/AzureADConnect.msi "$protected_dir/AzureADConnect.msi"
   sudo test -s "$protected_dir/AzureADConnect.msi"
   sudo stat -c '%U %G %a %n' "$protected_dir/AzureADConnect.msi"
   ```

3. After the file check succeeds and shows `ludus ludus 600`, remove the
   temporary copy with `sudo rm -- /tmp/AzureADConnect.msi`.
   The role stages the installer at `C:\ludus\AzureADConnect.msi` on SYNC01.

## 2. Deployment

### Apply and review

1. Select an existing target range, or [create one](https://docs.ludus.cloud/docs/using-ludus/blueprints/#applying-a-blueprint)
   first. Applying a blueprint replaces its configuration; use that range ID
   in every command.
2. Apply the blueprint and display the configuration:

   ```bash
   ludus blueprint apply defender-xdr-lab/hybrid-join \
     --target-range <RANGE_ID>
   ludus -r <RANGE_ID> range config get
   ```

3. Edit and save the tenant values under the indicated hosts' `role_vars`:

   ```bash
   ludus -r <RANGE_ID> range config edit
   ludus -r <RANGE_ID> range config get
   ```

   - DC01: set `hybrid_identity_upn_suffix` to the copied verified sign-in domain.
   - WKS01: set `hybrid_join_tenant_id` and
     `hybrid_join_tenant_name` to the copied tenant GUID and domain.

4. Review the hosts, templates, and resources against **What it builds** above.
   Confirm `mde_targets` contains DC01 and SYNC01.
   Confirm `hybrid_identity_scope_computers` contains WKS01.

### Deploy

1. Deploy and follow progress:

   ```bash
   ludus -r <RANGE_ID> range deploy
   ludus -r <RANGE_ID> range logs -f
   ```

2. Confirm the final recap has zero failed or unreachable hosts. This completes
   automated local provisioning; post-deployment commissioning follows.

## 3. Post-deployment

### Enroll updated UEFI certificates

Complete this before the first Testing Mode snapshot. For BitLocker-protected
clients, have the recovery key available and suspend protection before enrollment;
resume it after boot.

1. Shut down WKS01.
2. In Proxmox, select each client's **Hardware > EFI disk > Disk Action >
   Enroll Updated Certificates**.
3. Boot WKS01 and confirm the Microsoft UEFI 2023 certificate warning
   (`ms-cert=2023k`) has cleared in Proxmox.

For a failed Testing Mode stop or an older snapshot, use
[UEFI troubleshooting](../troubleshooting.md#testing-mode-will-not-stop-and-proxmox-shows-an-efi-certificate-warning).

### Configure Entra Connect

> [!WARNING]
> **The test-user passwords are public.** Keep Connect in staging until both
> users have unique passwords; PHS makes their AD passwords cloud sign-in
> credentials. Reapplying the directory-population role can restore the public
> passwords: reset them again before resuming synchronization.

1. On SYNC01, run the staged Microsoft-signed `C:\ludus\AzureADConnect.msi`
   as administrator. Select [**Customize**](https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/how-to-connect-install-custom).
2. Set the wizard choices:
   - retain defaults unless a choice is listed below;
   - select **Password Hash Synchronization**;
   - sign in with a tenant-local **Hybrid Identity Administrator**;
   - add `defender.test`, choose **Create new account**, and temporarily provide
     AD DS **Enterprise Administrator** credentials;
   - keep `userPrincipalName` and confirm both users have the verified suffix;
   - select only `OU=EntraSync,DC=defender,DC=test` and its children, including **Devices**;
   - filter by `CN=Entra Sync Scope,OU=Groups,OU=EntraSync,DC=defender,DC=test`;
   - on **Optional features**, keep PHS selected and leave writeback,
     **Exchange hybrid deployment**, and **Directory extension attribute sync** clear;
   - enable **Staging mode** and initial synchronization, then finish setup.
3. On DC01, use **Active Directory Users and Computers > EntraSync > Users** to
   reset both public test-user passwords to unique lab passwords. Leave
   **User must change password at next logon** unchecked.
4. On SYNC01, reopen **Microsoft Entra Connect > Configure > Configure staging
   mode**, authenticate, clear **Enable staging mode**, and select **Next**.
   Select **Start the synchronization process** and **Configure**.

### Verify synchronization and user sign-in

In Entra **Entra ID > Users** and **Groups**, confirm `sync.alice`,
`sync.bob`, and `Hybrid Lab Users` appear after synchronization.

1. In Entra **Users**, open `sync.alice` or `sync.bob` and copy its **User
   principal name**.
2. Open [Microsoft My Account](https://myaccount.microsoft.com) in a private
   browser window. Sign in with that UPN and the user's current AD password.
3. Confirm the account page opens for that user. This completes the browser
   sign-in check for Password Hash Sync.

### Confirm WKS01 hybrid join and PRT

1. After sync completes, sign in to WKS01 as Bob with his verified UPN and
   current AD password. Sign out, then sign back in.
2. From Bob's non-elevated session, run `dsregcmd /status`. Confirm
   `DomainJoined : YES`, `AzureAdJoined : YES`, and `AzureAdPrt : YES`.

3. In Entra **Entra ID > Devices**, confirm WKS01 appears.

For failed join or PRT, use
[registration troubleshooting](../troubleshooting.md#i-get-no-prt-after-signing-in).

### Confirm Arc and MDE onboarding

1. In **Azure Arc > Machines**, confirm DC01 and SYNC01 are **Connected** and
   each has `MDE.Windows` under **Extensions**.
2. In Defender **Assets > Devices**, open DC01 and SYNC01 and confirm recent
   **Timeline** activity on each host.

For DC01 telemetry failure after onboarding, use
[DC01 telemetry troubleshooting](../troubleshooting.md#dc01-has-no-mde-telemetry-after-onboarding).

### Update the MDE hosts

1. Keep Testing Mode off and update the blueprint's `mde_targets` group before
   MDI activation and the first Testing Mode snapshot:

   ```bash
   ludus -r <RANGE_ID> testing update -n mde_targets
   ```

2. Allow all reboots to finish and confirm successful command completion. This
   is the servicing gate for MDI v3's July 2026 or later cumulative update.

### Activate DC01 MDI v3

After the MDE host update succeeds:

1. In Defender **Settings > Identities > On-premises > Sensor management**,
   select the current DC01 when eligible and [activate its sensor](https://learn.microsoft.com/en-us/defender-for-identity/deploy/activate-sensor).
2. In **Settings > Identities > General > Advanced features**, enable
   **Automatic Windows auditing configuration**.
3. In **Settings > Identities > Microsoft Defender for Identity > Manage action
   accounts**, enable **Automatically use the sensor's local system account for
   all sensors**.
4. In **Sensor management**, wait for DC01 to report **Healthy**.

For missing eligibility or failed activation/auditing, use
[MDI troubleshooting](../troubleshooting.md#dc01-is-missing-from-mdi-v3).

### Activate SYNC01 MDI v3

After Connect setup, host servicing, and Healthy DC01:

1. In Defender **Settings > Identities > On-premises > Sensor management**,
   select the current SYNC01 Entra Connect row when eligible and choose **Activate**.
2. Wait for SYNC01 to report **Healthy**. The DC01 steps above configure
   auditing and LocalSystem action accounts for the workspace.

For missing eligibility, use
[MDI troubleshooting](../troubleshooting.md#ca01-or-sync01-is-missing-from-mdi-v3).

### Remove onboarding credentials

1. After the servers are connected, remove the Arc script on the Ludus host:

   ```bash
   sudo rm -- "$protected_dir/OnboardingScript.ps1"
   ```

2. In Entra **Enterprise applications**, delete the temporary Arc onboarding
   service principal by its chosen name. Remove its deployment-specific Azure
   role assignment if it remains.

### Acceptance

The results above confirm:

- Successful recap: local deployment completed.
- Two pilot users, `Hybrid Lab Users`, and WKS01 visible in Entra.
- Successful pilot-user My Account sign-in with its current AD password.
- `DomainJoined`, `AzureAdJoined`, and `AzureAdPrt` are `YES` in Bob's WKS01
  session.
- DC01 and SYNC01 Connected in Arc, with recent MDE Timeline activity and
  Healthy MDI v3 sensors: cloud commissioning completed.

## 4. Cleanup

Select the lab range, Azure resource group, and tenant used for this deployment.

### Retire Entra Connect

Keep DC01, SYNC01, and WKS01 running until Entra deletion sync is verified.

1. Remove any lab-user license assignments.
2. On DC01, open **Active Directory Users and Computers > EntraSync** and
   delete `sync.alice`, `sync.bob`, `Hybrid Lab Users`, and WKS01's computer object.
   Keep `Entra Sync Scope` and Connect until sync completes. Reapplying
   directory population during cleanup can recreate these objects.
3. On SYNC01, with Connect active and out of staging, run:

   ```powershell
   Start-ADSyncSyncCycle -PolicyType Delta
   ```

4. In Entra **Users**, **Groups**, and **Devices**, confirm those objects are no longer active.
   Deleted users may remain in retention.
   In **Devices**, delete any remaining lab entries for WKS01.
5. Shut down WKS01 after deletion sync.
6. On SYNC01, open **Control Panel > Uninstall a program > Microsoft Entra
   Connect** and select **Remove** in the uninstaller.
7. Remove the protected Connect MSI from the Ludus host:

   ```bash
   sudo rm -- "$protected_dir/AzureADConnect.msi"
   ```

8. After uninstalling Connect, remove old `ConnectSyncProvisioning` app
   registrations and corresponding **Enterprise applications** from the test tenant.

### Retire the deployment resources

1. Verify the exact range and VMs, then destroy the range:

   ```bash
   ludus -r <RANGE_ID> range rm
   ```

2. In Azure **Resource groups**, delete the lab's resource group and confirm its
   name. This removes its Arc machines and extensions.
3. In Defender **Sensor management**, remove the disconnected DC01 and SYNC01 MDI sensors.
4. In Entra **App registrations** and **Enterprise applications**, remove any
   remaining temporary Arc onboarding applications and their deployment role
   assignments.
5. Remove any remaining onboarding scripts from `$protected_dir` on the Ludus host.
6. In Defender **Assets > Devices**, exclude DC01 and SYNC01 as
   **Device doesn't exist**.
7. In **Defender for Cloud > Environment settings**, disable the Servers plan
   and Endpoint protection enabled solely for this lab. Review the lab's charges
   in **Azure Cost Management**.

MDE exclusion and MDI sensor removal leave history under Microsoft's retention
policies ([MDE](https://learn.microsoft.com/en-us/defender-endpoint/exclude-devices),
[MDI](https://learn.microsoft.com/en-us/defender-for-identity/technical-faq)). Rebuilds create
new device and forest identities even when names are reused.

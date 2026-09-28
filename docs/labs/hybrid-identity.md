# Hybrid identity

> Current version: **0.3.2** · Last tested version: **0.3.0**.

Deploy Entra Connect Sync, Password Hash Sync (PHS), and Defender for Identity
v3 on a dedicated sync server. The Entra Connect sensor path is a Microsoft
preview.

Since 0.3.0, DC01 gained Server 2022 ASR Audit and the diagnostic-only state
report was removed. `complete` 0.1.3 exercised the shared DC01 role path; this
blueprint version has not been deployed.

## What it builds

See [host configuration](../host-configuration.md#hybrid-identity)
for automated settings and purpose.

| Host | Resources | Purpose |
| --- | --- | --- |
| DC01 | 2 vCPU, 6 GB RAM | `defender.test` domain controller; scoped users and groups; ASR Audit |
| SYNC01 | 2 vCPU, 6 GB RAM | Entra Connect Sync, PHS, Defender services, and MDI v3 |

The deployment creates `OU=EntraSync` with `sync.alice`, `sync.bob`, `Hybrid
Lab Users`, and the `Entra Sync Scope` pilot group.

## 1. Preparation

Complete [common preparation](../getting-started.md), then prepare the items below.

- Confirm `win2022-server-x64-template` is available.
- Reserve 2 vCPU and 6 GB RAM per host (4 vCPU and 12 GB total), plus router,
  host, template-storage, and snapshot capacity.
- Use Entra Connect Sync 2.5.79.0 or later. See Microsoft's
  [minimum-version notice](https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/security-updates-pks).

### Collect tenant values

1. In Entra **Entra ID > Domain names**, copy a verified sign-in domain for
   `hybrid_identity_upn_suffix`. The listed `onmicrosoft.com` domain is suitable.

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
   ludus blueprint apply defender-xdr-lab/hybrid-identity \
     --target-range <RANGE_ID>
   ludus -r <RANGE_ID> range config get
   ```

3. Edit and save the tenant values under the indicated hosts' `role_vars`:

   ```bash
   ludus -r <RANGE_ID> range config edit
   ludus -r <RANGE_ID> range config get
   ```

   - DC01: set `hybrid_identity_upn_suffix` to the copied verified sign-in domain.

4. Review the hosts, templates, and resources against **What it builds** above.
   Confirm `mde_targets` contains DC01 and SYNC01.

### Deploy

1. Deploy and follow progress:

   ```bash
   ludus -r <RANGE_ID> range deploy
   ludus -r <RANGE_ID> range logs -f
   ```

2. Confirm the final recap has zero failed or unreachable hosts. This completes
   automated local provisioning; post-deployment commissioning follows.

## 3. Post-deployment

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
   - keep `userPrincipalName`, confirm both users have the verified suffix, and
     select **Continue without matching all UPN suffixes to verified domains**
     (`defender.test` is the lab's unverified internal suffix);
   - select only `OU=EntraSync,DC=defender,DC=test` and its children;
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

In Entra **Entra ID > Users** and **Groups**, confirm `sync.alice`, `sync.bob`,
and `Hybrid Lab Users` appear after synchronization.

1. In Entra **Users**, open `sync.alice` or `sync.bob` and copy its **User
   principal name**.
2. Open [Microsoft My Account](https://myaccount.microsoft.com) in a private
   browser window. Sign in with that UPN and the user's current AD password.
3. Confirm the account page opens for that user. This completes the browser
   sign-in check for Password Hash Sync.

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
- Two pilot users and `Hybrid Lab Users` visible in Entra.
- Successful pilot-user My Account sign-in with its current AD password.
- DC01 and SYNC01 Connected in Arc, with recent MDE Timeline activity and
  Healthy MDI v3 sensors: cloud commissioning completed.

## 4. Cleanup

Select the lab range, Azure resource group, and tenant used for this deployment.

### Retire Entra Connect

Keep DC01 and SYNC01 running until Entra deletion sync is verified.

1. On DC01, open **Active Directory Users and Computers > EntraSync** and
   delete `sync.alice`, `sync.bob`, and `Hybrid Lab Users`.
   Keep `Entra Sync Scope` and Connect until sync completes. Reapplying
   directory population during cleanup can recreate these objects.
2. On SYNC01, with Connect active and out of staging, run:

   ```powershell
   Start-ADSyncSyncCycle -PolicyType Delta
   ```

3. In Entra **Users**, **Groups**, confirm those objects are no longer active.
   Deleted users may remain in retention.
4. On SYNC01, open **Control Panel > Uninstall a program > Microsoft Entra
   Connect** and select **Remove** in the uninstaller.
5. Remove the protected Connect MSI from the Ludus host:

   ```bash
   sudo rm -- "$protected_dir/AzureADConnect.msi"
   ```

6. After uninstalling Connect, remove old `ConnectSyncProvisioning` app
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

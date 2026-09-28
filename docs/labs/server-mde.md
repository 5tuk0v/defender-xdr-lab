# Server MDE

> Current version: **1.3.2** · Last tested version: **1.3.2**.

Deploy the three-host Defender lab with server MDE and DC01 MDI.
Client MDE entitlement is not required.

Version 1.3.2 completed local provisioning. Cloud commissioning and practical
test cases were not performed as part of that deployment.

## What it builds

| Host | Resources | Purpose |
| --- | --- | --- |
| DC01 | 2 vCPU, 6 GB RAM | Windows Server 2022 domain controller, Arc/MDE, MDI v3, ASR Audit |
| SRV01 | 2 vCPU, 6 GB RAM | Windows Server 2022 member server, ASR Audit, Arc/MDE |
| WKS01 | 2 vCPU, 4 GB RAM | Windows 11 25H2, Microsoft 365 Apps, ASR Audit, no MDE |

See [host configuration](../host-configuration.md#server-mde) for automated settings.

## 1. Preparation

Complete [common preparation](../getting-started.md), then prepare the items below.

- Confirm `win2022-server-x64-template` and the stock non-TPM
  `win11-25h2-x64-enterprise-template` are built in Ludus.
- Reserve 16 GB RAM / 6 vCPUs for guests, plus router, host, template,
  and snapshot overhead.

## 2. Deployment

### Apply and review

1. Select an existing target range, or [create one](https://docs.ludus.cloud/docs/using-ludus/blueprints/#applying-a-blueprint)
   first. Applying a blueprint replaces its configuration; use that range ID
   in every command.
2. Apply the blueprint and display the configuration:

   ```bash
   ludus blueprint apply defender-xdr-lab/server-mde \
     --target-range <RANGE_ID>
   ludus -r <RANGE_ID> range config get
   ```

3. Review the hosts, templates, and resources against **What it builds** above.
   Confirm `mde_targets` contains DC01 and SRV01.

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

### Confirm Arc and MDE onboarding

1. In **Azure Arc > Machines**, confirm DC01 and SRV01 are **Connected** and
   each has `MDE.Windows` under **Extensions**.
2. In Defender **Assets > Devices**, open DC01 and SRV01 and confirm recent
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

- Recap with zero failed or unreachable hosts: local deployment completed.
- DC01 and SRV01 Connected in Azure Arc.
- Recent MDE Timeline activity on DC01 and SRV01.
- Healthy DC01 MDI v3 sensor: cloud commissioning completed.

## 4. Cleanup

Select the lab range, Azure resource group, and tenant used for this deployment.

### Retire the deployment resources

1. Verify the exact range and VMs, then destroy the range:

   ```bash
   ludus -r <RANGE_ID> range rm
   ```

2. In Azure **Resource groups**, delete the lab's resource group and confirm its
   name. This removes its Arc machines and extensions.
3. In Defender **Sensor management**, remove the disconnected DC01 MDI sensor.
4. In Entra **App registrations** and **Enterprise applications**, remove any
   remaining temporary Arc onboarding applications and their deployment role
   assignments.
5. Remove any remaining onboarding scripts from `$protected_dir` on the Ludus host.
6. In Defender **Assets > Devices**, exclude DC01 and SRV01 as
   **Device doesn't exist**.
7. In **Defender for Cloud > Environment settings**, disable the Servers plan
   and Endpoint protection enabled solely for this lab. Review the lab's charges
   in **Azure Cost Management**.

MDE exclusion and MDI sensor removal leave history under Microsoft's retention
policies ([MDE](https://learn.microsoft.com/en-us/defender-endpoint/exclude-devices),
[MDI](https://learn.microsoft.com/en-us/defender-for-identity/technical-faq)). Rebuilds create
new device and forest identities even when names are reused.

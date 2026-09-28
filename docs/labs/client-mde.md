# Client MDE

> Current version: **0.1.0** · Last tested version: **0.1.0**.

Deploy a three-host lab for phased client EDR testing. WKS01 remains outside
MDE, WKS02 uses direct client onboarding, and DC01 provides the domain and lab
policies without Arc, MDE, or MDI.

The 0.1.0 blueprint completed successfully in Ludus on 2026-09-28, and recent
WKS02 activity was confirmed in the MDE Timeline.

## What it builds

| Host | Resources | Purpose |
| --- | --- | --- |
| DC01 | 2 vCPU, 6 GB RAM | Windows Server 2022 domain controller, domain policies, and ASR Audit; no MDE or MDI |
| WKS01 | 2 vCPU, 4 GB RAM | Windows 11 25H2, Microsoft 365 Apps, and ASR Audit; no MDE |
| WKS02 | 2 vCPU, 4 GB RAM | Matching Windows 11 client with direct MDE onboarding |

See [host configuration](../host-configuration.md#client-mde) for automated settings.

## 1. Preparation

Complete [common preparation](../getting-started.md), including Source
installation and the protected staging directory. The Azure-connected server
preparation does not apply to this blueprint.

- Confirm `win2022-server-x64-template` and the stock non-TPM
  `win11-25h2-x64-enterprise-template` are built in Ludus.
- Reserve 14 GB RAM / 6 vCPUs for guests, plus router, host, template, and
  snapshot overhead.
- Confirm client MDE entitlement for WKS02.

Use `ludus_ssh_target` and `protected_dir` from common preparation for the
file-transfer and installation commands below.

### Stage WKS02 onboarding

1. In Defender **Settings > Endpoints > Device management > Onboarding**, choose
   **Windows 10 and 11 > Local script**, download the package, and extract
   `WindowsDefenderATPLocalOnboardingScript.cmd`.

2. Transfer the script from the download machine:

   ```bash
   mde_script='/absolute/path/to/WindowsDefenderATPLocalOnboardingScript.cmd'
   scp -- "$mde_script" "${ludus_ssh_target}:/tmp/WindowsDefenderATPLocalOnboardingScript.cmd"
   ```

3. On the Ludus host, install and check it in the protected directory:

   ```bash
   sudo install -o ludus -g ludus -m 600 /tmp/WindowsDefenderATPLocalOnboardingScript.cmd "$protected_dir/WindowsDefenderATPLocalOnboardingScript.cmd"
   sudo test -s "$protected_dir/WindowsDefenderATPLocalOnboardingScript.cmd"
   sudo stat -c '%U %G %a %n' "$protected_dir/WindowsDefenderATPLocalOnboardingScript.cmd"
   ```

4. Require a successful file check and `ludus ludus 600`, then remove the
   temporary transfer copy:

   ```bash
   sudo rm -- /tmp/WindowsDefenderATPLocalOnboardingScript.cmd
   ```

## 2. Deployment

### Apply and review

1. Select an existing target range, or [create one](https://docs.ludus.cloud/docs/using-ludus/blueprints/#applying-a-blueprint)
   first. Applying a blueprint replaces its configuration; use that range ID
   in every command.
2. Apply the blueprint and display the configuration:

   ```bash
   ludus blueprint apply defender-xdr-lab/client-mde \
     --target-range <RANGE_ID>
   ludus -r <RANGE_ID> range config get
   ```

3. Review the hosts, templates, and resources against **What it builds** above.
   Confirm `mde_targets` contains only WKS02.

### Deploy

1. Deploy and follow progress:

   ```bash
   ludus -r <RANGE_ID> range deploy
   ludus -r <RANGE_ID> range logs -f
   ```

2. Confirm the final recap has zero failed or unreachable hosts. This completes
   automated local provisioning; MDE portal acceptance follows.

## 3. Post-deployment

### Enroll updated UEFI certificates

Complete this before the first Testing Mode snapshot. For BitLocker-protected
clients, have the recovery key available and suspend protection before enrollment;
resume it after boot.

1. Shut down WKS01 and WKS02.
2. In Proxmox, select each client's **Hardware > EFI disk > Disk Action >
   Enroll Updated Certificates**.
3. Boot the clients and confirm the Microsoft UEFI 2023 certificate warning
   (`ms-cert=2023k`) has cleared in Proxmox.

For a failed Testing Mode stop or an older snapshot, use
[UEFI troubleshooting](../troubleshooting.md#testing-mode-will-not-stop-and-proxmox-shows-an-efi-certificate-warning).

### Confirm client MDE onboarding

1. In Defender **Assets > Devices**, open WKS02 and confirm recent **Timeline**
   activity.
2. Confirm WKS01 and DC01 were not newly onboarded from this range.

### Remove the onboarding package

After WKS02 is onboarded, remove its protected script from the Ludus host:

```bash
sudo rm -- "$protected_dir/WindowsDefenderATPLocalOnboardingScript.cmd"
```

### Acceptance

The results above confirm:

- Recap with zero failed or unreachable hosts: local deployment completed.
- Recent WKS02 Timeline activity: client MDE commissioning completed.
- WKS01 and DC01 remain outside MDE: the phased client comparison is ready.

Continue with the [phased EDR testing overview](../../README.md#phased-edr-testing).

## 4. Cleanup

1. Verify the exact range and VMs, then destroy the range:

   ```bash
   ludus -r <RANGE_ID> range rm
   ```

2. Remove any remaining WKS02 onboarding script from `$protected_dir` on the
   Ludus host.
3. In Defender **Assets > Devices**, exclude WKS02 as **Device doesn't exist**.

MDE exclusion leaves history under Microsoft's
[retention policy](https://learn.microsoft.com/en-us/defender-endpoint/exclude-devices).
Rebuilds create a new device identity even when the hostname is reused.

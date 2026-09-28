# Server MDE blueprint

**Current version:** 1.3.2 · **Last tested version:** 1.3.2

Choose `server-mde` for the three-host Defender lab when client MDE onboarding
is unavailable.

Version 1.3.2 completed local provisioning. Cloud commissioning and practical
test cases were not performed as part of that deployment.

## Hosts

- **DC01:** Windows Server 2022 domain controller with ASR Audit, Arc, MDE,
  and MDI v3.
- **SRV01:** Windows Server 2022 member server with ASR Audit, Arc, and MDE.
- **WKS01:** Windows 11 25H2 with Microsoft 365 Apps and ASR Audit, without
  MDE.

## Deploy and finish

1. Complete [common preparation](../../docs/getting-started.md) for Source
   installation and Azure/Arc setup.
2. Follow the [Server MDE runbook](../../docs/labs/server-mde.md) for additional
   preparation, deployment, commissioning, acceptance, and cleanup.

See [host configuration](../../docs/host-configuration.md#server-mde)
for the settings applied to each machine.

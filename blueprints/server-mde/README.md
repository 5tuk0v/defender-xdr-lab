# Server MDE blueprint

**Current version:** 1.3.2 · **Last tested version:** 1.3.0

Choose `server-mde` for the three-host Defender lab when client MDE onboarding
is unavailable.

The 1.3.0 run passed local provisioning; cloud commissioning was not performed
in that run.

Since 1.3.0, DC01 gained Server 2022 ASR Audit and the diagnostic-only state
report was removed. `complete` 0.1.3 exercised the shared DC01 role path; this
blueprint version has not been deployed.

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

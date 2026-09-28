# Standard blueprint

**Current version:** 2.0.2 · **Last tested version:** 2.0.0

Choose `standard` for the default four-host R&D lab and paired Windows 11
workstations: WKS01 without MDE and WKS02 with direct client MDE onboarding.

Since 2.0.0, DC01 gained Server 2022 ASR Audit and the diagnostic-only state
report was removed. `complete` 0.1.3 exercised the shared DC01 role path; this
blueprint version has not been deployed.

## Hosts

- **DC01:** Windows Server 2022 domain controller with ASR Audit, Arc, MDE,
  and MDI v3.
- **SRV01:** Windows Server 2022 member server with ASR Audit, Arc, and MDE.
- **WKS01:** Windows 11 25H2 with Microsoft 365 Apps and ASR Audit.
- **WKS02:** matching Windows 11 workstation with direct client MDE onboarding.

## Deploy and finish

1. Complete [common preparation](../../docs/getting-started.md) for Source
   installation and Azure/Arc setup.
2. Follow the [Standard runbook](../../docs/labs/standard.md) for additional
   preparation, deployment, commissioning, acceptance, and cleanup.

See [host configuration](../../docs/host-configuration.md#standard)
for the settings applied to each machine.

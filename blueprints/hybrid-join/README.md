# Hybrid join

**Current version:** 0.2.2 · **Last tested version:** 0.2.0

Choose this three-host pilot to test Entra Connect Sync, Password Hash Sync,
targeted Microsoft Entra hybrid join, and a synchronized user's Primary Refresh
Token (PRT). The 0.2.0 run confirmed WKS01 hybrid join and Bob's PRT;
MDI health was not rechecked in that run.

Since 0.2.0, DC01 gained Server 2022 ASR Audit and the diagnostic-only state
report was removed. `complete` 0.1.3 exercised the shared DC01 role path; this
blueprint version has not been deployed.

## Hosts

- **DC01:** `defender.test` domain controller, scoped test users and groups,
  ASR Audit, and MDI v3.
- **SYNC01:** Entra Connect Sync, Password Hash Sync, and MDI v3 preview sensor.
- **WKS01:** Windows 11 25H2 hybrid-join client with Microsoft 365 Apps, without MDE.

## Deploy and finish

1. Complete [common preparation](../../docs/getting-started.md) for Source
   installation and Azure/Arc setup.
2. Follow the [Hybrid join runbook](../../docs/labs/hybrid-join.md) for additional
   preparation, deployment, commissioning, acceptance, and cleanup.

See [host configuration](../../docs/host-configuration.md#hybrid-join)
for the settings applied to each machine.

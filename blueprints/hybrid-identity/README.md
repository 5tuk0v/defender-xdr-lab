# Hybrid identity

**Current version:** 0.3.2 · **Last tested version:** 0.3.0

Choose this two-server scenario to test Entra Connect Sync, Password Hash Sync,
and Defender for Identity v3 on a dedicated sync server. The Entra Connect
sensor path is a Microsoft preview.

Since 0.3.0, DC01 gained Server 2022 ASR Audit and the diagnostic-only state
report was removed. `complete` 0.1.3 exercised the shared DC01 role path; this
blueprint version has not been deployed.

## Hosts

- **DC01:** `defender.test` domain controller, scoped test users and groups,
  ASR Audit, and MDI v3.
- **SYNC01:** Entra Connect Sync, Password Hash Sync, and the MDI v3 preview
  sensor.

## Deploy and finish

1. Complete [common preparation](../../docs/getting-started.md) for Source
   installation and Azure/Arc setup.
2. Follow the [Hybrid identity runbook](../../docs/labs/hybrid-identity.md) for additional
   preparation, deployment, commissioning, acceptance, and cleanup.

See [host configuration](../../docs/host-configuration.md#hybrid-identity)
for the settings applied to each machine.

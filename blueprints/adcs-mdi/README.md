# Vulnerable AD CS and Defender for Identity

**Current version:** 0.3.3 · **Last tested version:** 0.3.0

Choose this two-host scenario for attack-path exercises using an intentionally
vulnerable Enterprise Root CA and Defender for Identity visibility. It applies
the pinned Bad Sector Labs AD CS vulnerability set and creates public lab
credentials.

Since 0.3.0, DC01 and CA01 gained Server 2022 ASR Audit and the diagnostic-only
state report was removed. `complete` 0.1.3 exercised both shared role paths; this
blueprint version has not been deployed.

## Hosts

- **DC01:** `defender.test` domain controller and MDI v3 sensor host, with ASR Audit.
- **CA01:** Windows Server 2022 Enterprise Root CA and MDI v3 preview sensor
  host, with ASR Audit.

## Deploy and finish

1. Complete [common preparation](../../docs/getting-started.md) for Source
   installation and Azure/Arc setup.
2. Follow the [Vulnerable AD CS and Defender for Identity runbook](../../docs/labs/adcs-mdi.md) for additional
   preparation, deployment, commissioning, acceptance, and cleanup.

See [host configuration](../../docs/host-configuration.md#adcs-mdi)
for the settings applied to each machine.

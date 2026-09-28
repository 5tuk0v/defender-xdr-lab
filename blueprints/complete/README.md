# Complete

**Current version:** 0.1.3 · **Last tested version:** 0.1.3

Choose this five-host lab to combine the WKS01/WKS02 endpoint comparison,
Entra Connect, hybrid join, server and client MDE, MDI v3, and vulnerable AD CS.
It includes the full pinned ESC vulnerability set on CA01.

The 0.1.3 Ludus deployment succeeded with Server 2022 ASR Audit assigned to
DC01 and CA01 and the diagnostic-only state report removed. Cloud commissioning
was not repeated; the 0.1.0 deployment remains the recorded integrated cloud
acceptance. SYNC01 and CA01 took longer to appear as eligible MDI v3 targets
during that run; this portal delay is expected.

## Hosts

- **DC01:** domain controller, scoped sync users/groups/devices, server MDE,
  ASR Audit, and MDI v3.
- **WKS01:** Windows 11 25H2 hybrid-join client without MDE.
- **WKS02:** Windows 11 25H2 hybrid-join client with direct MDE onboarding.
- **SYNC01:** Entra Connect Sync, Password Hash Sync, server MDE, and MDI v3
  preview sensor.
- **CA01:** vulnerable AD CS, ASR Audit, server MDE, and MDI v3 preview sensor.

## Deploy and finish

1. Complete [common preparation](../../docs/getting-started.md) for Source
   installation and Azure/Arc setup.
2. Follow the [Complete runbook](../../docs/labs/complete.md) for additional
   preparation, deployment, commissioning, acceptance, and cleanup.

See [host configuration](../../docs/host-configuration.md#complete)
for the settings applied to each machine.

# Client MDE blueprint

**Current version:** 0.1.0 · **Last tested version:** 0.1.0

Choose `client-mde` for a focused three-host comparison between a Windows 11
client without MDE and a matching client with direct MDE onboarding. DC01
provides the domain and lab policies without Arc, MDE, or MDI.

The 0.1.0 blueprint completed successfully in Ludus on 2026-09-28, and recent
WKS02 activity was confirmed in the MDE Timeline.

## Hosts

- **DC01:** Windows Server 2022 domain controller with the lab's domain policies
  and Server ASR Audit; no MDE or MDI.
- **WKS01:** Windows 11 25H2 with Microsoft 365 Apps and ASR Audit; no MDE.
- **WKS02:** matching Windows 11 workstation with direct client MDE onboarding.

## Deploy and finish

1. Complete [common preparation](../../docs/getting-started.md) for Source
   installation and protected staging. The Azure-connected server preparation
   does not apply to this blueprint.
2. Follow the [Client MDE runbook](../../docs/labs/client-mde.md) for onboarding
   package staging, deployment, acceptance, and cleanup.

See [host configuration](../../docs/host-configuration.md#client-mde) for the
settings applied to each machine.

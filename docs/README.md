# Documentation

Choose a lab in the [project README](../README.md), complete
[common preparation](getting-started.md), then follow its runbook to cleanup.

## Lab runbooks

Each runbook contains preparation, deployment, post-deployment commissioning
and acceptance, and cleanup.

| Lab | Runbook |
| --- | --- |
| Client comparison with client MDE only | [Client MDE](labs/client-mde.md) |
| Default client and server comparison | [Standard](labs/standard.md) |
| Server protection without client MDE entitlement | [Server MDE](labs/server-mde.md) |
| Entra Connect and identity monitoring | [Hybrid identity](labs/hybrid-identity.md) |
| Workstation registration and cloud sign-in | [Hybrid join](labs/hybrid-join.md) |
| Vulnerable certificate services and identity monitoring | [AD CS and MDI](labs/adcs-mdi.md) |
| Combined endpoint, identity, and certificate lab | [Complete](labs/complete.md) |

## Supporting guides

- [Troubleshooting](troubleshooting.md): fix missed preparation, missing MDI
  sensors, PRT sign-in, and Proxmox EFI certificate warnings.
- [Host configuration](host-configuration.md): understand the automated
  defaults and settings applied to each host.
- [Role index](../ansible/roles/README.md): component inputs, behavior, and validation.

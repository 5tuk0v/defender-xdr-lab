# Defender XDR Lab for Ludus

We all know by now that Ludus is awesome for building lab ranges quickly and
easily, especially Active Directory environments. I built this project to make
it easier to connect those labs to Microsoft 365, Entra ID, and Microsoft
Defender, especially MDE and MDI.

The basic workflow is: prepare the files and cloud resources required by a
blueprint, apply it, and deploy the range. Each lab comes with a runbook
explaining any manual steps needed before and after deployment.

I built this around a real use case: phased EDR testing against Defender for
Endpoint in a controlled lab, with the usual Ludus features like repeatable
deployments, snapshots, and Internet blocking.

\<Insert AI-generated README file here :D\>

## Getting started (choose your lab)

1. Choose a blueprint below and check its runbook's prerequisites.
2. Complete [common preparation](docs/getting-started.md): install the Source,
   create the protected staging directory, and prepare the services required by
   that blueprint.
3. Follow your selected runbook through deployment, commissioning, acceptance,
   and cleanup.

| Blueprint | Choose it for | Guests / RAM |
| --- | --- | --- |
| [client-mde](docs/labs/client-mde.md) | Compare Windows clients using only client MDE | 3 / 14 GB |
| [**standard (default)**](docs/labs/standard.md) | Client comparison with server MDE and DC01 MDI | 4 / 20 GB |
| [server-mde](docs/labs/server-mde.md) | Server protection without client MDE entitlement | 3 / 16 GB |
| [hybrid-identity](docs/labs/hybrid-identity.md) | Entra Connect, password hash sync, and MDI | 2 / 12 GB |
| [hybrid-join](docs/labs/hybrid-join.md) | Workstation hybrid join and Windows cloud sign-in | 3 / 16 GB |
| [adcs-mdi](docs/labs/adcs-mdi.md) | Intentionally vulnerable certificate services and MDI | 2 / 12 GB |
| [complete](docs/labs/complete.md) | Endpoint, identity, and AD CS together; omits SRV01 | 5 / 26 GB |

Guest totals exclude router, host, and snapshot overhead.

## Default lab settings

- **Defender Antivirus:** scanning and cloud protection enabled; Network
  Protection in Block mode.
- **Attack surface reduction (ASR):** log rule activity in Audit mode on
  all Windows guests.
- **Sample submission:** automatic Defender/MDE sample uploads disabled.
- **Public-analysis sinkhole:** selected sample-upload domains redirected to
  `0.0.0.0` in each guest's hosts file (configurable).
- **Windows clients:** Microsoft 365 Apps installed for optional Office tests.
- **Other protections:** Controlled Folder Access and Credential Guard retain
  Windows defaults (configurable).

See [host configuration](docs/host-configuration.md) for which
settings apply to each host and the scenario-specific additions.

## Phased EDR testing

The lab makes phased EDR testing easier. `client-mde`, `standard`, and `complete`
include both clients, with Testing Mode's RAM-inclusive snapshots for restoring
the commissioned baseline between runs.

| Phase | Host | Workflow |
| --- | --- | --- |
| Without EDR | WKS01 | Run the case with Defender Antivirus active and no MDE. |
| MDE offline | WKS02 | Testing Mode blocks Internet; allow case/C2 destinations while keeping MDE cloud access blocked. |
| MDE online | WKS02 | Keep Testing Mode snapshots; give WKS02 and its DNS server DC01 Internet access. |

For the online phase, set `testing.block_internet: false` on WKS02 and DC01.
Restore `true` before the next offline run; VM snapshots do not restore range
configuration. See [Ludus Testing Mode](https://docs.ludus.cloud/docs/quick-start/testing-mode/)
for the commands and per-host settings.

Sample safeguards remain active in every phase. Other Defender cloud telemetry
can flow when online.

## Documentation

- [Documentation index](docs/README.md) — lab runbooks, troubleshooting,
  and component references.

## Credits and license

This project began with [ZephrFish's Ludus Defender Lab](https://github.com/ZephrFish/ludus-defender-lab)
and has since been independently redesigned and substantially rewritten. It
uses maintained Microsoft, Ludus, Bad Sector Labs, and community components.

OpenAI Codex helped write and revise the automation and documentation. The
maintainer directed the design, reviewed the changes, and manually performed
the workflows identified as tested.

Licensed under [LICENSE](LICENSE).

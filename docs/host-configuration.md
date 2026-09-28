# What deployment configures on each host

Blueprint defaults are listed below. Role variables can change these settings;
see the [role contracts](../ansible/roles/README.md) for inputs. Deployment and
cloud commissioning are covered in the [lab runbooks](README.md#lab-runbooks).

## Shared defaults

| Setting | Automated configuration |
| --- | --- |
| Domain | DC01 creates `defender.test`; other guests join it as members. |
| Defender Antivirus | Domain GPO enables real-time, behavior, IOAV, and script scanning, plus PUA protection. |
| Cloud and network protection | High cloud protection with a 50-second timeout; Network Protection in Block mode, including servers; datagram processing disabled. |
| Sample submission | Domain GPO sets Defender sample consent to Never Send and disables MDE sample collection. Other Defender cloud-telemetry settings are unchanged. |
| Public-analysis sinkhole | Every guest maps the configured exact-name analysis/submission domains to `0.0.0.0` in its hosts file, preserving unrelated entries. This is configurable. |
| Controlled Folder Access and Credential Guard | Both use `native`: retain operating-system defaults without a lab policy override. Configurable through their roles. |
| Group Policy | Every guest refreshes computer policy after domain GPO configuration. |
| Testing Mode | Every guest uses RAM-inclusive snapshots and Internet blocking. |
| Range | VLAN 10; inter-VLAN traffic rejected by default; America/Toronto time zone. |

## Protection and application components

| Component | Automated configuration |
| --- | --- |
| ASR | Pinned Windows Server 2022 or Windows 11 25H2 preset in Audit mode on every guest. |
| Defender platform | Install and verify Microsoft's current signed platform package on `mde_targets`. |
| Azure Arc | Run the protected onboarding script on the listed servers, remove its guest copy, and validate the connection. |
| Client MDE | Run the protected client onboarding script on WKS02, remove its guest copy, and validate local onboarding. |
| Microsoft 365 Apps | Install 64-bit Apps for enterprise, Monthly Enterprise channel, en-US, using Microsoft's Office Deployment Tool. |
| MDI preparation | Set High Performance on DC01 and the identity servers listed below. |

## standard

Four-host endpoint comparison; no AD CS.

| Host | Additional automated configuration |
| --- | --- |
| DC01 | Domain controller and domain GPOs; Server ASR Audit; High Performance; Defender platform; Arc onboarding. |
| SRV01 | Server ASR Audit; Defender platform; Arc onboarding. |
| WKS01 | Windows 11 ASR Audit; Microsoft 365 Apps; no MDE. |
| WKS02 | Windows 11 ASR Audit; Microsoft 365 Apps; Defender platform; client MDE onboarding. |

`mde_targets`: DC01, SRV01, WKS02.

## client-mde

Three-host client comparison without Azure Arc, server MDE, or MDI.

| Host | Additional automated configuration |
| --- | --- |
| DC01 | Domain controller and domain GPOs; Server ASR Audit; no MDE or MDI. |
| WKS01 | Windows 11 ASR Audit; Microsoft 365 Apps; no MDE. |
| WKS02 | Windows 11 ASR Audit; Microsoft 365 Apps; Defender platform; client MDE onboarding. |

`mde_targets`: WKS02.

## server-mde

Same DC01, SRV01, and WKS01 configuration as `standard`, without WKS02.

`mde_targets`: DC01, SRV01.

## hybrid-identity

Two-server Entra Connect lab.

| Host | Additional automated configuration |
| --- | --- |
| DC01 | `EntraSync` OU with Users and Groups children; `sync.alice`, `sync.bob`, `Hybrid Lab Users`, and `Entra Sync Scope`; configured UPN suffix and direct sync-scope membership; Server ASR Audit; High Performance; Defender platform; Arc onboarding. |
| SYNC01 | .NET feature; TLS 1.2 for Schannel/.NET; signed PowerShell execution preparation; staging of the supplied Microsoft-signed Connect MSI; High Performance; Server ASR Audit; Defender platform; Arc onboarding. |

`Hybrid Lab Users` is a direct member of `Entra Sync Scope`. Directory
reapplication can restore the configured public test-user passwords.

`mde_targets`: DC01, SYNC01.

## hybrid-join

DC01 and SYNC01 use the `hybrid-identity` configuration, with these additions:

| Host | Additional automated configuration |
| --- | --- |
| DC01 | `Devices` OU under `EntraSync`; WKS01's computer object moved there and added directly to `Entra Sync Scope`. |
| WKS01 | Windows 11 ASR Audit; Microsoft 365 Apps; supplied tenant ID/domain written to client-side hybrid-join discovery registry values; no MDE. |

`mde_targets`: DC01, SYNC01.

## adcs-mdi

Two-server certificate lab with intentional ESC1–ESC16 weaknesses, both ESC10
cases, and the ESC3 enrollment-agent variant from Bad Sector Labs AD CS 1.6.0.
This includes weak templates, web enrollment, certificate mapping, CA settings,
and public test accounts.

| Host | Additional automated configuration |
| --- | --- |
| DC01 | Domain controller; Server ASR Audit; High Performance; Defender platform; Arc onboarding. |
| CA01 | Enterprise Root CA `defender-CA`; Server ASR Audit; running CertSvc and Windows Time; Certification Services Success/Failure auditing; CA audit filter `127`; High Performance; Defender platform; Arc onboarding. |

`mde_targets`: DC01, CA01.

## complete

Combines `hybrid-identity`, `hybrid-join`, and `adcs-mdi` with both clients from
`standard`; omits SRV01.

| Host | Additional automated configuration |
| --- | --- |
| DC01 | Hybrid test users/groups; both workstation objects in `EntraSync/Devices` and direct sync scope; Server ASR Audit; High Performance; Defender platform; Arc onboarding. |
| SYNC01 | Same Connect host preparation, Server ASR Audit, High Performance, Defender platform, and Arc onboarding as `hybrid-identity`. |
| CA01 | Same vulnerable CA, Server ASR Audit, auditing, High Performance, Defender platform, and Arc onboarding as `adcs-mdi`. |
| WKS01 | Windows 11 ASR Audit; Microsoft 365 Apps; client-side hybrid-join discovery; no MDE. |
| WKS02 | Windows 11 ASR Audit; Microsoft 365 Apps; client-side hybrid-join discovery; Defender platform; client MDE onboarding. |

`mde_targets`: DC01, WKS02, SYNC01, CA01.

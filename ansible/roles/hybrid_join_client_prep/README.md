# hybrid_join_client_prep

Prepares a selected domain-member Windows workstation for a targeted Microsoft Entra
hybrid join pilot. When the operator supplies both tenant values before the
normal Ludus deployment, the role sets and verifies Microsoft's documented
client-side discovery values under:

```text
HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CDJ\AAD
```

The values are applied directly to the selected workstation rather than to the
forest-wide Active Directory service connection point. This is equivalent to
the effective client-side state delivered by Microsoft's targeted-deployment
GPO example and scopes discovery to the selected workstations. The role validates
that it is running on a domain-member workstation, and an unchanged second
application reports no registry drift.

The blueprints apply this role to WKS01 in `hybrid-join` and to WKS01 and WKS02
in `complete`.

## Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `hybrid_join_client_prep_enabled` | `true` | Run the local workstation preparation |
| `hybrid_join_tenant_id` | empty | Microsoft Entra tenant GUID |
| `hybrid_join_tenant_name` | empty | Actual verified domain from Entra ID > Domain names |

For this managed PHS setup, `hybrid_join_tenant_name` accepts the tenant's
actual `onmicrosoft.com` domain or a verified custom domain. It does not accept
the Overview display name; do not construct a domain from that display name.

The two tenant values are a pair: supply both or neither. Empty values produce
a visible skip so the local lab remains deployable without tenant context.
They identify the intended tenant but are not credentials; tenant
authentication and device registration remain operator-led commissioning.

Microsoft reference: [Targeted deployments of Microsoft Entra hybrid join](https://learn.microsoft.com/en-us/entra/identity/devices/hybrid-join-control).

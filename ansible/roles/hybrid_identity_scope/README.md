# hybrid_identity_scope

Reconciles the direct users, groups, and optional computer accounts in the
Entra pilot-filter group. Applies a supplied UPN suffix to the forest and its
in-scope users.

## Inputs

| Variable | Default | Purpose |
| --- | --- | --- |
| `hybrid_identity_scope_group` | `Entra Sync Scope` | Pilot-filter group |
| `hybrid_identity_scope_member_groups` | `Hybrid Lab Users` | Direct payload groups |
| `hybrid_identity_scope_computers` | Empty list | Existing computers and intended OU paths |
| `hybrid_identity_upn_suffix` | Empty | Operator-supplied verified sign-in suffix |

The role derives users from `ludus_users` entries that directly name the scope
group. Adding a test user requires membership in both the scope and payload
groups. Computer entries use this form:

```yaml
hybrid_identity_scope_computers:
  - name: WKS01
    path: OU=Devices,OU=EntraSync,DC=defender,DC=test
```

## Behavior and validation

- Add and verify the declared payload groups after BSL creates the objects.
- Move declared computer accounts with `microsoft.ad.computer`, add their direct
  scope membership, and validate it.
- Validate exact declared direct users, groups, and computers; nested membership
  does not satisfy the scope.
- When a suffix is supplied, check UPN collisions, add the forest suffix, update
  the resolved users, and verify the result. Empty input skips only UPN work.
- An unchanged reapplication preserves the selected membership and suffix state.

Entra domain verification remains an operator input; the role manages local AD.
The local reconciliation compensates for the pinned BSL custom-OU group-nesting
issue while retaining its maintained population role.

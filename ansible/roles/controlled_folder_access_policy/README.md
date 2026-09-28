# controlled_folder_access_policy

Creates a domain-linked Group Policy Object for Controlled Folder Access. Run
the role on `DC01`; GPO writes use the domain administrator configured in
Ludus `defaults`.

`controlled_folder_access_policy_state` supports:

- `native` (default): removes the role-owned GPO and link;
- `audit`: records CFA activity without blocking;
- `block`: enables CFA blocking.

Use `audit` before selecting `block`.

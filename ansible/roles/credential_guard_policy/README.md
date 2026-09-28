# credential_guard_policy

Creates a Group Policy Object for member computers in the Ludus `Servers` and
`Workstations` OUs. Run the role on `DC01`; GPO writes use the domain
administrator configured in Ludus `defaults`.

`credential_guard_policy_state` supports:

- `native` (default): removes the role-owned GPO and links;
- `enabled`: enables Credential Guard without UEFI lock;
- `disabled`: explicitly disables Credential Guard.

Policy changes require Group Policy refresh and a member-computer reboot.
After Credential Guard has started, apply `disabled`, refresh, and reboot
before returning to `native`; removing policy alone is not a runtime rollback.

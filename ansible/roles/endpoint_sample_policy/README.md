# endpoint_sample_policy

Creates a domain-linked GPO for the two endpoint sample-transfer controls used
by this lab. Run the role on `DC01`; GPO writes use the domain administrator
configured in Ludus `defaults`.

`endpoint_sample_policy_state` supports:

- `blocked` (default): sets Defender sample consent to Never Send and disables
  MDE sample collection;
- `native`: removes the two role-owned policy values.

The GPO applies to all authenticated domain computers.

# defender_baseline

Creates a domain-linked Defender Antivirus baseline GPO for all domain
computers. Run the role on `DC01`; GPO writes use the domain administrator
configured in Ludus `defaults`.

The enabled baseline configures real-time, behavior, IOAV, and script scanning;
High cloud protection with a 50-second timeout; PUA protection; and Network
Protection block mode. It explicitly opts Windows Server into Network
Protection so the requested mode is not ignored by the operating system, while
keeping datagram processing disabled for stable DC, DNS, and server operation.

Each registry-policy mutation retries only transient `0x80070005` access
denials with a bounded 1/2/4-second backoff, then reads the value back before
continuing. Other errors fail immediately, and a persistent access denial
still fails with the role's GPO, AD, and SYSVOL diagnostics.

`defender_baseline_enabled` defaults to `true`. Setting it to `false`
removes the role-owned baseline values from the GPO.

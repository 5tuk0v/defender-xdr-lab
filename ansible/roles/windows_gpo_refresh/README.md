# windows_gpo_refresh

Refreshes computer Group Policy on a domain-joined Windows host after the
GPO-authoring roles complete. It runs `gpupdate` for the computer target,
waits up to 120 seconds, and fails when refresh is unsuccessful.

`windows_gpo_refresh_enabled` defaults to `true`. The role reports unchanged
because it is a synchronization barrier rather than configuration ownership.

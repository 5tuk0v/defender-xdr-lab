# mdi_sensor_performance

Sets and validates the Windows **High Performance** power plan on a Defender
for Identity v3 sensor host. It supports domain controllers and selected
domain-member identity servers such as SYNC01 and CA01.

`mdi_sensor_performance_enabled` defaults to `true`.
`mdi_sensor_performance_allowed_domain_roles` defaults internally to Windows
member-server and domain-controller values (`3`, `4`, and `5`). Blueprints do
not normally override this safety check. Standalone systems and workstations
fail before mutation. Reapplying the requested state is idempotent.

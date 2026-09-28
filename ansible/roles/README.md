# Role reference

These roles provide the project-specific behavior used by the blueprints.
Open a role page for its inputs, actions, validation, and cleanup behavior.
End-to-end deployment and cloud procedures belong in the [user documentation](../../docs/README.md).

| Role | Purpose |
| --- | --- |
| [`azure_arc_onboard`](azure_arc_onboard/README.md) | Stage a protected Azure Arc script, connect a Windows server, and verify its resource ID |
| [`controlled_folder_access_policy`](controlled_folder_access_policy/README.md) | Manage the lab's Controlled Folder Access domain policy |
| [`credential_guard_policy`](credential_guard_policy/README.md) | Manage Credential Guard policy for domain member computers |
| [`defender_baseline`](defender_baseline/README.md) | Apply the domain Defender Antivirus baseline |
| [`endpoint_sample_policy`](endpoint_sample_policy/README.md) | Block Defender and MDE sample transfer through domain policy |
| [`hybrid_identity_host_prep`](hybrid_identity_host_prep/README.md) | Prepare a server for Entra Connect and optionally stage its installer |
| [`hybrid_identity_scope`](hybrid_identity_scope/README.md) | Reconcile the hybrid pilot group, devices, and optional UPN suffix |
| [`hybrid_join_client_prep`](hybrid_join_client_prep/README.md) | Configure targeted Entra tenant discovery on selected workstations |
| [`mde_client_onboard`](mde_client_onboard/README.md) | Onboard a selected Windows client with a protected MDE script |
| [`mde_windows_host_prep`](mde_windows_host_prep/README.md) | Update and verify the local Defender platform before onboarding |
| [`mdi_adcs_host_prep`](mdi_adcs_host_prep/README.md) | Prepare auditing and CA service state for an MDI v3 AD CS sensor |
| [`mdi_sensor_performance`](mdi_sensor_performance/README.md) | Select the High Performance power plan on an MDI sensor host |
| [`microsoft_365_apps`](microsoft_365_apps/README.md) | Install and verify Microsoft 365 Apps for enterprise |
| [`sample_submission_sinkhole`](sample_submission_sinkhole/README.md) | Manage the lab's exact-name sample-submission sinkhole entries |
| [`windows_gpo_refresh`](windows_gpo_refresh/README.md) | Refresh computer policy after domain GPO changes |

Reusable ASR policy is maintained separately in `ludus_asr_presets`.

#!/usr/bin/env python3
"""Offline structural checks for Defender XDR Lab Source blueprints."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "source.yml"
BLUEPRINT_SPECS = {
    "client-mde": {
        "version": "0.1.0",
        "kind": "client",
        "hosts": {"DC01", "WKS01", "WKS02"},
        "mde_targets": {"WKS02"},
        "requirements": {
            "roles": {("5tuk0v.ludus_asr_presets", "v0.1.0")},
            "collections": set(),
        },
    },
    "server-mde": {
        "version": "1.3.2",
        "kind": "baseline",
        "hosts": {"DC01", "SRV01", "WKS01"},
        "mde_targets": {"DC01", "SRV01"},
        "requirements": {
            "roles": {("5tuk0v.ludus_asr_presets", "v0.1.0")},
            "collections": set(),
        },
    },
    "standard": {
        "version": "2.0.2",
        "kind": "baseline",
        "hosts": {"DC01", "SRV01", "WKS01", "WKS02"},
        "mde_targets": {"DC01", "SRV01", "WKS02"},
        "requirements": {
            "roles": {("5tuk0v.ludus_asr_presets", "v0.1.0")},
            "collections": set(),
        },
    },
    "hybrid-identity": {
        "version": "0.3.2",
        "kind": "hybrid",
        "hosts": {"DC01", "SYNC01"},
        "mde_targets": {"DC01", "SYNC01"},
        "requirements": {
            "roles": {("5tuk0v.ludus_asr_presets", "v0.1.0")},
            "collections": {
                ("badsectorlabs.ludus_windows_utils", "1.2.0"),
                ("microsoft.ad", "1.8.0"),
            },
        },
    },
    "hybrid-join": {
        "version": "0.2.2",
        "kind": "hybrid-join",
        "hosts": {"DC01", "SYNC01", "WKS01"},
        "mde_targets": {"DC01", "SYNC01"},
        "requirements": {
            "roles": {("5tuk0v.ludus_asr_presets", "v0.1.0")},
            "collections": {
                ("badsectorlabs.ludus_windows_utils", "1.2.0"),
                ("microsoft.ad", "1.8.0"),
            },
        },
    },
    "adcs-mdi": {
        "version": "0.3.3",
        "kind": "adcs",
        "hosts": {"DC01", "CA01"},
        "mde_targets": {"DC01", "CA01"},
        "requirements": {
            "roles": {
                ("5tuk0v.ludus_asr_presets", "v0.1.0"),
                ("badsectorlabs.ludus_adcs", "1.6.0"),
            },
            "collections": {("microsoft.ad", "1.8.0")},
        },
    },
    "complete": {
        "version": "0.1.3",
        "kind": "complete",
        "hosts": {"DC01", "WKS01", "WKS02", "SYNC01", "CA01"},
        "mde_targets": {"DC01", "WKS02", "SYNC01", "CA01"},
        "requirements": {
            "roles": {
                ("5tuk0v.ludus_asr_presets", "v0.1.0"),
                ("badsectorlabs.ludus_adcs", "1.6.0"),
            },
            "collections": {
                ("badsectorlabs.ludus_windows_utils", "1.2.0"),
                ("microsoft.ad", "1.8.0"),
            },
        },
    },
}
EXPORT_ATTRIBUTES_PATH = ROOT / ".gitattributes"
PRIVATE_DOCUMENT_NAMES = {
    "AGENTS.md",
    "PROJECT_STATUS.md",
}
SINKHOLE_ROLE_DIR = ROOT / "ansible" / "roles" / "sample_submission_sinkhole"
ENDPOINT_POLICY_ROLE_DIR = ROOT / "ansible" / "roles" / "endpoint_sample_policy"
GPO_REFRESH_ROLE_DIR = ROOT / "ansible" / "roles" / "windows_gpo_refresh"
MICROSOFT_365_APPS_ROLE_DIR = ROOT / "ansible" / "roles" / "microsoft_365_apps"
AZURE_ARC_ONBOARD_ROLE_DIR = ROOT / "ansible" / "roles" / "azure_arc_onboard"
MDE_CLIENT_ONBOARD_ROLE_DIR = ROOT / "ansible" / "roles" / "mde_client_onboard"
MDE_WINDOWS_HOST_PREP_ROLE_DIR = ROOT / "ansible" / "roles" / "mde_windows_host_prep"
MDI_PERFORMANCE_ROLE_DIR = ROOT / "ansible" / "roles" / "mdi_sensor_performance"
HYBRID_HOST_PREP_ROLE_DIR = ROOT / "ansible" / "roles" / "hybrid_identity_host_prep"
HYBRID_SCOPE_ROLE_DIR = ROOT / "ansible" / "roles" / "hybrid_identity_scope"
HYBRID_JOIN_CLIENT_PREP_ROLE_DIR = ROOT / "ansible" / "roles" / "hybrid_join_client_prep"
MDI_ADCS_HOST_PREP_ROLE_DIR = ROOT / "ansible" / "roles" / "mdi_adcs_host_prep"
GPO_ROLE_DIRS = (
    ENDPOINT_POLICY_ROLE_DIR,
    ROOT / "ansible" / "roles" / "controlled_folder_access_policy",
    ROOT / "ansible" / "roles" / "credential_guard_policy",
    ROOT / "ansible" / "roles" / "defender_baseline",
)


def load_yaml(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def require_mapping(value: object, label: str) -> dict:
    require(isinstance(value, dict), f"{label} must be a mapping")
    return value


def role_names(vm: dict) -> set[str]:
    roles = vm.get("roles", [])
    require(isinstance(roles, list), f"{vm['hostname']} roles must be a list")
    return {str(role) for role in roles}


def validate() -> None:
    require((ROOT / "LICENSE").is_file(), "root LICENSE is required")
    actual_blueprint_ids = {path.name for path in (ROOT / "blueprints").iterdir() if path.is_dir()}
    require(actual_blueprint_ids == set(BLUEPRINT_SPECS), "unexpected Source blueprint directory set")
    roles_root = ROOT / "ansible" / "roles"
    for role_dir in roles_root.iterdir():
        if role_dir.is_dir():
            require((role_dir / "README.md").is_file(), f"source-local role lacks README: {role_dir.name}")
            version_data = require_mapping(
                load_yaml(role_dir / "meta" / "version.yml"),
                f"{role_dir.name} version metadata",
            )
            role_version = str(version_data.get("version", ""))
            require(
                re.fullmatch(r"\d+\.\d+\.\d+", role_version) is not None,
                f"{role_dir.name} version must be semantic x.y.z",
            )
            require(
                role_version != "0.1.0"
                or role_dir.name in {"hybrid_identity_scope", "hybrid_join_client_prep"},
                f"{role_dir.name} must not reuse the stale initial installed-role version",
            )
    for obsolete_path in (
        ROOT / "roles",
        ROOT / "zsec-mde-mdi-lab.yml",
        ROOT / "blueprints" / "ludus_hybrid_lab",
        ROOT / "tests" / "ranges",
        ROOT / "ansible" / "roles" / "mdi_v3_preflight",
        ROOT / "ansible" / "roles" / "windows_state_report",
    ):
        require(not obsolete_path.exists(), f"obsolete artifact must remain absent: {obsolete_path.relative_to(ROOT)}")

    export_attributes = EXPORT_ATTRIBUTES_PATH.read_text(encoding="utf-8")
    required_export_ignores = {f"{name} export-ignore" for name in PRIVATE_DOCUMENT_NAMES}
    require(
        required_export_ignores <= set(export_attributes.splitlines()),
        "public archive export-ignore boundary is incomplete",
    )
    private_document_paths = {ROOT / name for name in PRIVATE_DOCUMENT_NAMES}
    public_markdown_paths = {
        path
        for path in ROOT.rglob("*.md")
        if path not in private_document_paths and ".git" not in path.parts
    }
    for public_path in public_markdown_paths:
        public_text = public_path.read_text(encoding="utf-8")
        relative_path = public_path.relative_to(ROOT)
        for private_name in PRIVATE_DOCUMENT_NAMES:
            require(
                private_name not in public_text,
                f"public Markdown references private document {private_name}: {relative_path}",
            )
        require(
            re.search(
                r"/opt/ludus/users/(?!(?:<ludus-profile>|\$\{ludus_profile\}))(?:[^/\s`]+)",
                public_text,
            )
            is None,
            f"public Markdown contains an operator-specific Ludus profile: {relative_path}",
        )
        require(
            re.search(r"sp-[a-z0-9-]+-arc-onboard-\d{8}", public_text) is None,
            f"public Markdown contains a range-specific dated service-principal example: {relative_path}",
        )

    source = require_mapping(load_yaml(SOURCE_PATH), "source.yml")
    require(source.get("manifest_version") == 1, "source manifest_version must be 1")
    require(source.get("name") == "Defender XDR Lab for Ludus", "unexpected Source name")

    sinkhole_defaults = require_mapping(
        load_yaml(SINKHOLE_ROLE_DIR / "defaults" / "main.yml"),
        "sample_submission_sinkhole defaults",
    )
    canonical_domains = sinkhole_defaults.get("sample_submission_sinkhole_canonical_domains")
    require(
        isinstance(canonical_domains, list) and len(canonical_domains) == 17,
        "sample_submission_sinkhole must contain the 17-name reviewed corpus",
    )
    require(
        sinkhole_defaults.get("sample_submission_sinkhole_enabled") is True,
        "sample_submission_sinkhole must default to enabled",
    )
    sinkhole_tasks = (SINKHOLE_ROLE_DIR / "tasks" / "main.yml").read_text(encoding="utf-8")
    require(
        "Inspect entries owned by the sample-submission sinkhole role" in sinkhole_tasks
        and "Remove stale entries owned by the sample-submission sinkhole role"
        in sinkhole_tasks,
        "sample_submission_sinkhole must reconcile only its owned state",
    )
    endpoint_defaults = require_mapping(
        load_yaml(ENDPOINT_POLICY_ROLE_DIR / "defaults" / "main.yml"),
        "endpoint_sample_policy defaults",
    )
    require(
        endpoint_defaults.get("endpoint_sample_policy_state") == "blocked",
        "endpoint_sample_policy must default to blocked",
    )
    gpo_refresh_defaults = require_mapping(
        load_yaml(GPO_REFRESH_ROLE_DIR / "defaults" / "main.yml"),
        "windows_gpo_refresh defaults",
    )
    require(
        gpo_refresh_defaults.get("windows_gpo_refresh_enabled") is True,
        "windows_gpo_refresh must default to enabled",
    )
    gpo_refresh_tasks = (GPO_REFRESH_ROLE_DIR / "tasks" / "main.yml").read_text(encoding="utf-8")
    require(
        "gpupdate.exe /target:computer /force /wait:120" in gpo_refresh_tasks
        and "changed_when: false" in gpo_refresh_tasks,
        "windows_gpo_refresh must synchronize computer policy without reporting configuration drift",
    )
    microsoft_365_apps_defaults = require_mapping(
        load_yaml(MICROSOFT_365_APPS_ROLE_DIR / "defaults" / "main.yml"),
        "microsoft_365_apps defaults",
    )
    require(
        microsoft_365_apps_defaults.get("microsoft_365_apps_enabled") is True
        and microsoft_365_apps_defaults.get("microsoft_365_apps_product_id") == "O365ProPlusRetail"
        and str(microsoft_365_apps_defaults.get("microsoft_365_apps_edition")) == "64",
        "microsoft_365_apps must default to 64-bit Microsoft 365 Apps for enterprise",
    )
    microsoft_365_apps_tasks = (MICROSOFT_365_APPS_ROLE_DIR / "tasks" / "main.yml").read_text(encoding="utf-8")
    require(
        "Get-AuthenticodeSignature" in microsoft_365_apps_tasks
        and "stops before mutation" in (MICROSOFT_365_APPS_ROLE_DIR / "README.md").read_text(encoding="utf-8")
        and "TenantAssociationKey" not in microsoft_365_apps_tasks,
        "microsoft_365_apps must verify ODT and keep activation and tenant material out of automation",
    )
    for role_dir in GPO_ROLE_DIRS:
        role_tasks = (role_dir / "tasks" / "main.yml").read_text(encoding="utf-8")
        require(
            "defaults.ad_domain_admin" in role_tasks
            and "defaults.ad_domain_admin_password" in role_tasks
            and "become_method: runas" in role_tasks,
            f"{role_dir.name} must use the Ludus-configured domain administrator for GPO mutations",
        )
    defender_baseline_tasks = (ROOT / "ansible" / "roles" / "defender_baseline" / "tasks" / "main.yml").read_text(
        encoding="utf-8"
    )
    require(
        "AllowNetworkProtectionOnWinServer" in defender_baseline_tasks
        and "EnableNetworkProtection" in defender_baseline_tasks
        and "Invoke-GpoRegistryOperation" in defender_baseline_tasks
        and "$maximumAttempts = 4" in defender_baseline_tasks
        and "-2147024891" in defender_baseline_tasks
        and "Start-Sleep -Seconds $delaySeconds" in defender_baseline_tasks
        and "GPO write verification failed" in defender_baseline_tasks,
        "Defender baseline must configure Network Protection and bound transient GPO write retries",
    )
    defender_baseline_version = require_mapping(
        load_yaml(ROOT / "ansible" / "roles" / "defender_baseline" / "meta" / "version.yml"),
        "defender_baseline version",
    )
    require(
        str(defender_baseline_version.get("version")) == "0.1.3",
        "defender_baseline installed content version must be 0.1.3",
    )
    azure_arc_defaults = require_mapping(
        load_yaml(AZURE_ARC_ONBOARD_ROLE_DIR / "defaults" / "main.yml"),
        "azure_arc_onboard defaults",
    )
    controller_artifact_path = str(azure_arc_defaults.get("azure_arc_onboard_controller_artifact_path", ""))
    require(
        "defender-xdr-lab-protected/OnboardingScript.ps1" in controller_artifact_path
        and "/roles/" not in controller_artifact_path,
        "azure_arc_onboard artifact must live outside the Source-managed role directory",
    )
    azure_arc_tasks = (AZURE_ARC_ONBOARD_ROLE_DIR / "tasks" / "artifact.yml").read_text(encoding="utf-8")
    for required_fragment in (
        "execution_exit_code",
        "agent_state",
        "guest_artifact_removed",
        "No cloud or agent state was rolled back",
        "secret command output remains suppressed",
    ):
        require(
            required_fragment in azure_arc_tasks,
            f"azure_arc_onboard lacks sanitized failure behavior: {required_fragment}",
        )
    require(
        "{{ role_path }}/files/OnboardingScript.ps1" not in azure_arc_tasks,
        "azure_arc_onboard must not read its protected artifact from the managed role directory",
    )
    mde_client_defaults = require_mapping(
        load_yaml(MDE_CLIENT_ONBOARD_ROLE_DIR / "defaults" / "main.yml"),
        "mde_client_onboard defaults",
    )
    mde_controller_artifact_path = str(
        mde_client_defaults.get("mde_client_onboard_controller_artifact_path", "")
    )
    require(
        "defender-xdr-lab-protected/WindowsDefenderATPLocalOnboardingScript.cmd"
        in mde_controller_artifact_path
        and "/roles/" not in mde_controller_artifact_path,
        "mde_client_onboard artifact must live outside the Source-managed role directory",
    )
    mde_client_tasks = (MDE_CLIENT_ONBOARD_ROLE_DIR / "tasks" / "artifact.yml").read_text(encoding="utf-8")
    require(
        "mde_client_onboard_mode" not in mde_client_defaults
        and "mde_client_onboard_expected_hostname" not in mde_client_defaults
        and "mde_client_onboard_expected_hostname" not in mde_client_tasks,
        "mde_client_onboard must use artifact gating without mode or hostname restrictions",
    )
    for required_fragment in (
        "execution_exit_code",
        "onboarding_state",
        "sense_status",
        "guest_artifact_removed",
        "No cloud or sensor state was rolled back",
        "protected command output remains suppressed",
    ):
        require(
            required_fragment in mde_client_tasks,
            f"mde_client_onboard lacks sanitized failure behavior: {required_fragment}",
        )
    require(
        "{{ role_path }}/files/WindowsDefenderATPLocalOnboardingScript.cmd" not in mde_client_tasks,
        "mde_client_onboard must not read its protected artifact from the managed role directory",
    )
    mde_host_prep_defaults = require_mapping(
        load_yaml(MDE_WINDOWS_HOST_PREP_ROLE_DIR / "defaults" / "main.yml"),
        "mde_windows_host_prep defaults",
    )
    mde_host_prep_vars = require_mapping(
        load_yaml(MDE_WINDOWS_HOST_PREP_ROLE_DIR / "vars" / "main.yml"),
        "mde_windows_host_prep internal variables",
    )
    require(
        mde_host_prep_defaults.get("mde_windows_host_prep_enabled") is True
        and len(mde_host_prep_defaults) == 1,
        "mde_windows_host_prep must expose only its enabled switch",
    )
    require(
        mde_host_prep_vars.get("_mde_windows_host_prep_platform_url")
        == "https://go.microsoft.com/fwlink/?LinkID=870379&arch=x64&clcid=0x409"
        and mde_host_prep_vars.get("_mde_windows_host_prep_platform_path")
        == r"C:\ludus\updateplatform.exe"
        and str(mde_host_prep_vars.get("_mde_windows_host_prep_manual_update_baseline"))
        == "4.18.2001.10"
        and str(mde_host_prep_vars.get("_mde_windows_host_prep_minimum_platform_version"))
        == "4.18.2211.5"
        and str(mde_host_prep_vars.get("_mde_windows_host_prep_minimum_engine_version"))
        == "1.1.19900.2"
        and str(
            mde_host_prep_vars.get(
                "_mde_windows_host_prep_minimum_security_intelligence_version"
            )
        )
        == "1.391.345.0",
        "mde_windows_host_prep must use the current Microsoft x64 package and documented minimums",
    )
    require(
        not any(
            "password" in str(key).lower() or "token" in str(key).lower()
            for key in mde_host_prep_defaults | mde_host_prep_vars
        ),
        "mde_windows_host_prep must not accept credentials or tokens",
    )
    mde_host_prep_tasks = (MDE_WINDOWS_HOST_PREP_ROLE_DIR / "tasks" / "main.yml").read_text(
        encoding="utf-8"
    )
    for required_fragment in (
        "Get-MpComputerStatus",
        "Get-AuthenticodeSignature",
        "Microsoft Corporation",
        "Get-FileHash -LiteralPath $PlatformPath -Algorithm SHA256",
        "Update-MpSignature -UpdateSource MMPC",
        "Start-Process -FilePath $PlatformPath -Wait -PassThru",
        "$after.platform -lt $before.platform",
        "finally",
        "Remove-Item -LiteralPath $PlatformPath",
        "$Ansible.Changed",
    ):
        require(
            required_fragment in mde_host_prep_tasks,
            f"mde_windows_host_prep lacks required behavior: {required_fragment}",
        )
    require(
        "MDE.Windows" not in mde_host_prep_tasks
        and "azcmagent" not in mde_host_prep_tasks
        and "OnboardingState" not in mde_host_prep_tasks,
        "mde_windows_host_prep must not own Arc, MDE onboarding, or sensor state",
    )
    mde_host_prep_version = require_mapping(
        load_yaml(MDE_WINDOWS_HOST_PREP_ROLE_DIR / "meta" / "version.yml"),
        "mde_windows_host_prep version",
    )
    require(
        str(mde_host_prep_version.get("version")) == "0.1.2",
        "mde_windows_host_prep installed content version must be 0.1.2",
    )
    mdi_performance_defaults = require_mapping(
        load_yaml(MDI_PERFORMANCE_ROLE_DIR / "defaults" / "main.yml"),
        "mdi_sensor_performance defaults",
    )
    require(
        mdi_performance_defaults.get("mdi_sensor_performance_enabled") is True
        and mdi_performance_defaults.get("mdi_sensor_performance_allowed_domain_roles") == [3, 4, 5],
        "mdi_sensor_performance must support only member servers and domain controllers",
    )
    mdi_performance_tasks = (MDI_PERFORMANCE_ROLE_DIR / "tasks" / "main.yml").read_text(encoding="utf-8")
    require(
        "mdi_sensor_performance_allowed_domain_roles" in mdi_performance_tasks
        and "Unsupported MDI sensor host domain role" in mdi_performance_tasks
        and "High Performance power plan is not active" in mdi_performance_tasks,
        "mdi_sensor_performance must validate host type and the selected power plan",
    )
    mdi_performance_version = require_mapping(
        load_yaml(MDI_PERFORMANCE_ROLE_DIR / "meta" / "version.yml"),
        "mdi_sensor_performance version",
    )
    require(
        str(mdi_performance_version.get("version")) == "0.1.3",
        "mdi_sensor_performance installed content version must be 0.1.3",
    )
    require(
        not (ROOT / "ansible" / "roles" / "mdi_dc_performance").exists(),
        "the retired mdi_dc_performance role directory must remain absent",
    )
    hybrid_host_defaults = require_mapping(
        load_yaml(HYBRID_HOST_PREP_ROLE_DIR / "defaults" / "main.yml"),
        "hybrid_identity_host_prep defaults",
    )
    hybrid_connect_artifact_path = str(
        hybrid_host_defaults.get("hybrid_identity_host_prep_connect_installer_controller_path", "")
    )
    require(
        hybrid_host_defaults.get("hybrid_identity_host_prep_enabled") is True
        and hybrid_host_defaults.get("hybrid_identity_host_prep_connect_installer_guest_path")
        == r"C:\ludus\AzureADConnect.msi"
        and "hybrid_identity_host_prep_minimum_memory_gb" not in hybrid_host_defaults
        and "hybrid_identity_host_prep_minimum_system_disk_gb" not in hybrid_host_defaults
        and "hybrid_identity_host_prep_connect_minimum_version" not in hybrid_host_defaults
        and "hybrid_identity_host_prep_connect_installer_guest_directory" not in hybrid_host_defaults,
        "hybrid_identity_host_prep defaults are incorrect",
    )
    require(
        "defender-xdr-lab-protected/AzureADConnect.msi" in hybrid_connect_artifact_path
        and "/roles/" not in hybrid_connect_artifact_path,
        "the optional Connect MSI must live outside the managed role directory",
    )
    hybrid_host_tasks = (HYBRID_HOST_PREP_ROLE_DIR / "tasks" / "main.yml").read_text(encoding="utf-8")
    for required_fragment in (
        "NET-Framework-45-Core",
        "SystemDefaultTlsVersions",
        "SchUseStrongCrypto",
        "SCHANNEL",
        "Set-ExecutionPolicy",
        "RemoteSigned",
        "Get-AuthenticodeSignature",
        "Microsoft Corporation",
        "AzureADConnect.msi was not found",
    ):
        require(
            required_fragment in hybrid_host_tasks,
            f"hybrid_identity_host_prep lacks required behavior: {required_fragment}",
        )
    for forbidden_fragment in (
        "MinimumMemoryGb",
        "MinimumSystemDiskGb",
        "MinimumVersion",
        "ProductVersion",
        "productComparable",
        "Win32_LogicalDisk",
        "TotalPhysicalMemory",
        "Desktop Experience",
    ):
        require(
            forbidden_fragment not in hybrid_host_tasks,
            f"hybrid_identity_host_prep must not enforce support policy: {forbidden_fragment}",
        )
    require(
        "AccessKey" not in hybrid_host_tasks and "Azure ATP sensor" not in hybrid_host_tasks,
        "hybrid_identity_host_prep must not stage or install tenant-bound MDI material",
    )
    hybrid_host_version = require_mapping(
        load_yaml(HYBRID_HOST_PREP_ROLE_DIR / "meta" / "version.yml"),
        "hybrid_identity_host_prep version",
    )
    require(
        str(hybrid_host_version.get("version")) == "0.1.4",
        "hybrid_identity_host_prep installed content version must be 0.1.4",
    )
    hybrid_scope_defaults = require_mapping(
        load_yaml(HYBRID_SCOPE_ROLE_DIR / "defaults" / "main.yml"),
        "hybrid_identity_scope defaults",
    )
    require(
        hybrid_scope_defaults.get("hybrid_identity_upn_suffix") == ""
        and hybrid_scope_defaults.get("hybrid_identity_scope_group") == "Entra Sync Scope"
        and hybrid_scope_defaults.get("hybrid_identity_scope_member_groups") == ["Hybrid Lab Users"]
        and hybrid_scope_defaults.get("hybrid_identity_scope_computers") == []
        and "hybrid_identity_upn_users" not in hybrid_scope_defaults,
        "hybrid_identity_scope defaults are incorrect",
    )
    hybrid_scope_version = require_mapping(
        load_yaml(HYBRID_SCOPE_ROLE_DIR / "meta" / "version.yml"),
        "hybrid_identity_scope version",
    )
    require(
        str(hybrid_scope_version.get("version")) == "0.2.2",
        "hybrid_identity_scope installed content version must be 0.2.2",
    )
    hybrid_scope_tasks = (HYBRID_SCOPE_ROLE_DIR / "tasks" / "main.yml").read_text(encoding="utf-8")
    for required_fragment in (
        "Add-ADGroupMember",
        "Set-ADForest",
        "Set-ADUser",
        "Get-ADGroupMember",
        "Compare-Object",
        "ludus_users",
        "direct_groups",
        "direct_computers",
        "microsoft.ad.computer",
        "UPN validation failed",
        "hybrid_identity_upn_suffix is empty",
    ):
        require(
            required_fragment in hybrid_scope_tasks,
            f"hybrid_identity_scope lacks required behavior: {required_fragment}",
        )
    require(
        "defaults.ad_domain_admin" in hybrid_scope_tasks
        and "defaults.ad_domain_admin_password" in hybrid_scope_tasks
        and "become_method: runas" in hybrid_scope_tasks,
        "hybrid_identity_scope must use the Ludus-configured domain administrator",
    )
    require(
        "hybrid_identity_upn_users" not in hybrid_scope_tasks
        and not (ROOT / "ansible" / "roles" / "hybrid_identity_upn").exists(),
        "hybrid_identity_scope must replace the retired UPN-only role without a duplicate user list",
    )
    hybrid_join_client_defaults = require_mapping(
        load_yaml(HYBRID_JOIN_CLIENT_PREP_ROLE_DIR / "defaults" / "main.yml"),
        "hybrid_join_client_prep defaults",
    )
    require(
        hybrid_join_client_defaults.get("hybrid_join_client_prep_enabled") is True
        and hybrid_join_client_defaults.get("hybrid_join_tenant_id") == ""
        and hybrid_join_client_defaults.get("hybrid_join_tenant_name") == ""
        and len(hybrid_join_client_defaults) == 3,
        "hybrid_join_client_prep defaults are incorrect",
    )
    hybrid_join_client_version = require_mapping(
        load_yaml(HYBRID_JOIN_CLIENT_PREP_ROLE_DIR / "meta" / "version.yml"),
        "hybrid_join_client_prep version",
    )
    require(
        str(hybrid_join_client_version.get("version")) == "0.1.2",
        "hybrid_join_client_prep installed content version must be 0.1.2",
    )
    hybrid_join_client_tasks = (
        HYBRID_JOIN_CLIENT_PREP_ROLE_DIR / "tasks" / "main.yml"
    ).read_text(encoding="utf-8")
    for required_fragment in (
        r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CDJ\AAD",
        "TenantId",
        "TenantName",
        "DomainRole",
        "discovery_scope = 'local-client'",
        "must either both be",
    ):
        require(
            required_fragment in hybrid_join_client_tasks,
            f"hybrid_join_client_prep lacks required behavior: {required_fragment}",
        )
    require(
        "azureADId" not in hybrid_join_client_tasks
        and "azureADName" not in hybrid_join_client_tasks
        and "New-GPO" not in hybrid_join_client_tasks,
        "hybrid_join_client_prep must not publish a forest-wide SCP or create a broad GPO",
    )
    mdi_adcs_defaults = require_mapping(
        load_yaml(MDI_ADCS_HOST_PREP_ROLE_DIR / "defaults" / "main.yml"),
        "mdi_adcs_host_prep defaults",
    )
    require(
        mdi_adcs_defaults
        == {
            "mdi_adcs_host_prep_enabled": True,
            "mdi_adcs_host_prep_audit_filter": 127,
        },
        "mdi_adcs_host_prep defaults are incorrect",
    )
    mdi_adcs_tasks = (MDI_ADCS_HOST_PREP_ROLE_DIR / "tasks" / "main.yml").read_text(
        encoding="utf-8"
    )
    mdi_adcs_version = require_mapping(
        load_yaml(MDI_ADCS_HOST_PREP_ROLE_DIR / "meta" / "version.yml"),
        "mdi_adcs_host_prep version",
    )
    require(
        str(mdi_adcs_version.get("version")) == "0.2.0",
        "mdi_adcs_host_prep installed content version must be 0.2.0",
    )
    for required_fragment in (
        "ADCS-Cert-Authority",
        "MDI v3 AD CS target",
        "0CCE9221-69AE-11D9-BED3-505054503030",
        "$activeCaProperties.PSObject.Properties['AuditFilter']",
        "$null -eq $auditFilterBefore",
        "certutil.exe -setreg 'CA\\AuditFilter'",
        "Restart-Service -Name CertSvc",
        "W32Time",
        "$Ansible.Changed = $auditChanged -or $filterChanged -or $serviceChanged",
    ):
        require(
            required_fragment in mdi_adcs_tasks,
            f"mdi_adcs_host_prep lacks required behavior: {required_fragment}",
        )
    require(
        "Get-ItemPropertyValue -Path $activeCaPath -Name AuditFilter -ErrorAction SilentlyContinue"
        not in mdi_adcs_tasks
        and "NET Framework" not in mdi_adcs_tasks
        and "dotnet" not in mdi_adcs_tasks.lower(),
        "mdi_adcs_host_prep must treat a missing AuditFilter as unconfigured and avoid v2-only .NET installation",
    )
    require(
        "AccessKey" not in mdi_adcs_tasks
        and "Azure ATP sensor setup" not in mdi_adcs_tasks
        and "MDE.Windows" not in mdi_adcs_tasks,
        "mdi_adcs_host_prep must not own tenant-bound sensor or MDE state",
    )

    required_blueprint_keys = {
        "manifest_version",
        "id",
        "name",
        "description",
        "version",
        "config",
    }
    required_vm_keys = {
        "vm_name",
        "hostname",
        "template",
        "vlan",
        "ip_last_octet",
        "ram_gb",
        "cpus",
    }
    required_workstation_roles = {
        "5tuk0v.ludus_asr_presets",
        "5tuk0v.sample_submission_sinkhole",
        "5tuk0v.microsoft_365_apps",
        "5tuk0v.windows_gpo_refresh",
    }
    validated_hosts: dict[str, dict[str, dict]] = {}
    validated_configs: dict[str, dict] = {}

    for blueprint_id, spec in BLUEPRINT_SPECS.items():
        blueprint_dir = ROOT / "blueprints" / blueprint_id
        blueprint_path = blueprint_dir / "blueprint.yml"
        range_path = blueprint_dir / "range-config.yml"
        requirements_path = blueprint_dir / "requirements.yml"
        label = f"blueprint {blueprint_id}"

        blueprint = require_mapping(load_yaml(blueprint_path), f"{label} metadata")
        require(required_blueprint_keys <= blueprint.keys(), f"{label} metadata is incomplete")
        require(blueprint["manifest_version"] == 1, f"{label} manifest_version must be 1")
        require(blueprint["id"] == blueprint_id, f"{label} id is incorrect")
        require(
            re.fullmatch(r"\d+\.\d+\.\d+", str(blueprint["version"])) is not None,
            f"{label} version must be semantic x.y.z",
        )
        require(blueprint["version"] == spec["version"], f"{label} version is incorrect")
        require(blueprint["config"] == range_path.name, f"{label} config path is incorrect")

        requirements = require_mapping(load_yaml(requirements_path), f"{label} requirements")
        for section in ("roles", "collections"):
            require(isinstance(requirements.get(section), list), f"{label} {section} must be a list")
        for section, expected_entries in spec["requirements"].items():
            actual_entries = {
                (str(entry.get("name")), str(entry.get("version")))
                for entry in requirements[section]
                if isinstance(entry, dict)
            }
            require(actual_entries == expected_entries, f"{label} {section} dependencies are incorrect")
        if blueprint_id in {"adcs-mdi", "complete"}:
            adcs_role_requirement = next(
                entry
                for entry in requirements["roles"]
                if isinstance(entry, dict) and entry.get("name") == "badsectorlabs.ludus_adcs"
            )
            require(
                adcs_role_requirement.get("src") == "https://github.com/badsectorlabs/ludus_adcs",
                f"{label} must pin the reviewed off-Galaxy BSL AD CS source",
            )

        range_lines = range_path.read_text(encoding="utf-8").splitlines()
        require(
            any(line.startswith("# yaml-language-server: $schema=") for line in range_lines[:3]),
            f"{label} schema header is missing",
        )
        range_config = require_mapping(load_yaml(range_path), f"{label} range config")
        vms = range_config.get("ludus")
        require(isinstance(vms, list) and vms, f"{label} range config must contain VMs")

        addresses: set[tuple[int, int]] = set()
        hostnames: set[str] = set()
        hosts: dict[str, dict] = {}
        for index, raw_vm in enumerate(vms):
            vm = require_mapping(raw_vm, f"{label} ludus[{index}]")
            require(required_vm_keys <= vm.keys(), f"{label} ludus[{index}] is incomplete")
            require("{{ range_id }}" in vm["vm_name"], f"{label} ludus[{index}] lacks range_id")
            hostname = str(vm["hostname"])
            require(0 < len(hostname) <= 15, f"{label} has invalid Windows hostname: {hostname}")
            require(hostname not in hostnames, f"{label} has duplicate hostname: {hostname}")
            hostnames.add(hostname)
            hosts[hostname] = vm
            address = (int(vm["vlan"]), int(vm["ip_last_octet"]))
            require(address not in addresses, f"{label} has duplicate VLAN/address: {address}")
            addresses.add(address)
            require(isinstance(vm.get("windows"), dict), f"{label} {hostname} must define windows")
            require(isinstance(vm.get("domain"), dict), f"{label} {hostname} must define domain")
            if "role_vars" in vm:
                require(isinstance(vm["role_vars"], dict), f"{label} {hostname} role_vars must be a mapping")
            testing = require_mapping(vm.get("testing"), f"{label} {hostname} testing")
            require(testing.get("snapshot") is True, f"{label} {hostname} testing snapshots must default on")
            require(
                testing.get("block_internet") is True,
                f"{label} {hostname} testing internet blocking must default on",
            )
            ansible_groups = vm.get("ansible_groups", [])
            require(isinstance(ansible_groups, list), f"{label} {hostname} ansible_groups must be a list")
            require(
                len(ansible_groups) == len(set(ansible_groups)),
                f"{label} {hostname} ansible_groups contains duplicates",
            )

        require(set(hosts) == spec["hosts"], f"{label} has an unexpected host set")
        dc01 = hosts["DC01"]
        dc_roles = [str(role) for role in dc01.get("roles", [])]
        dc_vars = require_mapping(dc01.get("role_vars"), f"{label} DC01 role_vars")
        require(
            dc_roles.count("5tuk0v.ludus_asr_presets") == 1
            and dc_vars.get("ludus_asr_presets_preset") == "windows_server_2022"
            and dc_vars.get("ludus_asr_presets_mode") == "audit",
            f"{label} DC01 must use the Server 2022 ASR Audit preset",
        )
        require(
            dc_roles.index("5tuk0v.defender_baseline")
            < dc_roles.index("5tuk0v.ludus_asr_presets")
            < dc_roles.index("5tuk0v.windows_gpo_refresh"),
            f"{label} DC01 must configure ASR after the Defender baseline and before policy refresh",
        )
        actual_mde_targets = {
            hostname
            for hostname, vm in hosts.items()
            if "mde_targets" in vm.get("ansible_groups", [])
        }
        require(actual_mde_targets == spec["mde_targets"], f"{label} mde_targets membership is incorrect")
        defaults = require_mapping(range_config.get("defaults"), f"{label} defaults")
        require(defaults.get("snapshot_with_RAM") is True, f"{label} testing snapshots must include RAM")

        for hostname, vm in hosts.items():
            roles = [str(role) for role in vm.get("roles", [])]
            is_mde_target = hostname in spec["mde_targets"]
            require(
                ("5tuk0v.mde_windows_host_prep" in roles) is is_mde_target,
                f"{label} {hostname} MDE host preparation scope is incorrect",
            )
            if not is_mde_target:
                continue
            role_vars = require_mapping(vm.get("role_vars"), f"{label} {hostname} role_vars")
            require(
                role_vars.get("mde_windows_host_prep_enabled") is True,
                f"{label} {hostname} MDE host preparation must be enabled",
            )
            if "5tuk0v.azure_arc_onboard" in roles:
                require(
                    roles.index("5tuk0v.mde_windows_host_prep")
                    < roles.index("5tuk0v.azure_arc_onboard"),
                    f"{label} {hostname} must prepare Defender before Arc onboarding",
                )
            if "5tuk0v.mde_client_onboard" in roles:
                require(
                    roles.index("5tuk0v.mde_windows_host_prep")
                    < roles.index("5tuk0v.mde_client_onboard"),
                    f"{label} {hostname} must prepare Defender before direct MDE onboarding",
                )

        if "CA01" in hosts:
            ca01 = hosts["CA01"]
            ca_roles = [str(role) for role in ca01.get("roles", [])]
            ca_vars = require_mapping(ca01.get("role_vars"), f"{label} CA01 role_vars")
            require(
                "5tuk0v.ludus_asr_presets" in ca_roles
                and ca_vars.get("ludus_asr_presets_preset") == "windows_server_2022"
                and ca_vars.get("ludus_asr_presets_mode") == "audit",
                f"{label} CA01 must use the Server 2022 ASR Audit preset",
            )
            require(
                ca_roles.index("5tuk0v.ludus_asr_presets")
                < ca_roles.index("5tuk0v.windows_gpo_refresh"),
                f"{label} CA01 must configure ASR before policy refresh",
            )

        expected_domain_roles = {
            "DC01": "primary-dc",
            "SRV01": "member",
            "WKS01": "member",
            "WKS02": "member",
            "SYNC01": "member",
            "CA01": "member",
        }
        for hostname, domain_role in expected_domain_roles.items():
            if hostname not in hosts:
                continue
            domain = require_mapping(hosts[hostname]["domain"], f"{label} {hostname} domain")
            require(domain.get("fqdn") == "defender.test", f"{label} {hostname} must use defender.test")
            require(domain.get("role") == domain_role, f"{label} {hostname} domain role is incorrect")

        if spec["kind"] == "complete":
            expected_server_sizing = (6, 2)
            for hostname in ("DC01", "SYNC01", "CA01"):
                require(
                    (hosts[hostname].get("ram_gb"), hosts[hostname].get("cpus")) == expected_server_sizing,
                    f"{label} {hostname} lab sizing is incorrect",
                )
            for hostname in ("WKS01", "WKS02"):
                require(
                    hosts[hostname].get("template") == "win11-25h2-x64-enterprise-template"
                    and hosts[hostname].get("ram_gb") == 4
                    and hosts[hostname].get("cpus") == 2,
                    f"{label} {hostname} client sizing or template is incorrect",
                )
            require(
                sum(int(vm["ram_gb"]) for vm in hosts.values()) == 26
                and sum(int(vm["cpus"]) for vm in hosts.values()) == 10,
                f"{label} total guest resource allocation is incorrect",
            )

            dc01 = hosts["DC01"]
            expected_dc_roles = {
                "5tuk0v.ludus_asr_presets",
                "5tuk0v.endpoint_sample_policy",
                "5tuk0v.sample_submission_sinkhole",
                "5tuk0v.controlled_folder_access_policy",
                "5tuk0v.credential_guard_policy",
                "5tuk0v.defender_baseline",
                "5tuk0v.mdi_sensor_performance",
                "badsectorlabs.ludus_windows_utils.ludus_bulk_ad_content",
                "5tuk0v.hybrid_identity_scope",
                "5tuk0v.windows_gpo_refresh",
                "5tuk0v.mde_windows_host_prep",
                "5tuk0v.azure_arc_onboard",
            }
            require(role_names(dc01) == expected_dc_roles, f"{label} DC01 roles are incorrect")
            dc_vars = require_mapping(dc01.get("role_vars"), f"{label} DC01 role_vars")
            require(
                {
                    (item.get("name"), item.get("path"))
                    for item in dc_vars.get("hybrid_identity_scope_computers", [])
                    if isinstance(item, dict)
                }
                == {
                    ("WKS01", "OU=Devices,OU=EntraSync,DC=defender,DC=test"),
                    ("WKS02", "OU=Devices,OU=EntraSync,DC=defender,DC=test"),
                },
                f"{label} both workstations must be included in hybrid sync scope",
            )
            require(
                dc_vars.get("mdi_sensor_performance_enabled") is True,
                f"{label} DC01 MDI performance preparation must be enabled",
            )

            required_workstation_roles = {
                "5tuk0v.ludus_asr_presets",
                "5tuk0v.sample_submission_sinkhole",
                "5tuk0v.microsoft_365_apps",
                "5tuk0v.hybrid_join_client_prep",
                "5tuk0v.windows_gpo_refresh",
            }
            for hostname in ("WKS01", "WKS02"):
                client = hosts[hostname]
                expected_client_roles = set(required_workstation_roles)
                if hostname == "WKS02":
                    expected_client_roles |= {
                        "5tuk0v.mde_windows_host_prep",
                        "5tuk0v.mde_client_onboard",
                    }
                require(role_names(client) == expected_client_roles, f"{label} {hostname} roles are incorrect")
                client_vars = require_mapping(client.get("role_vars"), f"{label} {hostname} role_vars")
                require(
                    client_vars.get("hybrid_join_client_prep_enabled") is True
                    and client_vars.get("microsoft_365_apps_enabled") is True
                    and client_vars.get("ludus_asr_presets_preset") == "windows_11_25h2"
                    and "hybrid_join_tenant_id" in client_vars
                    and "hybrid_join_tenant_name" in client_vars
                    and (client_vars.get("hybrid_join_tenant_id") == "")
                    == (client_vars.get("hybrid_join_tenant_name") == ""),
                    f"{label} {hostname} hybrid-join/app configuration is incorrect",
                )
                if hostname == "WKS01":
                    require("ansible_groups" not in client, f"{label} WKS01 must remain MDE-negative")
                else:
                    require("mde_targets" in client.get("ansible_groups", []), f"{label} WKS02 must be MDE-positive")

            sync01 = hosts["SYNC01"]
            require(
                {"5tuk0v.hybrid_identity_host_prep", "5tuk0v.mdi_sensor_performance"}
                <= role_names(sync01),
                f"{label} SYNC01 hybrid identity and MDI roles are incomplete",
            )
            ca01 = hosts["CA01"]
            require(
                {"badsectorlabs.ludus_adcs", "5tuk0v.mdi_adcs_host_prep", "5tuk0v.mdi_sensor_performance"}
                <= role_names(ca01),
                f"{label} CA01 AD CS and MDI roles are incomplete",
            )
            ca_vars = require_mapping(ca01.get("role_vars"), f"{label} CA01 role_vars")
            require(
                ca_vars.get("mdi_adcs_host_prep_enabled") is True
                and ca_vars.get("mdi_sensor_performance_enabled") is True
                and all(
                    ca_vars.get(f"ludus_adcs_{name}") is True
                    for name in (
                        "esc1", "esc2", "esc3", "esc3_cra", "esc4", "esc5", "esc6", "esc7",
                        "esc8", "esc9", "esc10", "esc10_case1", "esc10_case2", "esc11", "esc13",
                        "esc14", "esc15", "esc16",
                    )
                ),
                f"{label} CA01 must enable the reviewed AD CS and MDI v3 configuration",
            )
            validated_hosts[blueprint_id] = hosts
            validated_configs[blueprint_id] = range_config
            continue

        if spec["kind"] in {"hybrid", "hybrid-join"}:
            dc01 = hosts["DC01"]
            expected_dc_roles = {
                "5tuk0v.ludus_asr_presets",
                "5tuk0v.endpoint_sample_policy",
                "5tuk0v.sample_submission_sinkhole",
                "5tuk0v.controlled_folder_access_policy",
                "5tuk0v.credential_guard_policy",
                "5tuk0v.defender_baseline",
                "5tuk0v.mdi_sensor_performance",
                "badsectorlabs.ludus_windows_utils.ludus_bulk_ad_content",
                "5tuk0v.hybrid_identity_scope",
                "5tuk0v.windows_gpo_refresh",
                "5tuk0v.mde_windows_host_prep",
                "5tuk0v.azure_arc_onboard",
            }
            require(role_names(dc01) == expected_dc_roles, f"{label} DC01 roles are incorrect")
            require(str(dc01["vm_name"]).endswith("-dc01-mde"), f"{label} DC01 VM name must expose MDE intent")
            require(
                dc01.get("ram_gb") == 6 and dc01.get("cpus") == 2,
                f"{label} DC01 lab sizing is incorrect",
            )
            dc_role_order = [str(role) for role in dc01["roles"]]
            require(
                dc_role_order.index("badsectorlabs.ludus_windows_utils.ludus_bulk_ad_content")
                < dc_role_order.index("5tuk0v.hybrid_identity_scope"),
                f"{label} must create users before scope reconciliation",
            )
            dc_vars = require_mapping(dc01.get("role_vars"), f"{label} DC01 role_vars")
            require(dc_vars.get("endpoint_sample_policy_state") == "blocked", f"{label} sample policy must be blocked")
            require(dc_vars.get("controlled_folder_access_policy_state") == "native", f"{label} DC01 CFA must be native")
            require(dc_vars.get("credential_guard_policy_state") == "native", f"{label} DC01 Credential Guard must be native")
            require(dc_vars.get("defender_baseline_enabled") is True, f"{label} DC01 Defender baseline must be enabled")
            require(dc_vars.get("mdi_sensor_performance_enabled") is True, f"{label} DC01 MDI High Performance preparation must be enabled")
            require(dc_vars.get("mde_windows_host_prep_enabled") is True, f"{label} DC01 MDE host preparation must be enabled")
            require(dc_vars.get("ludus_ad_content_mode") == "custom", f"{label} BSL content mode must be custom")
            require(
                dc_vars.get("hybrid_identity_upn_suffix") == ""
                and dc_vars.get("hybrid_identity_scope_group") == "Entra Sync Scope"
                and dc_vars.get("hybrid_identity_scope_member_groups") == ["Hybrid Lab Users"]
                and "hybrid_identity_upn_users" not in dc_vars,
                f"{label} hybrid scope input contract is incorrect",
            )
            require("badsectorlabs.ludus_adcs" not in role_names(dc01), f"{label} DC01 must not install AD CS")

            expected_ous = [
                {"name": "EntraSync", "path": "DC=defender,DC=test"},
                {"name": "Users", "path": "OU=EntraSync,DC=defender,DC=test"},
                {"name": "Groups", "path": "OU=EntraSync,DC=defender,DC=test"},
            ]
            if spec["kind"] == "hybrid-join":
                expected_ous.append(
                    {"name": "Devices", "path": "OU=EntraSync,DC=defender,DC=test"}
                )
            require(dc_vars.get("ludus_organisation_units") == expected_ous, f"{label} OU fixture is incorrect")
            expected_scope_computers = (
                [
                    {
                        "name": "WKS01",
                        "path": "OU=Devices,OU=EntraSync,DC=defender,DC=test",
                    }
                ]
                if spec["kind"] == "hybrid-join"
                else None
            )
            if spec["kind"] == "hybrid-join":
                require(
                    dc_vars.get("hybrid_identity_scope_computers") == expected_scope_computers,
                    f"{label} computer sync scope is incorrect",
                )
            else:
                require(
                    "hybrid_identity_scope_computers" not in dc_vars,
                    f"{label} must retain its identity-only scope input",
                )
            expected_groups = {
                "global": [
                    {
                        "name": "Hybrid Lab Users",
                        "path": "OU=Groups,OU=EntraSync,DC=defender,DC=test",
                    },
                    {
                        "name": "Entra Sync Scope",
                        "path": "OU=Groups,OU=EntraSync,DC=defender,DC=test",
                    },
                ],
                "domainlocal": [],
                "universal": [],
            }
            require(dc_vars.get("ludus_groups") == expected_groups, f"{label} group fixture is incorrect")
            users = dc_vars.get("ludus_users")
            require(isinstance(users, list), f"{label} user fixture must be a list")
            users_by_name = {
                str(user.get("name")): user
                for user in users
                if isinstance(user, dict)
            }
            expected_users = {"sync.alice", "sync.bob"}
            require(set(users_by_name) == expected_users, f"{label} user fixture is incorrect")
            for username in ("sync.alice", "sync.bob"):
                user = users_by_name[username]
                require(
                    user.get("path") == "OU=Users,OU=EntraSync,DC=defender,DC=test"
                    and user.get("groups") == ["Hybrid Lab Users", "Entra Sync Scope"]
                    and user.get("password_never_expires") is True,
                    f"{label} {username} sync scope is incorrect",
                )
            require(
                {user.get("password") for user in users_by_name.values()} == {"LabOnly-Passw0rd!"},
                f"{label} must use the documented disposable fixture password",
            )

            sync01 = hosts["SYNC01"]
            expected_sync_roles = {
                "5tuk0v.hybrid_identity_host_prep",
                "5tuk0v.mdi_sensor_performance",
                "5tuk0v.ludus_asr_presets",
                "5tuk0v.sample_submission_sinkhole",
                "5tuk0v.windows_gpo_refresh",
                "5tuk0v.mde_windows_host_prep",
                "5tuk0v.azure_arc_onboard",
            }
            require(role_names(sync01) == expected_sync_roles, f"{label} SYNC01 roles are incorrect")
            require(str(sync01["vm_name"]).endswith("-sync01-mde"), f"{label} SYNC01 VM name must expose MDE intent")
            expected_sync_sizing = (6, 2)
            require(
                (sync01.get("ram_gb"), sync01.get("cpus")) == expected_sync_sizing,
                f"{label} SYNC01 lab sizing is incorrect",
            )
            sync_vars = require_mapping(sync01.get("role_vars"), f"{label} SYNC01 role_vars")
            require(
                sync_vars.get("hybrid_identity_host_prep_enabled") is True
                and "hybrid_identity_host_prep_minimum_memory_gb" not in sync_vars
                and "hybrid_identity_host_prep_minimum_system_disk_gb" not in sync_vars
                and "hybrid_identity_host_prep_connect_minimum_version" not in sync_vars,
                f"{label} SYNC01 prerequisite contract is incorrect",
            )
            require(
                sync_vars.get("mdi_sensor_performance_enabled") is True
                and "mdi_sensor_performance_allowed_domain_roles" not in sync_vars,
                f"{label} SYNC01 must use the MDI performance role's default host-role allow-list",
            )
            require(sync_vars.get("ludus_asr_presets_preset") == "windows_server_2022", f"{label} SYNC01 ASR preset is incorrect")
            require(sync_vars.get("ludus_asr_presets_mode") == "audit", f"{label} SYNC01 ASR mode must be audit")
            require(sync_vars.get("mde_windows_host_prep_enabled") is True, f"{label} SYNC01 MDE host preparation must be enabled")
            require(
                all("5tuk0v.mde_client_onboard" not in role_names(vm) for vm in hosts.values()),
                f"{label} must use only the Defender for Servers MDE path",
            )

            if spec["kind"] == "hybrid-join":
                wks01 = hosts["WKS01"]
                expected_hybrid_join_workstation_roles = required_workstation_roles | {
                    "5tuk0v.hybrid_join_client_prep"
                }
                require(
                    role_names(wks01) == expected_hybrid_join_workstation_roles,
                    f"{label} WKS01 roles are incorrect",
                )
                require(
                    str(wks01["vm_name"]).endswith("-wks01")
                    and wks01.get("template") == "win11-25h2-x64-enterprise-template"
                    and "ansible_groups" not in wks01,
                    f"{label} WKS01 must remain the stock EDR-negative workstation",
                )
                wks_vars = require_mapping(wks01.get("role_vars"), f"{label} WKS01 role_vars")
                require(
                    wks_vars.get("hybrid_join_client_prep_enabled") is True
                    and wks_vars.get("hybrid_join_tenant_id") == ""
                    and wks_vars.get("hybrid_join_tenant_name") == ""
                    and wks_vars.get("microsoft_365_apps_enabled") is True,
                    f"{label} WKS01 targeted discovery contract is incorrect",
                )
                require(
                    "5tuk0v.mde_windows_host_prep" not in role_names(wks01)
                    and "5tuk0v.azure_arc_onboard" not in role_names(wks01)
                    and "5tuk0v.mde_client_onboard" not in role_names(wks01),
                    f"{label} WKS01 must not receive an MDE path",
                )

            validated_hosts[blueprint_id] = hosts
            validated_configs[blueprint_id] = range_config
            continue

        if spec["kind"] == "adcs":
            dc01 = hosts["DC01"]
            expected_dc_roles = {
                "5tuk0v.ludus_asr_presets",
                "5tuk0v.endpoint_sample_policy",
                "5tuk0v.sample_submission_sinkhole",
                "5tuk0v.controlled_folder_access_policy",
                "5tuk0v.credential_guard_policy",
                "5tuk0v.defender_baseline",
                "5tuk0v.mdi_sensor_performance",
                "5tuk0v.windows_gpo_refresh",
                "5tuk0v.mde_windows_host_prep",
                "5tuk0v.azure_arc_onboard",
            }
            require(role_names(dc01) == expected_dc_roles, f"{label} DC01 roles are incorrect")
            require(str(dc01["vm_name"]).endswith("-dc01-mde"), f"{label} DC01 VM name must expose MDE intent")
            require(dc01.get("template") == "win2022-server-x64-template", f"{label} DC01 must remain Server 2022")
            dc_vars = require_mapping(dc01.get("role_vars"), f"{label} DC01 role_vars")
            require(
                dc_vars.get("endpoint_sample_policy_state") == "blocked"
                and dc_vars.get("controlled_folder_access_policy_state") == "native"
                and dc_vars.get("credential_guard_policy_state") == "native"
                and dc_vars.get("defender_baseline_enabled") is True,
                f"{label} DC01 Defender policy contract is incorrect",
            )
            require(
                dc_vars.get("mdi_sensor_performance_enabled") is True,
                f"{label} DC01 MDI performance preparation must be enabled",
            )
            require(dc_vars.get("mde_windows_host_prep_enabled") is True, f"{label} DC01 MDE host preparation must be enabled")
            require("badsectorlabs.ludus_adcs" not in role_names(dc01), f"{label} DC01 must not install AD CS")
            require(
                "badsectorlabs.ludus_windows_utils.ludus_bulk_ad_content" not in role_names(dc01)
                and "ludus_users" not in dc_vars,
                f"{label} must not add bulk AD content to DC01",
            )

            ca01 = hosts["CA01"]
            expected_ca_roles = {
                "badsectorlabs.ludus_adcs",
                "5tuk0v.ludus_asr_presets",
                "5tuk0v.mdi_adcs_host_prep",
                "5tuk0v.mdi_sensor_performance",
                "5tuk0v.sample_submission_sinkhole",
                "5tuk0v.windows_gpo_refresh",
                "5tuk0v.mde_windows_host_prep",
                "5tuk0v.azure_arc_onboard",
            }
            require(role_names(ca01) == expected_ca_roles, f"{label} CA01 roles are incorrect")
            require(str(ca01["vm_name"]).endswith("-ca01-mde"), f"{label} CA01 VM name must expose MDE intent")
            require(ca01.get("template") == "win2022-server-x64-template", f"{label} CA01 must remain Server 2022")
            require(ca01.get("ram_gb") == 6 and ca01.get("cpus") == 2, f"{label} CA01 lab sizing is incorrect")
            ca_role_order = [str(role) for role in ca01["roles"]]
            require(
                ca_role_order.index("badsectorlabs.ludus_adcs")
                < ca_role_order.index("5tuk0v.mdi_adcs_host_prep")
                < ca_role_order.index("5tuk0v.mdi_sensor_performance"),
                f"{label} must install the CA before validating MDI prerequisites",
            )
            ca_vars = require_mapping(ca01.get("role_vars"), f"{label} CA01 role_vars")
            expected_esc_vars = {
                "ludus_adcs_esc1",
                "ludus_adcs_esc2",
                "ludus_adcs_esc3",
                "ludus_adcs_esc3_cra",
                "ludus_adcs_esc4",
                "ludus_adcs_esc5",
                "ludus_adcs_esc6",
                "ludus_adcs_esc7",
                "ludus_adcs_esc8",
                "ludus_adcs_esc9",
                "ludus_adcs_esc10",
                "ludus_adcs_esc10_case1",
                "ludus_adcs_esc10_case2",
                "ludus_adcs_esc11",
                "ludus_adcs_esc13",
                "ludus_adcs_esc14",
                "ludus_adcs_esc15",
                "ludus_adcs_esc16",
            }
            require(
                all(ca_vars.get(name) is True for name in expected_esc_vars),
                f"{label} must explicitly enable the complete reviewed BSL ESC set",
            )
            require(
                ca_vars.get("ludus_adcs_ca_common_name") == "defender-CA",
                f"{label} CA common name is incorrect",
            )
            require(
                ca_vars.get("mdi_adcs_host_prep_enabled") is True
                and ca_vars.get("mdi_adcs_host_prep_audit_filter") == 127,
                f"{label} CA01 MDI v3 readiness contract is incorrect",
            )
            require(
                ca_vars.get("mdi_sensor_performance_enabled") is True
                and "mdi_sensor_performance_allowed_domain_roles" not in ca_vars,
                f"{label} CA01 MDI performance configuration is incorrect",
            )
            require(ca_vars.get("mde_windows_host_prep_enabled") is True, f"{label} CA01 MDE host preparation must be enabled")
            require(
                all("5tuk0v.mde_client_onboard" not in role_names(vm) for vm in hosts.values()),
                f"{label} must use only the Defender for Servers MDE path",
            )

            validated_hosts[blueprint_id] = hosts
            validated_configs[blueprint_id] = range_config
            continue

        if spec["kind"] == "client":
            require(
                sum(int(vm["ram_gb"]) for vm in hosts.values()) == 14
                and sum(int(vm["cpus"]) for vm in hosts.values()) == 6,
                f"{label} total guest resource allocation is incorrect",
            )

            dc01 = hosts["DC01"]
            expected_dc_roles = {
                "5tuk0v.ludus_asr_presets",
                "5tuk0v.endpoint_sample_policy",
                "5tuk0v.sample_submission_sinkhole",
                "5tuk0v.controlled_folder_access_policy",
                "5tuk0v.credential_guard_policy",
                "5tuk0v.defender_baseline",
                "5tuk0v.windows_gpo_refresh",
            }
            require(role_names(dc01) == expected_dc_roles, f"{label} DC01 roles are incorrect")
            require(
                str(dc01["vm_name"]).endswith("-dc01")
                and not str(dc01["vm_name"]).endswith("-dc01-mde")
                and dc01.get("template") == "win2022-server-x64-template"
                and dc01.get("ram_gb") == 6
                and dc01.get("cpus") == 2,
                f"{label} DC01 identity, template, or sizing is incorrect",
            )
            dc_vars = require_mapping(dc01.get("role_vars"), f"{label} DC01 role_vars")
            require(
                dc_vars.get("endpoint_sample_policy_state") == "blocked"
                and dc_vars.get("controlled_folder_access_policy_state") == "native"
                and dc_vars.get("credential_guard_policy_state") == "native"
                and dc_vars.get("defender_baseline_enabled") is True,
                f"{label} DC01 Defender policy contract is incorrect",
            )

            expected_client_roles = set(required_workstation_roles)
            for hostname in ("WKS01", "WKS02"):
                workstation = hosts[hostname]
                workstation_roles = set(expected_client_roles)
                if hostname == "WKS02":
                    workstation_roles |= {
                        "5tuk0v.mde_windows_host_prep",
                        "5tuk0v.mde_client_onboard",
                    }
                require(
                    role_names(workstation) == workstation_roles,
                    f"{label} {hostname} roles are incorrect",
                )
                require(
                    workstation.get("template") == "win11-25h2-x64-enterprise-template"
                    and workstation.get("ram_gb") == 4
                    and workstation.get("cpus") == 2,
                    f"{label} {hostname} client sizing or template is incorrect",
                )
                workstation_vars = require_mapping(
                    workstation.get("role_vars"), f"{label} {hostname} role_vars"
                )
                require(
                    workstation_vars.get("ludus_asr_presets_preset") == "windows_11_25h2"
                    and workstation_vars.get("ludus_asr_presets_mode") == "audit"
                    and workstation_vars.get("microsoft_365_apps_enabled") is True,
                    f"{label} {hostname} workstation configuration is incorrect",
                )

            require(
                str(hosts["WKS01"]["vm_name"]).endswith("-wks01")
                and "ansible_groups" not in hosts["WKS01"],
                f"{label} WKS01 must remain MDE-negative",
            )
            require(
                str(hosts["WKS02"]["vm_name"]).endswith("-wks02-mde")
                and hosts["WKS02"].get("ip_last_octet") == 40
                and "mde_targets" in hosts["WKS02"].get("ansible_groups", []),
                f"{label} WKS02 must be the only MDE-positive client",
            )
            require(
                all(
                    "5tuk0v.azure_arc_onboard" not in role_names(vm)
                    and "5tuk0v.mdi_sensor_performance" not in role_names(vm)
                    for vm in hosts.values()
                ),
                f"{label} must not configure Azure Arc or MDI",
            )

            validated_hosts[blueprint_id] = hosts
            validated_configs[blueprint_id] = range_config
            continue

        dc01 = hosts["DC01"]
        require(str(dc01["vm_name"]).endswith("-dc01-mde"), f"{label} DC01 VM name must expose MDE intent")
        require(
            {
                "5tuk0v.ludus_asr_presets",
                "5tuk0v.endpoint_sample_policy",
                "5tuk0v.sample_submission_sinkhole",
                "5tuk0v.controlled_folder_access_policy",
                "5tuk0v.credential_guard_policy",
                "5tuk0v.defender_baseline",
                "5tuk0v.windows_gpo_refresh",
                "5tuk0v.mdi_sensor_performance",
                "5tuk0v.mde_windows_host_prep",
                "5tuk0v.azure_arc_onboard",
            }
            <= role_names(dc01),
            f"{label} DC01 roles are incomplete",
        )
        dc_vars = require_mapping(dc01.get("role_vars"), f"{label} DC01 role_vars")
        require("badsectorlabs.ludus_adcs" not in role_names(dc01), f"{label} DC01 must not install AD CS")
        require(
            not any(name.startswith("ludus_adcs_") for name in dc_vars),
            f"{label} DC01 must not define AD CS variables",
        )
        require(dc_vars.get("endpoint_sample_policy_state") == "blocked", f"{label} sample policy must be blocked")

        srv01 = hosts["SRV01"]
        require(str(srv01["vm_name"]).endswith("-srv01-mde"), f"{label} SRV01 VM name must expose MDE intent")
        required_srv_roles = {
            "5tuk0v.ludus_asr_presets",
            "5tuk0v.sample_submission_sinkhole",
            "5tuk0v.windows_gpo_refresh",
            "5tuk0v.mde_windows_host_prep",
            "5tuk0v.azure_arc_onboard",
        }
        require(required_srv_roles <= role_names(srv01), f"{label} SRV01 roles are incomplete")
        srv_vars = require_mapping(srv01.get("role_vars"), f"{label} SRV01 role_vars")
        require(srv_vars.get("ludus_asr_presets_preset") == "windows_server_2022", f"{label} SRV01 ASR preset is incorrect")
        require(srv_vars.get("ludus_asr_presets_mode") == "audit", f"{label} SRV01 ASR mode must be audit")
        require(
            not any(key.startswith("ludus_smb_") or key.startswith("ludus_files_") for key in srv_vars),
            f"{label} SRV01 must not define scenario content",
        )

        wks01 = hosts["WKS01"]
        require(str(wks01["vm_name"]).endswith("-wks01"), f"{label} WKS01 VM identity must remain stable")
        require(role_names(wks01) == required_workstation_roles, f"{label} WKS01 roles are incorrect")
        workstations = [("WKS01", wks01)]
        if "WKS02" in hosts:
            wks02 = hosts["WKS02"]
            require(
                role_names(wks02)
                == required_workstation_roles
                | {"5tuk0v.mde_windows_host_prep", "5tuk0v.mde_client_onboard"},
                f"{label} WKS02 roles are incorrect",
            )
            require(str(wks02["vm_name"]).endswith("-wks02-mde"), f"{label} WKS02 VM name must expose MDE intent")
            require(wks02["template"] == wks01["template"], f"{label} workstation templates must match")
            require(wks02["vlan"] == wks01["vlan"], f"{label} workstation VLANs must match")
            require(wks02["ip_last_octet"] == 40, f"{label} WKS02 must use IP suffix 40")
            workstations.append(("WKS02", wks02))
        else:
            require(
                all("5tuk0v.mde_client_onboard" not in role_names(vm) for vm in hosts.values()),
                f"{label} must not use client MDE onboarding",
            )

        for hostname, workstation in workstations:
            wks_vars = require_mapping(workstation.get("role_vars"), f"{label} {hostname} role_vars")
            require(
                wks_vars.get("ludus_asr_presets_preset") == "windows_11_25h2",
                f"{label} {hostname} ASR preset is incorrect",
            )
            require(wks_vars.get("ludus_asr_presets_mode") == "audit", f"{label} {hostname} ASR mode must be audit")
            require(
                wks_vars.get("microsoft_365_apps_enabled") is True,
                f"{label} {hostname} Microsoft 365 Apps must be enabled",
            )

        require(dc_vars.get("controlled_folder_access_policy_state") == "native", f"{label} DC01 CFA must be native")
        require(dc_vars.get("credential_guard_policy_state") == "native", f"{label} DC01 Credential Guard must be native")
        require(dc_vars.get("defender_baseline_enabled") is True, f"{label} DC01 Defender baseline must be enabled")
        require(dc_vars.get("mdi_sensor_performance_enabled") is True, f"{label} DC01 MDI performance must be enabled")
        require("5tuk0v.mde_onboarding_status" not in role_names(dc01), f"{label} DC01 uses a retired MDE role")
        require("5tuk0v.mdi_v3_readiness" not in role_names(dc01), f"{label} DC01 uses a retired MDI role")
        require("5tuk0v.mdi_v3_preflight" not in role_names(dc01), f"{label} DC01 uses a retired MDI role")
        require("5tuk0v.mde_onboarding_status" not in role_names(srv01), f"{label} SRV01 uses a retired MDE role")
        validated_hosts[blueprint_id] = hosts
        validated_configs[blueprint_id] = range_config

    for hostname in ("DC01", "SRV01", "WKS01"):
        require(
            validated_hosts["server-mde"][hostname] == validated_hosts["standard"][hostname],
            f"shared host {hostname} differs between Source blueprints",
        )
    for section in ("network", "defaults"):
        require(
            validated_configs["server-mde"].get(section) == validated_configs["standard"].get(section),
            f"shared {section} differs between Source blueprints",
        )
    for hostname in ("WKS01", "WKS02"):
        require(
            validated_hosts["client-mde"][hostname] == validated_hosts["standard"][hostname],
            f"shared host {hostname} differs between client-mde and standard",
        )
    for section in ("network", "defaults"):
        require(
            validated_configs["client-mde"].get(section) == validated_configs["standard"].get(section),
            f"shared {section} differs between client-mde and standard",
        )


if __name__ == "__main__":
    try:
        validate()
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"M0 validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    print("Source blueprint static validation passed")

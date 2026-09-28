# Getting started — common preparation

Choose a blueprint from the [project README](../README.md). Complete sections
1–3 for every lab. The Azure-connected server blueprints also complete section 4.

## 1. Check access and capacity

- Use an existing Ludus installation with Source/Blueprint support and Internet
  access for deployment and commissioning downloads.
- Have a test Microsoft tenant and the Defender entitlement required by the
  selected scenario.
- Check templates, capacity, and additional prerequisites in your selected
  [lab runbook](#5-continue-with-your-lab).

## 2. Install the Source

1. Install the project Source:

   ```bash
   ludus source add https://github.com/5tuk0v/defender-xdr-lab \
     --id defender-xdr-lab \
     --all
   ```

2. Set `blueprint_id` to your chosen blueprint and review its installed details:

   ```bash
   blueprint_id='<BLUEPRINT_ID>'
   ludus blueprint info "defender-xdr-lab/${blueprint_id}"
   ```

## 3. Create the protected staging directory

Keep credentials and protected onboarding files outside Git, range YAML, Source
archives, reports, and logs.

1. On the download machine, set the Ludus host's SSH target:

   ```bash
   ludus_ssh_target='<admin-user>@<ludus-host>'
   ```

2. On the Ludus host, choose the protected directory. For per-profile roles,
   use the profile directory name under `/opt/ludus/users/`:

   ```bash
   ludus_profile='<ludus-profile>'
   protected_dir="/opt/ludus/users/${ludus_profile}/.ansible/defender-xdr-lab-protected"
   ```

   For globally installed roles, set `protected_dir` to
   `/opt/ludus/resources/defender-xdr-lab-protected`.

3. Create the protected directory on the Ludus host:

   ```bash
   sudo install -d -o ludus -g ludus -m 700 "$protected_dir"
   ```

## 4. Prepare Azure-connected server labs

Complete this section for `standard`, `server-mde`, `hybrid-identity`,
`hybrid-join`, `adcs-mdi`, and `complete`. For `client-mde`, continue with its
[runbook](labs/client-mde.md).

### Check Azure and MDI access

- Have a billing-enabled Azure subscription in the lab's Microsoft tenant.
- Confirm a qualifying MDI license using the current
  [MDI v3 prerequisites](https://learn.microsoft.com/en-us/defender-for-identity/deploy/prerequisites-sensor-version-3).
- Use a **Security Administrator** or the documented Unified RBAC permissions
  to activate sensors. Check the same prerequisites for OS and connectivity
  requirements on DC01 and any scenario sensor hosts.

### Create the Azure resource group

1. In Azure **Resource groups > Create**, select the lab subscription. Create a
   new group for this deployment with a recognizable range/date suffix.
2. Confirm [Azure Arc provider and connectivity prerequisites](https://learn.microsoft.com/en-us/azure/azure-arc/servers/prerequisites)
   for the chosen lab's servers.

### Enable Defender for Servers

1. Review the current [plan, trial, scope, and pricing](https://learn.microsoft.com/en-us/azure/defender-for-cloud/plan-defender-for-servers-select-plan).
   If the subscription has other servers, review its resource-level coverage first.
2. In **Defender for Cloud > Environment settings**, select the subscription,
   enable **Servers**, choose **Plan 1**, and set **Endpoint protection** to On
   under **Settings and monitoring**.
3. Track lab charges in **Azure Cost Management** through retirement.

### Create the Arc onboarding identity

1. In **Azure Arc > Additional setup > Service principals**, create a new
   identity named, for example, `sp-<range-id>-arc-onboard-<yyyymmdd>`.
2. Scope it to the dedicated resource group, grant **Azure Connected Machine
   Onboarding**.
3. In **Azure Arc > Machines > Add/Create > Add a machine**, choose the
   Windows/on-premises flow and **Authenticate automatically**. Select the new
   identity and resource group, then download `OnboardingScript.ps1`.

### Stage the Arc script

The Arc script contains a service-principal secret.

1. Transfer the Arc script from the download machine to the Ludus host:

   ```bash
   arc_script='/absolute/path/to/OnboardingScript.ps1'
   scp -- "$arc_script" "${ludus_ssh_target}:/tmp/OnboardingScript.ps1"
   ```

2. On the Ludus host, install and check the Arc file:

   ```bash
   sudo install -o ludus -g ludus -m 600 /tmp/OnboardingScript.ps1 "$protected_dir/OnboardingScript.ps1"
   sudo test -s "$protected_dir/OnboardingScript.ps1"
   sudo stat -c '%U %G %a %n' "$protected_dir/OnboardingScript.ps1"
   ```

3. Require a successful file check and `ludus ludus 600` in the output, then
   remove the temporary transfer copy:

   ```bash
   sudo rm -- /tmp/OnboardingScript.ps1
   ```

## 5. Continue with your lab

Open the selected runbook and follow it through additional preparation,
deployment, post-deployment commissioning, acceptance, and cleanup.

| Runbook |
| --- |
| [client-mde](labs/client-mde.md) |
| [standard](labs/standard.md) |
| [server-mde](labs/server-mde.md) |
| [hybrid-identity](labs/hybrid-identity.md) |
| [hybrid-join](labs/hybrid-join.md) |
| [adcs-mdi](labs/adcs-mdi.md) |
| [complete](labs/complete.md) |

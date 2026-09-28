# `mdi_adcs_host_prep`

Prepares and validates stable local readiness for a Microsoft Defender for
Identity v3 sensor on a dedicated, domain-member Active Directory Certificate
Services server.

The role:

- requires a domain-member server rather than a domain controller;
- requires the AD CS Certification Authority Role Service and a running
  `CertSvc` service;
- keeps Windows Time running for normal domain synchronization;
- enables Success and Failure for the Certification Services advanced audit
  subcategory using its locale-independent GUID;
- creates or corrects the CA audit filter at Microsoft's full value of `127`,
  restarting only `CertSvc` when the value changes; and
- validates the server role, service, audit policy, CA audit filter, and time
  service or fails clearly.

Creating the audit-filter value is intentional. Microsoft automatic Windows
auditing for v3 can update an existing AD CS audit filter but does not create a
missing value. The role establishes that local prerequisite before portal
activation; tenant-bound MDE onboarding, sensor activation, and automatic
auditing remain operator commissioning actions.

Reapplying the selected state is meaningful: unchanged audit settings do not
restart the CA service.

Microsoft references:

- [MDI v3 sensor prerequisites](https://learn.microsoft.com/en-us/defender-for-identity/deploy/deploy-sensor-v3)
- [Activate an MDI v3 sensor](https://learn.microsoft.com/en-us/defender-for-identity/deploy/activate-sensor)
- [Configure Windows event auditing](https://learn.microsoft.com/en-us/defender-for-identity/deploy/configure-windows-event-collection)

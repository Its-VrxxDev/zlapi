---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ''

---

---

## Description of the problem
Example: Logging in fails when the character `#` is in the password. A specific password that fails is `password_with_#_char`

## Code to reproduce
```py
# Example code
from zlapi import ZaloAPI

client = ZaloAPI("phone", "password_with_#_char")
```

## Traceback
```
# Traceback Login Error
```

## Environment information
- Python version
- `zlapi` version
- If relevant, output from `python -m pip list`

If you have done any research, include that.
Make sure to redact all personal information.

# Project template

This is the starting point for **Frida's project repository**.

Create your repository in the **IDATA2502 organisation on GitHub** (the same
organisation this template lives in), using this template as the starting
point. From there the repository is yours: you build it out over time, and
everything you add goes into it.

## What you get

```
.
|-- app/          # A small Flask app to build on
|-- terraform/    # Your infrastructure code goes here
|-- ansible/      # Your configuration management goes here
`-- .gitignore    # Keeps secrets, state files and .env out of git
```

`app/` is the only folder with code in it. `terraform/` and `ansible/` are
empty on purpose - you fill them in yourself.

## Never commit secrets

`.gitignore` is pre-configured to exclude the usual suspects: `.env` files,
SSH private keys, `clouds.yaml`, Terraform state and `*.tfvars`. Leave those
entries in place.

If a secret does end up in a commit, removing it in a later commit is not
enough - it stays in the history. Rotate the secret immediately and treat the
old one as compromised.

# Infra PR33 review (head d7ec908), 2026-10-04
Verdict: no blockers.

Checked read-only (diff plus fresh clone; no terraform, AWS or Nexus).

## Blockers
None.

## Verified
- set-secret:
  - The value is read with Read-Host -AsSecureString. There is no value parameter.
  - It is never printed and never on argv. Only file:// goes to the AWS CLI.
  - Empty and CHANGE_ME are rejected before the typed SET prompt.
  - Merge is get, then replace one key, then put. Other keys are kept.
  - Key regex is strict.
  - The temp file is outside the repo with a GUID name and is removed in finally.
- ViteApiUrl: it is only allowed for the web service. The strict regex excludes spaces, commas, query and credentials, and the duplicate-arg check holds.
- Staged .dockerignore: it is rewritten only inside the zip, so the checkout is untouched.
- State key: pulso/prod/hackathon/terraform.tfstate is consistent across the script, backend.hcl.example and the docs.
- Terraform:
  - The CodeBuild change only alters the CONTEXT_DIR environment variable. That is an in-place update, with no replace or destroy.
  - The secret version has ignore_changes on secret_string, so adding OPENROUTER_API_KEY to the key list does not rewrite the secret.
  - The key is added at runtime by set-secret.
- Python contract tests: 6 of 6 pass locally.

## Non-blockers
1. The secret is briefly on disk in %TEMP% (the user's profile), as plaintext JSON of the whole secret. It is deleted in finally, but a hard kill would leave it. Consider in-memory alternatives or a restricted ACL.
2. The ViteApiUrl and BuildArg regexes use `$`, which accepts a trailing newline. This is an edge case only.
3. The .dockerignore filter matches exact lines only (contracts, /contracts/). A pattern like contracts/** would not be stripped.
4. The secret JSON holds all secret values in memory as strings, and a failed set-secret leaves them in the session variables. Minor.
5. The Pester tests mock Read-SecretValue and Invoke-Aws, so the real SecureString path is untested. The python test "no Write-Host $value" is a weak static check.
6. CI is red (contract-suite on both OSes). The jobs fail in 2s with no steps, and main fails the same way, so this is a runner or account problem, not PR-caused. It needs fixing before the merge gate is meaningful.
7. I did not execute the Pester suite (not run locally).

## Destructive paths
The diff does not touch the destroy or apply confirmations. set-secret itself requires typing SET.

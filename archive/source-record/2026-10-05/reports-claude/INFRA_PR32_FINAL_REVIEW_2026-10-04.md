# Infra PR 32 final review (head e59b1f1)

Verdict: no blockers found.

Verified
- Secrets/PII/Nexus: no keys, account ids, tfvars, tfstate or receipts in the tracked tree; .nexus-outbox ignored. Only placeholder account ids (111111111111) in tests.
- X-Origin-Verify: random_password in hackathon_data, stored in the single secret as COMMON__ORIGIN_VERIFY, output sensitive, Caddy rejects 403 before proxying, start script fails closed on empty value, /healthz open. CloudFront prefix-list SG as second layer. Good.
- IAM: host boundary denies iam/organizations/account; Resource "*" only on ecr:GetAuthorizationToken and read-only SSM/EC2 describe actions, with tests asserting this. S3 "Principal *" statements are Deny statements (TLS/policy guards).
- hackathon_compute: ignore_changes = [associate_public_ip_address] plus aws_ec2_instance_state depending on both volume attachments is coherent; inactive host created running, attached, then stopped; contract test and tftest cover it.
- aws-prod.ps1: profile refusal list, saved-plan + typed APPLY/DESTROY, zip excludes secrets/state/tfvars, bucket/state names consistent with docs.
- Local run: python unittest discover = 194 tests OK (1 skipped).

NON-BLOCKERS
1. docs/security-model.md "What is not protected" still says X-Origin-Verify is "unset and not checked by Caddy", and graduation step 4 says to enforce it. Contradicts architecture.md, troubleshooting.md and the Caddyfiles. Fix the text.
2. State key mismatch: aws-prod.ps1 and docs use pulso/prod/hackathon/terraform.tfstate; terraform/envs/hackathon/backend.hcl.example and bootstrap var state_key default use pulso/prod/terraform.tfstate. A manual init from the example would create a second, empty state. Align the example (and ideally the bootstrap default).
3. CI did not run: both contract-suite jobs failed in 2s with a GitHub billing/spending-limit annotation, so Pester, terraform fmt/validate and tftests have no CI evidence on this head. Resolve billing and re-run before relying on it (I ran the python suite and compute tftest locally only).
4. deploy -Yes skips the typed DEPLOY confirmation; the header comment claims no flag skips prompts (true for apply/destroy only). Minor wording.
5. Residual risks already documented: single secret readable by all host roles, HTTP CloudFront-to-origin hop, compose plugin downloaded without checksum.

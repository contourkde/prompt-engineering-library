# Security Policy

## Private Reporting

Do not post credentials, personal data, or exploit details in public issues or
pull requests. If GitHub private vulnerability reporting is enabled for this
repository, use **Security > Advisories > Report a vulnerability**. This policy
does not imply that reporting is enabled. If that option is unavailable, contact
a maintainer through a private contact method listed on their GitHub profile.
If no private channel is listed, request one without disclosing sensitive details.

Include affected paths or commit IDs, impact, and reproduction steps with secrets
redacted. Never send a working credential merely to demonstrate exposure.

## Exposed Credentials

1. Revoke or rotate exposed credentials immediately, even if a scanner reports
   them as inactive or a later commit deletes them.
2. Review provider audit logs and access scope for misuse. Replace credentials in
   dependent systems using an appropriate secret store.
3. Remove the sensitive content from current files. Coordinate any history
   rewrite with maintainers and collaborators; forks, clones, caches, logs, and
   artifacts may retain copies after a rewrite.

`.gitignore`, scanner allowlists, and ignore comments do not remove tracked files
or erase Git history. Suppress only reviewed false positives, not real exposures.
Keep local `.env` files and private/personal scripts out of commits; ignoring a
path is not a security boundary for content already committed.

## CI Coverage

`.github/workflows/ci.yml` runs on pushes to any branch, pull requests, and manual
`workflow_dispatch` runs. Tag-only pushes are not included. There are no path
filters. Python 3.11, 3.12, and 3.13 run
`uv run --locked python -m unittest discover -s tests -v`, `uv run --locked ty check`,
and prompt-definition validation. uv installs the locked development environment;
tests and type checks are separate from secret scans.

Both scanners fetch full Git history (`fetch-depth: 0`), but fetching history does
not mean every scanner examines every fetched commit on every event:

- **TruffleHog** scans history reachable from the checked-out `HEAD`, including
  the pull request merge commit when GitHub provides one. Explicit `head: HEAD`
  avoids incremental event ranges. It fails on verified and unknown findings and
  scan errors. Unknown means verification encountered an error; unverified
  findings are not included in this job's results.
- **Gitleaks** complements verification with static rules and entropy checks for
  common tokens, passwords, and private keys, without requiring credentials to
  remain live. Push and PR runs use the action's incremental commit ranges;
  manual runs scan history reachable from the selected checkout without an
  event-specific range. Run CI manually on the default branch for an initial
  baseline and periodically thereafter, and on other branches as needed.
- The pinned Gitleaks action uses first-parent, non-merge ranges for push/PR
  events. Its PR commit API call is not paginated, so long PRs can be only
  partially scanned (the API defaults to 30 commits). Push payload limits, root
  commits, and rewritten history can also limit ranges or cause errors. A full
  fetch does not fix these upstream behaviors. Use manual scans for broader
  static coverage; do not treat an incomplete or failed run as a clean scan.

CI scans committed Git content available to its checkout, not local untracked
files. It does not audit issues, comments, external storage, GitHub secrets,
unreachable/deleted commits, every fork, or every branch automatically. Submodule
repositories and Git LFS payloads are not fetched by this workflow. No private
script or environment-file path is exempted if its content enters scanned Git
history.

## Scanner Limitations

Both tools can produce false positives and false negatives. Encoded, encrypted,
split, novel, or unsupported secrets can escape detection. These are credential
scanners, not comprehensive personal-data, confidential-document, dependency,
or application-vulnerability audits. Passing tests and scans do not prove safety.

TruffleHog verification can send candidate credentials to their corresponding
provider APIs or verification services, creating network traffic and audit
events. Review that behavior against your data-handling requirements before
enabling CI. Gitleaks performs static detection, not proof that a credential is
usable. Network failures, timeouts, configuration, and ignore rules can affect
coverage.

Gitleaks PR comments, report artifact uploads, and job summaries are disabled to
reduce disclosure and avoid write permissions. Gitleaks invokes its scanner with
redaction, but scan logs and TruffleHog annotations can still contain sensitive
context. Treat findings and CI output as sensitive; redaction is not guaranteed
to hide every secret. Restrict access and remove exposed logs where appropriate.

## Gitleaks License

The official Gitleaks Action v3 requires `GITLEAKS_LICENSE` for repositories owned
by organizations, but not personal accounts. Obtain a license under the upstream
terms and store it as an encrypted repository or organization Actions secret.
The action's license terms are separate from the open-source Gitleaks CLI.
Consult the [official action documentation](https://github.com/gitleaks/gitleaks-action/tree/v3.0.0)
and [license](https://github.com/gitleaks/gitleaks-action/blob/v3.0.0/LICENSE.txt).

GitHub normally withholds repository secrets from fork and Dependabot PRs.
Organization-owned repositories can therefore fail the Gitleaks job on those
events because the license is unavailable. This workflow does not silently skip
that failure or use `pull_request_target` to expose secrets to untrusted code.
TruffleHog runs independently. Arrange a trusted manual scan of reviewed commits
when needed; do not execute untrusted tests with privileged secrets. Upstream
documents license validation metadata being sent to its licensing service;
review current licensing and data-handling terms when updating the action.

## Hardening and Maintenance

Enable GitHub secret scanning and push protection where available for this
repository and account, and review bypasses. These settings are recommended,
not asserted to be enabled. CI runs after code reaches GitHub and cannot undo
an exposure. Require test and scanner checks through branch protection or
rulesets after resolving license and contributor-workflow requirements.

Actions are pinned to full upstream commit SHAs with release-version comments.
TruffleHog's container version and Gitleaks' downloaded CLI version are also
explicit, rather than `latest`. These version tags/release assets are not digest
pins; pinning an action does not make all downloaded dependencies immutable.
Review upstream releases and update pins regularly to receive detector and
security fixes. Workflow permissions are read-only, checkout credentials are not
persisted, and tests run separately from scanner credentials.

Upstream references used for scanner behavior:

- [TruffleHog v3.97.4 documentation](https://github.com/trufflesecurity/trufflehog/tree/v3.97.4)
- [TruffleHog action implementation](https://github.com/trufflesecurity/trufflehog/blob/363923b901c911a9164f50b6c423f47c15372b1c/action.yml)
- [Gitleaks Action v3.0.0 implementation](https://github.com/gitleaks/gitleaks-action/tree/e0c47f4f8be36e29cdc102c57e68cb5cbf0e8d1e/src)

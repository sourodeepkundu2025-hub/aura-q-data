# Security policy

The utilities read local CSV/JSON files and produce local analysis outputs. They do not require credentials, call a language model, or submit quantum jobs. The benchmark includes authored adversarial prompts; those strings must remain inert evaluation data.

## Reporting

For a suspected vulnerability, email Sourodeep Kundu at `sourodeep.kundu2025@vitstudent.ac.in`. Include the affected utility/version, a minimal synthetic example and the expected impact. Avoid public disclosure of secrets or personal data in an issue.

The current repository snapshot is the supported utility version. Historical dataset commits remain available for citation and comparison. Fixes are documented in the changelog; the project makes no guaranteed response-time commitment.

## Maintainer practices

Keep CI permissions read-only, pin third-party action references, avoid `pull_request_target` for contributor code, and keep frozen source data distinct from generated output. Validation rejects manifest traversal and non-finite regret values. Dataset hashes establish file identity, not trust in arbitrary code bundled by another source.

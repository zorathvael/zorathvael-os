# Changelog

## [Unreleased]

### Fixed
- Add an offer-aligned actionable-problem gate before drafting, selecting, emailing, or posting outreach; reject operational checklists and meta-instructions as customer context.

### Fixed
- Reject arbitrary first-paragraph text and known operational recaps from outreach personalization.
- Revalidate retained lead records against supported problem-to-offer fit and repair stale offer assignments before qualification metrics are refreshed.
- Report explicit lead-cleanup counters so each acquisition run explains why records were dropped or corrected.
- Clarify that public GitHub outreach is conditional and guarded, rather than describing the acquisition loop as discovery-only.


All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-08-06

### Added
- Complete production-ready implementation of core modules: `AIRouter`, `MemoryEngine`, `WorkflowEngine`, `AutomationEngine`, `IntegrationEngine`, `ReportEngine`, `MissionCenter`, and `Dashboard`.
- Robust exception handling, type hints, and structured logging across all modules.
- Comprehensive automated test suite (`pytest`) achieving 16 passing tests with zero failures.
- CI/CD workflow automation via GitHub Actions (`ci.yml`).
- Professional technical documentation under `docs/`.

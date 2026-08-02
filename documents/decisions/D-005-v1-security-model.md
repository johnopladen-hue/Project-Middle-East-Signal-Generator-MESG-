# D-005 — v1 security model

**Date:** 2026-08-02
**Status:** Decided

## Decision

Start with simple username/password authentication for the web application. The email/SMS recipient list is a whitelist manually curated by the Owner.

## Context

The Owner's day-one objective brief specifies the delivery mechanism (web app, email, SMS) and states security should start simple.

## Options rejected

- **Build a more sophisticated auth model (OAuth/SSO, MFA, RBAC) from day one.** Rejected as premature per the Owner's explicit instruction to start simple and harden later, once there's an actual system worth attacking.

## Evidence

- Owner's initial kickoff message, 2026-08-02 (OBJECTIVE section): "Security to begin with will be simple, user name and password to start."

## Supersedes

None.

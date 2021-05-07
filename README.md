# Budgery

Budgery is a self-hosted financial application for setting budgets, tracking expenses, and reaching financial goals. It uses the [zero-based budgeting](https://www.investopedia.com/terms/z/zbb.asp) method.

## Features

 * Self-hosted first, with support for single sign-on (SSO).
 * Multi-user with cooperation and data sharing.
 * Audit trail/history/append-only logging.
 * Easy reconciliation by keeping a time-based running total of accounts.
 * Zero-based budgeting - every dollar has a job and a label.
 * Imports from various systems (Bank CSV, OFX).

## Running

Budgery uses [hypercorn](https://gitlab.com/pgjones/hypercorn) and 
[quart](https://gitlab.com/pgjones/quart). You can run a server with:

```
hypercorn budgery:app -b 192.168.1.1:10100
```

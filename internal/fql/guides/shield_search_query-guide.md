# Falcon Shield Query Parameter Guide

## Common Parameters

|Parameter|Type|Values|Used By|
|-|-|-|-|
|status|String|Passed, Failed, Dismissed, Pending, Can't Run, Stale|shield_checks, shield_posture_metrics|
|impact|String|Low, Medium, High|shield_checks, shield_posture_metrics|
|check_type|String|apps, devices, users, assets, permissions, custom, Falcon Shield Security Check|shield_checks, shield_posture_metrics|
|integration_id|String|Comma-separated integration IDs|Most tools|
|compliance|Boolean|true/false (filters on catalog-level framework mapping, not populated compliance data)|shield_checks, shield_posture_metrics|

## Alert Types
configuration_drift, check_degraded, integration_failure, threat

## App Types
oauth, sign_in, api_token, App Registration, Connected Apps, browser_extension, Portal, Service Principal

## App Statuses
approved, in review, rejected, unclassified

## Time-Based Filters
Format: 'was N' (within N days) or 'was not N' (not within N days). N is an integer — do NOT append 'days'.
- last_activity — used by shield_apps
- last_accessed — used by shield_data_shares
- last_modified — used by shield_data_shares
Examples: 'was not 90' (inactive >90 days), 'was 30' (active within 30 days)

## Activity Monitor Categories
Events, Threat, IoC

## Activity Monitor Projection Fields
timestamp_utc, severity, datetime, event_name, actor, integration_id, integration_name, type, category, created_by, ip, asn_name, country, browser, os, target, object_type, object, status

## Supported SaaS Platforms
Use `GetSupportedSaasV3` via the API to get the current list of platforms available for integration.

## Pagination Notes
- `meta.pagination.total` is always null — iterate until empty results
- Activity Monitor: use `meta.pagination.next` as `to_date` and `meta.pagination.offset` as `skip`
- Alerts: use `last_id` for cursor-based pagination (alternative to offset)
- Activity Monitor has 24-hour date range limit when using integration_id/category/actor filters

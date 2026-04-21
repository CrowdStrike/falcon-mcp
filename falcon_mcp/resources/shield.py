"""Falcon Shield (SaaS Security) query parameter documentation."""

from falcon_mcp.common.utils import generate_md_table

SHIELD_COMMON_PARAMS = [
    ("Parameter", "Type", "Values", "Used By"),
    (
        "status",
        "String",
        "Passed, Failed, Dismissed, Pending, Can't Run, Stale, Not Available",
        "shield_checks, shield_posture_metrics",
    ),
    ("impact", "String", "Low, Medium, High", "shield_checks, shield_posture_metrics"),
    (
        "check_type",
        "String",
        "apps, devices, users, assets, permissions, custom",
        "shield_checks, shield_posture_metrics",
    ),
    (
        "integration_id",
        "String",
        "Comma-separated integration IDs",
        "Most tools",
    ),
    (
        "compliance",
        "Boolean",
        "true/false",
        "shield_checks, shield_posture_metrics",
    ),
]

SHIELD_QUERY_DOCUMENTATION = f"""# Falcon Shield Query Parameter Guide

## Common Parameters

{generate_md_table(SHIELD_COMMON_PARAMS)}

## Alert Types
configuration_drift, check_degraded, integration_failure, threat

## App Types
oauth, sign_in, api_token, App Registration, Connected Apps, browser_extension, Portal, Service Principal

## App Statuses
approved, in review, rejected, unclassified

## Activity Monitor Categories
Events, Threat, IoC

## Activity Monitor Projection Fields
timestamp_utc, severity, datetime, event_name, actor, integration_id, integration_name, type, category, \
created_by, ip, asn_name, country, browser, os, target, object_type, object, status

## Supported SaaS Platforms
Use `GetSupportedSaasV3` via the API to get the current list of platforms available for integration.

## Pagination Notes
- `meta.pagination.total` is always null — iterate until empty results
- Activity Monitor: use `meta.pagination.next` as `to_date` and `meta.pagination.offset` as `skip`
- Alerts: use `last_id` for cursor-based pagination (alternative to offset)
- Activity Monitor has 24-hour date range limit when using integration_id/category/actor filters
"""

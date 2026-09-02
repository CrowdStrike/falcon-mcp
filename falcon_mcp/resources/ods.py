"""FQL documentation for the On-Demand Scan module."""

SEARCH_ODS_SCANS_FQL_DOCUMENTATION = """# ODS scan FQL

Filter fields include: id, profile_id, description, description.keyword,
initiated_from, filecount.scanned, filecount.malicious, filecount.quarantined,
filecount.skipped, affected_hosts_count, status, severity, scan_started_on,
scan_completed_on, created_on, created_by, last_updated, targeted_host_count,
missing_host_count, targeted_platforms, and targeted_platforms.keyword.

Example: `status:'completed'+filecount.malicious:>0`
"""

SEARCH_ODS_SCAN_HOSTS_FQL_DOCUMENTATION = """# ODS scan-host FQL

Filter fields include: id, profile_id, host_id, scan_id, host_scan_id,
filecount.scanned, filecount.malicious, filecount.quarantined,
filecount.skipped, affected_hosts_count, status, severity, completed_on,
started_on, last_updated, and scan_control_reason.

Example: `scan_id:'SCAN_ID'+filecount.malicious:>0`
"""

SEARCH_ODS_MALICIOUS_FILES_FQL_DOCUMENTATION = """# ODS malicious-file FQL

Filter fields include: id, scan_id, host_id, host_scan_id, filepath,
filename, hash, pattern_id, severity, quarantined, and last_updated.

Example: `scan_id:'SCAN_ID'+quarantined:true`
"""

SEARCH_ODS_SCHEDULED_SCANS_FQL_DOCUMENTATION = """# ODS scheduled-scan FQL

Filter fields include: id, description, description.keyword, initiated_from,
status, schedule.start_timestamp, schedule.interval, created_on, created_by,
last_updated, deleted, targeted_platforms, and channel_file_status.

Example: `status:'active'+deleted:false`
"""

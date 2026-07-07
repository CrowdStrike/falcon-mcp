Falcon Query Language (FQL) - Search Report Executions Guide

=== BASIC SYNTAX ===
property_name:[operator]'value'

=== AVAILABLE OPERATORS ===
• No operator = equals (default)
• ! = not equal to
• > = greater than
• >= = greater than or equal
• < = less than
• <= = less than or equal
• ~ = text match (ignores case, spaces, punctuation)
• * = wildcard matching (not supported on all fields — see endpoint-specific notes below)

=== DATA TYPES & SYNTAX ===
• Strings: 'value' or ['exact_value'] for exact match
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format) or relative: 'now-7d', 'now-24h' (lowercase, single-quoted)
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)
• Wildcards: 'partial*' or '*partial' or '*partial*'

=== COMBINING CONDITIONS ===
• + = AND condition (e.g., platform_name:'Windows'+status:'normal')
• , = OR condition (e.g., severity_name:'Critical',severity_name:'High')
• ( ) = Group expressions

IMPORTANT: Use + for AND and , for OR — do NOT use the words AND/OR.
Values must be single-quoted. Relative dates must be lowercase ('now-7d' not 'NOW-7d').

=== MULTIPLE VALUES ===
Use brackets for OR logic: filter=status:['FAILED','NO_DATA']
Or repeat filter name: filter=status:'FAILED',status:'NO_DATA'

=== MULTIPLE FILTERS ===
Use URL-encoded + (%2B) between filters:
filter=status:'DONE'%2Bfilter=created_on:>'2023-01-01'

=== falcon_search_report_executions FQL filter options ===

|Name|Type|Operators|Description|
|-|-|-|-|
|id|String|Yes|The unique ID of an execution. Use this to retrieve specific executions by ID. Supports multiple values. Ex: id:'f1984ff006a94980b352f18ee79aed77' Ex: id:['id1','id2']|
|created_on|Timestamp|Yes|The date and time an execution was generated. Ex: created_on:'2021-10-12' Ex: created_on:<'2021-10-12' Ex: created_on:>'2021-10-12T03:00'|
|expiration_on|Timestamp|Yes|The date and time that an execution will be deleted from the system. Set at 30 days after the execution is generated. Ex: expiration_on:'2021-12-15' Ex: expiration_on:>'2021-11-15T18' Ex: expiration_on:<'2021-12-03T03:30'|
|last_updated_on|Timestamp|Yes|The date and time of the last update made to a scheduled report/search execution. Execution updates refer to a change in status. Ex: last_updated_on:'2021-10-12' Ex: last_updated_on:>'2021-10-12' Ex: last_updated_on:<'2021-10-12T03:00'|
|result_metadata.*|Various|Yes|Scheduled search result details. Fields: execution_start, execution_duration, execution_finish, report_file_name, report_finish, result_count, result_id, search_window_start, search_window_end, queue_duration, queue_start Ex: result_metadata.execution_start:<'2021-10-12' Ex: result_metadata.result_count:>100|
|scheduled_report_id|String|Yes|The unique ID of the scheduled report/search entity. Use this to get all executions for a specific entity. Supports multiple values and negation. Ex: scheduled_report_id:'e163544433ab1020b1a4117d1a8421b5' Ex: scheduled_report_id:['id1','id2'] Ex: scheduled_report_id:!'e163544433ab1020b1a4117d1a8421b5'|
|shared_with|String|Yes|The unique ID of a user who has been shared on the scheduled report that generated the execution. Supports multiple values and negation. Ex: shared_with:'ae6b126d-0b73-452d-b807-afc58f097aad' Ex: shared_with:!'ae6b126d-0b73-452d-b807-afc58f097aad'|
|status|String|Yes|The current status of an execution. Supports multiple values and negation. Values must be in all capital letters. Values: PENDING, PROCESSING, DONE, FAILED, FAILED_NOTIFICATION, NO_DATA Ex: status:'PENDING' Ex: status:['FAILED','NO_DATA'] Ex: status:!['FAILED','FAILED_NOTIFICATION'] Ex: status:!'NO_DATA'|
|type|String|Yes|The type of entity (scheduled report or scheduled search). Supports multiple values and negation. Values must be in all lowercase letters. Values: event_search (scheduled searches), cloud_security_posture_detections_ioa, cloud_security_posture_detections_iom, cloud_security_image_vulnerabilities, cloud_security_container_vulnerabilities, cloud_security_container_details, cloud_security_image_detections, dashboard, discover_applications, filevantage, hosts, spotlight_installed_patches, spotlight_remediations, spotlight_vulnerabilities, spotlight_vulnerability_logic Ex: type:'event_search' (scheduled search executions only) Ex: type:!'event_search' (scheduled report executions only) Ex: type:['hosts','spotlight_remediations']|
|user_id|String|Yes|The ID of the user who created the scheduled report/search entity that generated the execution. Ex: user_id:'diana.hudson@email.com' Ex: user_id:!'diana.hudson@email.com' Ex: user_id:['diana.hudson@email.com','jack.evans@email.com']|

=== EXAMPLE USAGE ===

• id:'f1984ff006a94980b352f18ee79aed77' - Get specific execution by ID
• id:['id1','id2'] - Get multiple executions by ID
• status:'DONE' - Completed successfully
• status:'FAILED' - Failed executions
• status:'PROCESSING' - Currently running
• status:'PENDING' - Queued
• scheduled_report_id:'abc123' - All executions for entity abc123
• status:'DONE'+created_on:>'2023-01-01' - Successful runs after date
• type:'event_search'+status:'DONE' - Completed scheduled search executions
• result_metadata.result_count:>100 - Executions with more than 100 results

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• Status values are case-sensitive (use ALL CAPS)
• Type values must be lowercase

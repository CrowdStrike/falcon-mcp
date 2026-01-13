"""
Contains Scheduled Reports resources.
"""

from falcon_mcp.common.utils import generate_md_table

# Scheduled report/search entity FQL filters
SEARCH_SCHEDULED_REPORTS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description"
    ),
    (
        "id",
        "String",
        "Yes",
        """
        The unique ID of a scheduled report/search entity. Use this to retrieve
        specific entities by ID. Supports multiple values.

        Ex: id:'45c59557ded4413cafb8ff81e7640456'
        Ex: id:['id1','id2']
        """
    ),
    (
        "created_on",
        "Timestamp",
        "Yes",
        """
        The date and time a scheduled report/search entity was created.

        Ex: created_on:'2021-10-12'
        Ex: created_on:<'2021-10-12'
        Ex: created_on:>'2021-10-12T03:00'
        """
    ),
    (
        "description",
        "String",
        "Yes",
        """
        A single term found in a scheduled report/search entity description.
        The value must be entered in all lowercase letters. Supports multiple values and negation.

        Ex: description:'process'
        Ex: description:!'process'
        Ex: description:['process','data']
        """
    ),
    (
        "expiration_on",
        "Timestamp",
        "Yes",
        """
        The date and time that a STOPPED scheduled report/search entity will be deleted.
        Set at 30 days after the report is stopped.

        Ex: expiration_on:'2021-12-15'
        Ex: expiration_on:>'2021-11-15T18'
        Ex: expiration_on:<'2021-12-03T03:30'
        """
    ),
    (
        "last_execution.last_updated_on",
        "Timestamp",
        "Yes",
        """
        The date and time of the last scheduled or manual execution.

        Ex: last_execution.last_updated_on:'2021-09-22'
        Ex: last_execution.last_updated_on:>'2021-09-22T11:30'
        """
    ),
    (
        "last_execution.status",
        "String",
        "Yes",
        """
        The status of the last execution. Supports multiple values and negation.
        Values must be in all capital letters.

        Values: PENDING, PROCESSING, DONE, FAILED, FAILED_NOTIFICATION, NO_DATA

        Ex: last_execution.status:'FAILED'
        Ex: last_execution.status:['PENDING','DONE']
        Ex: last_execution.status:!'PENDING'
        """
    ),
    (
        "last_updated_on",
        "Timestamp",
        "Yes",
        """
        The date and time of the last update made to a scheduled report/search entity.

        Ex: last_updated_on:'2021-10-12'
        Ex: last_updated_on:>'2021-10-12'
        Ex: last_updated_on:<'2021-10-12T03:00'
        """
    ),
    (
        "name",
        "String",
        "Yes",
        """
        Filters on exact matches to the full scheduled report/search entity name.
        Case-sensitive. Supports multiple values and negation.

        Ex: name:'My Test Report'
        Ex: name:['My Test scheduled Report','My test scheduled search']
        Ex: name:!'My Test scheduled Report'
        """
    ),
    (
        "next_execution_on",
        "Timestamp",
        "Yes",
        """
        The date and time of the next scheduled execution.

        Ex: next_execution_on:<'2021-11-01'
        """
    ),
    (
        "shared_with",
        "String",
        "Yes",
        """
        The unique ID of a user who the scheduled report has been shared with.
        (Scheduled searches cannot be shared.) Supports multiple values and negation.

        Ex: shared_with:'26eab16d-0b73-452d-b807-afc58f097aad'
        Ex: shared_with:!'26eab16d-0b73-452d-b807-afc58f097aad'
        """
    ),
    (
        "start_on",
        "Timestamp",
        "Yes",
        """
        The date and time to begin generating executions. Set to the Start date
        defined in the entity configuration.

        Ex: start_on:<'2021-10-01'
        """
    ),
    (
        "status",
        "String",
        "Yes",
        """
        The current status of a scheduled report/search entity.
        Supports multiple values and negation. Values must be in all capital letters.

        Values: ACTIVE, PENDING, STOPPED, UPDATING

        Ex: status:'PENDING'
        Ex: status:!'ACTIVE'
        Ex: status:['STOPPED','UPDATING']
        Ex: status:!['STOPPED','UPDATING']
        """
    ),
    (
        "stop_on",
        "Timestamp",
        "Yes",
        """
        The date and time to stop generating executions. Set to the End date
        defined in the entity configuration.

        Ex: stop_on:'2021-12-31'
        """
    ),
    (
        "type",
        "String",
        "Yes",
        """
        The type of entity (scheduled report or scheduled search).
        Supports multiple values and negation. Values must be in all lowercase letters.

        Values: event_search (scheduled searches), cloud_security_posture_detections_ioa,
        cloud_security_posture_detections_iom, cloud_security_image_vulnerabilities,
        cloud_security_container_vulnerabilities, cloud_security_container_details,
        cloud_security_image_detections, dashboard, discover_applications, filevantage,
        hosts, spotlight_installed_patches, spotlight_remediations, spotlight_vulnerabilities,
        spotlight_vulnerability_logic

        Ex: type:'event_search' (scheduled searches only)
        Ex: type:!'event_search' (scheduled reports only)
        Ex: type:['hosts','spotlight_remediations']
        """
    ),
    (
        "user_id",
        "String",
        "Yes",
        """
        The username (typically an email address) who created the scheduled report/search entity.

        Ex: user_id:'diana.hudson@email.com'
        Ex: user_id:!'diana.hudson@email.com'
        Ex: user_id:['diana.hudson@email.com','aiden.dean@email.com']
        """
    ),
]

SEARCH_SCHEDULED_REPORTS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search Scheduled Reports Guide

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
• !~ = does not text match
• * = wildcard matching (one or more characters)

=== DATA TYPES & SYNTAX ===
• Strings: 'value' or ['exact_value'] for exact match
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format)
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)
• Wildcards: 'partial*' or '*partial' or '*partial*'

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition
• ( ) = Group expressions

=== MULTIPLE VALUES ===
Use brackets for OR logic: filter=type:['hosts','filevantage']
Or repeat filter name: filter=type:'hosts',type:'filevantage'

=== MULTIPLE FILTERS ===
Use URL-encoded + (%2B) between filters:
filter=status:'ACTIVE'%2Bfilter=type:'event_search'

=== falcon_search_scheduled_reports FQL filter options ===

""" + generate_md_table(SEARCH_SCHEDULED_REPORTS_FQL_FILTERS) + """

=== EXAMPLE USAGE ===

• id:'45c59557ded4413cafb8ff81e7640456' - Get specific report by ID
• id:['id1','id2'] - Get multiple reports by ID
• status:'ACTIVE' - Active reports/searches
• type:'event_search' - Scheduled searches only
• type:!'event_search' - Scheduled reports only
• status:'ACTIVE'+type:'event_search' - Active scheduled searches
• created_on:>'2023-01-01' - Created after date
• user_id:'user@email.com' - Created by specific user
• last_execution.status:'FAILED' - Last execution failed
• status:'ACTIVE'+created_on:<'2021-09-15' - Active reports created before date
• type:['hosts','spotlight_remediations'] - Specific report types

=== IMPORTANT NOTES ===
• Use single quotes around string values: 'value'
• Use square brackets for exact matches: ['exact_value']
• Date format must be UTC: 'YYYY-MM-DDTHH:MM:SSZ'
• Status values are case-sensitive (use ALL CAPS)
• Type values must be lowercase
"""

# Scheduled report/search execution FQL filters
SEARCH_REPORT_EXECUTIONS_FQL_FILTERS = [
    (
        "Name",
        "Type",
        "Operators",
        "Description"
    ),
    (
        "id",
        "String",
        "Yes",
        """
        The unique ID of an execution. Use this to retrieve specific executions
        by ID. Supports multiple values.

        Ex: id:'f1984ff006a94980b352f18ee79aed77'
        Ex: id:['id1','id2']
        """
    ),
    (
        "created_on",
        "Timestamp",
        "Yes",
        """
        The date and time an execution was generated.

        Ex: created_on:'2021-10-12'
        Ex: created_on:<'2021-10-12'
        Ex: created_on:>'2021-10-12T03:00'
        """
    ),
    (
        "expiration_on",
        "Timestamp",
        "Yes",
        """
        The date and time that an execution will be deleted from the system.
        Set at 30 days after the execution is generated.

        Ex: expiration_on:'2021-12-15'
        Ex: expiration_on:>'2021-11-15T18'
        Ex: expiration_on:<'2021-12-03T03:30'
        """
    ),
    (
        "last_updated_on",
        "Timestamp",
        "Yes",
        """
        The date and time of the last update made to a scheduled report/search execution.
        Execution updates refer to a change in status.

        Ex: last_updated_on:'2021-10-12'
        Ex: last_updated_on:>'2021-10-12'
        Ex: last_updated_on:<'2021-10-12T03:00'
        """
    ),
    (
        "result_metadata.*",
        "Various",
        "Yes",
        """
        Scheduled search result details. Fields: execution_start, execution_duration,
        execution_finish, report_file_name, report_finish, result_count, result_id,
        search_window_start, search_window_end, queue_duration, queue_start

        Ex: result_metadata.execution_start:<'2021-10-12'
        Ex: result_metadata.result_count:>100
        """
    ),
    (
        "scheduled_report_id",
        "String",
        "Yes",
        """
        The unique ID of the scheduled report/search entity. Use this to get all
        executions for a specific entity. Supports multiple values and negation.

        Ex: scheduled_report_id:'e163544433ab1020b1a4117d1a8421b5'
        Ex: scheduled_report_id:['id1','id2']
        Ex: scheduled_report_id:!'e163544433ab1020b1a4117d1a8421b5'
        """
    ),
    (
        "shared_with",
        "String",
        "Yes",
        """
        The unique ID of a user who has been shared on the scheduled report that
        generated the execution. Supports multiple values and negation.

        Ex: shared_with:'ae6b126d-0b73-452d-b807-afc58f097aad'
        Ex: shared_with:!'ae6b126d-0b73-452d-b807-afc58f097aad'
        """
    ),
    (
        "status",
        "String",
        "Yes",
        """
        The current status of an execution. Supports multiple values and negation.
        Values must be in all capital letters.

        Values: PENDING, PROCESSING, DONE, FAILED, FAILED_NOTIFICATION, NO_DATA

        Ex: status:'PENDING'
        Ex: status:['FAILED','NO_DATA']
        Ex: status:!['FAILED','FAILED_NOTIFICATION']
        Ex: status:!'NO_DATA'
        """
    ),
    (
        "type",
        "String",
        "Yes",
        """
        The type of entity (scheduled report or scheduled search). Supports multiple
        values and negation. Values must be in all lowercase letters.

        Values: event_search (scheduled searches), cloud_security_posture_detections_ioa,
        cloud_security_posture_detections_iom, cloud_security_image_vulnerabilities,
        cloud_security_container_vulnerabilities, cloud_security_container_details,
        cloud_security_image_detections, dashboard, discover_applications, filevantage,
        hosts, spotlight_installed_patches, spotlight_remediations, spotlight_vulnerabilities,
        spotlight_vulnerability_logic

        Ex: type:'event_search' (scheduled search executions only)
        Ex: type:!'event_search' (scheduled report executions only)
        Ex: type:['hosts','spotlight_remediations']
        """
    ),
    (
        "user_id",
        "String",
        "Yes",
        """
        The ID of the user who created the scheduled report/search entity that
        generated the execution.

        Ex: user_id:'diana.hudson@email.com'
        Ex: user_id:!'diana.hudson@email.com'
        Ex: user_id:['diana.hudson@email.com','jack.evans@email.com']
        """
    ),
]

SEARCH_REPORT_EXECUTIONS_FQL_DOCUMENTATION = """Falcon Query Language (FQL) - Search Report Executions Guide

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
• !~ = does not text match
• * = wildcard matching (one or more characters)

=== DATA TYPES & SYNTAX ===
• Strings: 'value' or ['exact_value'] for exact match
• Dates: 'YYYY-MM-DDTHH:MM:SSZ' (UTC format)
• Booleans: true or false (no quotes)
• Numbers: 123 (no quotes)
• Wildcards: 'partial*' or '*partial' or '*partial*'

=== COMBINING CONDITIONS ===
• + = AND condition
• , = OR condition
• ( ) = Group expressions

=== MULTIPLE VALUES ===
Use brackets for OR logic: filter=status:['FAILED','NO_DATA']
Or repeat filter name: filter=status:'FAILED',status:'NO_DATA'

=== MULTIPLE FILTERS ===
Use URL-encoded + (%2B) between filters:
filter=status:'DONE'%2Bfilter=created_on:>'2023-01-01'

=== falcon_search_report_executions FQL filter options ===

""" + generate_md_table(SEARCH_REPORT_EXECUTIONS_FQL_FILTERS) + """

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
"""

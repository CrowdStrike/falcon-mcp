"""
NGSIEM resources for Falcon MCP Server.

Contains references and brief guidance for NGSIEM/LogScale query functions.
"""

NGSIEM_QUERY_FUNCTIONS_DOCUMENTATION = """\
NGSIEM / LogScale query functions reference.

Use this when composing the queryString for NGSIEM searches. The canonical list of
functions, syntax, and examples is maintained in the LogScale documentation:
https://library.humio.com/data-analysis/functions.html
"""

NGSIEM_EVENT_FIELDS_DOCUMENTATION = """\
Sample queries

For some sample queries, you must insert your own data. For example, you can use a
query to show a list of EndOfProcess events on a specific host that you specify.

Go to Investigate > Search > Advanced event search and run this query:

    #event_simpleName=EndOfProcess ComputerName=my-host-name
    | groupBy(ComputerName, function=(sum("MaxThreadCount", as=MaxThreadCount)))

For more sample queries, see Hunting Queries: CrowdStrike Query Language.

Key data fields

These are some of the most commonly used data fields associated with events. Fields
that begin with lowercase letters are present in all events.

Field Name: aid
Description: The sensor ID. This value is unique to each installation of a Falcon
sensor. When a sensor is reinstalled, the host gets a new aid. In those situations,
a single host could have multiple aid values over time.
Example value: "a26a23c103cb4c9s5c39aa09effa5662"

Field Name: aip
Description: The sensor's IP, as seen from the CrowdStrike cloud. This is typically
the public IP of the sensor. This helps determine the location of a computer,
depending on your network.
Example value: "#.##.#.###"

Field Name: ComputerName
Description: The name of the host.
Example value: "my-host-name"

Field Name: ContextProcessId
Description: The unique ID of a process that was spawned by another process. For
example, if Process 1 spawns Process 2, the TargetProcessId of Process 1 will match
the ContextProcessId of Process 2.
Example value: "22603276734"

Field Name: ContextThreadId
Description: UTID of thread originating this event.
Example value: "395202677966"

Field Name: ContextTimeStamp
Description: The time at which an event occurred on the system, as seen by the
sensor. Not to be confused with timestamp which is the time the event was received
by the cloud.
Example value: "1309294523.160"

Field Name: event_platform
Description: The platform on which the sensor is running.
Example value: "Win"/"Mac"/"Lin"

Field Name: event_simpleName
Description: The name of the event.
Example value: "SuspiciousDnsRequest"

Field Name: FileName
Description: The name of the file.
Example value: "my_file.docx"

Field Name: FilePath
Description: The full path of the file, including the file name.
Example value: "\\Device\\HarddiskVolume1\\sds2\\1043\\asdj64.exe"

Field Name: TargetProcessId
Description: The unique ID of a target process. This field exists in almost all
events, and it represents the ID of the process that is responsible for the activity
of the event in focus. For example, the TargetProcessId of a process that performed
thread injection in an InjectedThread event.
Example value: "167558096500"

Field Name: timestamp
Description: Timestamp when the event was received by the CrowdStrike cloud. Not to
be confused with the time the event was generated locally on the system. timestamp is
epoch formatted. To make timestamps reader-friendly, add the search parameter that
corresponds to your environment.
Example value: 1508334994001

Field Name: _time
Description: Timestamp of the moment that the event was received by the CrowdStrike
cloud. This is not to be confused with the time the event was generated locally on
the system. This is the timestamp of the event from the cloud's point of view. This
value can be converted to any time format and can be used for calculations.
Example value: "10/19/2017 18:10:29.396"

Field Name: TreeId
Description: If this event is part of a detection tree, the tree ID it is part of.
Example value: "42958187116"
"""

NGSIEM_EVENT_ONTOLOGY_DOCUMENTATION = """\
NGSIEM event ontology reference.

This resource describes the local ontology metadata for NGSIEM events. Use the
tools `falcon_get_ngsiem_event_schema` and `falcon_search_ngsiem_events` to query
the local ontology_events.json data for:
- event_simpleName values (tables)
- field names available per event
- descriptions that explain each event
"""

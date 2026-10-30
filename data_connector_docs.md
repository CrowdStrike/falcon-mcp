Next-Gen SIEM




  Copyright © CrowdStrike
                                                         Next-Gen SIEM


1. Data Connectors
   1.1. Overview
   1.2. Requirements
   1.3. Understanding third-party connectors
          1.3.1. Data sources
          1.3.2. Connector types
          1.3.3. Provisioning
                   1.3.3.1. Pull connectors
                   1.3.3.2. Push connectors
          1.3.4. Data ingestion
                   1.3.4.1. Push-based connector ingestion
                             1.3.4.1.1. Push-based connector endpoints
                                       1.3.4.1.1.1. HEC Collector
                                       1.3.4.1.1.2. HEC Raw Collector
                                       1.3.4.1.1.3. Humio Structured
                                       1.3.4.1.1.4. Humio Unstructured
                                       1.3.4.1.1.5. Humio Raw
          1.3.5. Data ingestion limits
                   1.3.5.1. Event truncation behaviors
                   1.3.5.2. Limits for push-based connectors
                   1.3.5.3. Limits for pull-based connectors
                   1.3.5.4. Limits for streaming-based connectors
                   1.3.5.5. Limits for AWS S3-based connectors
          1.3.6. Third-party data source integration guides

   1.4. Manage connectors
          1.4.1. Add a new connector
                   1.4.1.1. Add a pull-based connector
                   1.4.1.2. Add a push-based connector
          1.4.2. View and manage connections
          1.4.3. View connection details
                    1.4.3.1. Connection Activity
                   1.4.3.2. Execution History
          1.4.4. Edit a connection
                   1.4.4.1. Manage sources and ingestion
          1.4.5. Generate a push connector API key
          1.4.6. Pause a connection
          1.4.7. Delete a connection
          1.4.8. Show error history
          1.4.9. Show events
         1.4.10. View audit logs

   1.5. Manage alerts for third-party data connectors
   1.6. Falcon Flight Control for third-party data connections
          1.6.1. View connectors and daily data ingestion for child CIDs
          1.6.2. Manage daily data ingestion limits for child CIDs
          1.6.3. Manage alerts for child CIDs

   1.7. View the Next-Gen SIEM Connector dashboard
   1.8. Manage parsers
   1.9. Manage Third-Party Detection Exclusions
  1.10. Common issues
         1.10.1. Data connection errors




                                                              Page 2 of 29
                                                 Next-Gen SIEM



Data Connectors
Set up and manage automated data ingestion pipelines between third-party systems and Falcon.


Overview
Create data connectors in the Falcon console to automate and manage ingestion from third-party data sources. You can
seamlessly bring in data from a range of CrowdStrike Store applications for downstream analysis and processing in
Falcon to unlock insights and enhance your overall security posture.




Requirements
Requires one of more of these subscriptions:

       For asset and event data ingestion:

                 Falcon Next-Gen SIEM

                 Falcon Next-Gen SIEM 10GB

       For asset and risk data ingestion:

                 Falcon Exposure Management

Default roles:

These roles can create, view, and manage connectors and parsers:

       Falcon Administrator

       Next-Gen SIEM Administrator

       Falcon Exposure Management Manager

       Connector Manager

This role can view connectors and parsers only: Connector Viewer

Custom role permissions:




                                                    Page 3 of 29
                                                  Next-Gen SIEM

       Third Party Ingest:

               Read data connector

               Write data connector

               Read data connectors alerts

               Write data connectors alerts

               Read data connectors notification preferences

               Write data connectors notification preferences

               ​Read permission on parser

               Write permission on parser

       Marketplace Services:

               Activate store app

               Read store app

               Create app config

               Delete app config

               Read app config

               Update app config

               Read app config schema

CrowdStrike clouds: Available in US-1, US-2, US-3, and EU-1. For info about the availability of data connectors in US-
GOV-1 and US-GOV-2, see the documentation specific to the data connector.




Understanding third-party connectors
Connectors offload the complexity around setting up and managing data ingestion pipelines from sources outside of
Falcon. You create connectors in the Falcon console and configure settings on the data source that set up the service-
to-service integration between the third-party system and the Falcon cloud. The connector facilitates secure access to
the data source, automates ingestion, and sends ingested data to a predefined destination in Falcon for processing.

Data sources

Data connectors support data ingestion from select data sources. You can view the supported data connectors
available for configuration from the Falcon console at Next-Gen SIEM > Log management > Data onboarding or
Connectors > Data connectors > Data connections .

Certain connectors allow you to streamline data ingestion by importing multiple types of data for use across multiple
Falcon features. For more info, see Data connectors for multiple solutions.




Connector types

Falcon uses two types of connectors, which are defined by the way data is served up from the source. Based on the
nature of the interaction between Falcon and the data source, a connector operates in either a push- or pull-based
manner.


                                                     Page 4 of 29
                                                   Next-Gen SIEM

       Push-based connectors: Push connectors let other systems send, or “push,” data to Falcon. The data source
       drives the transfer operation and pushes new data to a CrowdStrike-provided URL whenever it’s available.
       Pull connectors manually retrieve, or “pull,” data from a source. Data is pulled from a third-party data source,
       such as a vendor's API. The schedule and frequency of the data retrieval depends on the data connector.




Provisioning

Part of the connector setup process includes configuration at the data source level. Each provider has its own unique
settings and details that are required. Depending on the connector type, this configuration occurs at a different point in
the workflow and in either the Falcon console or the provider interface.

Pull connectors

Pull connectors contain a Data source configuration model with provider-specific fields that define how Falcon should
access and retrieve data from the source. When creating a new connector in the Falcon console, the system prompts
you to create a data source configuration and presents you with the fields required by your data source. This
configuration is saved in Falcon and can be reused in other connectors your organization creates for the data source.
For more info, see Add a pull-based connector. To learn more about specific provider configuration field requirements,
see the CrowdStrike third-party integration documentation for your data source.




Push connectors

Falcon assigns each push connector a unique ingest URL and key. After creating a connector in the Falcon console,
you enter this info and configure other settings directly on the third-party system that define how to push data on the
URL with the key. You can find more info about required configuration steps in the CrowdStrike third-party integration
documentation for your data source.




Data ingestion

Review the following data ingestion details and requirements before configuring your data connector type.

Push-based connector ingestion

Push-based connectors require an authorization header with bearer token to route data to Falcon Next-Gen SIEM.

To establish a data connection, you generate an API key and API URL in Next-Gen SIEM during push-based connector
setup. This API URL contains the endpoint for your data connection.

There are five endpoint types used by push-based data connectors. See these topics for each of the following
endpoints:

       HEC Collector
       HEC Raw Collector
       Humio Structured
       Humio Unstructured
       Humio Raw

For efficient data ingestion with push-based data connector endpoints, we recommend these techniques:




                                                      Page 5 of 29
                                                    Next-Gen SIEM

        Event batching: Batch multiple events per request, based on the maximum payload size and a feasible
        maximum local time window, to ensure efficiency and timely delivery.

        Compression: Compressing the request payload reduces network latency. Supported formats include gzip and
        Deflate.

        Optional header: Adding the Uncompressed-Content-Length header to requests fails the request faster if it
        exceeds payload size limit. This value should be in the number of bytes.

        Request time out: Setting request time out to 35 seconds to avoid connection issues.

Once a connection is established, you can see one of the following HTTP response codes as received by your data
shipper.


  Code               Description

  200                Success. The data sent in the payload should be searchable.

  400                Bad request. Might indicate invalid data format or no data.

  403
                     Bad request. Might indicate one of these issues:

                             Authorization token is incorrect

                             Data connection is deleted

                             Data connection ID format is invalid

                             Data connection is paused

                     Check the data connection ID in the URL, the data connection's status, and if the valid API key is
                     configured for the request.

                     You can also regenerate an API key to help resolve this issue. For more info, see Generate a push
                     connector API key.


  401
                     Bad request. Might indicate the provided API key doesn't have required permission to ingest data
                     into Next-Gen SIEM. You might be using an invalid API key.

                     You can regenerate an API key to help resolve this issue. For more info, see Generate a push
                     connector API key.


  413                Bad request. The payload size exceeds the allowed limit.

  404                Bad request. Connection is accessing non-existent endpoints.

  429                Too many requests. This is a transient error that might occur in rare cases. Wait and retry the
                     request.

  5xx/timeouts       This transient error might occur in rare cases. Wait and retry the request.


Push-based connector endpoints


API endpoints available for push-based data connectors.




                                                       Page 6 of 29
                                                         Next-Gen SIEM
HEC Collector



Endpoints

            /api/ingest/hec/<dataconnection_id>/v1/services/collector
            https://<dataconnection_id>.<baseURL>/services/collector
            /api/ingest/hec/<dataconnection_id>/v1/services/collector/event

Payload format: Request payload can be a single JSON object, multiple line-delimited JSON objects, or a JSON array of
objects.

Payload specifications:

            Each object is ingested as a single event.

            Objects can contain a batch of events.

            Each object can contain one or more of the fields in this table. All fields are optional.


    Field          Description                                           Representation in Next-Gen SIEM
    Name

    time                                                                 Represented as time with millisecond precision on
                   Time, in seconds as of January 1, 1970, in
                                                                         ingestion. This is translated to @timestamp on
                   UTC. This can be an integer or floating point         ingestion. For more info, see Metadata Fields -
                   number to support milliseconds.                       @timestamp.
                   Time can be interpreted in any of these
                   formats:

                           Integer: Treated as seconds.

                           Float/Double: Treated as seconds plus
                           milliseconds.

                           String: Parsed to an integer or float
                           and then treated seconds plus
                           milliseconds.


    event          This can be a JSON object, a string, or an            This is translated to the @rawstring field on
                   array. If a JSON array, the entire array              ingestion. For more info, see Metadata Fields -
                   represents one event only.                            @rawstring.

    fields         JSON object containing extra event metadata           For more info about adding tags, see Tags.
                   fields. Tags can be added to the event by
                   specifying fields starting with #.


Example: This line-delimited JSON object example request creates 3 events, as there are 3 line-delimited JSON objects
in the request payload.

curl -v -X POST $3PI_BASE_URL/api/ingest/hec/<dataconnection_id>/v1/services/collector \
      -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: text/plain; charset=utf-8" \
      -d @- << EOF
{
      "time": 1537537729.0,
      "event": "Fri, 21 Sep 2018 13:48:49 GMT - system started name=webserver",
      "fields": {
                "#env": "prod",
                "someField1": "data-value1",


                                                              Page 7 of 29
                                                Next-Gen SIEM

           "someField2": "data-value2",
           "category": [
                "foo",
                "bar"
           ]
      }
}
{
      "time": 1537535729.0,
      "event": {
           "message": "System shutdown",
           "host": {
                "ip": "127.0.0.1",
                "port": 2222
           }
      },
      "fields": {
           "#datacenter": "amazon-east1"
      }
}
{
      "time": 1537535729.0,
      "event": ["a","b","c"],
      "fields": {
           "#datacenter": "amazon-east1"
      }
}
EOF

Example: This JSON array example request creates 2 events, as there are 2 objects in the JSON array.

curl -v -X POST $3PI_BASE_URL/api/ingest/hec/<dataconnection_id>/v1/services/collector \
      -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: text/plain; charset=utf-8" \
      -d @- << EOF
[
      {
           "time": 1537537729.0,
           "event": "Fri, 21 Sep 2018 13:48:49 GMT - system started name=webserver",
           "fields": {
                "#env": "prod",
                "someField1": "data-value1",
                "someField2": "data-value2",
                "category": [
                     "foo",
                     "bar"
                ]
           }
      },
      {
           "time": 1537535729.0,
           "event": {
                "message": "System shutdown",
                "host": {
                     "ip": "127.0.0.1",
                     "port": 2222
                }
           },
           "fields": {
                "#datacenter": "amazon-east1"
           }
      }




                                                   Page 8 of 29
                                                      Next-Gen SIEM

]
EOF




HEC Raw Collector



Endpoint: /api/ingest/hec/<dataconnection_id>/v1/services/collector/raw

Payload format: Request payload is a series of line-delimited raw strings.

Payload specifications:

            Each line represents an event.

            A batch of events can be sent in a single request.

            Each line is translated to the @rawstring field on ingestion.

Example: Creating two events with the HEC Raw Collector endpoint.

curl -v -X POST $3PI_BASE_URL/api/ingest/hec/<dataconnection_id>/v1/services/collector/raw \
      -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: text/plain" \
      -d @- << EOF
2024-10-18 06:51:33 [Helper Tool] Info CD063E71-9F0A-4861-99A8-28204DE1234: Helper Tool Initialized.
2024-10-18 06:51:33 [Helper Tool] Info CD063E71-9F0A-4861-99A8-28204DE1234: New Connection requested
from pid: 33184
EOF




Humio Structured



Endpoints

            /api/ingest/humio/<dataconnection_id>/v1/humio-structured

            /api/ingest/humio/<dataconnection_id>/api/v1/ingest/humio-structured

Payload format: Request payload is a JSON array of JSON objects.

Payload specifications:

            A batch of events can be sent in a single request.

            Each JSON object can contain an array of events, which are JSON objects, containing one or more of these
            fields in the table.


    Field            Required          Description                                   Representation in Next-Gen SIEM
    name

    timestamp        Yes                                                             Represented as time with
                                       You can specify the timestamp in two          millisecond precision on
                                       formats:                                      ingestion. This is translated to
                                                                                     @timestamp on ingestion. For
                                                                                     more info, see Metadata Fields -
                                                                                     @timestamp.




                                                         Page 9 of 29
                                                Next-Gen SIEM

                                        A number, which must be provided
                                        as an integer, that sets the time in
                                        milliseconds (Unix time). The number
                                        must be in UTC time, not local time.

                                        An ISO 8601 formatted string, for
                                        example, yyyy-MM-
                                        dd'T'HH:mm:ss.SSSZ.


    timezone       Yes,                                                           This field is translated to
                                 The time zone is only required if you specify
                   depending                                                      @timezone on ingestion.
                   on            the timestamp in milliseconds. Time zone         @timezone is the timezone the
                   timestamp     specifies the local time zone for the event.     event originated in, if known. For
                                 Important: You must still specify the            more info, see Metadata Fields -
                                 timestamp as an integer in UTC time.             @timezone.



    attributes     No                                                             If you don’t provide the rawstring
                                 A JSON object representing key-value pairs
                                                                                  field, then the JSON
                                 for the event. These key-value pairs add
                                                                                  representation of the attributes
                                 metadata fields to events, making it easier to   field is translated to @rawstring
                                 search.
                                                                                  instead of adding metadata fields
                                 Attributes can be nested JSON objects, but       to the event. For more info, see
                                                                                  Metadata Fields - @rawstring.
                                 it is recommended to limit the amount of
                                 nesting. In the case of nested objects, they
                                 are flattened to string values.


    rawstring      No            The raw string represents the event.
                                                                                  This field is translated to a
                                                                                  @rawstring on ingestion.

                                                                                  If you don’t provide the rawstring
                                                                                  field, then the JSON value of the
                                                                                  attributes field is translated to
                                                                                  @rawstring. For more info, see
                                                                                  Metadata Fields - @rawstring.


    tags           No
                                 A JSON object containing key-value pairs         On ingestion, any value specified
                                 that act as metadata,                            here become tags, such as
                                                                                  #mytagname.
                                 applied to all the events within the same
                                 JSON object. Can’t be specified for              For more info, see Tags.
                                 individual events.



Example: Create two events from the first JSON object and one event from the second object in the JSON array.

curl -v -X POST $3PI_BASE_URL/api/ingest/humio/<dataconnection_id>/v1/humio-structured \
      -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: text/plain; charset=utf-8" \
      -d @- << EOF
[
      {
           "tags": {
                 "host": "server1",
                 "source": "application.log"


                                                   Page 10 of 29
                                                         Next-Gen SIEM

             },
             "events": [
                     {
                           "timestamp": "2016-06-06T13:00:00+02:00",
                           "attributes": {
                                "hello": "world"
                           }
                     },
                     {
                           "timestamp": "2016-06-06T13:00:01+02:00",
                           "attributes": {
                                "statuscode": "200",
                                "url": "/index.html"
                           }
                     }
             ]
      },
      {
             "tags": {
                     "host": "server2",
                     "source": "application.log"
             },
             "events": [
                     {
                           "timestamp": 1748167746000,
                           "timezone": "UTC",
                           "attributes": {
                                "key1": "value1"
                           },
                           "rawstring": "my raw string"
                     }
             ]
      }
]
EOF




Humio Unstructured



Endpoints

            /api/ingest/humio/<dataconnection_id>/api/v1/ingest/humio-unstructured

            /api/ingest/humio/<dataconnection_id>/v1/humio-unstructured

            https://<dataconnection_id>.<baseURL>/api/v1/ingest/humio-unstructured

Payload format: The request payload is a JSON array of JSON objects, containing one or more of the fields in the table.

Payload specification: A batch of events can be sent in a single request.


    Field                 Required   Description                                      Representation in Next-Gen SIEM
    name

    messages              yes        A JSON array of line-delimited raw               Each raw string is translated to
                                     strings. Each string represents an event.        @rawstring on ingestion. For more
                                                                                      info, see Metadata Fields - @rawstring.

    fields                no         Every message field is annotated with the        These are translated to user fields
                                     value in this field. This value is in the form   associated with the event on ingestion.


                                                            Page 11 of 29
                                                Next-Gen SIEM

                              key: value. Values must be strings.

    tags           no         Annotates each of the messages with
                                                                          Become tags, for example
                              metadata using these key-values as tags.
                                                                          #mytagname, on ingestion.

                                                                          For more info, see Tags.



Example: Create four events from the messages array in the first JSON object and one event from the messages array
in the second JSON object, from the outermost JSON array.

curl -v -X POST $3PI_BASE_URL/api/ingest/humio/<dataconnection_id>/v1/humio-unstructured \
      -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: text/plain" \
      -d @- << EOF
[
      {
            "fields": {
                 "host": "webhost1"
            },
            "tags": {
                 "mytag": "mytag1"
            },
            "messages": [
                 "192.168.1.21 - user1 [02/Nov/2017:13:48:26 +0000] \"POST /humio/api/v1/ingest/elastic-
bulk HTTP/1.1\" 200 0 \"-\" \"useragent\" 0.015 664 0.015",
                 "192.168.1.49 - user1 [02/Nov/2017:13:48:33 +0000] \"POST /humio/api/v1/ingest/elastic-
bulk HTTP/1.1\" 200 0 \"-\" \"useragent\" 0.014 657 0.014",
                 "192.168.1.21 - user2 [02/Nov/2017:13:49:09 +0000] \"POST /humio/api/v1/ingest/elastic-
bulk HTTP/1.1\" 200 0 \"-\" \"useragent\" 0.013 565 0.013",
                 "192.168.1.54 - user1 [02/Nov/2017:13:49:10 +0000] \"POST /humio/api/v1/ingest/elastic-
bulk HTTP/1.1\" 200 0 \"-\" \"useragent\" 0.015 650 0.015"
            ]
      },
      {
            "fields": {
                 "host": "webhost2"
            },
            "tags": {
                 "mytag": "mytag2"
            },
            "messages": [
                 "192.168.1.74 - user1 [02/Nov/2017:13:48:26 +0000] \"POST /humio/api/v1/ingest/elastic-
bulk HTTP/1.1\" 200 0 \"-\" \"useragent\" 0.015 664 0.015"
            ]
      }
]
EOF




Humio Raw



Endpoints

           /api/ingest/humio/<dataconnection_id>/v1/raw

           /api/ingest/humio/<dataconnection_id>/api/v1/ingest/raw

Payload format: The entire request payload represents one event.




                                                  Page 12 of 29
                                                      Next-Gen SIEM

Payload specifications

       Sending a batch of events in one request is not possible.

       Avoid ingesting large volumes of events as it can slow data processing.

Example: Creating one event.

curl -v -X POST $3PI_BASE_URL/api/ingest/humio/<dataconnection_id>/v1/raw \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: text/plain; charset=utf-8" \
    -d 'My raw Message generated at "2016-06-06T12:00:00+02:00"'




Data ingestion limits

Each data connector has data ingestion limits for both size and rate. These limits can vary by type of connector as well
as per product or vendor.

Event truncation behaviors

Event trunctation behaviors for all data connectors:

       Event size is calculated as the total of the raw message (@rawstring), fields, tags, and other metadata, like
       timestamp and time zone. Events exceeding the maximum event size limit are truncated.

       If an event contains fields, they are sorted and removed in reverse alphabetical order (z-a) until the event is
       within the size limit. Tags are not removed.

       If an event still exceeds max size, trailing bytes of the raw message are removed until event size is within the
       size limit.

Event truncation behavior definitions for pull-based, streaming-based, and AWS S3-based data connectors:

       Simple removal: Data from the end of the event is removed until the event is within the size limit.

       Field removal: If the event contains fields, the fields are sorted and removed in reverse alphabetical order (z-a)
       until the event is within the size limit. Tags are not removed from the event. If the event does not contain fields, or
       if the event is still too large after structured fields are removed, data from the end of the event is removed until
       the event is within the size limit.

       Discarded: If the event is larger than the size limit, the event is not ingested.

To identify events that have been truncated, look for these indicators:

       The raw message ends with an ellipsis (...).
       An extra field, @error_msg, is appended to the event.
       The event field @error has the value True.




Limits for push-based connectors

All push-based connector endpoints share the same data ingestion limits.




                                                       Page 13 of 29
                                                  Next-Gen SIEM

         Maximum 7999 fields per event. Additional fields are ignored.

         Maximum payload size before compression. If exceeded, a 413 error is returned.

                Humio Raw endpoint: 999,000 bytes.

                All other endpoints: 32MB (32*1000*1000 bytes)
                Tip: We recommend keeping log files at least 2MB below the 32MB maximum limit, as approximately
                1MB of metadata is added during ingestion.

         Maximum payload size for all endpoints, except the Humio Raw endpoint after compression, is 32MB
         (32*1000*1000 bytes). If exceeded, a 413 error is returned.

         Maximum event size is 950KB (950*1000 bytes). If exceeded, the event is truncated.




Limits for pull-based connectors

For pull-based connectors, polling frequency limits are different for each connector depending on the third-party
vendor's configurations.


  Data connector            Lookback period                        Polling frequency          Max         Max event
                                                                   limit                      event       size before
                                                                                              size        truncation

  1Password                 31 days                                10 minutes                 950,000     1MB
  Extended Access                                                                             bytes
  Management

  Abnormal Security         240 minutes                            10 minutes                 950,000     1MB
                                                                                              bytes

  Akamai App and            4 minutes                              0.1 seconds                950,000     1MB
  API Protector                                                                               bytes

  Akamai Secure             15 days                                10 minutes                 950,000     1MB
  Internet Access                                                                             bytes
  Enterprise (SIA)

  Amazon S3 Access          Real time                              Real time                  950,000     1MB
  Logs                                                                                        bytes

  AWS Network               Real time                              Real time                  950,000     1MB
  Firewall                                                                                    bytes

  Amazon CloudFront         Real time                              Real time                  950,000     1MB
                                                                                              bytes

  Amazon Route 53           Real time                              Real time                  950,000     1MB
                                                                                              bytes

  AWS CloudTrail            Real time                              Real time                  950,000     1MB
                                                                                              bytes

  AWS Security Hub          Real time                              Real time                  950,000     1MB
                                                                                              bytes




                                                     Page 14 of 29
                                      Next-Gen SIEM

Amazon                 Real time                  Real time               950,000   1MB
CloudWatch                                                                bytes

Amazon Virtual         Real time                  Real time               950,000   1MB
Private Cloud (VPC                                                        bytes
Flow)

Amazon Security        Real time                  Real time               950,000   1MB
Lake                                                                      bytes

AWS Config             Real time                  Real time               950,000   1MB
                                                                          bytes

AWS Web                Real time                  Real time               950,000   1MB
Application Firewall                                                      bytes
(WAF)

Amazon GuardDuty       Real time                  Real time               950,000   1MB
                                                                          bytes

Armis Centrix for      90 days                    10 minutes              950,000   1MB
OT/IoT Security                                                           bytes

Atlassian Jira Cloud   1 day                      4 seconds               950,000   1MB
                                                                          bytes

Authentik              Current Time               5 minutes               950,000   1MB
                                                                          bytes

Box                    Current Time               10 minutes              950,000   1MB
                                                                          bytes

Cato SASE Cloud        Real time                  0.1 second when the     950,000   1MB
                                                  connector is actively   bytes
                                                  pulling data. If no
                                                  data is returned,
                                                  there is a 30 second
                                                  wait before the next
                                                  poll.

Cisco Duo MFA          60 minutes                 3 minutes               950,000   1MB
                                                                          bytes

Cisco Meraki           2 hours                    10 minutes              950,000   1MB
                                                                          bytes

Cisco Secure           Real time                  10 minutes              950,000   1MB
Access/Umbrella                                                           bytes

Claroty xDome          90 days                    60 minutes              950,000   1MB
                                                                          bytes

CrowdStrike Falcon     Real time                  Real time               950,000   1MB
Data Replicator                                                           bytes
(FDR)




                                       Page 15 of 29
                                  Next-Gen SIEM

CyberArk Audit       30 minutes               5 minutes    950,000   1MB
                                                           bytes

Dragos               1 day                    30 minutes   950,000   1MB
                                                           bytes

ForgeRock            15 second                2 minutes    950,000   1MB
(PingOne                                                   bytes
Advanced Identity
Cloud)

Fortinet FortiNDR    1 day                    5 minutes    950,000   1MB
Cloud                                                      bytes

Fortinet FortiCASB   2 hours                  10 minutes   950,000   1MB
                                                           bytes

OCI Streaming        Real time                Real time    950,000   1MB
                                                           bytes

Google Cloud         Real time                Real time    950,000   1MB
Pub/Sub                                                    bytes

Azure Event Hub      Real time                Real time    950,000   1MB
(Generic)                                                  bytes

AWS S3 (Generic)     Real time                Real time    950,000   1MB
                                                           bytes

Google Cloud         Real time                Real time    950,000   1MB
Identity Platform                                          bytes

Google Cloud         Real time                Real time    950,000   1MB
Firewall Rules                                             bytes

Google Workspace     Real time                Real time    950,000   1MB
                                                           bytes

Google Cloud Audit   Real time                Real time    950,000   1MB
Logs                                                       bytes

Google VPC Flow      Real time                Real time    950,000   1MB
Logs                                                       bytes

Lookout              10 days                  2 minutes    950,000   1MB
                                                           bytes

Menlo Security SSE   Real time                5 minutes    950,000   1MB
                                                           bytes

Menlo Security       Real time                5 minutes    950,000   1MB
Cloud Isolation                                            bytes
Platform

Microsoft Defender   Real time                Real time    950,000   1MB
XDR                                                        bytes




                                   Page 16 of 29
                                    Next-Gen SIEM

Microsoft 365          30 minutes               6-10 minutes,         950,000   1MB
                                                depending on ingest   bytes
                                                source

Microsoft Virtual      Real time                Real time             950,000   1MB
Network Flow Logs                                                     bytes

Microsoft Azure        Real time                Real time             950,000   1MB
VPN Gateway                                                           bytes

Microsoft Web          Real time                Real time             950,000   1MB
Application Firewall                                                  bytes

Microsoft Storage      Real time                Real time             950,000   1MB
Account Logs                                                          bytes

Microsoft Azure        Real time                Real time             950,000   1MB
Virtual Machine                                                       bytes

Microsoft Defender     Real time                Real time             950,000   1MB
for Office 365                                                        bytes
(Event Hubs)

Microsoft Defender     30 days                  10 minutes            950,000   1MB
XDR Alerts &                                                          bytes
Incidents

Microsoft Defender     Real time                Real time             950,000   1MB
for Cloud                                                             bytes

Microsoft Azure        Real time                Real time             950,000   1MB
Network Security                                                      bytes
Group

Microsoft Azure        Real time                Real time             950,000   1MB
Firewall                                                              bytes

Microsoft Defender     Real time                Real time             950,000   1MB
for Identity                                                          bytes

Microsoft Defender     Real time                10 minutes            950,000   1MB
for Endpoint                                                          bytes

Azure Activity Log     Real time                Real time             950,000   1MB
                                                                      bytes

Microsoft Azure Key    Real time                Real time             950,000   1MB
Vault                                                                 bytes

Microsoft Entra ID     Real time                Real time             950,000   1MB
                                                                      bytes

Microsoft Defender     30 minutes               10 minutes            950,000   1MB
for Office 365                                                        bytes
(Graph API)




                                     Page 17 of 29
                                   Next-Gen SIEM

Microsoft Intune       Real time               12 hours     950,000   1MB
                                                            bytes

Microsoft Azure        Real time               Real time    950,000   1MB
Managed Redis                                               bytes

Microsoft O365         1 day                   10 minutes   950,000   1MB
Message Trace                                               bytes

Mimecast               7 days                  10 minutes   950,000   1MB
                                                            bytes

Netskope Security      1 minute                10 minutes   950,000   1MB
Service Edge                                                bytes

Okta Identity          Real time               12 hours     950,000   1MB
                                                            bytes

Proofpoint On          Real time               Real time    950,000   1MB
Demand                                                      bytes

Proofpoint TAP         Real time               10 minutes   950,000   1MB
                                                            bytes

Proofpoint Cloud       1 day                   10 minutes   950,000   1MB
Threat Response                                             bytes

Qualys Vulnerability   1 day                   2 seconds    950,000   1MB
Management                                                  bytes

SailPoint Identity     1 day                   10 minutes   950,000   1MB
Security Cloud                                              bytes

Salesforce             7 days                  10 minutes   950,000   1MB
                                                            bytes

ServiceNow             1 day                   10 minutes   950,000   1MB
                                                            bytes

Slack                  1 day                   1 second     950,000   1MB
                                                            bytes

Snowflake              1 day                   5 minutes    950,000   1MB
                                                            bytes

SpyCloud               7 days                  30 minutes   950,000   1MB
Workforce Threat                                            bytes
Protection

Trellix Email          1 hour                  10 seconds   950,000   1MB
Security                                                    bytes

Vectra Respond UX      7 days                  10 minutes   950,000   1MB
                                                            bytes

Workday                7 days                  5 minutes    950,000   1MB
                                                            bytes


                                    Page 18 of 29
                                                  Next-Gen SIEM

  Zoom                     7 days                                 6 seconds                   950,000     1MB
                                                                                              bytes




Limits for streaming-based connectors

For streaming-based connectors, the data ingestion limits are different depending on the third-party vendor.


  Data connector                                                        Max event size      Event truncation behavior

  Data Connector built for Azure Virtual Machines                       950,000 bytes       Simple removal

  Data Connector built for Generic Microsoft Azure Event Hubs           950,000 bytes       Simple removal

  Data Connector built for Generic Microsoft Azure Event Hubs           950,000 bytes       Simple removal

  Data Connector built for Microsoft Azure Firewall                     950,000 bytes       Simple removal

  Data Connector built for Microsoft Azure Network Security Groups      950,000 bytes       Simple removal

  Data Connector built for Microsoft Azure VPN Gateway                  950,000 bytes       Simple removal

  Data Connector built for Microsoft Defender for Cloud                 950,000 bytes       Simple removal

  Data Connector built for Microsoft Defender for Identity              950,000 bytes       Simple removal

  Data Connector built for Microsoft Defender XDR Events                950,000 bytes       Simple removal

  Data Connector built for Microsoft Entra ID                           950,000 bytes       Simple removal

  Google Cloud Audit Logs Data Connector                                950,000 bytes       Simple removal

  Google Cloud Pub/Sub Data Connector                                   950,000 bytes       Simple removal

  Google Workspace Data Connector                                       950,000 bytes       Simple removal

  Netskope Transaction Logs Data Connector                              950,000 bytes       Simple removal




Limits for AWS S3-based connectors

For AWS S3-based connectors, the data ingestion limits are different depending on the third-party vendor and product.


  Data connector                                Max event size    Event truncation behavior

  Amazon CloudWatch Data Connector              950,000 bytes     Simple removal

  Amazon GuardDuty Data Connector               950,000 bytes     Simple removal

  Amazon S3 Access Log Data Connector           950,000 bytes     Simple removal

  Amazon S3 Data Connector                      950,000 bytes     Simple removal




                                                      Page 19 of 29
                                                  Next-Gen SIEM

  Amazon Security Lake Data Connector           950,000 bytes       Simple removal

  AWS Cloudtrail Data Connector                 950,000 bytes       Simple removal

  AWS Config Data Connector                     950,000 bytes       Simple removal

  AWS Network Firewall Data Connector           950,000 bytes       Simple removal

  AWS Security Hub Data Connector               950,000 bytes       Simple removal

  AWS VPC Flow Data Connector                   950,000 bytes       Simple removal

  AWS WAF Data Connector                        950,000 bytes       Simple removal

  Cisco Umbrella Data Connector                 950,000 bytes       Simple removal




Third-party data source integration guides

Find detailed information about data ingestion configuration in the CrowdStrike documentation for your data source.

       Third-Party Data Sources
       Falcon Insight for ChromeOS: Set up data ingestion




Manage connectors
Important: New data connector setup and configuration features are currently being released in phases across
CrowdStrike clouds. Setup instructions may not fully reflect your Falcon console environment.

Add a new connector

Connectors are configured from the Falcon console at Next-Gen SIEM > Log management > Data onboarding or
Connectors > Data connectors > Data connections .

The process is different for data that must be pushed or pulled from the source. For more info, see Add a push-based
connector and Add a pull-based connector.

Tip: You can also create a data connection using a parser from the Parsers tab in Next-Gen SIEM > Log management >
Data onboarding . For more info, see Add a data connection using a parser.

Add a pull-based connector

    1. In the Falcon console, go to Connectors > Data connectors > Data connections .

    2. Click + Add connection.
    3. In the Data Connectors page, filter or sort by Connector name, Vendor, Product, Connector Type, Author, or
       Subscription to find and select the connector you want to configure.
    4. In the New connection dialog, review connector metadata, version, and description. Click Configure.
       Note: For connectors that are in a Pre-production state, a warning dialog appears. Click Accept to continue
       configuration.
    5. In the Add new connector page, click Manage configurations.
    6. Create a configuration by entering values for the required fields in the configuration window or select an existing
       configuration. To edit a configuration from this window, select Edit   , then modify the field values.




                                                     Page 20 of 29
                                                  Next-Gen SIEM

       Important: For information about the required vendor-specific configuration fields, see Third-party data source
       integration guides. Modifications to a configuration are applied anywhere the configuration is used.
    7. Enter a name and an optional description to identify the connector.
    8. Optional. Verify if your event data includes timezone information. If not, select a timezone to ensure accurate
       search results and correlation rule processing. Important details about timezone:
              Timezone is only applied to event data that doesn't have existing timezone information.
              Daylight Saving Time adjustments are applied automatically to event data when a timezone is selected.
              If an event doesn't contain timezone information and a timezone is not selected, the parser assumes UTC
              as timezone. As a best practice, select the timezone matching your event source to align search results
               with the original event timestamps to avoid search result offsets.
    9. Optional. Host enrichment and User enrichment are enabled by default. If necessary, you can disable this
       feature by clicking the toggle off.

   10. Click the Terms and Conditions box, then click Save.




Add a push-based connector

    1. In the Falcon console, go to Connectors > Data connectors > Data connections .

    2. Click + Add connection.
    3. In the Data Connectors page, filter or sort by Connector name, Vendor, Product, Connector Type, Author, or
       Subscription to find and select the connector you want to configure.
       Tip: This data connector's name is located in the header. For example, Step 1: Configure and activate
       <the_data_connector_name>.
    4. In New connection, review connector metadata, version, and description. Click Configure.
       Note: For connectors that are in a Pre-production state, a warning appears. Click Accept to continue
       configuration.

    5. In the Add new connector page, enter a name and optional description to identify the connector.

    6. Optional. Verify if your event data includes timezone information. If not, select a timezone to ensure accurate
       search results and correlation rule processing. Important details about timezone:
              Timezone is only applied to event data that doesn't have existing timezone information.
              Daylight Saving Time adjustments are applied automatically to event data when a timezone is selected.
              If an event doesn't contain timezone information and a timezone is not selected, the parser assumes UTC
              as timezone. As a best practice, select the timezone matching your event source to align search results
              with the original event timestamps to avoid search result offsets.

    7. Click the Terms and Conditions box, then click Save.

    8. Optional. Host enrichment and User enrichment are enabled by default. If necessary, you can disable this
       feature by clicking the toggle off.
    9. A banner message appears in the Falcon console when your API key and API URL are ready to be generated.

       To generate the API key, go to Connectors > Data connectors > Data connections , click Open menu            for the
       data connector, and click Generate API key.
   10. Copy and safely store the API key and API URL to use during connector configuration.
       Important: Record your API key somewhere safe as it displays only once during connector setup. For more
       information about vendor-specific connector setup, see Third-party data source integration guides.




View and manage connections

Use the Data connections page to monitor the health of your data sources and optimize your data ingestion. The page
provides a real-time overview of connection statuses, comparative metrics for 30-day data volumes, and detailed



                                                    Page 21 of 29
                                                  Next-Gen SIEM

management capabilities for each configured connection.

Status of connections: View total counts per status and number of data connections.

Data ingest: In this chart, compare 30-day average and measured data ingest volumes, to optimize storage, costs, and
resources.

       Next-Gen SIEM: View the daily data ingest volume as a 30-day moving average, for Next-Gen SIEM only. Click
       Other to update the chart with ingest totals from other Falcon subscriptions, like Exposure Management, Falcon
       Discover for IoT and Endpoint Security.

Connections: See a summary information and access management capabilities for each connection.

       Connection name: The name you gave the connection when you configured it.

       Vendor: The name and logo of the company that the data source belongs to.

       Product: The name of the product to which the data source belongs to.

       Connector type: The type of connection defined by ingestion type. Ingestion type is either Push or Pull.

       Status: The status of the connection.

              Pending: A connection whose configuration is still in progress and not completed.

              Disconnected: The connection is down and data is not being ingested.

              Paused: The data connection is paused and cannot ingest or receive data.

              Active: A data connection receiving data with no error (has received data at least in one hour).

              Idle: A data connection that did not receive any data in the last one hour based on the event timestamp is
              an idle data connection.

              Error: A data connection that encountered an error in the last one hour is set to state Error. For the status
              to become Active, the connection must successfully ingest data without any errors for an hour. Click the
              Error link to see all errors for the selected data connection in Advanced Event Search. For more info
              about errors, see Show error history.

       Ingest (24h): The volume of data ingested by a connector in the last 24 hours, displayed in bytes.
       Note: A returned quantity of zero indicates the data connector has not ingested any data and might be
       misconfigured. For troubleshooting suggestions, see Data connection errors.

       Parser: The parser used by the data connection.

       Data type: The type of data ingested by the data connector. Data types include Events, Assets, or Risks. For
       more info, see Data ingested for each solution.

       Subscription: The part of the Falcon platform that is receiving the data, based on your Falcon subscription.
       Subscriptions include Next-Gen SIEM, Exposure Management, Falcon Discover for IoT, and Endpoint Security.


       Repo name: This column is hidden by default. To add it, click     Configure table columns and select Repo
       name. Click any repo name in this column to view details about the associated repo, including the repo name,
       data retention period (in days), latest data ingestion timestamp, and uncompressed data size.


       Actions: Options to view and manage a connection. Click Open menu       to see available actions. The list of
       actions changes based on the type of connector. For example, the Generate API key action is only available for
       Push-based connectors. The full list of actions includes Show details, Edit connection, Generate API key,
       Regenerate API key, Show error history, Show events, and Regenerate CFT URL.




                                                    Page 22 of 29
                                                   Next-Gen SIEM

View connection details

The Connection Details page provides information and management options for your connections.

       Connection identity: View and copy the connection name, description, and unique Connection ID for
       troubleshooting.

       Parser information: Access parser status, data source details, and scripts directly.

       Monitoring tools: Track connection status, 24-hour ingestion volume, and the most recent data ingestion
       timestamp.

       Configuration data: Access API URLs (push-based connectors) or data source configurations (pull-based
       connections).

       Management options: Edit connection settings, delete connections, and regenerate API keys (push-based
       connectors only).

To access the Connection details page in the Falcon console:

     1. Go to Data connectors > Data connectors > Data connections.

     2. In the Actions column, click Open menu and select Show details.

Connection Activity

Note: This feature is available only for data connections that support multiple sources.

The Connection Activity section gives you tools to monitor and manage your data connection and sources.

       View the status, 24-hour data ingestion volume (in bytes), and last ingestion date for a connection and its
       sources.

       View connection and source details in Advanced Event Search. From the Actions column, click Open ⋮ menu
       and select Show error history or Show events.




Execution History

View the last 72 hours of execution history for a data connection. For data connections with multiple ingest sources, see
the execution based on the sub-connections you’ve selected.

Filter by Error status to see all errors for a connection and begin resolving issues. For more info about troubleshooting
errors, see Data connection errors.




Edit a connection

You can edit the name and description of an existing connection. For pull-based connection, you can also modify the
data source configuration if you want to ingest a different dataset. If your connection has Enable parser selection
available, you can also change which parser is used to transform incoming data. For more info about parsers, see
Manage parsers.

Note: The connector’s data source and the assigned API URL (push-based connectors) cannot be changed.

     1. In the Falcon console, go to Connectors > Data connectors > Data connections .


     2. In the Actions column, click Open menu        and select Edit connection. The Connection details page opens.



                                                     Page 23 of 29
                                                    Next-Gen SIEM

     3. Make changes to the connection name, description, selected parser, or for pull-based connections make data
       source configurations as needed.

     4. Optional. Host enrichment and User enrichment are enabled by default. If necessary, you can disable this
        feature by clicking the toggle off.

     5. Click Save changes.

Manage sources and ingestion

Note: This feature is available only for data connections that support multiple sources.

On the Edit a Connection page, you can manage data ingestion for each source.

     1. To stop data ingestion from a source, deselect the source checkbox.

     2. Click Save changes. A warning message opens to confirm your changes.

     3. Click Save changes.

Important: After you confirm your changes, data ingestion stops immediately. To resume data ingestion, reselect the
source checkbox and click Save changes.




Generate a push connector API key

You generate an API key when you configure a Push connector. If you lose your API key or suspect that it’s been
compromised, you can generate a new one.

     1. In the Falcon console, go to Connectors > Data connectors > Data connections .

     2. In the Actions column, click Open menu         and select Generate API key. If you need to regenerate an API key,
        select Regenerate API key.

Important: When you regenerate an API key, the old key is no longer active. You must configure any third-party systems
or data shippers with the new API key. All access tokens issued before regenerating the API key are immediately
invalidated when the new key is created.




Pause a connection

Note: This action is only available for Push type connectors with a Status of Active, Error, or Idle.

Pausing a data connection stops the flow of data from your applications until resumed. You can temporarily pause a
connection from the Connections table:


     1. In the Actions column, click Open menu         and select Pause connection.
     2. In the Pause connection dialog, click Pause connection.

When a connection is paused, the Actions menu shows the Resume connection option. Click Resume connection to
enable the flow of data from your application to Next-Gen SIEM.




Delete a connection

You can delete a connection that you no longer need.
Important: After a connection is deleted it’s permanently removed from the system and cannot be restored.


                                                      Page 24 of 29
                                                     Next-Gen SIEM

     1. In the Falcon console, go to Connectors > Data connectors > Data connections .


     2. In the Actions column, click Open menu         and select Delete connection.

     3. A confirmation prompt appears. Click Delete connection to confirm deletion.




Show error history

You can learn more about errors generated by a data connection by accessing Advanced Event Search from the Data
Connections page.

     1. In the Falcon console, go to Connectors > Data connectors > Data connections .

     2. In the Actions column, click Open menu         and select Show error history.

     3. The Advanced event search page opens and an error query is run.

     4. Review Results to learn more about an error.

To learn more about investigating errors, see Data connection errors.




Show events

You can see a full list of events generated by a data connection by accessing Advanced Event Search from the Data
Connections page.

     1. In the Falcon console, go to Data connectors > Data connectors > Data connections.

     2. In the Actions column, click Open menu ⋮ and select Show events.

     3. The Advanced event search page opens and an events query is run.

     4. Review Results to learn more about an event.




View audit logs

You can review third-party data connection activities in the Falcon console as audit logs:

     1. Go to Audit logs > Audit logs > Falcon UI.

     2. From the Category filter, select Third party data connections.

Audit logs for third-party data connections display this information:




                                                      Page 25 of 29
                                                   Next-Gen SIEM

       Time: The action’s date and time.

       Analyst: The email address associated with the action.

       Action: The action’s type. These actions generate logs:

               Data connection creation
               Data connection update
               Data connection pause
               Data connection resume
               Data connection deletion
                API key generation
                API key regeneration
                Data connection state update
                Alert status update
       Activity details: The data connection name and ID associated with the action.
       Note: For the Data connection update action only, change details about connection properties are also available.
       For example, "Name":{"Old":"user_hec1","New":"user_hec2"}.

       User IP, City, State, Country, and Company: Location and company details where the change occurred.




Manage alerts for third-party data connectors
You can receive alerts as email notifications and view your alerts in the Falcon console when a third-party data
connector in your environment is disconnected, encounters an error, or has not received data for a specified time frame.
You can also receive alerts if daily or 30-day data ingestion is exceeded for your CID. For more info, see Alerts for Data
Connections.

For Flight Control environments, see Manage alerts for child CIDs.




Falcon Flight Control for third-party data connections
View and manage third-party daily data ingestion volume limits, alerts, and alert statuses for your Falcon Flight Control
and multi-CID accounts. Falcon Administrators and NG SIEM Administrators can complete these tasks for child CIDs in
the parent CID:

       View data ingestion volume and data connection details

       Manage daily data ingestion limits

       Configure alerts for daily data ingestion

       Review and update alert statuses for data connections

For more info about Flight Control, see Falcon Flight Control and Multi-CID Support.

View connectors and daily data ingestion for child CIDs

     1. In the parent CID, go to Next-Gen SIEM > Log management > Data onboarding or Connectors > Data connectors
        > Data connections .
     2. On the Data connections tab, view the status of data connections and data ingestion volume for your CIDs.
        Note: The default view shows data ingestion for the parent and all child CIDs. Daily data ingestion refers to data
        ingested since 00:00:00 UTC to the last completed hour. The daily ingested data info is updated every hour.
     3. To view more specific info, click the CID filter and select one or multiple child CIDs.



                                                     Page 26 of 29
                                                     Next-Gen SIEM

Manage daily data ingestion limits for child CIDs

Note: Exceeding your daily data ingestion limit won’t cause immediate data loss. If you are regularly exceeding your
ingestion limit, upgrade your license or contact your CrowdStrike account representative.

     1. In the parent CID, go to Next-Gen SIEM > Log management > Data onboarding or Connectors > Data connectors
        > Data connections .
     2. Click CID data management.
     3. In the CID data allocation table, view the status for the parent and child CIDs:
                Over limit: Exceeded daily data ingestion limit.
                Nearing limit: Above 80% but within daily data ingestion limit.
                Within normal range: Below 80% of daily data ingestion limit.
                No limit assigned: Daily data ingestion limit is set to 0.
        Note: The default view shows data ingestion for the parent CID and its child CIDs. Daily data ingestion refers to
        data ingested since 00:00:00 UTC to the last completed hour. The daily ingested data info is updated every
        hour.
     4. Click Manage ingest limits.
     5. In the CID data allocation table, enter the daily ingest limit and select a data size unit (KB, MB, GB, TB, or PB) in
        the Set daily ingest limit column for your CID.
        Note: To remove daily data ingestion limits for a CID, select 0 and any data size unit.
     6. Optional. To set an aggregated ingest threshold or an upper limit for an individual CID’s daily ingestion limit, click
            Set aggregated ingest threshold, enter the aggregated ingest threshold limit and data size unit, and click
       Save. For example, if your aggregated ingest threshold is 100 GB, then all your CIDs must have a daily ingest
       limit set below 100 GB.
     7. Click Save.




Manage alerts for child CIDs

Note: For data connection alerts for individual CIDs, see Manage alerts for third-party data connectors.

     1. In the parent CID, go to Next-Gen SIEM > Log management > Data onboarding or Connectors > Data connectors
        > Data connections .
     2. Click Alerts.
     3. Click Manage alerts settings.
     4. In Alerts settings, click Manage CID alerts.
     5. In the CID alerts table, complete these tasks for each of your CIDs:
             a. Click to turn Over-limit alert status or ​Warning alert status on or off. You can set up two types of alerts for
               a CID:
                        Over-limit alert: Receive an alert when the CID has exceeded its daily data ingestion limit. To set
                        the daily data ingestion limit for a CID, see Manage daily data ingestion limits for child CIDs.
                        Warning alert: Receive an alert when the CID has exceeded a warning threshold you set. To set
                        your warning threshold for daily data ingestion, in the Warning alert threshold column, select a
                        threshold percentage of the Daily ingest limit you want to be alerted at. For example, if the daily
                        ingestion limit is set to 100 GB and you select 70% as your warning threshold, then you will
                        receive an alert when your CID has ingested over 70 GB (70% of 100 GB) of data.
            b. Click      CID alert settings to add or update email notification recipients and then click   Edit
               notification preference. In CID alert settings, enter up to 10 email addresses from that CID’s domain and
               click Save changes.
     6. Click Save.




                                                       Page 27 of 29
                                                  Next-Gen SIEM

View the Next-Gen SIEM Connector dashboard
The Next-Gen SIEM Connector Dashboard shows data ingested volumes from third-party sources over time. Gain
insight on how your actual data ingestion volume compares to your licensed data ingestion volume limit.

To view the ingestion volume dashboard, go to Connectors > Data connectors > Dashboards .
Tip: From this page you can also access the Data health dashboard, to monitor data quality and resolve ingestion
issues. For more info, see Data Health Dashboard.

The default time period for the ingestion volume dashboard is Last 30 days. To specify a different time period, click Date
Range and select a time period from these options:

       Last 24 hours

       Last 48 hours

       Last 7 days

       Last 30 days

       Date Range: Specify a time period up to 90 days by selecting a start and end date.

The dashboard displays this info:


  Chart                   Description

  Data ingested           Shows the volume of data ingested per day, the 30-day moving average of data ingested
                          per day, and your licensed data ingestion limit per day.

  Connectors by           Shows the volume of data ingested by each connector over a specified time period. Click
  data volume             Select connectors in this section to search for and select data sources.

  Data volume all         Shows total volume of data ingested by all your connectors over a specified time period.
  sources

  Data sources by         Shows the total volume of data ingested from each data source over a specified period of
  volume                  time. Click Select data sources in this section to search for and select data sources.




Manage parsers
You can use default parsers to parse incoming data in common formats. To parse incoming data in other formats,
create and manage your own custom parsers. For more info about parsing data, see Manage Parsers and Parsing
Data.




Manage Third-Party Detection Exclusions
If the Falcon console is showing detections generated from ingested third-party data that you don’t want to see, you can
create exclusions. These exclusions prevent detections from being generated, based on criteria you specify. For more
info, see Third-Party Detection Exclusions.




                                                    Page 28 of 29
                                                   Next-Gen SIEM

Common issues
Data connection errors

Connection errors occur for multiple reasons. For example, data may be invalid or missing, or resources required for
configuration may be missing, or the data connection may not be authorized to authenticate with a third-party system.

In the Data Connections page, the Error status is displayed for connections that encounter data ingestion errors in the
last hour. Begin your error investigation from this page.

     1. In the Falcon console, go to Connectors > Data connectors > Data connections .

     2. Run the automatically generated error query in Advanced Event Search. In the Status column, click Error or in
        the Actions column, click Open menu ⋮ and select Show error history. An example of an error query:

       #repo.cid = <customer-id> | #repo = 3pi_connection_errors | @dataConnectionID =
       <id_of_connection>

       Tip: If you need to troubleshoot parser errors, you can run this query, which includes the parser errors and
       excludes the connection errors: #repo.cid = <customer-id> | #error=true | #repo !=
       3pi_connection_errors | @dataConnectionID=<id_of_connection>.
               #repo.cid = <customer-id>: Scopes errors to a specific customer ID (CID).

               #repo=3pi_connection_errors: The repository where all data connection errors are stored.

               @dataConnectionID=<id_of_connection>: The ID of a data connection.

     3. In Advanced Event Search, the error query runs and results are returned.
     4. In the Results tab, review the Field List content to learn more about an error.

       #error:true
       #repo:3pi_connection_errors
       #repo.cid:82769abc90834def088bg688ccd5h123
       #type:json
       @dataConnectionID:b1234b5dc67a408c912e34f7ab12c8d9
       @error:true
       @error_msg: Ingest credentials don't have permissions. Verify all required permissions as per
       connector integration guide have been granted
       @event_parsed:false
       @id:5abcdXY9RkMnA3stuvWxPyZ3_12_345_1234567890
       @ingesttimestamp:1739570223511
       @rawstring:{"@error_msg":"Ingest credentials don't have permissions. Verify all required
       permissions as per connector integration guide have been
       granted","status_code":404,"@error":true,"@timestamp":"2025-02-14T21:57:02Z","error_count":1}

               Error field definitions
                        @error_msg: The string provided by the third-party system. This string can be plain text or
                        JSON. You can click any Field List entry and click Message to view the error message. An error
                        message provides more details about an error that stems from a third-party system. For example,
                       an error message can notify you of permissions or misconfiguration issues in a third-party system.
                       status_code: The status code received from the third-party system.
                       error_count: The number of times an error occurs in a short period of time. For example, if you
                       misconfigured the LogScale Collector or another data shipper during data connector setup, this
                       appears as one event in search. However, the associated error count reflects the total number of
                       requests that are reported as failed.
                       @timestamp: When the error occurred. If not provided, the timestamp is set to the current time. A
                       timestamp can be used to correlate errors with changes that might have occurred in your
                       environment around that time. For example, if an error occurs not long after you changed a client
                       or access token in a Pull-based connector configuration or modified settings in a third-party
                       system.




                                                      Page 29 of 29

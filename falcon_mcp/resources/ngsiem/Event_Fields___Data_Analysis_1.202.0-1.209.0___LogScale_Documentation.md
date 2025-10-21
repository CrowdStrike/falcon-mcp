# Event Fields | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-event-fields.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

## Event Fields

In LogScale, you can search either the raw data of events or the fields extracted from the event when the data is [parsed](parsers.html "Parse Data"). 

There are different kinds of fields coming from the events: 

  * **Metadata fields** using the prefix @ contain metadata about each event extracted during ingestion. All events will have these default fields, for example [@id](searching-data-event-fields.html#searching-data-event-fields-metadata-id) or [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp). See [Metadata Fields](searching-data-event-fields.html#searching-data-event-fields-metadata "Metadata Fields") for the complete list of these fields. 

  * **Tag fields** using the prefix # define how events are physically stored and indexed. See [Tag Fields](searching-data-event-fields.html#searching-data-event-fields-tag "Tag Fields") for the list of these fields. 

  * **User fields** is any field that is not a tag field or metadata field. 




Event fields can be viewed and managed from the LogScale User Interface. See [_Search Data_](searching-data.html "Search Data"). 

For more information on how to query event fields in LogScale and discover what you can achieve with query writings, see [Query management](writing-queries-manage.html "Query management") and [Common Queries](writing-queries-operations.html "Frequent query operations"). 

### Metadata Fields

Each event has some metadata attached to it on ingestion; all metadata fields start with @ to make them easy to identify. All events will contain the following metadata fields by default. 

Metadata Field |  Description   
---|---  
[@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) |  The original text of the event. As it keeps the original data on ingestion, this field allows you to do free-text searching across all logs and to extract virtual fields in queries.   
[@id](searching-data-event-fields.html#searching-data-event-fields-metadata-id) |  A unique identifier for the event. Can be used to refer to and re-find specific events.   
[@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) |  Timestamp in milliseconds since the epoch (`1st Jan 1970, 00:00`) of the ingested event, for example `2022-11-22 09:50:20.100` if the event has an identifiable timestamp. Timestamps are in UTC. See also [Parsing Timestamps](parsers-parsing-timestamps.html "Parsing Timestamps") for more details.   
[@timezone](searching-data-event-fields.html#searching-data-event-fields-metadata-timezone) |  The timezone the event originated in, if known. This is often set when the event's timestamp is parsed.   
[@ingesttimestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-ingesttimestamp) |  The timestamp of when the event was ingested. The value is milliseconds-since-epoch. Timestamps are in UTC.   
[@timestamp.nanos](searching-data-event-fields.html#searching-data-event-fields-metadata-timestampnanos) |  Extended precision of timestamp below millisecond. For example, `295000`. Timestamps are in UTC. See also [Parsing Timestamps](parsers-parsing-timestamps.html "Parsing Timestamps") for more details.   
  
### Tag Fields

Each event has some tagged data attached to it on ingestion; all tag fields start with # to make them easy to identify. All events will contain the following tag fields by default. 

Tag Field |  Description   
---|---  
[#repo](searching-data-event-fields.html#searching-data-event-fields-tag-repo) |  Name of the repo where the event is stored. For example, `sandbox`  
[#type](searching-data-event-fields.html#searching-data-event-fields-tag-type) |  Name of the parser that was used to parse and ingest the data into the repo.

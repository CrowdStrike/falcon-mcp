# Event Information Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-event.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Event Information Query Functions

LogScale's event information functions allow event information and field selection. These are designed to work with event fields, rather than the data within the event. 

**Table: Event Information Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`copyEvent(type)`](functions-copyevent.html "copyEvent\(\)")| [_`type`_](functions-copyevent.html#query-functions-copyevent-type)|  |  Duplicates an event so that the pipeline will see both events.   
[`createEvents(rawstring)`](functions-createevents.html "createEvents\(\)")| [_`rawstring`_](functions-createevents.html#query-functions-createevents-rawstring)|  |  Generates temporary events as part of the query.   
[`default(field, [replaceEmpty], value)`](functions-default.html "default\(\)")| [_`value`_](functions-default.html#query-functions-default-value)|  |  Creates a field to given parameter and given value.   
[`drop(fields)`](functions-drop.html "drop\(\)")| [_`fields`_](functions-drop.html#query-functions-drop-fields)|  |  Removes specified fields from each event.   
[`dropEvent()`](functions-dropevent.html "dropEvent\(\)")|  |  |  Drops completely an event in parser pipeline to stop it from being ingested.   
[`eventFieldCount([as])`](functions-eventfieldcount.html "eventFieldCount\(\)")|  |  |  Computes number of fields event uses internally for the values.   
[`eventInternals([prefix])`](functions-eventinternals.html "eventInternals\(\)")|  |  |  Add a set of fields describing the storage locations of this event.   
[`eventSize([as])`](functions-eventsize.html "eventSize\(\)")|  |  |  Determines the number of bytes that this event uses internally for the values, not counting the bytes for storing the field names.   
[`fieldset()`](functions-fieldset.html "fieldset\(\)")|  |  |  Retrieves a list of available fields.   
[`fieldstats([limit])`](functions-fieldstats.html "fieldstats\(\)")|  |  |  Displays statistics about fields.   
[`hash([as], field, [limit], [seed])`](functions-hash.html "hash\(\)")| [_`field`_](functions-hash.html#query-functions-hash-field)|  |  Computes a non-cryptographic hash of a list of fields.   
[`readFile(file, [include], [limit])`](functions-readfile.html "readFile\(\)")| [_`file`_](functions-readfile.html#query-functions-readfile-file)|  |  Uses a `.csv` lookup file or ad-hoc table as data input for the query.   
[`rename([as], field)`](functions-rename.html "rename\(\)")| [_`field`_](functions-rename.html#query-functions-rename-field)|  |  Renames one or more given fields.   
[`select(fields)`](functions-select.html "select\(\)")| [_`fields`_](functions-select.html#query-functions-select-fields)|  |  Used to specify a set of fields to select from each event.   
[`test(expression)`](functions-test.html "test\(\)")| [_`expression`_](functions-test.html#query-functions-test-expression)|  |  Evaluates boolean expression and filters events.

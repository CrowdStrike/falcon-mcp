# createEvents() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-createevents.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`createEvents()`](functions-createevents.html "createEvents\(\)")

Generates temporary events as part of the query and is ideal for generating sample data for testing or troubleshooting. It is regarded as an aggregator function and, therefore, discards all incoming events and outputs the generated ones. The events are generated with no extracted fields but [`createEvents()`](functions-createevents.html "createEvents\(\)") can, advantageously, be combined with one of the many parsers. For example, given raw strings in the format of key/value pairs, the pairs can be parsed to fields using the [`kvParse()`](functions-kvparse.html "kvParse\(\)") function. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`rawstring`_](functions-createevents.html#query-functions-createevents-rawstring)[a]| string| required |  |  Specification of events to emit. Each event is given as a [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) which is not processed further.   
[a] The parameter name [_`rawstring`_](functions-createevents.html#query-functions-createevents-rawstring) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`rawstring`_](functions-createevents.html#query-functions-createevents-rawstring) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     createEvents("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     createEvents(rawstring="value")
> 
> These examples show basic structure only.

### [`createEvents()`](functions-createevents.html "createEvents\(\)") Examples

Click + next to an example below to get the full details.

#### Create Two Temporary Events for Troubleshooting - Example 1

**Create two temporary events for testing or troubleshooting using the[`createEvents()`](functions-createevents.html "createEvents\(\)") function **

##### Query

logscale
    
    
    createEvents(["animal=dog weight=7.0", "animal=cat weight=4.2"])

##### Introduction

The [`createEvents()`](functions-createevents.html "createEvents\(\)") function generates temporary events as part of the query. The function is ideal for generating sample data for testing or troubleshooting. 

Example incoming data might look like this: 

animal=dog weight=7.0  
---  
animal=cat weight=4.2  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         createEvents(["animal=dog weight=7.0", "animal=cat weight=4.2"])

Creates two temporary events to be used for testing purposes. An event with `dog` and an event with `cat`. 

  3. Event Result set.




##### Summary and Results

The query is used to create temporary events. The [`createEvents()`](functions-createevents.html "createEvents\(\)") function can be combined with different parsers to generate more interesting events, for example, with [`kvParse()`](functions-kvparse.html "kvParse\(\)") or [`parseJson()`](functions-parsejson.html "parseJson\(\)"). 

Sample output from the incoming example data: 

@rawstring| @timestamp| @timestamp.nanos  
---|---|---  
animal=dog weight=7.0| 1733310508872| 0  
animal=cat weight=4.2| 1733310508872| 0  
  
#### Create Two Temporary Events for Troubleshooting - Example 2

**Create two temporary events for testing or troubleshooting using the[`createEvents()`](functions-createevents.html "createEvents\(\)") function with [`parseJson()`](functions-parsejson.html "parseJson\(\)") **

##### Query

logscale
    
    
    createEvents(["{\"animal\":{\"kind\":\"dog\", \"weight\":7.0}}", "{\"animal\":{\"kind\":\"cat\", \"weight\":4.2}}"])
    | parseJson()

##### Introduction

In this example, the [`createEvents()`](functions-createevents.html "createEvents\(\)") function is combined with [`parseJson()`](functions-parsejson.html "parseJson\(\)") to parse @rawstring as JSON. 

Example incoming data might look like this: 

json
    
    
    [
    {"animal":{"kind":"dog", "weight":7.0}},
    {"animal":{"kind":"cat", "weight":4.2}}
    ]

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         createEvents(["{\"animal\":{\"kind\":\"dog\", \"weight\":7.0}}", "{\"animal\":{\"kind\":\"cat\", \"weight\":4.2}}"])

Creates two temporary events. An event with `dog` and an event with `cat`. 

  3. logscale
         
         | parseJson()

Parses specified fields as JSON. 

  4. Event Result set.




##### Summary and Results

The query is used to create temporary events and parse the @rawstring as JSON. 

Sample output from the incoming example data: 

@timestamp| animal.kind| animal.weight  
---|---|---  
1733311547717| dog| 7.0  
1733311547717| cat| 4.2  
  
#### Create Two Temporary Events for Troubleshooting - Example 3

**Create two temporary events for testing or troubleshooting using the[`createEvents()`](functions-createevents.html "createEvents\(\)") function with [`kvParse()`](functions-kvparse.html "kvParse\(\)") **

##### Query

logscale
    
    
    createEvents(["animal=dog weight=7.0", "animal=cat weight=4.2"])
    | kvParse()

##### Introduction

In this example, the [`createEvents()`](functions-createevents.html "createEvents\(\)") function is combined with [`kvParse()`](functions-kvparse.html "kvParse\(\)") to parse @rawstring as JSON. 

Example incoming data might look like this: 

animal=dog weight=7.0  
---  
animal=cat weight=4.2  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         createEvents(["animal=dog weight=7.0", "animal=cat weight=4.2"])

Creates two temporary events. An event with `dog` and an event with `cat`. 

  3. logscale
         
         | kvParse()

Parses the string into key value pairs. 

  4. Event Result set.




##### Summary and Results

The query is used to create temporary events and parse the @rawstring as key value pairs. 

Sample output from the incoming example data: 

animal| weight  
---|---  
dog| 7.0  
cat| 4.2  
  
#### Generate Temporary Event With Bit Flags For Troubleshooting

**Generate temporary events with the[`createEvents()`](functions-createevents.html "createEvents\(\)") function as part of the query to generate sample data for testing or troubleshooting **

##### Query

logscale
    
    
    createEvents(["flags=4"])
    | kvParse()
    | bitfield:extractFlags(
    field=flags,
    output=[
    [1, ErrorFlag],
    [2, WarningFlag]
    ])

##### Introduction

In this example, the bit field is named `flags` and has the value `4` corresponding to the bit string `00000100`. The goal is to extract two flags based on their bit value. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         createEvents(["flags=4"])

Creates a temporary event that includes a new field named flag to be used for testing purposes. Bit flags are one or more (up to 32) Boolean values stored in a single number variable. 

  3. logscale
         
         | kvParse()

Parses the raw text looking for the key/value pairs and creates the corresponding fields in the event. In this case a single field named flags with the value `8`. 

  4. logscale
         
         | bitfield:extractFlags(
         field=flags,
         output=[
         [1, ErrorFlag],
         [2, WarningFlag]
         ])

When specifying the values for the bit field, values start from bit 0 (`2^0` or decimal 1). The invidual bit values are defined using an array of arrays. Each array index should specify the bit number (not literal value) and the field to be created. Each field will then be set to `true` if the bit was enabled in the compared field. 

In the above example, `ErrorFlag` located at bit 1 (2^1, decimal 2), and `WarningFlag` located at index `2` (decimal 4). 

  5. Event Result set.




##### Summary and Results

The query is used to extract and match values to bit flags. Creating events based on bit flags are useful when testing and troubleshooting on values, as it is faster to compare values stored as bitmasks compared to a series of booleans. Furthermore, events based on bit flags uses considerably less memory. 

Sample output from the incoming example data: 

ErrorFlag| WarningFlag  
---|---  
false| true  
  
#### Perform a Free-Text Search in Rawstring

**Perform a free-text search in a rawstring using the[`createEvents()`](functions-createevents.html "createEvents\(\)") function **

##### Query

logscale
    
    
    createEvents(["foobar"])|@rawstring="*foo*"

##### Introduction

In this example, the [`createEvents()`](functions-createevents.html "createEvents\(\)") function is used to do a free-text search for `foo`in a rawstring. The `*` around the value is to ensure, that we are looking for any value in @rawstring where `foo` is in the middle with any prefix or suffix. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         createEvents(["foobar"])|@rawstring="*foo*"

Free-text searches for `foo` in a rawstring. Notice that you must add `*` around the free text string `foo`. 

  3. Event Result set.




##### Summary and Results

The query is used specifically to perform a free-text search in the @rawstring field. This can be useful in any case you may want to search a specific field name to check for that first part.

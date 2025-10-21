# parseTimestamp() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-parsetimestamp.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Sep 23, 2025

## [`parseTimestamp()`](functions-parsetimestamp.html "parseTimestamp\(\)")

Parses a string into a timestamp. 

This function is important for creating parsers, as it is used to parse the timestamp for an incoming event. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`addErrors`_](functions-parsetimestamp.html#query-functions-parsetimestamp-adderrors)|  boolean| optional[a] | `true`|  Whether to add an error field to the event, if it was not possible to find a timestamp.   
[_`as`_](functions-parsetimestamp.html#query-functions-parsetimestamp-as)|  string| optional[[a]](functions-parsetimestamp.html#ftn.table-functions-parsetimestamp-optparamfn) | `@timestamp`|  Name of output field that will contain the parsed timestamp. The timestamp is represented as milliseconds since 1970 in UTC. LogScale expects to find the timestamp in the field @timestamp, so do not change this when creating parsers.   
[_`caseSensitive`_](functions-parsetimestamp.html#query-functions-parsetimestamp-casesensitive)|  boolean| optional[[a]](functions-parsetimestamp.html#ftn.table-functions-parsetimestamp-optparamfn) | [`true`](functions-parsetimestamp.html#query-functions-parsetimestamp-casesensitive-option-true)|  Whether the timestamp format pattern is case sensitive. For example, the format LLL will accept Feb but not feb in case sensitive mode, while both will be accepted in case insensitive mode.   
|  |  | **Values**  
|  |  | [`false`](functions-parsetimestamp.html#query-functions-parsetimestamp-casesensitive-option-false)| Pattern is not case sensitive  
|  |  | [`true`](functions-parsetimestamp.html#query-functions-parsetimestamp-casesensitive-option-true)| Pattern is case sensitive  
[ _`field`_](functions-parsetimestamp.html#query-functions-parsetimestamp-field)|  string| required |  |  The field holding the timestamp to be parsed.   
[_`format`_](functions-parsetimestamp.html#query-functions-parsetimestamp-format)[b]| string| optional[[a]](functions-parsetimestamp.html#ftn.table-functions-parsetimestamp-optparamfn) | `yyyy-MM-dd'T'HH:mm:ss[.SSSSSSSSS]XXXXX`|  Pattern used to parse the timestamp. Either a format string as specified in [Java's DateTimeFormatter](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/time/format/DateTimeFormatter.html), or one of the special format specifiers (these specifiers are not case-sensitive, that is, `MilliSeconds` works as well).   
|  |  | **Values**  
|  |  | [`millis`](functions-parsetimestamp.html#query-functions-parsetimestamp-format-option-millis)| Epoch time in milliseconds (UTC)  
|  |  | [`milliseconds`](functions-parsetimestamp.html#query-functions-parsetimestamp-format-option-milliseconds)| Epoch time in milliseconds (UTC)  
|  |  | [`nanos`](functions-parsetimestamp.html#query-functions-parsetimestamp-format-option-nanos)| Epoch time in nanoseconds (UTC)  
|  |  | [`seconds`](functions-parsetimestamp.html#query-functions-parsetimestamp-format-option-seconds)| Epoch time in seconds (UTC)  
|  |  | [`unixTimeMillis`](functions-parsetimestamp.html#query-functions-parsetimestamp-format-option-unixtimemillis)| Epoch time in milliseconds (UTC)  
|  |  | [`unixTimeSeconds`](functions-parsetimestamp.html#query-functions-parsetimestamp-format-option-unixtimeseconds)| Epoch time in seconds (UTC)  
|  |  | [`unixtime`](functions-parsetimestamp.html#query-functions-parsetimestamp-format-option-unixtime)| Epoch time in seconds (UTC)  
[_`timezone`_](functions-parsetimestamp.html#query-functions-parsetimestamp-timezone)|  string| optional[[a]](functions-parsetimestamp.html#ftn.table-functions-parsetimestamp-optparamfn) |  |  If the timestamp does not contain a timezone and this parameter is not set and the field specified in the [_`timezoneField`_](functions-parsetimestamp.html#query-functions-parsetimestamp-timezonefield) parameter does not contain a valid timezone, then the timestamp will not be parsed. The timezone can be specified as a named timezone or as an offset. Examples are Europe/London, America/New_York, UTC or UTC+12:30. See the full list of timezones supported by {}ls_shortname{} at [Supported Time Zones](syntax-time-timezones.html "Supported Time Zones"). If the timezone is specified here, and one also exists in the timestamp, then this parameter overrides the timezone in the event.   
[_`timezoneAs`_](functions-parsetimestamp.html#query-functions-parsetimestamp-timezoneas)|  string| optional[[a]](functions-parsetimestamp.html#ftn.table-functions-parsetimestamp-optparamfn) | `@timezone`|  Name of output field that will contain the parsed timezone. LogScale expects to find the timezone in the field [@timezone](searching-data-event-fields.html#searching-data-event-fields-metadata-timezone) , so do not change when creating parsers.   
[_`timezoneField`_](functions-parsetimestamp.html#query-functions-parsetimestamp-timezonefield)|  string| optional[[a]](functions-parsetimestamp.html#ftn.table-functions-parsetimestamp-optparamfn) | `@timezone`|  The name of the field containing the timezone to use if the timestamp does not include a timezone. The [_`timezoneField`_](functions-parsetimestamp.html#query-functions-parsetimestamp-timezonefield) parameter allows you to select a dynamic default timezone from each event so that the timestamp can be parsed regardless of whether the timestamp contains a timezone. The parameter enables having different default timezones in different contexts without having to customize the parser. These contexts might be events coming from different data sources or for packages used in multiple organizations. The timezone can be specified as a named timezone or as an offset. Examples are Europe/London, America/New_York, UTC or UTC+12:30. See the full list of timezones supported by _ls_shortname_ at [Supported Time Zones](syntax-time-timezones.html "Supported Time Zones"). (**added in 1.207**)  
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`format`_](functions-parsetimestamp.html#query-functions-parsetimestamp-format) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`format`_](functions-parsetimestamp.html#query-functions-parsetimestamp-format) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     parseTimestamp("value",field="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     parseTimestamp(format="value",field="value")
> 
> These examples show basic structure only.

### [`parseTimestamp()`](functions-parsetimestamp.html "parseTimestamp\(\)") Function Operation

Before parsing the timestamp, the part of the log containing the timestamp should have been captured in a field. Typically this is done during parsing, but can be extracted during queries using functions like [`regex()`](functions-regex.html "regex\(\)") and [`parseJson()`](functions-parsejson.html "parseJson\(\)") before [`parseTimestamp()`](functions-parsetimestamp.html "parseTimestamp\(\)"). 

The [`parseTimestamp()`](functions-parsetimestamp.html "parseTimestamp\(\)") function formats times using a subset of [Java's DateTimeFormatter](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/time/format/DateTimeFormatter.html). 

LogScale also supports some special format strings like `seconds`, `milliseconds`, and `unixtime` (see in table below the description of the [_`format`_](functions-parsetimestamp.html#query-functions-parsetimestamp-format) parameter for a full list of options). 

  * `unixtimeMillis` UTC time since 1970 in milliseconds 

  * `unixtime` UTC time since 1970 in seconds 




For the special formats that specify seconds (that is `seconds`, `unixtime`, and `unixtimeseconds`), the function also supports specifying milliseconds using floating point numbers. 

For example, `1690480444.589` means `2023-07-27 19:54:04 and 589 milliseconds`. 

LogScale can also parse timestamps that use nanosecond precision, the nanosecond component will be extracted during the process. For example: 
    
    
    nanos := 1451606399999998965
    parseTimestamp("nanos")

Would extract `2024-03-07 12:04:14` and `547998965` nanoseconds. 

If the timestamp is parsed it will create a field [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) containing the parsed timestamp in UTC milliseconds and a [@timezone](searching-data-event-fields.html#searching-data-event-fields-metadata-timezone) field containing the original timezone. 

It is possible to parse time formats leaving out the year designator as is sometime seen in time formats from Syslog. For example, `Mar 15 07:48:13` can be parsed using the format `MM d HH:mm:ss`. In this case LogScale will guess the year. 

The logic used for guessing the year is as follows: if the date (without a specified year) is less than 8 days into the future, or in the past, then the current year is used. Otherwise, if the date is more than 8 days into the future, then the previous year is used. For example, if the current date is `March 10 2025 06:00:00`, then the inferred year of `Mar 18 00:00:00` is `2025`. If the current date is `March 7 2025` then the inferred year is `2024`. 

### [`parseTimestamp()`](functions-parsetimestamp.html "parseTimestamp\(\)") Syntax Examples

Extract a timestamp that is using millisecond precision embedded in a JSON value: 

logscale
    
    
    parseJson()
    | parseTimestamp("millis", field=timestamp)

Events having a timestamp in ISO8601 format that include a timezone offset can be parsed using the default format: 

logscale
    
    
    expiryTime := "2018-09-08T17:51:04.777Z"
    | parseTimestamp(field=expiryTime)

Note that LogScale suports up to 9 digits (`2018-09-08T17:51:04.777777777Z`) and not just only 3 second-fractions. 

Another example is a timestamp like `2017-12-18T20:39:35-04:00`: 

logscale
    
    
    /(?<timestamp>\S+)/
    | parseTimestamp(field=timestamp)

Parse timestamps in an accesslog where the timestamp includes an explicit timezone offset like `192.168.1.19 [02/Apr/2014:16:29:32 +0200] GET /hello/test/123 ...`

logscale
    
    
    /(?<client>\S+) \[(?<@timestamp>.+)\] (?<method>\S+) (?<url>\S+)/
    | parseTimestamp("dd/MMM/yyyy:HH:mm:ss Z", field=timestamp)

When parsing a timestamp without a timezone, such as `2015-12-18T20:39:35`, you must specify the timezone using the `timezone` parameter, as shown in the following example: 

logscale
    
    
    parseTimestamp("yyyy-MM-dd'T'HH:mm:ss", field=timestamp, timezone="America/New_York")

### Important

If the timestamp does not contain a timezone, then one must be specified using the `timezone` parameter, otherwise an error is generated. 

Parse an event with a timestamp not containing year, like `Feb 9 12:22:44 hello world`

logscale
    
    
    /(?<timestamp>\S+\s+\S+\s+\S+)/
    | parseTimestamp("MMM [ ]d HH:mm:ss", field=timestamp, timezone="Europe/London")

### [`parseTimestamp()`](functions-parsetimestamp.html "parseTimestamp\(\)") Examples

Click + next to an example below to get the full details.

#### Bucket Events Into Groups

**Bucket events into 24 groups using the[`count()`](functions-count.html "count\(\)") function and [`bucket()`](functions-bucket.html "bucket\(\)") function **

##### Query

logscale
    
    
    bucket(buckets=24, function=sum("count"))
    | parseTimestamp(field=_bucket,format=millis)

##### Introduction

In this example, the [`bucket()`](functions-bucket.html "bucket\(\)") function is used to request 24 buckets over a period of one day in the [humio-metrics](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-metrics.html) repository. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bucket(buckets=24, function=sum("count"))

Buckets the events into 24 groups spanning over a period of one day, using the [`sum()`](functions-sum.html "sum\(\)") function on the count field. 

  3. logscale
         
         | parseTimestamp(field=_bucket,format=millis)

Extracts the timestamp from the generated bucket and converts the timestamp to a date time value. In this example, the bucket outputs the timestamp as an epoch value in the _bucket field. This results in an additional bucket containing all the data after the requested timespan for the requested number of buckets. 

  4. Event Result set.




##### Summary and Results

The query is used to optimizing data storage and query performance by making et easier to manage and locate data subsets when performing analytics tasks. Note that the resulting outputs shows 25 buckets; the original requested 24 buckets and in addition the bucket for the extracted timestamp. 

Sample output from the incoming example data: 

_bucket| _sum| @timestamp  
---|---|---  
1681290000000| 1322658945428| 1681290000000  
1681293600000| 1879891517753| 1681293600000  
1681297200000| 1967566541025| 1681297200000  
1681300800000| 2058848152111| 1681300800000  
1681304400000| 2163576682259| 1681304400000  
1681308000000| 2255771347658| 1681308000000  
1681311600000| 2342791941872| 1681311600000  
1681315200000| 2429639369980| 1681315200000  
1681318800000| 2516589869179| 1681318800000  
1681322400000| 2603409167993| 1681322400000  
1681326000000| 2690189000694| 1681326000000  
1681329600000| 2776920777654| 1681329600000  
1681333200000| 2873523432202| 1681333200000  
1681336800000| 2969865160869| 1681336800000  
1681340400000| 3057623890645| 1681340400000  
1681344000000| 3144632647026| 1681344000000  
1681347600000| 3231759376472| 1681347600000  
1681351200000| 3318929777092| 1681351200000  
1681354800000| 3406027872076| 1681354800000  
1681358400000| 3493085788508| 1681358400000  
1681362000000| 3580128551694| 1681362000000  
1681365600000| 3667150316470| 1681365600000  
1681369200000| 3754207997997| 1681369200000  
1681372800000| 3841234050532| 1681372800000  
1681376400000| 1040019734927| 1681376400000  
  
#### Parse ISO8601 Timestamps

**Convert ISO8601 Formatted Timestamps to Unix Epoch Milliseconds using the[`parseTimestamp()`](functions-parsetimestamp.html "parseTimestamp\(\)") function **

##### Query

logscale
    
    
    expiryTime := "2018-09-08T17:51:04.777Z"
      | parseTimestamp(field=expiryTime,as=newts)

##### Introduction

In this example, the [`parseTimestamp()`](functions-parsetimestamp.html "parseTimestamp\(\)") function is used to convert ISO8601 formatted timestamp strings into Unix epoch milliseconds. 

Example incoming data might look like this: 

@timestamp| event_type| expiryTime| user  
---|---|---|---  
1536426664777| session| 2018-09-08T17:51:04.777Z| john.doe  
1536426664888| session| 2018-09-08T17:51:04.888+00:00| jane.smith  
1536426664999| session| 2018-09-08T19:51:04.999+02:00| bob.wilson  
1536426665000| session| 2018-09-08T12:51:04.000-05:00| alice.jones  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         expiryTime := "2018-09-08T17:51:04.777Z"

Creates a test timestamp string in ISO8601 format with `Z` timezone indicator (UTC) and assigns it to the expiryTime field. 

Note that LogScale suports up to 9 digits (`2018-09-08T17:51:04.777777777Z`). 

  3. logscale
         
         | parseTimestamp(field=expiryTime,as=newts)

Parses the timestamp string in the expiryTime field and returns the result in the same field. By default, [`parseTimestamp()`](functions-parsetimestamp.html "parseTimestamp\(\)") will overwrite the value of the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field. Here, the [_`as`_](functions-parsetimestamp.html#query-functions-parsetimestamp-as) has been used to store the new timestamp value as an epoch. The function automatically recognizes the ISO8601 format with timezone information ('Z' for UTC, or offset like '+00:00'). The parsed result is stored as Unix epoch milliseconds. 

### Note

The LogScale search interface by default will format the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field as a human-readable date, even if the underlying data is an epoch in seconds. Be aware that this can hide the conversion of values when viewed within the UI as the conversion and formatting happens automatically. You can change this view in the UI using the `Format Panel`. 

  4. Event Result set.




##### Summary and Results

The query is used to convert ISO8601 formatted timestamp strings into Unix epoch milliseconds, which is LogScale's native timestamp format. LogScale supports up to 9 digits (nanoseconds) and not just only 3 second-fractions. 

This query is useful, for example, to normalize timestamp fields in your data for consistent time-based analysis and correlation across different data sources. 

Sample output from the incoming example data: 

@timestamp| @timestamp.nanos| @timezone| event_type| expiryTime| user  
---|---|---|---|---|---  
1536429184777| 0| Z| session| 2018-09-08T17:53:04.777Z| john.doe  
1536429184777| 0| Z| session| 2018-09-08T17:53:04.777Z| jane.smith  
1536429184777| 0| Z| session| 2018-09-08T17:53:04.777Z| bob.wilson  
1536429184777| 0| Z| session| 2018-09-08T17:53:04.777Z| alice.jones  
  
For further timestamp manipulation, you might want to explore the [`formatTime()`](functions-formattime.html "formatTime\(\)") function to format the Unix timestamp into different string representations. 

#### Parse Timestamp Without Timezone Information

**Convert local time strings to timestamps with timezone specification using the[`parseTimestamp()`](functions-parsetimestamp.html "parseTimestamp\(\)") function with [_`timezone`_](functions-parsetimestamp.html#query-functions-parsetimestamp-timezone) **

##### Query

logscale
    
    
    parseTimestamp("yyyy-MM-dd'T'HH:mm:ss", field=event_time, timezone="America/New_York")

##### Introduction

In this example, the [`parseTimestamp()`](functions-parsetimestamp.html "parseTimestamp\(\)") is used to convert timestamp strings without timezone information into properly formatted timestamps by explicitly specifying the [_`timezone`_](functions-parsetimestamp.html#query-functions-parsetimestamp-timezone). 

Example incoming data might look like this: 

event_time| action| user  
---|---|---  
2023-05-02T10:30:00| login| jsmith  
2023-05-02T10:35:00| logout| jsmith  
2023-05-02T10:40:00| login| awhite  
2023-05-02T10:45:00| update| awhite  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         parseTimestamp("yyyy-MM-dd'T'HH:mm:ss", field=event_time, timezone="America/New_York")

Parses the timestamp string in event_time using the specified format pattern. The [_`timezone`_](functions-parsetimestamp.html#query-functions-parsetimestamp-timezone) parameter is set to `America/New_York` to properly interpret the local time. The result is stored in a new field named [@timezone](searching-data-event-fields.html#searching-data-event-fields-metadata-timezone). 

Note that if the timestamp string does not contain a timezone, then one must be specified using the [_`timezone`_](functions-parsetimestamp.html#query-functions-parsetimestamp-timezone) parameter, otherwise an error is generated. 

  3. Event Result set.




##### Summary and Results

The query is used to convert local timestamp strings into properly formatted timestamps with timezone information. 

This query is useful, for example, to standardize timestamp fields in logs that contain local time information without explicit timezone data. 

Sample output from the incoming example data: 

@timezone| action| event_time| user  
---|---|---|---  
America/New_York| login| 2023-05-02T10:30:00| jsmith  
America/New_York| logout| 2023-05-02T10:35:00| jsmith  
America/New_York| login| 2023-05-02T10:40:00| awhite  
America/New_York| update| 2023-05-02T10:45:00| awhite

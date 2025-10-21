# findTimestamp() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-findtimestamp.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Sep 2, 2025

## [`findTimestamp()`](functions-findtimestamp.html "findTimestamp\(\)")

Finds a timestamp in the given field and parses it, trying different formats for timestamps. The function returns the first timestamp in the field that matches one of its formats. The function only finds timestamps starting within the first 128 characters of the text. 

Self-hosted customers can adjust this behaviour setting the variable [`MAX_CHARS_TO_FIND_TIMESTAMP`](https://library.humio.com/falcon-logscale-self-hosted/envar-max_chars_to_find_timestamp.html). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`addErrors`_](functions-findtimestamp.html#query-functions-findtimestamp-adderrors)|  boolean| optional[a] | `true`|  Whether to add an error field to the event, if it was not possible to find a timestamp.   
[_`as`_](functions-findtimestamp.html#query-functions-findtimestamp-as)|  string| optional[[a]](functions-findtimestamp.html#ftn.table-functions-findtimestamp-optparamfn) | `@timestamp`|  The output field that will contain the parsed timestamp. The timestamp is represented as milliseconds since Unix epoch (01-01-1970 00:00:00 UTC). LogScale expects to find the timestamp for the event in the field [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) , so do not set this parameter to anything else in a parser.   
[_`field`_](functions-findtimestamp.html#query-functions-findtimestamp-field)|  string| optional[[a]](functions-findtimestamp.html#ftn.table-functions-findtimestamp-optparamfn) | `@rawstring`|  The field to search for a timestamp.   
[_`timezone`_](functions-findtimestamp.html#query-functions-findtimestamp-timezone)|  string| optional[[a]](functions-findtimestamp.html#ftn.table-functions-findtimestamp-optparamfn) |  |  If the timestamp does not contain a timezone and this parameter is not set and the field specified in the [_`timezoneField`_](functions-findtimestamp.html#query-functions-findtimestamp-timezonefield) parameter does not contain a valid timezone, then the timestamp will not be parsed. The timezone can be specified as a named timezone or as an offset. Examples are Europe/London, America/New_York, UTC or UTC+12:30. See the full list of timezones supported by LogScale at [Supported Time Zones](syntax-time-timezones.html "Supported Time Zones").   
[_`timezoneAs`_](functions-findtimestamp.html#query-functions-findtimestamp-timezoneas)|  string| optional[[a]](functions-findtimestamp.html#ftn.table-functions-findtimestamp-optparamfn) | `@timezone`|  The output field that will contain the parsed timezone. LogScale expects to find the timezone for the event in the field [@timezone](searching-data-event-fields.html#searching-data-event-fields-metadata-timezone) , so do not set this parameter to anything else in a parser.   
[_`timezoneField`_](functions-findtimestamp.html#query-functions-findtimestamp-timezonefield)|  string| optional[[a]](functions-findtimestamp.html#ftn.table-functions-findtimestamp-optparamfn) | `@timezone`|  The name of the field containing the timezone to use if the timestamp does not include a timezone. The [_`timezoneField`_](functions-findtimestamp.html#query-functions-findtimestamp-timezonefield) parameter allows you to select a dynamic default timezone from each event so that the timestamp can be parsed regardless of whether the timestamp contains a timezone. The parameter enables having different default timezones in different contexts without having to customize the parser. These contexts might be events coming from different data sources or for packages used in multiple organizations. The timezone can be specified as a named timezone or as an offset. Examples are Europe/London, America/New_York, UTC or UTC+12:30. See the full list of timezones supported by LogScale at [Supported Time Zones](syntax-time-timezones.html "Supported Time Zones"). (**added in 1.204**)  
[a] Optional parameters use their default value unless explicitly set.  
  
### [`findTimestamp()`](functions-findtimestamp.html "findTimestamp\(\)") Function Operation

This function is primarily meant to be used in generic parsers that can be used for different event types. If the format of the timestamp is known, consider using the [`parseTimestamp()`](functions-parsetimestamp.html "parseTimestamp\(\)") function instead. 

The function supports the following formats: 

  * `year month day hour minute second [subsecond] [timezone]`

  * `month day [year] hour minute second [subsecond] [timezone]`

  * `month day hour minute second [subsecond] [timezone] year4`

  * `day monthLetter [year4] hour minute second [subsecond] [timezone]`

  * `hour minute second [subsecond] [timezone]`

  * `epochsecond [subsecond]`




Values within brackets (for example, `[timezone]`) are optional. 

The different formats are described as follows: 

Type |  Description   
---|---  
`year` |  The year with either two or four digits.   
`year4` |  The year with four digits.   
`month` |  The month as two digits or three letters (for example, 01 or Jan).   
`monthLetter` |  The month as three letters (for example, Jan)   
`day` |  The day as two digits.   
`hour` |  The hour as two digits (0-23 or 1-12).   
`minute` |  The minutes as two digits.   
`second` |  The seconds as two digits.   
`subsecond` |  The sub-seconds as one to nine digits, for Unix epoch time only 3, 6 or 9 digits.   
`timezone` |  The time zone as either a named timezone (for example, UTC or America/New_York) or an offset (for example, UTC+12:30).   
`epochsecond` |  The seconds since Unix epoch (01-01-1970 00:00:00 UTC) as 10 digits.   
  
Additional notes: 

  * If the time zone is missing, the [_`timezone`_](functions-findtimestamp.html#query-functions-findtimestamp-timezone) parameter is used. 

### Note

If timestamps are written in a time zone with Daylight Saving Time, it is recommended that the _`timezone`_ parameter is specified and written as an offset. Otherwise, when switching from Daylight Saving Time to Standard Time, there is no way to differentiate between the last hour before the switch and the first hour after. 

  * If the date (`year`, `month` and `day`) is missing, the current date is used if the time is at most 10 minutes into the future; otherwise, the previous days date is used. 

  * If the `year` is missing, the largest of last year, this year and next year is used so that the date is at most 7 days into the future. 

  * If the `year` is only two digits, it is assumed to be between 2013 and 2099. If you need to parse dates before 2013 with only two digits for year, use the [`parseTimestamp()`](functions-parsetimestamp.html "parseTimestamp\(\)") function instead. 

  * Leap seconds are ignored, so 60 seconds is converted to 59 seconds. 

  * Up to 9 digits of subseconds are accepted, but since timestamps are stored with millisecond precision, only the first 3 digits are used. 

  * If a timestamp is found, two fields are added to the event: one contains the parsed timestamp in milliseconds since Unix epoch (01-01-1970 00:00:00 UTC) and gets its name from the [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") parameter; the other contains the parsed timezone, if available, and otherwise the _`timezone`_ parameter, and gets its name from the _`timezoneAs`_ parameter. 




### [`findTimestamp()`](functions-findtimestamp.html "findTimestamp\(\)") Syntax Examples

In a parser with `UTC` set as the timezone. 

logscale
    
    
    findTimestamp(timezone="UTC")

In a parser with `America/New_York` set as the timezone. 

logscale
    
    
    findTimestamp(timezone="America/New_York")

In a parser where the timestamp is located in a field named date. 

logscale
    
    
    findTimestamp(field=date, timezone="Europe/London")

In a query function where the timestamp should be stored in a field datetime and the timezone in a field tz. 

logscale
    
    
    findTimestamp(as="datetime", timezoneAs="tz")

In a parser where the timestamp is located in a field named _timezone. 

logscale
    
    
    findTimestamp(timezoneField="_timezone")

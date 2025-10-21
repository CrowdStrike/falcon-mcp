# formatTime() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-formattime.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`formatTime()`](functions-formattime.html "formatTime\(\)")

Formats a string according to `strftime`, similar to unix `strftime`. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-formattime.html#query-functions-formattime-as)|  string| required |  |  Specifies the output field.   
[_`field`_](functions-formattime.html#query-functions-formattime-field)|  string| optional[a] | `@timestamp`|  Contains a 64-bit integer that is interpreted as either seconds or milliseconds since the Unix epoch (00:00:00 on 1 January 1970, in the timezone specified by [_`timezone`_](functions-formattime.html#query-functions-formattime-timezone)). Whether the integer is interpreted as seconds or milliseconds is controlled by the [_`unit`_](functions-formattime.html#query-functions-formattime-unit) parameter.   
[_`format`_](functions-formattime.html#query-functions-formattime-format)[b]| string| required |  |  Format string. A subset of Java Date/Time escapes is supported by LogScale, see the following table.   
[_`locale`_](functions-formattime.html#query-functions-formattime-locale)|  string| optional[[a]](functions-formattime.html#ftn.table-functions-formattime-optparamfn) |  |  Specifies the locale such as `US` or `en_GB`.   
[_`timezone`_](functions-formattime.html#query-functions-formattime-timezone)|  string| optional[[a]](functions-formattime.html#ftn.table-functions-formattime-optparamfn) | `UTC`|  Specifies the timezone such as GMT, EST or Europe/London. See the full list of timezones supported by LogScale at [Supported Time Zones](syntax-time-timezones.html "Supported Time Zones"). If no timezone is present, UTC is used.   
[_`unit`_](functions-formattime.html#query-functions-formattime-unit)|  string| optional[[a]](functions-formattime.html#ftn.table-functions-formattime-optparamfn) | [`auto`](functions-formattime.html#query-functions-formattime-unit-option-auto)|  Controls whether the value in [_`field`_](functions-formattime.html#query-functions-formattime-field) is interpreted as seconds or milliseconds.   
|  |  | **Values**  
|  |  | [`auto`](functions-formattime.html#query-functions-formattime-unit-option-auto)| If the number is less than or equals to 100,000,000,000, it's interpreted as seconds, otherwise it's interpreted as milliseconds.  
|  |  | [`milliseconds`](functions-formattime.html#query-functions-formattime-unit-option-milliseconds)| The number is unconditionally interpreted as milliseconds.  
|  |  | [`seconds`](functions-formattime.html#query-functions-formattime-unit-option-seconds)| The number is unconditionally interpreted as seconds.  
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`format`_](functions-formattime.html#query-functions-formattime-format) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`format`_](functions-formattime.html#query-functions-formattime-format) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     formatTime("value",as="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     formatTime(format="value",as="value")
> 
> These examples show basic structure only.

### [`formatTime()`](functions-formattime.html "formatTime\(\)") Function Operation

The [`formatTime()`](functions-formattime.html "formatTime\(\)") function formats times using a subset of the [Java Formatter pattern](https://docs.oracle.com/en/java/javase/11/docs/api/java.base/java/util/Formatter.html#dt) format. The following formats are supported: 

Symbol |  Description |  Example   
---|---|---  
`%H` |  Hour of the day for the 24-hour clock, formatted as two digits with a leading zero as necessary. |  00, 23   
`%I` |  Hour for the 12-hour clock, formatted as two digits with a leading zero as necessary. |  01, 12   
`%k` |  Hour of the day for the 24-hour clock. |  0, 23   
`%l` |  Hour for the 12-hour clock. |  1, 12   
`%M` |  Minute within the hour formatted as two digits with a leading zero as necessary. |  00, 59   
`%S` |  Seconds within the minute, formatted as two digits with a leading zero as necessary. |  00, 60 (leap second)   
`%L` |  Millisecond within the second formatted as three digits with leading zeros as necessary. |  000 - 999   
`%N` |  Nanosecond within the second, formatted as nine digits with leading zeros as necessary. |  000000000 - 999999999   
`%p` |  Locale-specific morning or afternoon marker in lower case. |  am, pm   
`%z` |  RFC 822 style numeric time zone offset from GMT. |  -0800   
`%Z` |  A string representing the abbreviation for the time zone. |  UTC, EAT   
`%s` |  Seconds since the beginning of the epoch starting at 1 January 1970 00:00:00 UTC (UNIXTIME) |  1674304923   
`%Q` |  Milliseconds since the beginning of the epoch starting at 1 January 1970 00:00:00 UTC |  1674304923001\.   
`%B` |  Locale-specific full month name. |  "January", "February"   
`%b` |  Locale-specific abbreviated month name. |  "Jan", "Feb"   
`%h` |  Same as 'b'. |  "Jan", "Feb"   
`%A` |  Locale-specific full name of the day of the week. |  "Sunday", "Monday"   
`%a` |  Locale-specific short name of the day of the week. |  "Sun", "Mon".   
`%C` |  Four-digit year divided by 100, formatted as two digits with leading zero as necessary |  00, 99   
`%Y` |  Year, formatted as at least four digits with leading zeros as necessary. |  0092, 2023   
`%y` |  Last two digits of the year, formatted with leading zeros as necessary. |  00, 23   
`%j` |  Day of year, formatted as three digits with leading zeros as necessary. |  001 - 366   
`%m` |  Month, formatted as two digits with leading zeros as necessary. |  01 - 13   
`%d` |  Day of month, formatted as two digits with leading zeros as necessary. |  01 - 31   
`%e` |  Day of month, formatted as two digits. |  1 - 31   
`%R` |  Time formatted as `%H:%M`. |  23:59   
`%T` |  Time formatted as `%H:%M:%S`. |  23:59:59   
`%r` |  Time formatted as `%I:%M:%S %p`. AM and PM will be uppercase unlike for `%p`. |  01:21:11 PM   
`%D` |  Date formatted as `%m/%d/%y`. |  01/31/23   
`%F` |  ISO 8601 complete date formatted as `%Y-%m-%d`. |  1989-06-04   
`%c` |  Date and time formatted as `%a %b %d %T %Z %Y`. |  Thu Feb 02 11:03:28 Z 2023   
  
By default, the function will automatically detect whether the field contains a timestamp in seconds or milliseconds, based on its numeric value: 

  * If the given timestamp has less than 12 digits, it is interpreted as a timestamp in seconds. 

  * if it has 12 digits or more, it is interpreted as a timestamp in milliseconds. 




You can change the default auto-detection by specifically setting parameter [_`unit`_](functions-formattime.html#query-functions-formattime-unit) to seconds or milliseconds. 

When specifying the [_`unit`_](functions-formattime.html#query-functions-formattime-unit), the value must be a long integer and not a floating point value. 

### [`formatTime()`](functions-formattime.html "formatTime\(\)") Syntax Examples

Format time as 2021/11/26 06:54:45 using the timestamp field and UTC timezone using assignment to `fmttime`: 

logscale
    
    
    time := formatTime("%Y/%m/%d %H:%M:%S", field=@timestamp, locale=en_US, timezone=Z)

Format time as Thursday 18 November 2021, 22:59 using US locale and PST time zone setting the [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") parameter to `fmttime`: 

logscale
    
    
    formatTime("%A %d %B %Y, %R", as=fmttime, field=@timestamp, timezone=PST)

Format time variant where the unit is explicit: 

logscale
    
    
    formatTime("%A %d %B %Y, %R", as=fmttime, field=@timestamp, timezone=PST, unit=milliseconds)

Formatting a time where the unit is explicit and the supplied value is a floating-point figure: 

logscale
    
    
    regex(field=InstallDate, "(?<InstallDate>\\d+)")
    | formatTime("%A %d %B %Y, %R", as=fmttime, field=InstallDate, timezone=PST, unit=seconds)

In the above example, only the digits are extracted through the regular expression and then used as the basis for the [`formatTime()`](functions-formattime.html "formatTime\(\)") call. 

### [`formatTime()`](functions-formattime.html "formatTime\(\)") Examples

Click + next to an example below to get the full details.

#### Format Timestamp Using formatTime()

**Format a timestamp into a specific string pattern using the[`formatTime()`](functions-formattime.html "formatTime\(\)") function **

##### Query

logscale
    
    
    | time := formatTime("%Y/%m/%d %H:%M:%S", field=@timestamp, locale=en_US, timezone=Z)

##### Introduction

In this example, the [`formatTime()`](functions-formattime.html "formatTime\(\)") function is used to format the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field into a specific pattern with the format YYYY/MM/DD HH:mm:ss using US locale and UTC timezone and assigning the formatted timestamp to a new [time](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-query.html) field. 

Example incoming data might look like this: 

@timestamp| event_type| status  
---|---|---  
2025-08-27T08:51:51.312Z| login| success  
2025-08-27T09:15:22.445Z| logout| success  
2025-08-27T10:30:15.891Z| login| failed  
2025-08-27T11:45:33.167Z| update| success  
2025-08-27T12:20:44.723Z| login| success  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         | time := formatTime("%Y/%m/%d %H:%M:%S", field=@timestamp, locale=en_US, timezone=Z)

Creates a new field named [time](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-query.html) containing the formatted timestamp. The function takes the following parameters: 

     * Format pattern `%Y/%m/%d %H:%M:%S` specifies year, month, day with forward slashes and hours, minutes, seconds with colons. 

     * [_`field`_](functions-formattime.html#query-functions-formattime-field) parameter specifies the input timestamp field [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp). 

     * [_`locale`_](functions-formattime.html#query-functions-formattime-locale) parameter is set to `en_US` for US-style formatting. 

     * [_`timezone`_](functions-formattime.html#query-functions-formattime-timezone) parameter is set to `Z` for UTC timezone. 

  3. Event Result set.




##### Summary and Results

The query is used to transform ISO 8601 timestamps into a more readable format while maintaining UTC timezone. 

This query is useful, for example, to standardize timestamp formats for reporting, create human-readable date representations in logs, or prepare data for export to systems requiring specific date formats. 

Sample output from the incoming example data: 

@timestamp| event_type| status| time  
---|---|---|---  
2025-08-27T08:51:51.312Z| login| success| 2025/08/27 08:51:51  
2025-08-27T09:15:22.445Z| logout| success| 2025/08/27 09:15:22  
2025-08-27T10:30:15.891Z| login| failed| 2025/08/27 10:30:15  
2025-08-27T11:45:33.167Z| update| success| 2025/08/27 11:45:33  
2025-08-27T12:20:44.723Z| login| success| 2025/08/27 12:20:44  
  
#### List All EC2 Hosts With FirstSeen Data Within 14 Days

**List all the EC2 hosts with FirstSeen data within 14 days using the[`groupBy()`](functions-groupby.html "groupBy\(\)") function with [`selectLast()`](functions-selectlast.html "selectLast\(\)") **

##### Query

logscale
    
    
    #repo=sensor_metadata #data_source_name=aidmaster cloud.provider = "AWS_EC2_V2"
    | groupBy([aid], function=(selectLast([event_platform, aid, ComputerName, AgentVersion, FirstSeen])), limit=max)
    | FirstSeen := formatTime("%FT%T%z", field=FirstSeen)
    | TimeDelta := now() - duration("14d")

##### Introduction

In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") function is used with [`selectLast()`](functions-selectlast.html "selectLast\(\)") to retrieve the latest information about `AWS EC2` instances running CrowdStrike sensors, showing their platform, hostname, agent version, and when they were first seen, with a 14-day reference point for age comparison. 

Example incoming data (raw data in sensor_metadata) might look like this: 

@timestamp| aid| cloud.provider| event_platform| ComputerName| AgentVersion| FirstSeen  
---|---|---|---|---|---|---  
2025-05-20T10:00:00Z| 1234abcd| AWS_EC2_V2| Windows| ec2-web-01| 6.45.15678| 2025-01-15T08:30:00Z  
2025-05-21T11:00:00Z| 1234abcd| AWS_EC2_V2| Windows| ec2-web-01| 6.45.15679| 2025-01-15T08:30:00Z  
2025-05-22T12:00:00Z| 5678efgh| AWS_EC2_V2| Linux| ec2-app-02| 6.45.15678| 2025-02-01T14:45:00Z  
2025-05-23T13:00:00Z| 5678efgh| AWS_EC2_V2| Linux| ec2-app-02| 6.45.15679| 2025-02-01T14:45:00Z  
2025-05-24T14:00:00Z| 90123ijk| AWS_EC2_V2| Windows| ec2-db-03| 6.45.15678| 2025-03-10T09:15:00Z  
2025-05-25T15:00:00Z| 90123ijk| AWS_EC2_V2| Windows| ec2-db-03| 6.45.15679| 2025-03-10T09:15:00Z  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #repo=sensor_metadata #data_source_name=aidmaster cloud.provider = "AWS_EC2_V2"

Searches in the sensor_metadata repository, and filters for #data_source_name fields containing the value `aidmaster`, looking for cloud.provider of the type `AWS_EC2_V2` only. 

  3. logscale
         
         | groupBy([aid], function=(selectLast([event_platform, aid, ComputerName, AgentVersion, FirstSeen])), limit=max)

Groups results by the field aid (Agent ID). Then, for each unique group, selects the most recent values for the fields: event_platform, aid, ComputerName, AgentVersion, FirstSeen. 

Using the [`selectLast()`](functions-selectlast.html "selectLast\(\)") within the [`groupBy()`](functions-groupby.html "groupBy\(\)") is what actually selects the most recent record for each group. 

  4. logscale
         
         | FirstSeen := formatTime("%FT%T%z", field=FirstSeen)

Formats the timestamp in the FirstSeen field into ISO 8601 format. The result is stored back in the FirstSeen field. 

  5. logscale
         
         | TimeDelta := now() - duration("14d")

Calculates timestamp from 14 days ago, and returns the results into a new field named TimeDelta. The calculation is done by subtracting a 14-day duration from the current time using [`duration()`](functions-duration.html "duration\(\)"). 

This new TimeDelta field that represents a timestamp from 14 days ago, can be used for filtering or comparing against the FirstSeen timestamps. 

  6. Event Result set.




##### Summary and Results

The query is used to retrieve the latest information about AWS EC2 instances running CrowdStrike sensors, showing their platform, hostname, agent version, and when they were first seen, with a 14-day reference point for age comparison. 

The query is useful, for example, for auditing EC2 instance coverage, identifying newly added EC2 instances within the last two weeks, monitoring sensor versions or identifying aging or outdated installations. 

Sample output from the incoming example data: 

aid| event_platform| ComputerName| AgentVersion| FirstSeen| TimeDelta  
---|---|---|---|---|---  
1234abcd| Windows| ec2-web-01| 6.45.15679| 2025-01-15T08:30:00+0000| 2025-05-12T13:06:56+0000  
5678efgh| Linux| ec2-app-02| 6.45.15679| 2025-02-01T14:45:00+0000| 2025-05-12T13:06:56+0000  
90123ijk| Windows| ec2-db-03| 6.45.15679| 2025-03-10T09:15:00+0000| 2025-05-12T13:06:56+0000  
  
Each aid appears only once with its most recent values. Note that TimeDelta value is based on the current date provided (Mon, 26 May 2025 13:06:56 GMT).

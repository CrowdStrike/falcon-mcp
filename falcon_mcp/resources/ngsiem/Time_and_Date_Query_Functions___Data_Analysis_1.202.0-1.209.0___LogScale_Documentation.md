# Time and Date Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-time-date.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Time and Date Query Functions

LogScale's time and date functions manipulate or format time information from events. 

**Table: Time and Date Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`duration([as], duration)`](functions-duration.html "duration\(\)")| [_`duration`_](functions-duration.html#query-functions-duration-duration)|  |  Computes the number of milliseconds denoted by a human-readable specification.   
[`end([as])`](functions-end.html "end\(\)")| [_`as`_](functions-end.html#query-functions-end-as)|  |  Assign the end of the search time interval to the field provided by parameter [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters").   
[`findTimestamp([addErrors], [as], [field], [timezone], [timezoneAs], [timezoneField])`](functions-findtimestamp.html "findTimestamp\(\)")|  |  |  Finds timestamp in given field and parses, trying multiple timestamp formats.   
[`formatDuration([as], field, [from], [precision])`](functions-formatduration.html "formatDuration\(\)")| [_`field`_](functions-formatduration.html#query-functions-formatduration-field)|  |  Formats a duration into a more readable string.   
[`now([as])`](functions-now.html "now\(\)")| [_`as`_](functions-now.html#query-functions-now-as)|  |  Assign the current time to the field provided by parameter [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters").   
[`parseTimestamp([addErrors], [as], [caseSensitive], field, [format], [timezone], [timezoneAs], [timezoneField])`](functions-parsetimestamp.html "parseTimestamp\(\)")| [_`format`_](functions-parsetimestamp.html#query-functions-parsetimestamp-format)|  |  Parses a string into a timestamp.   
[`setTimeInterval([end], start, [timezone])`](functions-settimeinterval.html "setTimeInterval\(\)")| [_`start`_](functions-settimeinterval.html#query-functions-settimeinterval-start)|  |  Overwrites the time interval from API/UI.   
[`start([as])`](functions-start.html "start\(\)")| [_`as`_](functions-start.html#query-functions-start-as)|  |  Assign the start of the search time interval to the field provided by parameter [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters").   
[`time:dayOfMonth([as], [field], [timezone], [timezoneField])`](functions-time-dayofmonth.html "time:dayOfMonth\(\)")| [_`field`_](functions-time-dayofmonth.html#query-functions-time-dayofmonth-field)|  |  Gets the day of the month of a timestamp field.   
[`time:dayOfWeek([as], field, [timezone], [timezoneField])`](functions-time-dayofweek.html "time:dayOfWeek\(\)")| [_`field`_](functions-time-dayofweek.html#query-functions-time-dayofweek-field)|  |  Gets day of week from 1 (Mon) to 7 (Sun) of a timestamp.   
[`time:dayOfWeekName([as], [field], [timezone], [timezoneField])`](functions-time-dayofweekname.html "time:dayOfWeekName\(\)")| [_`field`_](functions-time-dayofweekname.html#query-functions-time-dayofweekname-field)|  |  Gets the English display name of day of the week of a timestamp field.   
[`time:dayOfYear([as], [field], [timezone], [timezoneField])`](functions-time-dayofyear.html "time:dayOfYear\(\)")| [_`field`_](functions-time-dayofyear.html#query-functions-time-dayofyear-field)|  |  Gets the day of the year of a timestamp field, from 1 to 365, or 366 in a leap year.   
[`time:hour([as], [field], [timezone], [timezoneField])`](functions-time-hour.html "time:hour\(\)")| [_`field`_](functions-time-hour.html#query-functions-time-hour-field)|  |  Gets the hour (24-hour clock) of a timestamp field.   
[`time:millisecond([as], [field], [timezone], [timezoneField])`](functions-time-millisecond.html "time:millisecond\(\)")| [_`field`_](functions-time-millisecond.html#query-functions-time-millisecond-field)|  |  Gets the millisecond of a timestamp field.   
[`time:minute([as], [field], [timezone], [timezoneField])`](functions-time-minute.html "time:minute\(\)")| [_`field`_](functions-time-minute.html#query-functions-time-minute-field)|  |  Gets the minute value of a timestamp field.   
[`time:month([as], [field], [timezone], [timezoneField])`](functions-time-month.html "time:month\(\)")| [_`field`_](functions-time-month.html#query-functions-time-month-field)|  |  Gets the month of a timestamp field (from 1 to 12).   
[`time:monthName([as], [field], [timezone], [timezoneField])`](functions-time-monthname.html "time:monthName\(\)")| [_`field`_](functions-time-monthname.html#query-functions-time-monthname-field)|  |  Gets the English name of month of a timestamp field (for example, January).   
[`time:second([as], [field], [timezone], [timezoneField])`](functions-time-second.html "time:second\(\)")| [_`field`_](functions-time-second.html#query-functions-time-second-field)|  |  Gets the second of a timestamp field.   
[`time:weekOfYear([as], [field], [timezone], [timezoneField])`](functions-time-weekofyear.html "time:weekOfYear\(\)")| [_`field`_](functions-time-weekofyear.html#query-functions-time-weekofyear-field)|  |  Gets the week number within a year of a timestamp, a value from 1 to 53.   
[`time:year([as], [field], [timezone], [timezoneField])`](functions-time-year.html "time:year\(\)")| [_`field`_](functions-time-year.html#query-functions-time-year-field)|  |  Gets the year of a timestamp field.

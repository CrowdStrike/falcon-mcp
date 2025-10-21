# upper() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-upper.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`upper()`](functions-upper.html "upper\(\)")

The [`upper()`](functions-upper.html "upper\(\)") function converts text to upper case letters. It can process text from event fields or other sources. By default, it uses the system locale, but it is possible to specify a different language and locale if needed. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-upper.html#query-functions-upper-as)|  string| optional[a] | `_upper`|  The name of the output field.   
[_`field`_](functions-upper.html#query-functions-upper-field)[b]| string| required |  |  The name of the input field with the value to convert to upper case.   
[_`locale`_](functions-upper.html#query-functions-upper-locale)|  string| optional[[a]](functions-upper.html#ftn.table-functions-upper-optparamfn) | `system locale`|  The name of the locale to use as ISO 639 language and an ISO 3166 country (for example, `da`, or `da_DK`). When not specified, it uses the system locale.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-upper.html#query-functions-upper-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-upper.html#query-functions-upper-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     upper("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     upper(field="value")
> 
> These examples show basic structure only.

### [`upper()`](functions-upper.html "upper\(\)") Function Operation

For the value of type, you can specify just the language, or you can refine that choice by including the country. For instance, you might specify: 

  * `en` for English. 

  * `en_UK` for UK English. 

  * `en_US` for US English. 




Specifying the correct locale is particularly important for languages with non-Latin alphabets, such as Russian with Cyrillic letters. 

### [`upper()`](functions-upper.html "upper\(\)") Examples

Click + next to an example below to get the full details.

#### Correlate Two Scheduled Task Events

**Correlate two scheduled task events (registration and deletion) within a 5-minute window using the`correlate` function **

##### Query

logscale
    
    
    correlate(
        ScheduledTaskRegistered: {
            #repo="base_sensor" #event_simpleName=ScheduledTaskRegistered RemoteIP=* 
        | upper(field=TaskName, as=scheduledTaskName)
        } include: [*],
      ScheduledTaskDeleted: {
              #repo="base_sensor" #event_simpleName=ScheduledTaskDeleted RemoteIP=* 
              | upper(field=TaskName, as=scheduledTaskName)
              | aid <=> ScheduledTaskRegistered.aid
              | scheduledTaskName <=> ScheduledTaskRegistered.scheduledTaskName
              } include: [*],
    sequence=false, within=5m)

##### Introduction

In this example, the [`correlate()`](functions-correlate.html "correlate\(\)") function is used to identify when scheduled tasks are registered and subsequently deleted by matching events based on the task identifier (aid field) and name (TaskName field) within a 5-minute window. 

The [`correlate()`](functions-correlate.html "correlate\(\)") function finds relationships between the events within the `ScheduledTaskRegistered` and `ScheduledTaskDeleted` queries. `sequence=false` means that events can occur in any order within the time window 

Example incoming data might look like this: 

@timestamp| #repo| #event_simpleName| aid| TaskName| RemoteIP  
---|---|---|---|---|---  
2023-06-15T10:00:00Z| base_sensor| ScheduledTaskRegistered| aid123| backup_task| 192.168.1.100  
2023-06-15T10:02:00Z| base_sensor| ScheduledTaskDeleted| aid123| backup_task| 192.168.1.100  
2023-06-15T10:05:00Z| base_sensor| ScheduledTaskRegistered| aid456| cleanup_task| 192.168.1.101  
2023-06-15T10:07:00Z| base_sensor| ScheduledTaskDeleted| aid456| cleanup_task| 192.168.1.101  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         correlate(
             ScheduledTaskRegistered: {
                 #repo="base_sensor" #event_simpleName=ScheduledTaskRegistered RemoteIP=* 
             | upper(field=TaskName, as=scheduledTaskName)
             } include: [*],

Defines the first query named ScheduledTaskRegistered to match scheduled task registrations. Filters for events from [#repo](searching-data-event-fields.html#searching-data-event-fields-tag-repo)=`base_sensor` with #event_simpleName=`ScheduledTaskRegistered` and any RemoteIP. RemoteIP=* ensures that the field exists. 

The [`upper()`](functions-upper.html "upper\(\)") function converts the TaskName field to uppercase and returns the converted results in a new field named scheduledTaskName. 

`include: [*]` ensures that the query includes all fields from matching events. 

  3. logscale
         
         ScheduledTaskDeleted: {
                   #repo="base_sensor" #event_simpleName=ScheduledTaskDeleted RemoteIP=* 
                   | upper(field=TaskName, as=scheduledTaskName)
                   | aid <=> ScheduledTaskRegistered.aid
                   | scheduledTaskName <=> ScheduledTaskRegistered.scheduledTaskName
                   } include: [*],

Defines the second query named ScheduledTaskDeleted to match scheduled task deletions. Filters for events from [#repo](searching-data-event-fields.html#searching-data-event-fields-tag-repo)=`base_sensor` with #event_simpleName=`ScheduledTaskDeleted` and any RemoteIP. RemoteIP=* ensures that the field exists. 

The correlation relationships (conditions) are specified using the ``<=>`` operator which requires exact matches between fields (field correlation matches). 

The aid field from this ScheduledTaskDeleted event must match the aid field from the ScheduledTaskRegistered event, and similarly for the scheduledTaskName field. The corresponding fields will be used to join the events together across all the queries in the set. This ensures that events will only by dcorrelated when related to the same task instance. 

`include: [*]` ensures that the query includes all fields from matching events. 

  4. logscale
         
         sequence=false, within=5m)

Sets correlation parameters: 

     * [_`sequence`_](functions-correlate.html#query-functions-correlate-sequence)=`false` allows events to match regardless of order. 

Setting the [_`sequence`_](functions-correlate.html#query-functions-correlate-sequence) parameter to `false` in this example is useful as `deletion events` could theoretically be recorded before `registration events` due to system delays. 

     * [_`within`_](functions-correlate.html#query-functions-correlate-within)=`5m` specifies a 5-minute time window for matching events meaning that only events within 5 minutes of each other will be correlated. 

By default, the query will match the event correlation only once per root query (return the first match), as the [_`maxPerRoot`_](functions-correlate.html#query-functions-correlate-maxperroot) parameter is not specified. 

The [`correlate()`](functions-correlate.html "correlate\(\)") function outputs each pair of matched events as a single event containing fields from both sources, prefixed with their respective subquery names (for example, ScheduledTaskRegistered.aid, ScheduledTaskDeleted.@timestamp). 

  5. Event Result set.




##### Summary and Results

The query is used to identify and correlate scheduled task registration and deletion events for the same task within a 5-minute window. 

The output demonstrates successful correlation of scheduled task registration and deletion events, showing the complete lifecycle of tasks that were both created and deleted within the specified timeframe. 

This query is useful, for example, to monitor task lifecycle patterns, detect unusual task deletion behavior, or audit scheduled task management activities. 

Sample output from the incoming example data: 

@timestamp| ScheduledTaskRegistered.aid| ScheduledTaskRegistered.scheduledTaskName| ScheduledTaskRegistered.RemoteIP| ScheduledTaskDeleted.@timestamp| ScheduledTaskDeleted.RemoteIP  
---|---|---|---|---|---  
2023-06-15T10:00:00Z| aid123| BACKUP_TASK| 192.168.1.100| 2023-06-15T10:02:00Z| 192.168.1.100  
2023-06-15T10:05:00Z| aid456| CLEANUP_TASK| 192.168.1.101| 2023-06-15T10:07:00Z| 192.168.1.101  
  
Note that the output includes timestamps from each query. In this case, this allows for analysis of the time between task creation and removal. 

#### Format a String to Upper Case and Lower Case

**Format a string to upper case and lower case using the[`upper()`](functions-upper.html "upper\(\)") and [`lower()`](functions-lower.html "lower\(\)") functions with [`concat()`](functions-concat.html "concat\(\)") **

##### Query

logscale
    
    
    lower(@error_msg[0], as=msg1)
     
    | upper(@error_msg[1], as=msg2)
     
    | concat([msg1, msg2], as=test)

##### Introduction

In this example, [`upper()`](functions-upper.html "upper\(\)") and [`lower()`](functions-lower.html "lower\(\)") functions are used with [`concat()`](functions-concat.html "concat\(\)") to concatenate two fields containing error messages, where one field's result is all lower case letters and the other field's results are all upper case letters. 

If no [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") parameter is set, the fields outputted to is by default named _upper and _lower, respectively. 

In this query, the [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") parameter is used for the [`lower()`](functions-lower.html "lower\(\)") and [`upper()`](functions-upper.html "upper\(\)") functions to label their results. These fields (msg1 and msg2) are then used with the [`concat()`](functions-concat.html "concat\(\)") function, returning the concatenated string into a field named test. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         lower(@error_msg[0], as=msg1)

Formats the first element (index 0) of the @error_msg array to lower case and returns the results in a field named msg1. 

  3. logscale
         
         | upper(@error_msg[1], as=msg2)

Formats the second element (index 1) of the  @error_msg array to upper case and returns the results in a field named msg2. 

  4. logscale
         
         | concat([msg1, msg2], as=test)

Concatenates (combines) the values in field msg1 and field msg2, and returns the concatenated string in a new field named test. 

If using the [`top()`](functions-top.html "top\(\)") function on the test field, like this: 

`| top(test)`

then the top 10 values for the field test is displayed with a count of their occurrences in a field named _count. 

  5. Event Result set.




##### Summary and Results

The query is used to either convert strings to lower case or upper case and return the new concatenated strings/results in a new field. In this example, concatenating error messages. 

The specific labeling of msg1 and msg2 is particularly useful when you have more than one field that use the same query function. 

By converting fields to consistent cases, it helps standardize data for easier analysis and comparison. The concatenation allows you to combine multiple fields into a single field, which can be useful for creating unique identifiers or grouping related information. 

#### Perform Formatting on All Values in an Array

**Perform formatting on all values in a flat array using the[`array:eval()`](functions-array-eval.html "array:eval\(\)") function **

##### Query

logscale
    
    
    array:eval("devices[]",  asArray="upperDevices[]", var=d, function={upperDevices :=upper("d")})

##### Introduction

In this example, the [`array:eval()`](functions-array-eval.html "array:eval\(\)") function is used to convert all values (for example `[Thermostat, Smart Light]`) in an array devices[] from lowercase to uppercase and show the results in a new array. 

Example incoming data might look like this: 

Raw Events

{\"devices\":[\"Thermostat\",\"Smart Plug\"],\"room\":\"Kitchen\"}"  
---  
{\"devices\":[\"Smart Light\",\"Thermostat\",\"Smart Plug\"],\"room\":\"Living Room\"}"  
{\"devices\":[\"Smart Light\",\"Smart Plug\"],\"room\":\"Bedroom\"}"  
{\"devices\":[\"Thermostat\",\"Smart Camera\"],\"room\":\"Hallway\"}"  
{\"devices\":[\"Smart Light\",\"Smart Lock\"],\"room\":\"Front Door\"}"  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:eval("devices[]",  asArray="upperDevices[]", var=d, function={upperDevices :=upper("d")})

Formats all values in the array devices[] to uppercase and returns the results in a new array named upperDevices[]. The values in the original array stay the same: `[Thermostat, Smart Plug, Smart Light]` and the new array contains the returned results: `[THERMOSTAT, SMART PLUG, SMART LIGHT]`

  3. Event Result set.




##### Summary and Results

The query is used to turn values in an array into uppercase. The [`array:eval()`](functions-array-eval.html "array:eval\(\)") function can also be used for squaring a list of numbers in an array. 

Sample output from the incoming example data: 

devices[]| upperDevices[]  
---|---  
Thermostat| THERMOSTAT  
Smart Plug| SMART PLUG  
Smart Light| SMART LIGHT  
  
#### Standardize Values And Combine Into Single Field

**Standardize values using the[`upper()`](functions-upper.html "upper\(\)") and [`lower()`](functions-lower.html "lower\(\)") functions and combine into single field with [`concat()`](functions-concat.html "concat\(\)") **

##### Query

logscale
    
    
    lower(#severity, as=severity)
     
    | upper(#category, as=category)
     
    | concat([severity, category], as=test)
     
    | top(test)

##### Introduction

Standardizing the format of fields is useful for consistent analysis. In this example, [`upper()`](functions-upper.html "upper\(\)") and [`lower()`](functions-lower.html "lower\(\)") functions are used with [`concat()`](functions-concat.html "concat\(\)") to concatenate the fields #category and severity, where one field's result is all lower case letters and the other field's results are all upper case letters. 

If no [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") parameter is set, the fields outputted to is by default named _upper and _lower, respectively. 

In this query, the [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") parameter is used for the [`lower()`](functions-lower.html "lower\(\)") and [`upper()`](functions-upper.html "upper\(\)") functions to label their results. These output fields (category and severity) are then used with the [`concat()`](functions-concat.html "concat\(\)") function, returning the concatenated string into a field named test. Finally, it uses the [`top()`](functions-top.html "top\(\)") function, to show which combinations of `severity` and `category` are most common in the data. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         lower(#severity, as=severity)

Converts the values in the #severity field to lower case and returns the results in a field named severity. 

  3. logscale
         
         | upper(#category, as=category)

Converts the values in the #category field to upper case and returns the results in a field named category. 

  4. logscale
         
         | concat([severity, category], as=test)

Concatenates (combines) the values in field category and field severity, and returns the concatenated string in a new field named test. 

  5. logscale
         
         | top(test)

Finds the most common values of the field test — the top of an ordered list of results - along with their count. The result of the count of their occurrences is displayed in a field named _count. 

  6. Event Result set.




##### Summary and Results

The query is used to standardize the format of the values in the fields #category and severity and concatenate the values into a single field, showing which combinations of `severity` and `category` are most common in the data. 

The specific labeling of category and severity is particularly useful when you have more than one field that use the same query function. 

By converting fields to consistent cases, it helps standardize data for easier analysis and comparison. The concatenation allows you to combine multiple fields into a single field, which can be useful for creating unique identifiers or grouping related information. It provides a quick overview of the distribution of events across different `severity-category` combinations. 

Sample output from the incoming example data (showing the first 10 rows only): 

test| _count  
---|---  
infoALERT| 90005  
infoFILTERALERT| 36640  
errorALERT| 17256  
warningGRAPHQL| 14240  
warningALERT| 13617  
warningSCHEDULEDSEARCH| 11483  
infoSCHEDULEDSEARCH| 5917  
warningFILTERALERT| 1646  
errorFILTERALERT| 1487  
infoACTION| 3  
  
Notice how the value of #severity is in lower case letters, and the value of #category is in upper case letters.

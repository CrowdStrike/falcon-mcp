# in() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-in.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Oct 1, 2024

## [`in()`](functions-in.html "in\(\)")

This query function may be used to select events in which the given field contains particular values. For instance, you might want to monitor events in which log messages contain error, warning, or other similar words in log entries, or perhaps particular numeric values in other fields. 

Although this query function allows for only three parameters, it is very useful and versatile. For the first parameter, you would specify the field on which to filter data. The second parameter sets whether the search should be case-insensitive. The third parameter would be the string or multiple strings on which to match the contents of the field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`field`_](functions-in.html#query-functions-in-field)[a]| string| required |  |  The field on which to filter events.   
[_`ignoreCase`_](functions-in.html#query-functions-in-ignorecase)|  string| optional[b] | `false`|  Allows for case-insensitive searching.   
[_`values`_](functions-in.html#query-functions-in-values)|  array of strings| required |  |  The values on which to match the field. Only one match is required. Values can contain wildcards (for example, `*`).   
[a] The parameter name [_`field`_](functions-in.html#query-functions-in-field) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-in.html#query-functions-in-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     in("value",values=["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     in(field="value",values=["value"])
> 
> These examples show basic structure only.

Hide negatable operation for this function

Show negatable operation for this function

> Negatable Function Operation
> 
> This function is negatable, implying the inverse of the result. For example:
> 
> logscale Syntax
>     
>     
>     !in()
> 
> Or:
> 
> logscale Syntax
>     
>     
>     not in()
> 
> For more information, see [Negating the Result of Filter Functions](syntax-operators.html#syntax-operators-negate "Negating the Result of Filter Functions").

### [`in()`](functions-in.html "in\(\)") Syntax Examples

Suppose you have a repository which is ingesting data from a few web servers. And suppose that you want to get a list of events in which the user received the HTTP code 404, for web pages Not Found. You could do that easily with this query: 

logscale
    
    
    status = 404

As this suggests, the field on which to check is status. 

Suppose further that you want to get a list of events in which the user received the HTTP codes 422 and 200. Those codes represent respectively Unable to be processed, and Successful. You could get those events with the [`in()`](functions-in.html "in\(\)") function like so: 

logscale
    
    
    in(status, values=["422","200"])

Using the status field for the first parameter; for the second parameter, the two statuses are listed, separated by commas, within an array — within square-brackets. Incidentally, if you wanted to include string values instead of numbers, each string value would have to be contained within double-quotes. 

The screenshot in [Figure 150, “`in()` Example”](functions-in.html#figure_functions-in-examples "Figure 150. in\(\) Example") below shows how this would look in the LogScale interface. 

![in\(\) Example](images/query-functions/in-function-example-1.png)  
---  
  
**Figure 150.[`in()`](functions-in.html "in\(\)") Example**

  


There are a few other HTTP codes related to errors besides these two. You could list all of them in the array, or you could add the wildcard (for example, `*`) like this: 

logscale
    
    
    in(status, values=["4*"])

This will return all events in which the status has a value starting with 4. Notice that even though only one value is given, you have to include the square-brackets. Also, notice that since the wildcard is used, the double-quotes is required. 

Using the _`field`_ parameter in addition to the `=~` syntax: 

logscale
    
    
    in(field=loglevel, values=["ERROR", "WARN"])

Negating an [`in()`](functions-in.html "in\(\)") filters: 

logscale
    
    
    !in(field=loglevel, values=["ERROR", "WARN"])

and 

logscale
    
    
    loglevel =~ !in(values=["ERROR", "WARN"])

### [`in()`](functions-in.html "in\(\)") Examples

Click + next to an example below to get the full details.

#### Categorize Errors in Log Levels

**Categorize errors in log levels using the[`in()`](functions-in.html "in\(\)") function in combination with [`if()`](functions-if.html "if\(\)") **

##### Query

logscale
    
    
    critical_status := if((in(status, values=["500", "404"])), then="Critical", else="Non-Critical")

##### Introduction

In this more advanced example, the [`if()`](functions-if.html "if\(\)") function is used to categorize errors based on a time condition and it compares the status of a log level and decides on the log's criticality. The field critical_status is going to be evaluated based on the [`if()`](functions-if.html "if\(\)") function. 

Example incoming data might look like this: 

Raw Events

srcIP=192.168.1.5 loglevel=ERROR status=404 user=admin  
---  
srcIP=10.0.0.1 loglevel=INFO status=200 user=user1  
srcIP=172.16.0.5 loglevel=WARN status=422 user=user2  
srcIP=192.168.1.15 loglevel=ERROR status=500 user=admin  
srcIP=10.0.0.12 loglevel=DEBUG status=302 user=user1  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         critical_status := if((in(status, values=["500", "404"])), then="Critical", else="Non-Critical")

Searches for events where the field status contains the values `500` or `400` and assigns the value `Critical` to a field named critical_status for the returned results. If the values are not equal to `500` or `400`, then the returned events will have the value `Non-Critical` assigned to the field critical_status. 

  3. Event Result set.




##### Summary and Results

The query is used to categorize errors in log levels according to their criticality. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user| critical_status  
---|---|---|---|---  
192.168.1.5| ERROR| 404| admin| Critical  
10.0.0.1| INFO| 200| user1| Non-Critical  
172.16.0.5| WARN| 422| user2| Non-Critical  
192.168.1.15| ERROR| 500| admin| Critical  
10.0.0.12| DEBUG| 302| user1| NonCritical  
  
#### Categorize Events Based on Values in More Fields

**Categorize events based on values across multiple fields - the example uses a combination of[`in()`](functions-in.html "in\(\)") with `case`, [`match()`](functions-match.html "match\(\)"), and [`if()`](functions-if.html "if\(\)") **

##### Query

logscale
    
    
    case {     in(srcIP, values=["192.168.1.*"])
    | type := "Internal";     !in(loglevel, values=["DEBUG", "INFO"])
    | type := "Critical";
    | type := "Other" }

##### Introduction

In this more advanced example, a case statement is used to categorize events based on the fields srcIP and loglevel, using both [`in()`](functions-in.html "in\(\)") and negated [`in()`](functions-in.html "in\(\)"). Notice that the semi-colon is used to end the different logical expressions. 

Example incoming data might look like this: 

Raw Events

srcIP=192.168.1.5 loglevel=ERROR status=404 user=admin  
---  
srcIP=10.0.0.1 loglevel=INFO status=200 user=user1  
srcIP=172.16.0.5 loglevel=WARN status=422 user=user2  
srcIP=192.168.1.15 loglevel=ERROR status=500 user=admin  
srcIP=10.0.0.12 loglevel=DEBUG status=302 user=user1  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         case {     in(srcIP, values=["192.168.1.*"])
         | type := "Internal";     !in(loglevel, values=["DEBUG", "INFO"])
         | type := "Critical";
         | type := "Other" }

Returns all events with values starting with `192.168.1.*` followed by anything in the scrIP field and then creates a new field named type with the assigned value `Internal` for the returned results. Notice that since the wildcard is used, the double-quotes is required. 

Next, the query searches for events where the field loglevel does not contain the values `DEBUG` or `INFO` and assigns the value `Critical` to the returned results in the type field. For anything else, it sets the value in the type field to `Other`. 

In this example, `INFO` and `DEBUG` will therefore be set to `Other`. The above case statement can also be expressed like this: If the sourceIP equals the value `192.168.1.*` followed by anything, then identify the type field as `Internal`. If it is not equal to the loglevel of debug or info, then identify the type field as `Critical`. If it does not match either of the above, identify the type field as `Other`. 

  3. Event Result set.




##### Summary and Results

The query is used to to categorize events and define their type. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user| type  
---|---|---|---|---  
192.168.1.5| ERROR| 404| admin| Internal  
10.0.0.1| INFO| 200| user1| Other  
172.16.0.5| WARN| 422| user2| Critical  
192.168.1.15| ERROR| 500| admin| Internal  
10.0.0.12| DEBUG| 302| user1| Other  
  
#### Differentiate Between Types of Log Levels

**Differentiate between types of log levels using the[`in()`](functions-in.html "in\(\)") function with the match expression **

##### Query

logscale
    
    
    loglevel match {     /.*ERROR.*/ => severity := "High";     in(values=["DEBUG", "INFO"]) => severity := "Low"; => severity := "Medium" }

##### Introduction

In this more advanced example, we match against the loglevel using the match filter statement. Notice that the semi-colon is used to end the different logical expressions. 

Example incoming data might look like this: 

Raw Events

srcIP=192.168.1.5 loglevel=ERROR status=404 user=admin  
---  
srcIP=10.0.0.1 loglevel=INFO status=200 user=user1  
srcIP=172.16.0.5 loglevel=WARN status=422 user=user2  
srcIP=192.168.1.15 loglevel=ERROR status=500 user=admin  
srcIP=10.0.0.12 loglevel=DEBUG status=302 user=user1  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         loglevel match {     /.*ERROR.*/ => severity := "High";     in(values=["DEBUG", "INFO"]) => severity := "Low"; => severity := "Medium" }

Matches all log levels which have the value/word `ERROR` inside their dataset and creates a new field named severity with the assigned value `High` for the returned results/matches. 

Then it matches events with the values `DEBUG` or `INFO` and assigns the value `Low` to the returned results in the severity field. If the severity field does not exist, it will create it, if the severity field does exist, it will overwrite the value of the field. For anything else, it sets the value in the severity field to `Medium`. 

In this example, a loglevel like `WARN` will therefore be set to `Medium`. 

Notice the use of double-quotes around the values to right of the assignment operator, if not used, it will be interpreted as a field and not a string. 

  3. Event Result set.




##### Summary and Results

The query is used to differentiate between types of log levels. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user| severity  
---|---|---|---|---  
192.168.1.5| ERROR| 404| admin| High  
10.0.0.1| INFO| 200| user1| Low  
172.16.0.5| WARN| 422| user2| Medium  
192.168.1.15| ERROR| 500| admin| High  
10.0.0.12| DEBUG| 302| user1| Low  
  
#### Exclude Events With Specific Values From Searches

**Exclude events with specific values from searches using the negated function[`in()`](functions-in.html "in\(\)") **

##### Query

logscale
    
    
    !in(loglevel, values=["ERROR", "WARN"])

##### Introduction

It is possible to exclude events with specific values using the [`in()`](functions-in.html "in\(\)") function with a negation in front. In this example, events will be excluded from the search result if the loglevel field contains the values `ERROR` or `WARNING`. 

Example incoming data might look like this: 

Raw Events

srcIP=192.168.1.5 loglevel=ERROR status=404 user=admin  
---  
srcIP=10.0.0.1 loglevel=INFO status=200 user=user1  
srcIP=172.16.0.5 loglevel=WARN status=422 user=user2  
srcIP=192.168.1.15 loglevel=ERROR status=500 user=admin  
srcIP=10.0.0.12 loglevel=DEBUG status=302 user=user1  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         !in(loglevel, values=["ERROR", "WARN"])

Returns all events in which the loglevel field does not contain the value `ERROR` or `WARNING`. 

  3. Event Result set.




##### Summary and Results

The query is used to exclude events with specific values from search results. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user  
---|---|---|---  
10.0.0.1| INFO| 200| user1  
10.0.0.12| DEBUG| 302| user1  
  
#### Filter on a Single Field for One Specific Value

**Filter the events using a single field matching a specific value**

##### Query

logscale
    
    
    status = 404

##### Introduction

In this example we want a list of events in which the user received the HTTP code `404`. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         status = 404

Filters for all events with the value `404` in the status field. 

  3. Event Result set.




##### Summary and Results

The query is used to search a single field for one specific value. In this example, it selects logs with a specific HTTP status. 

#### Perform Case-Insensitive Match on Field

**Perform a case-insensitive match on field using[`in()`](functions-in.html "in\(\)") function **

##### Query

logscale
    
    
    in(loglevel, ignoreCase=true, values=["error", "warn"])

##### Introduction

It is possible to perform case-insensitive searches on a field using the [`in()`](functions-in.html "in\(\)") function. In this example, the loglevel field is searched for occurrences of either `error` or `warning`. 

Example incoming data might look like this: 

Raw Events

srcIP=192.168.1.5 loglevel=ERROR status=404 user=admin  
---  
srcIP=10.0.0.1 loglevel=INFO status=200 user=user1  
srcIP=172.16.0.5 loglevel=WARN status=422 user=user2  
srcIP=192.168.1.15 loglevel=ERROR status=500 user=admin  
srcIP=10.0.0.12 loglevel=DEBUG status=302 user=user1  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         in(loglevel, ignoreCase=true, values=["error", "warn"])

Returns all events in which the loglevel field has the value `error` or `warning`. As it is case-insensitive, it returns all occurrences of the specified values in all their variants, regardless of the case. 

  3. Event Result set.




##### Summary and Results

The query is used to perform case-insensitive searches on a specific value in a given field. This is useful when searching for strings where values may appear in both both upper and lower case to ensure that all events are extracted. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user  
---|---|---|---  
192.168.1.5| ERROR| 404| admin  
172.16.0.5| WARN| 422| user2  
192.168.1.15| ERROR| 500| admin  
  
#### Search Single Field for Multiple Values

**Search single field for multiple values using the[`in()`](functions-in.html "in\(\)") function **

##### Query

logscale
    
    
    in(status, values=["404","422"])

##### Introduction

In this example, the [`in()`](functions-in.html "in\(\)") function is used to search for events in which the user received the HTTP codes `404` and `422`. 

Example incoming data might look like this: 

Raw Events

srcIP=192.168.1.5 loglevel=ERROR status=404 user=admin  
---  
srcIP=10.0.0.1 loglevel=INFO status=200 user=user1  
srcIP=172.16.0.5 loglevel=WARN status=422 user=user2  
srcIP=192.168.1.15 loglevel=ERROR status=500 user=admin  
srcIP=10.0.0.12 loglevel=DEBUG status=302 user=user1  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         in(status, values=["404","422"])

Searches for events with the values `404` and `422` in the status field. If you want to search for all values starting with 4, it is possible to just use the query `in(status, values=["4*"])` \- here it is important to remember the double-quotes because of the wildcard usage. 

  3. Event Result set.




##### Summary and Results

The query is used to search a single field for specific values. This is useful when monitoring events in which log messages contain error, warning, or other similar words in log entries, or perhaps specific numeric values in other fields. In this example, it selects logs with specific HTTP statuses. If you just want to search a single field for one specific value, use this query: `status = 404` instead of the [`in()`](functions-in.html "in\(\)") function. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user  
---|---|---|---  
192.168.1.5| ERROR| 404| admin  
172.16.0.5| WARN| 422| user2  
  
#### Search Status Field for All Status Codes Starting With "1" or "2"

**Use a wildcard with[`in()`](functions-in.html "in\(\)") to select all status codes starting with `"1"` or `"2"` **

##### Query

logscale
    
    
    in(status, values=["1*", "2*"])

##### Introduction

It is possible to use wildcards with the [`in()`](functions-in.html "in\(\)") function to select for example all status codes starting with "1" or "2". Notice that `""` must be used around the `*`. 

Example incoming data might look like this: 

Raw Events

srcIP=192.168.1.5 loglevel=ERROR status=404 user=admin  
---  
srcIP=10.0.0.1 loglevel=INFO status=200 user=user1  
srcIP=172.16.0.5 loglevel=WARN status=422 user=user2  
srcIP=192.168.1.15 loglevel=ERROR status=500 user=admin  
srcIP=10.0.0.12 loglevel=DEBUG status=302 user=user1  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         in(status, values=["1*", "2*"])

Returns all events in which the status has a value starting with either `1` or `2`. Notice that since the wildcard is used, the double-quotes is required. 

  3. Event Result set.




##### Summary and Results

The query is used to search status field for status codes starting with a given integer. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user  
---|---|---|---  
10.0.0.1| INFO| 200| user1  
  
#### Search Two Fields for Multiple Values in Either First Field or Second Field

**Search two fields for multiple values using the[`in()`](functions-in.html "in\(\)") function, using a case statement as an OR **

##### Query

logscale
    
    
    case
            { in(srcIP, values=["10.1.168.2", "127.0.0.1"]);
            in(targetIP, values=["10.0.0.1", "192.168.1.12"]); }

##### Introduction

In this example, the query will look for events in either the srcIP field or the targetIP. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         case
                 { in(srcIP, values=["10.1.168.2", "127.0.0.1"]);
                 in(targetIP, values=["10.0.0.1", "192.168.1.12"]); }

Filters for events in the srcIP field that contains the values `10.1.168.2` or `127.0.0.1` and filters for events in the targetIP field that contains the values `10.0.0.1` or `192.168.1.12`. The returned results would be events from both fields. Notice that because it is a case statement, it executes and returns whether either field contains the corresponding values in the array. 

  3. Event Result set.




##### Summary and Results

The query is used to query two fields for multiple/specific values in either first field or second field.

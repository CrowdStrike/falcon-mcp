# text:startsWith() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-text-startswith.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Page was created:Jul 29, 2025

## [`text:startsWith()`](functions-text-startswith.html "text:startsWith\(\)")

The [`text:startsWith()`](functions-text-startswith.html "text:startsWith\(\)") function compares two strings and evaluates whether one string begins with another string. 

[`text:startsWith()`](functions-text-startswith.html "text:startsWith\(\)") takes two arguments: [_`string`_](functions-text-startswith.html#query-functions-text-startswith-string) and [_`substring`_](functions-text-startswith.html#query-functions-text-startswith-substring), both of which can be provided as plain text, field values, or results of an expression. 

Similar to the [`test()`](functions-test.html "test\(\)") function, [`text:startsWith()`](functions-text-startswith.html "text:startsWith\(\)") returns the events where the condition is met. The function can be negated to find the events, where the substring is not found in the string. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`string`_](functions-text-startswith.html#query-functions-text-startswith-string)[a]| expression| required |  |  The string in which the starting substring is matched.   
[_`substring`_](functions-text-startswith.html#query-functions-text-startswith-substring)|  expression| required |  |  The substring which is matched at the beginning of the corresponding [_`string`_](functions-text-startswith.html#query-functions-text-startswith-string) parameter. It specifies the characters to match at the beginning of the string.   
[a] The parameter name [_`string`_](functions-text-startswith.html#query-functions-text-startswith-string) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`string`_](functions-text-startswith.html#query-functions-text-startswith-string) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     text:startsWith("value",substring="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     text:startsWith(string="value",substring="value")
> 
> These examples show basic structure only.

### [`text:startsWith()`](functions-text-startswith.html "text:startsWith\(\)") Syntax Examples

Filter events where a field value starts with a string (having the string as a field and the substring as a value): 

This example finds all events where files were accessed in a specific folder. 

logscale
    
    
    text:startsWith(string=file, substring="C:\\Windows\System32")

If input data was `file=C:\\Windows\\System32`, `file=C:\\Windows\\System32\Taskmgr.exe`, `file=C:\\MyDocuments\powerpoint.exe`, it would return: 

file  
---  
C:\\\Windows\\\System32  
C:\\\Windows\\\System32\Taskmgr.exe  
  
Filter events where a field value is the prefix of a string (having the string as a value and the substring as a field): 

This example finds all events where folders leading to a specific executable were accessed. 

logscale
    
    
    text:startsWith(string="C:\\Windows\System32\taskkill.exe", substring=file)

If input data was `file=C:\\Windows\\System32`, `file=C:\\Windows\\System32\Taskmgr.exe`, `file=C:\\MyDocuments\powerpoint.exe`, it would return: 

file  
---  
C:\\\Windows\\\System32  
  
Filter events where a field value does not start with a string (using negation): 

This example filters out events where a certain folder was accessed. 

logscale
    
    
    !text:startsWith(string=file, substring="C:\\MyDocuments")

If input data was `file=C:\\Windows\\System32`, `file=C:\\Windows\\System32\Taskmgr.exe`, `file=C:\\MyDocuments\powerpoint.exe`, it would return: 

file  
---  
C:\\\Windows\\\System32  
C:\\\Windows\\\System32\Taskmgr.exe  
  
Filter events where the evaluated value of an expression starts with a given string (having string as an expression): 

This example finds all commands attempting to access a certain executable. 

logscale
    
    
    text:startsWith(string=lower(commandline), substring="c:\\windows\system32\killtask.exe")

If input data was `commandline=C:\\Windows\\System32\KillTask.exe`, `commandline=C:\\Windows\\System32\killtask.exe`, `commandline=C:\\MyDocuments\powerpoint.exe`, it would return: 

commandline  
---  
C:\\\Windows\\\System32\KillTask.exe  
C:\\\Windows\\\System32\killtask.exe  
  
### Note

In expressions, quotation marks always mean a string value, while unquoted field names always mean the value of that field. 

To use the value of a field with such a name in an expression, the function [`getField()`](functions-getfield.html "getField\(\)") can be used with the quoted name, like `coalesce([host, getField("host-name")])`. 

For more information, see [Field Names in Expressions](syntax-expressions.html#syntax-expressions-field-names "Field Names in Expressions"). 

### [`text:startsWith()`](functions-text-startswith.html "text:startsWith\(\)") Examples

Click + next to an example below to get the full details.

#### Exclude Servers Beginning With Specific Prefix

**Filter out servers that begin with a specific prefix using the[`text:startsWith()`](functions-text-startswith.html "text:startsWith\(\)") function with negation **

##### Query

logscale
    
    
    !text:startsWith(string=hostname, substring="web-")

##### Introduction

In this example, the negated [`text:startsWith()`](functions-text-startswith.html "text:startsWith\(\)") function is used to filter out events where the hostname begins with `web-`, showing all non-web servers. 

Example incoming data might look like this: 

@timestamp| hostname| status| region  
---|---|---|---  
2023-06-06T10:00:00Z| web-server-01| running| us-east  
2023-06-06T10:00:01Z| webapp-prod-02| stopped| us-west  
2023-06-06T10:00:02Z| db-server-03| running| eu-west  
2023-06-06T10:00:03Z| web-prod-04| running| us-east  
2023-06-06T10:00:04Z| app-server-05| stopped| eu-west  
2023-06-06T10:00:05Z| web-test-06| running| us-west  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         !text:startsWith(string=hostname, substring="web-")

Filters events where the value in the hostname field does NOT start with `web-`. 

The exclamation mark (!) negates the function, inverting the match. The [_`string`_](functions-text-startswith.html#query-functions-text-startswith-string) parameter specifies the field to check, and the [_`substring`_](functions-text-startswith.html#query-functions-text-startswith-substring) parameter defines the prefix to exclude. The comparison remains case-sensitive. 

  3. Event Result set.




##### Summary and Results

The query is used to filter events by excluding servers with specific naming conventions, showing all non-web servers. 

This query is useful, for example, to monitor all backend infrastructure excluding web servers, analyze events from supporting services, or focus on specific server types by excluding others. 

Sample output from the incoming example data: 

@timestamp| hostname| status| region  
---|---|---|---  
2023-06-06T10:00:01Z| webapp-prod-02| stopped| us-west  
2023-06-06T10:00:02Z| db-server-03| running| eu-west  
2023-06-06T10:00:04Z| app-server-05| stopped| eu-west  
  
Note that all events where hostname does NOT begin with `web-` are included in the results. The negation excludes only exact matches of the prefix `web-`. 

#### Filter Hostnames Beginning With Specific Prefix

**Match server names that begin with a specific prefix using the[`text:startsWith()`](functions-text-startswith.html "text:startsWith\(\)") function **

##### Query

logscale
    
    
    text:startsWith(string=hostname, substring="web-")

##### Introduction

In this example, the [`text:startsWith()`](functions-text-startswith.html "text:startsWith\(\)") function is used to filter events where the hostname begins with `web-`, a common prefix for web servers. 

Example incoming data might look like this: 

@timestamp| hostname| status| region  
---|---|---|---  
2023-06-06T10:00:00Z| web-server-01| running| us-east  
2023-06-06T10:00:01Z| webapp-prod-02| stopped| us-west  
2023-06-06T10:00:02Z| db-server-03| running| eu-west  
2023-06-06T10:00:03Z| web-prod-04| running| us-east  
2023-06-06T10:00:04Z| app-server-05| stopped| eu-west  
2023-06-06T10:00:05Z| web-test-06| running| us-west  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         text:startsWith(string=hostname, substring="web-")

Filters events where the value in the hostname field starts with `web-`. 

The [_`string`_](functions-text-startswith.html#query-functions-text-startswith-string) parameter specifies the field to check, and the [_`substring`_](functions-text-startswith.html#query-functions-text-startswith-substring) parameter defines the prefix to match. The function performs a case-sensitive comparison. 

  3. Event Result set.




##### Summary and Results

The query is used to filter events based on server naming conventions, specifically identifying web-related servers. 

This query is useful, for example, to monitor specific server types in your infrastructure, analyze events from web servers, or filter logs based on standardized naming patterns. 

Sample output from the incoming example data: 

@timestamp| hostname| status| region  
---|---|---|---  
2023-06-06T10:00:00Z| web-server-01| running| us-east  
2023-06-06T10:00:03Z| web-prod-04| running| us-east  
2023-06-06T10:00:05Z| web-test-06| running| us-west  
  
Note that only events where hostname begins with `web-` are included in the results. The match is case-sensitive, so hostnames starting with `WEB-` would not be included.

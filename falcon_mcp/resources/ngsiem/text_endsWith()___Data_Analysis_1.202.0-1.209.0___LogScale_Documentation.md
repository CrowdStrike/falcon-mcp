# text:endsWith() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-text-endswith.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Page was created:Jul 29, 2025

## [`text:endsWith()`](functions-text-endswith.html "text:endsWith\(\)")

The [`text:endsWith()`](functions-text-endswith.html "text:endsWith\(\)") function compares two strings and evaluates whether one string ends with another string. 

[`text:endsWith()`](functions-text-endswith.html "text:endsWith\(\)") takes two arguments: [_`string`_](functions-text-endswith.html#query-functions-text-endswith-string) and [_`substring`_](functions-text-endswith.html#query-functions-text-endswith-substring), both of which can be provided as plain text, field values, or results of an expression. 

Similar to the [`test()`](functions-test.html "test\(\)") function, [`text:endsWith()`](functions-text-endswith.html "text:endsWith\(\)") returns the events where the condition is met. The function can be negated to find the events, where the substring is not found in the main string. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`string`_](functions-text-endswith.html#query-functions-text-endswith-string)[a]| expression| required |  |  The string in which the ending substring is matched.   
[_`substring`_](functions-text-endswith.html#query-functions-text-endswith-substring)|  expression| required |  |  The substring which is matched at the end of the corresponding [_`string`_](functions-text-endswith.html#query-functions-text-endswith-string) parameter. It specifies the characters to match at the end of the string.   
[a] The parameter name [_`string`_](functions-text-endswith.html#query-functions-text-endswith-string) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`string`_](functions-text-endswith.html#query-functions-text-endswith-string) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     text:endsWith("value",substring="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     text:endsWith(string="value",substring="value")
> 
> These examples show basic structure only.

### [`text:endsWith()`](functions-text-endswith.html "text:endsWith\(\)") Syntax Examples

Filter events where a field value ends with a string (having the string as a field and the substring as a value): 

This example finds all events where subdomains of a certain url were called. 

logscale
    
    
    text:endsWith(string=url, substring="crowdstrike.com")

If input data was `url=crowdstrike.com`, `url=app.crowdstrike.com`, `url=bitbucket.com`, `url=app.bitbucket.com`, it would return: 

url  
---  
crowdstrike.com  
app.crowdstrike.com  
  
Filter events where a field value is the suffix at the start of `logscale` (having the string as a value and the substring as a field): 

This example finds all events with domain matching a given url. 

logscale
    
    
    text:endsWith(string="app.crowdstrike.com", substring=domain))

If input data was `domain=crowdstrike.com`, `domain=bitbucket.com`, `domain=github.com`, it would return: 

domain  
---  
crowdstrike.com  
  
Filter events where a field value does not end with a string (using negation): 

This example filters out events where a certain url was accessed. 

logscale
    
    
    !text:endsWith(string=url, substring="crowdstrike.com")

If input data was `url=crowdstrike.com`, `url=app.crowdstrike.com`, `url=bitbucket.com`, `url=app.bitbucket.com`, it would return: 

url  
---  
bitbucket.com  
app.bitbucket.com  
  
Filter events where the evaluated value of an expression ends with a given string: 

This example finds all events where executables with a certain name were accessed. 

logscale
    
    
    text:endsWith(string=lower(commandline), substring="killtask.exe")

If input data was `commandline=C:\\Windows\\System32\KillTask.exe`, `commandline=C:\\Windows\\System32\killtask.exe`, `commandline=C:\\MyDocuments\powerpoint.exe`, it would return: 

commandline  
---  
C:\\\Windows\\\System32\KillTask.exe  
C:\\\Windows\\\System32\killtask.exe  
  
### Note

In expressions, quotation marks always mean a string value, while unquoted field names always mean the value of that field. 

To use the value of a field with such a name in an expression, the function [`getField()`](functions-getfield.html "getField\(\)") can be used with the quoted name, like `coalesce([host, getField("host-name")])`. 

For more information, see [Field Names in Expressions](syntax-expressions.html#syntax-expressions-field-names "Field Names in Expressions"). 

### [`text:endsWith()`](functions-text-endswith.html "text:endsWith\(\)") Examples

Click + next to an example below to get the full details.

#### Exclude Production Servers Ending With Specific Prefix

**Filter out servers that end with the production suffix using the[`text:endsWith()`](functions-text-endswith.html "text:endsWith\(\)") function with negation **

##### Query

logscale
    
    
    !text:endsWith(string=hostname, substring="prod")

##### Introduction

In this example, the negated [`text:endsWith()`](functions-text-endswith.html "text:endsWith\(\)") function is used to filter out events where the hostname ends with `prod`, showing all non-production servers. 

Example incoming data might look like this: 

@timestamp| hostname| status| region  
---|---|---|---  
2023-06-06T10:00:00Z| web-server-prod| running| us-east  
2023-06-06T10:00:01Z| db-prod| stopped| us-west  
2023-06-06T10:00:02Z| app-server-dev| running| eu-west  
2023-06-06T10:00:03Z| cache-prod| running| us-east  
2023-06-06T10:00:04Z| api-server-test| stopped| eu-west  
2023-06-06T10:00:05Z| queue-prod| running| us-west  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         !text:endsWith(string=hostname, substring="prod")

Filters events where the value in the hostname field does NOT end with `prod`. 

The exclamation mark (!) negates the function, inverting the match. The [_`string`_](functions-text-endswith.html#query-functions-text-endswith-string) parameter specifies the field to check, and the [_`substring`_](functions-text-endswith.html#query-functions-text-endswith-substring) parameter defines the suffix to exclude. The comparison remains case-sensitive. 

  3. Event Result set.




##### Summary and Results

The query is used to filter events by excluding production servers, showing only development and test environments. 

This query is useful, for example, to monitor non-production infrastructure, analyze events from development and test environments, or focus on pre-production testing activities. 

Sample output from the incoming example data: 

@timestamp| hostname| status| region  
---|---|---|---  
2023-06-06T10:00:02Z| app-server-dev| running| eu-west  
2023-06-06T10:00:04Z| api-server-test| stopped| eu-west  
  
Note that all events where hostname does NOT end with `prod` are included in the results. This effectively shows only development and test servers. The negation excludes any hostname that ends exactly with `prod`, regardless of what comes before it. 

#### Filter Servers Ending With Specific suffix

**Match server names that end with a specific environment suffix using the[`text:endsWith()`](functions-text-endswith.html "text:endsWith\(\)") function **

##### Query

logscale
    
    
    text:endsWith(string=hostname, substring="prod")

##### Introduction

In this example, the [`text:endsWith()`](functions-text-endswith.html "text:endsWith\(\)") function is used to filter events where the hostname ends with `prod`, identifying production servers. 

Example incoming data might look like this: 

@timestamp| hostname| status| region  
---|---|---|---  
2023-06-06T10:00:00Z| web-server-prod| running| us-east  
2023-06-06T10:00:01Z| db-prod| stopped| us-west  
2023-06-06T10:00:02Z| app-server-dev| running| eu-west  
2023-06-06T10:00:03Z| cache-prod| running| us-east  
2023-06-06T10:00:04Z| api-server-test| stopped| eu-west  
2023-06-06T10:00:05Z| queue-prod| running| us-west  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         text:endsWith(string=hostname, substring="prod")

Filters events where the value in the hostname field ends with `prod`. 

The [_`string`_](functions-text-endswith.html#query-functions-text-endswith-string) parameter specifies the field to check, and the [_`substring`_](functions-text-endswith.html#query-functions-text-endswith-substring) parameter defines the suffix to match. The function performs a case-sensitive comparison. 

  3. Event Result set.




##### Summary and Results

The query is used to filter events based on server environment suffixes, specifically identifying production servers. 

This query is useful, for example, to monitor production infrastructure, analyze events from production environments, or filter logs based on server environment types. 

Sample output from the incoming example data: 

@timestamp| hostname| status| region  
---|---|---|---  
2023-06-06T10:00:00Z| web-server-prod| running| us-east  
2023-06-06T10:00:01Z| db-prod| stopped| us-west  
2023-06-06T10:00:03Z| cache-prod| running| us-east  
2023-06-06T10:00:05Z| queue-prod| running| us-west  
  
Note that only events where hostname ends with `prod` are included in the results. The match is case-sensitive, so hostnames ending with `PROD` would not be included. This pattern matches common server naming conventions where the environment is indicated as a suffix.

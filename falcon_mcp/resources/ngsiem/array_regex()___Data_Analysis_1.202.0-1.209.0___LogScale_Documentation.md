# array:regex() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-regex.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:regex()`](functions-array-regex.html "array:regex\(\)")

Checks whether the given pattern matches any of the values of the array and excludes the event from the search result if it does not match on any value. 

### Note

To ensure compatibility, it is recommended to always test your regular expressions inside LogScale, instead of a 3rd party regex tool. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-regex.html#query-functions-array-regex-array)[a]| string| required |  |  A string in the format of a valid array index `[]`. A valid array can either be an identifier, a valid array followed by `.` and an identifier, or a valid array followed by an array index surrounded by square brackets. For example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents[]` .   
[_`flags`_](functions-array-regex.html#query-functions-array-regex-flags)|  string| optional[b] |  |  The regex modifier flags to use.   
|  |  | **Values**  
|  |  | [`F`](functions-array-regex.html#query-functions-array-regex-flags-value-f)| Use the LogScale Regex Engine v2  
|  |  | [`d`](functions-array-regex.html#query-functions-array-regex-flags-value-d)| Period (.) also includes newline characters  
|  |  | [`i`](functions-array-regex.html#query-functions-array-regex-flags-value-i)| Ignore case for matched values  
|  |  | [`m`](functions-array-regex.html#query-functions-array-regex-flags-value-m)| Multi-line parsing of regular expressions  
[ _`regex`_](functions-array-regex.html#query-functions-array-regex-regex)|  regex| required |  |  The regex pattern for the value on which to search the array.   
[a] The parameter name [_`array`_](functions-array-regex.html#query-functions-array-regex-array) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-regex.html#query-functions-array-regex-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:regex("value",regex="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:regex(array="value",regex="value")
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
>     !array:regex()
> 
> Or:
> 
> logscale Syntax
>     
>     
>     not array:regex()
> 
> For more information, see [Negating the Result of Filter Functions](syntax-operators.html#syntax-operators-negate "Negating the Result of Filter Functions").

A specific syntax applies for this query function, see [Array Syntax](syntax-array.html "Array Syntax") for details. 

### [`array:regex()`](functions-array-regex.html "array:regex\(\)") Examples

Click + next to an example below to get the full details.

#### Find Matches in Array Given a Regular Expression - Example 1

**Use regular expressions to search for and match specific patterns in flat arrays**

##### Query

logscale
    
    
    array:regex("incidents[]", regex="^Cozy Bear.*")
    | groupBy(host)

##### Introduction

In this example, the regular expression is used to search for patterns where the value `Cozy Bear` appears in a certain position across arrays. 

Example incoming data might look like this: 

host| incidents[0]| incidents[1]| incidents[2]  
---|---|---|---  
v1| Evil Bear| Cozy Bear|   
v15| Fancy Fly| Tiny Cat| Cozy Bears  
v22| Fancy Fly| Tiny Cat| Cold Bears  
v4| Fancy Fly| Tiny Cat| Cozy Bearskins  
v1| Evil Bear| Cozy Bears|   
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:regex("incidents[]", regex="^Cozy Bear.*")

Searches in the incidents array for values that only start with `Cozy Bear`. Find all matches given that regular expression. 

  3. logscale
         
         | groupBy(host)

Groups the returned results by host. 

  4. Event Result set.




##### Summary and Results

The query using the regex expression are used to quickly search and return results for specific values in arrays. Regular expressions are useful when searching for different strings containing the same patterns; such as social security numbers, URLs, email addresses, and other strings that follow a specific pattern. 

Sample output from the incoming example data: 

host| _count  
---|---  
v1| 2  
v15| 1  
v4| 1  
  
#### Find Matches in Array Given a Regular Expression - Example 2

**Use regular expressions to search for and match specific patterns ignoring case in flat arrays**

##### Query

logscale
    
    
    array:regex("responses[]", regex="bear$", flags="i")

##### Introduction

In this example, the regular expression is used to search for patterns where the value `bear` appears at the end of a value in an array element, ignoring the case. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:regex("responses[]", regex="bear$", flags="i")

Searches in the responses array for values that begins with `bear`, ignoring the case (due to the [`i`](functions-array-regex.html#query-functions-array-regex-flags-value-i) flag). 

  3. Event Result set.




##### Summary and Results

The queries using the regex expression are used to quickly search and return results for specific values in arrays. Regular expressions are useful when searching for different strings containing the same patterns; such as social security numbers, URLs, email addresses, and other strings that follow a specific pattern.

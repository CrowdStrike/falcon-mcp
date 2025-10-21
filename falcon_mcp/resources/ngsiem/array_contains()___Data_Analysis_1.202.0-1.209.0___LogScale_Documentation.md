# array:contains() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-contains.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:contains()`](functions-array-contains.html "array:contains\(\)")

Checks whether the given value matches any of the values of the array and excludes the event from the search result if it does not match any value. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-contains.html#query-functions-array-contains-array)[a]| string| required |  |  A string in the format of a valid array followed by `[]`. A valid array can either be an identifier, a valid array followed by `.` and an identifier, or a valid array followed by an array index surrounded by square brackets. For example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents[]`.   
[_`value`_](functions-array-contains.html#query-functions-array-contains-value)|  string| required |  |  The exact value of the array to search for.   
[a] The parameter name [_`array`_](functions-array-contains.html#query-functions-array-contains-array) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-contains.html#query-functions-array-contains-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:contains("value",value="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:contains(array="value",value="value")
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
>     !array:contains()
> 
> Or:
> 
> logscale Syntax
>     
>     
>     not array:contains()
> 
> For more information, see [Negating the Result of Filter Functions](syntax-operators.html#syntax-operators-negate "Negating the Result of Filter Functions").

A specific syntax applies for this query function, see [Array Syntax](syntax-array.html "Array Syntax") for details. 

### [`array:contains()`](functions-array-contains.html "array:contains\(\)") Examples

Click + next to an example below to get the full details.

#### Aggregate Array Content

****

##### Query

logscale
    
    
    array:contains("incidents[]", value="Cozy Bear")
    | groupBy(host)

##### Introduction

Given events containing an `incidents` array: 

Event 1 
    
    
    |--------------|-------------|
    | host         | v1          |
    | incidents[0] | Evil Bear   |
    | incidents[1] | Cozy Bear   |
    |--------------|-------------|

Event 2 
    
    
    |--------------|-------------|
    | host         | v15         |
    | incidents[0] | Fancy Fly   |
    | incidents[1] | Tiny Cat    |
    | incidents[2] | Cozy Bears  |
    |--------------|-------------|

Finds all the events where the field incidents contains the exact value `Cozy Bear` and group them by which hosts were affected, giving output event: 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:contains("incidents[]", value="Cozy Bear")

Extracts elements from the array incidents from the field host that match the text `Cozy Bear`. The items will be output into the host field. 

  3. logscale
         
         | groupBy(host)

Groups the result events extracted from the array by the host. 

  4. Event Result set.




##### Summary and Results

The result is an aggregated count of the array elements matching `Cozy Bear`. 

field| value  
---|---  
host| v1  
_count| 1  
  
#### Check for Values in Array

**Use array query filter[`array:contains()`](functions-array-contains.html "array:contains\(\)") to check for a value in a flat array **

##### Query

logscale
    
    
    array:contains("incidents[]", value="Cozy Bear")

##### Introduction

In this example, the [`array:contains()`](functions-array-contains.html "array:contains\(\)") function is used to check if a given value exists in a given array. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:contains("incidents[]", value="Cozy Bear")

Checks if the value of `Cozy Bear` exists within the incidents array field. If the array contains the value, the whole event is included in the search result. 

  3. Event Result set.




##### Summary and Results

The query is used as a filter to check if a given value exists in a given array within the event set. If the given value does not match any of the values of the array, then the event is excluded from the search result. Arrays are used when ingesting security event logs where fields may have more than one value. If the array contains other values along with the specified value, these are also included in the search results.

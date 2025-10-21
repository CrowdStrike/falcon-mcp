# array:append() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-append.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Jul 15, 2024

## [`array:append()`](functions-array-append.html "array:append\(\)")

Appends single or multiple values to an array, or creates a new array if it does not already exist. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-append.html#query-functions-array-append-array)[a]| string| required |  |  Name of the array to append values to. Must follow valid [Array Syntax](syntax-array.html "Array Syntax") for array of scalars. For example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents[]`.   
[_`values`_](functions-array-append.html#query-functions-array-append-values)|  array of expressions| required |  |  The list of expressions to be appended.   
[a] The parameter name [_`array`_](functions-array-append.html#query-functions-array-append-array) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-append.html#query-functions-array-append-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:append("foo[]",values=[a,b,c])
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:append(array="foo[]",values=[a,b,c])
> 
> These examples show basic structure only.

### [`array:append()`](functions-array-append.html "array:append\(\)") Syntax Examples

The syntax for [`array:append()`](functions-array-append.html "array:append\(\)") looks like this: 

logscale Syntax
    
    
    array:append(array="foo[]", values=[exp_1, … exp_n])

where [`array:append()`](functions-array-append.html "array:append\(\)") is used to either append the values of `exp_1` to `exp_n` at the end of the `foo[]` array, or create a new array of these values if the array `foo[]` is not present in the event. If one of the expressions does not evaluate to a value, then that expression is skipped. 

[`array:append()`](functions-array-append.html "array:append\(\)") requires that the input array has continuous, sequential indexes with no gaps. If there are gaps (that is, missing indexes), the function will start inserting new values at the first missing index, potentially overwriting existing elements. For example, having a missing index like in: 
    
    
    |-----------------|
    |array[0]  | foo  |
    |array[1]  | bar  |
    |array[3]  | baz  |
    |-----------------|

the query: 

logscale
    
    
    array:append("array[]", values=["x", "y", "z"])

will produce the following output: 

field| value  
---|---  
array[0]| foo  
array[1]| bar  
array[2]| x  
array[3]| y  
array[4]| z  
  
Showing that array[3] has been overwritten. 

### [`array:append()`](functions-array-append.html "array:append\(\)") Examples

Click + next to an example below to get the full details.

#### Create New Array by Appending Expressions

**Create a new flat array by appending new expressions using the[`array:append()`](functions-array-append.html "array:append\(\)") function **

##### Query

logscale
    
    
    array:append(array="related.user[]", values=[lower(source.user.name), lower(destination.user.name)])

##### Introduction

In this example, the [`array:append()`](functions-array-append.html "array:append\(\)") function is used to create a new array related.user[] containing information about all user names seen on the event. 

Example incoming data might look like this: 
    
    
    source.user.name="user_1" destination.user.name="USER_2"

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:append(array="related.user[]", values=[lower(source.user.name), lower(destination.user.name)])

Creates a new array related.user[] containing information about all user names seen on the event. Notice that the [`lower()`](functions-lower.html "lower\(\)") function formats the results into lower case before appending them to the array. 

  3. Event Result set.




##### Summary and Results

This query is used to create a new flat array based on values from an array of expressions. 

Sample output from the incoming example data: 

source.user.name| destination.user.name| related.user[0]| related.user[1]|   
---|---|---|---|---  
user_1| USER_2| user_1| user_2|   
  
#### Split Comma-Separated Strings in Array Into New Array

**Split comma-separated strings in array into new flat array and extend with new values using the[`array:append()`](functions-array-append.html "array:append\(\)") function **

##### Query

logscale
    
    
    splitString(field=numbers,by=",",as=numbarr)
    | array:append(array="numbarr[]", values=[4])

##### Introduction

The [`array:append()`](functions-array-append.html "array:append\(\)") function can be used to create a new array based on values from another flat array, provided that the input array has continuous, sequential indexes with no missing indexes. 

Example incoming data might look like this: 
    
    
    |-----------------------|
    | numbers   | "1,2,3"   |
    |-----------------------|

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         splitString(field=numbers,by=",",as=numbarr)
         | array:append(array="numbarr[]", values=[4])

Splits the comma-separated strings in the field numbers into a new array named numbarr[], and then extends this array with new values. 

  3. Event Result set.




##### Summary and Results

This query is used to create a new flat array based on values from another flat array, 

Sample output from the incoming example data: 

numbarr[0]| numbarr[1]| numbarr[2]| numbarr[3]  
---|---|---|---  
1| 2| 3| 4

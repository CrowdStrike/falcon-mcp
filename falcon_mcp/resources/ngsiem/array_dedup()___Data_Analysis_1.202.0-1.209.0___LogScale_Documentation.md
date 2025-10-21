# array:dedup() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-dedup.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:dedup()`](functions-array-dedup.html "array:dedup\(\)")

This function removes duplicate values from an array. The ordering of the first occurrence of each unique element is preserved. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-dedup.html#query-functions-array-dedup-array)[a]| array| required |  |  The array to deduplicate elements in.   
[_`asArray`_](functions-array-dedup.html#query-functions-array-dedup-asarray)|  string| optional[b] | `input array`|  Where to output the deduplicated array.   
[a] The parameter name [_`array`_](functions-array-dedup.html#query-functions-array-dedup-array) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-dedup.html#query-functions-array-dedup-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:dedup("foo[]")
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:dedup(array="foo[]")
> 
> These examples show basic structure only.

For instance, given a rawstring with array a[]: 

Raw Events

{ "a":["horse", "fish", "horse", "cow", "cow"] }  
---  
  
Specify the name of the array field from which to remove duplicates: 

logscale
    
    
    parseJson()
    | array:dedup("a[]")

The duplicate item will be removed: 

a[0]| a[1]| a[2]  
---|---|---  
horse| fish| cow  
  
### [`array:dedup()`](functions-array-dedup.html "array:dedup\(\)") Examples

Click + next to an example below to get the full details.

#### Deduplicate Values in Array

**Remove duplicate values in an array using[`array:dedup()`](functions-array-dedup.html "array:dedup\(\)") **

##### Query

logscale
    
    
    parseJson()
    | array:dedup("emails[]")

##### Introduction

In this example, the function removes duplicates in the array emails[]. 

Example incoming data might look like this: 

Raw Events

{"emails": ["john@mail.com", "admin@mail.com", "jane@mail.com", "admin@mail.com"]}  
---  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         parseJson()

Parses the incoming data to identify JSON values and converts them into a usable field. 

  3. logscale
         
         | array:dedup("emails[]")

Removes duplicate values in the array emails[]. 

  4. Event Result set.




##### Summary and Results

The query is used to remove duplicate values in an array. 

Sample output from the incoming example data: 

emails[0]| emails[1]| emails[2]  
---|---|---  
john@mail.com| admin@mail.com| jane@mail.com

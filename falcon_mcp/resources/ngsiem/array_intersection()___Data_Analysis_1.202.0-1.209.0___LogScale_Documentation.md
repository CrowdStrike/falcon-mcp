# array:intersection() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-intersection.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:intersection()`](functions-array-intersection.html "array:intersection\(\)")

### Important

This function must be enabled using the feature flag ArrayFunctions. See [Enabling & Disabling Feature Flags](https://library.humio.com/deployment/configuration-enabling-features.html). 

Did you find this function useful? We are soliciting feedback on this function. Please use [this form](https://docs.google.com/forms/d/e/1FAIpQLSct98ofJ_tASEdzenwJiuNTVlkgK-wCpKgGjKWyKYnZCxvC_Q/viewform) to provide input about how you've used the function and whether it met your needs. 

Determines the set intersection of array values over input events. Use this to compute the values that occur in all events supplied to this function. 

  * The output order of the values is not defined. 

  * Empty arrays are ignored. 

  * If no arrays are found, the output is empty. 




Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-intersection.html#query-functions-array-intersection-array)[a]| string| required |  |  The prefix of the array in LogScale, for example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents`.   
[_`as`_](functions-array-intersection.html#query-functions-array-intersection-as)|  string| optional[b] | `_intersection`|  The name of the output array.   
[a] The parameter name [_`array`_](functions-array-intersection.html#query-functions-array-intersection-array) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-intersection.html#query-functions-array-intersection-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:intersection("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:intersection(array="value")
> 
> These examples show basic structure only.

### [`array:intersection()`](functions-array-intersection.html "array:intersection\(\)") Examples

Click + next to an example below to get the full details.

#### Find Set Intersection Within an Array

**Find set intersection within a single flat array using the[`array:intersection()`](functions-array-intersection.html "array:intersection\(\)") function **

##### Query

logscale
    
    
    array:intersection("mailto[]", as=unique_mails)

##### Introduction

In this example, the [`array:intersection()`](functions-array-intersection.html "array:intersection\(\)") function will return the unique email addresses from an array. The intersection of the array is based on the intersection of unique values within each element. 

Example incoming data might look like this: 

logscale
    
    
    mailto[0]=foo@example.com
    mailto[1]=bar@example.com
    mailto[2]=bar@example.com

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:intersection("mailto[]", as=unique_mails)

Returns the intersection of element values in the array mailto[], in this case email addresses, storing the result in a new intersection set array unique_mails and stores them as unique values. 

  3. Event Result set.




##### Summary and Results

The result of the intersection operation is a new dataset that consists of all the common elements occurring in an array. The query is used to simplify data in an array for any common values and make a new array with only the unique values in it. This can be useful when processing a set of values and looking for the unique list, for example to use as labels within a graph, or as input parameters to a filter. 

Sample output from the incoming example data: 

logscale
    
    
    unique_mails[0]=foo@example.com
    unique_mails[1]=bar@example.com

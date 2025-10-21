# array:drop() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-drop.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:drop()`](functions-array-drop.html "array:drop\(\)")

This function takes the name of an array and drops all fields of this array. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-drop.html#query-functions-array-drop-array)[a]| string| required |  |  Name of the array to drop values for. Must follow valid [Array Syntax](syntax-array.html "Array Syntax") for array of scalars. For example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents[]`.   
[a] The parameter name [_`array`_](functions-array-drop.html#query-functions-array-drop-array) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-drop.html#query-functions-array-drop-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:drop("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:drop(array="value")
> 
> These examples show basic structure only.

### [`array:drop()`](functions-array-drop.html "array:drop\(\)") Function Operation

[`array:drop()`](functions-array-drop.html "array:drop\(\)") requires that the input array has continuous, sequential indexes with no gaps (empty indexes) and that the array starts at index [0], for example, incidents[0], incidents[1], incidents[2]. If there are gaps, for example, incidents[0], incidents[1], incidents[2], incidents[10] only the fields from index 0 up to the first empty index will be dropped. 

If no array with the given name exists, the function does nothing. 

Without this function, each element of an array would need to be dropped individually using [`drop()`](functions-drop.html "drop\(\)") or [`array:filter()`](functions-array-filter.html "array:filter\(\)") as shown below: 

logscale
    
    
    array:filter(array="a[]", function={false}, var="")

With the function, specify the name of the array field to drop: 

logscale
    
    
    array:drop("a[]")

**Validation** : 

The array parameter is validated to ensure the field is an array value. 

### [`array:drop()`](functions-array-drop.html "array:drop\(\)") Examples

Click + next to an example below to get the full details.

#### Drop Fields From Input Array

**Drop fields in an array using the[`array:drop()`](functions-array-drop.html "array:drop\(\)") function **

##### Query

logscale
    
    
    array:drop("a[]")

##### Introduction

In this example, the [`array:drop()`](functions-array-drop.html "array:drop\(\)") function is used to drop all fields of the array a[]. 

Example incoming data might look like this: 

a[0]=Dog  
---  
a[1]=Cat  
a[42]=Horse  
a[0]=Dog  
b[0]=Cat  
c[0]=Horse  
animal=cow  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:drop("a[]")

Takes the name of the array a[] and drops all fields of this array. Array b[] and array c[] will not be dropped in this example. Be aware that if there are empty entries in the array, only the fields from index 0 up to the first empty index will be dropped. 

  3. Event Result set.




##### Summary and Results

The query is used to drop all fields from a specific input array. 

Sample output from the incoming example data: 

b[0]| c[0]| animal  
---|---|---  
Cat| Horse| cow

# array:rename() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-rename.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:rename()`](functions-array-rename.html "array:rename\(\)")

This function takes the name of an array and renames all fields of this array. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-rename.html#query-functions-array-rename-array)[a]| string| required |  |  Name of the array to rename. Must follow valid [Array Syntax](syntax-array.html "Array Syntax") for array of scalars. For example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents[]`.   
[_`asArray`_](functions-array-rename.html#query-functions-array-rename-asarray)|  string| required |  |  The new name of the array. Must follow valid [Array Syntax](syntax-array.html "Array Syntax") for array of scalars.   
[a] The parameter name [_`array`_](functions-array-rename.html#query-functions-array-rename-array) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-rename.html#query-functions-array-rename-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:rename(""value"[]",asArray="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:rename(array=""value"[]",asArray="value")
> 
> These examples show basic structure only.

### [`array:rename()`](functions-array-rename.html "array:rename\(\)") Function Operation

[`array:rename()`](functions-array-rename.html "array:rename\(\)") requires that the input array has continuous, sequential indexes with no gaps (empty indexes) and that the array starts at index 0 (`array[0]`), for example a series of items in an array would include `incidents[0], incidents[1], incidents[2]`. If there are gaps in the source array, for example, `incidents[0], incidents[1], incidents[2], incidents[10]` only the fields from index 0 up to the first empty index will be renamed. 

If no array with the given name exists or the old and the new name are the same, the function does nothing. 

Without this function, each element of an array would need to be renamed individually with the [`rename()`](functions-rename.html "rename\(\)") function, or [`array:filter()`](functions-array-filter.html "array:filter\(\)") should be used as a workaround as shown below: 

logscale
    
    
    array:filter(array="a[]", function={true}, var="", asArray="b[]")
    | array:filter(array="a[]", function={false}, var="")

With the function, specify the name of the array to rename: 

logscale
    
    
    array:rename("a[]", asArray="b[]")

### [`array:rename()`](functions-array-rename.html "array:rename\(\)") Examples

Click + next to an example below to get the full details.

#### Rename Existing Fields in Array

**Rename existing fields in an array using the[`array:rename()`](functions-array-rename.html "array:rename\(\)") function **

##### Query

logscale
    
    
    array:rename(array="mail[]", asArray="user.email[]")

##### Introduction

In this example, the [`array:rename()`](functions-array-rename.html "array:rename\(\)") function is used to rename the array mail[] as user.email[]. 

Example incoming data might look like this: 
    
    
    'mail[0]'='user0@example.com'
    'mail[1]'='user1@example.com'
    'mail[2]'='user2@example.com'

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:rename(array="mail[]", asArray="user.email[]")

Renames the array mail[] as user.email[]. If there are empty entries in the array, only the fields from index 0 up to the first empty index will be renamed. If an array with the new name already exists, it will be overwritten. 

  3. Event Result set.




##### Summary and Results

The query is used to rename fields in an array. Renaming the mail[] array is useful when, for example, modifying vendor logs email addresses into ECS data model is needed. 

Sample output from the incoming example data: 
    
    
    user.email[0]->user0@example.com
    user.email[1]->user1@example.com
    user.email[2]->user2@example.com

# concatArray() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-concatarray.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`concatArray()`](functions-concatarray.html "concatArray\(\)")

Concatenates the values of all fields with the same name and an array suffix into a value in a new field. Such array fields typically come as output from either [`parseJson()`](functions-parsejson.html "parseJson\(\)") or [`splitString()`](functions-splitstring.html "splitString\(\)"). 

All array fields starting with index from and ending with index to are selected. If some index is missing, the concatenation stops with the previous index, thus if only index 0, 1 and 3 are present, only index 0 and 1 are concatenated. If the first index is missing, no field is added to the event. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-concatarray.html#query-functions-concatarray-as)|  string| optional[a] | `_concatArray`|  Name of output field.   
[_`field`_](functions-concatarray.html#query-functions-concatarray-field)[b]| string| required |  |  Base name for array fields to concatenate.   
[_`from`_](functions-concatarray.html#query-functions-concatarray-from)|  number| optional[[a]](functions-concatarray.html#ftn.table-functions-concatarray-optparamfn) | `0`|  First array index to include [0..∞].   
[_`prefix`_](functions-concatarray.html#query-functions-concatarray-prefix)|  string| optional[[a]](functions-concatarray.html#ftn.table-functions-concatarray-optparamfn) |  |  Prefix to prepend to the generated string.   
[_`separator`_](functions-concatarray.html#query-functions-concatarray-separator)|  string| optional[[a]](functions-concatarray.html#ftn.table-functions-concatarray-optparamfn) |  |  Separator between values.   
[_`suffix`_](functions-concatarray.html#query-functions-concatarray-suffix)|  string| optional[[a]](functions-concatarray.html#ftn.table-functions-concatarray-optparamfn) |  |  Suffix to append to the generated string.   
[_`to`_](functions-concatarray.html#query-functions-concatarray-to)|  number| optional[[a]](functions-concatarray.html#ftn.table-functions-concatarray-optparamfn) |  |  Last array index to include (leave out to get all). Must be equal to or larger than [_`from`_](functions-concatarray.html#query-functions-concatarray-from).   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-concatarray.html#query-functions-concatarray-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-concatarray.html#query-functions-concatarray-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     concatArray("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     concatArray(field="value")
> 
> These examples show basic structure only.

### [`concatArray()`](functions-concatarray.html "concatArray\(\)") Examples

Click + next to an example below to get the full details.

#### Concatenate Values From Deeply Nested Array Elements

**Concatenate deeply nested objects and arrays using[`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function with itself **

##### Query

logscale
    
    
    objectArray:eval(
            "in[]",
            asArray="out[]",
            function={
    objectArray:eval("in.others[]", asArray="tmp[]", function={tmp := "in.others.d"})
    | out := concatArray(tmp)
              }
              )

##### Introduction

In this example, the [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function is used with itself to concatenate a deeply nested arrays of objects values in the array in[] and return the concatenated values in the output field out[]. 

Example incoming data might look like this: 

in[0].others[0].d: 1  
---  
in[0].others[1].d: 2  
in[0].others[2].d: 3  
in[1].others[0].d: 4  
in[1].others[1].d: 5  
in[1].others[2].d: 6  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         objectArray:eval(
                 "in[]",
                 asArray="out[]",
                 function={

Iterates over the array from start to end (or to the first empty index in the array, applies the given function, and returns the concatenated results in a new output array name field out[]. 

  3. logscale
         
         objectArray:eval("in.others[]", asArray="tmp[]", function={tmp := "in.others.d"})
         | out := concatArray(tmp)
                   }
                   )

The nested [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") performs the concatenation of the values within the nested array by calling the [`concatArray()`](functions-concatarray.html "concatArray\(\)") function. 

Notice that in the nested call to [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)"), the given input array name is the nested array in.others[]. This works because it is translated to the field in[i].others[] by the parent [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") current array index `i`. 

To return the concatenated array, the [_`asArray`_](functions-objectarray-eval.html#query-functions-objectarray-eval-asarray) parameter is set to the tmp[] field, and then when we assign the value of the concatenated value. 

  4. Event Result set.




##### Summary and Results

The query is used to concatenate deeply nested arrays of objects. The use of this function in this way is often useful when incoming ingested data has been defined in a nested structure, but needs to be displayed or summarized. For example, importing the properties or configuration values may result in a list of potential values for a given property. Concatenating the values together makes them easier to use as a summary value for display in a table or graph. 

Sample output from the incoming example data: 
    
    
    out[0]: 123
    out[1]: 456

#### Concatenate Values in Arrays Into New Named Field

**Concatenate values in flat arrays into new named field**

##### Query

logscale
    
    
    concatArray("email", as=servers)

##### Introduction

In this example, the [`concatArray()`](functions-concatarray.html "concatArray\(\)") function concatenates the values of all fields with the same name into a value in a new defined field. 

Example incoming data might look like this: 
    
    
    email[0] := "dopey"
    email[1] := "sleepy"
    email[2] := "doc"
    email[3] := "happy"
    email[4] := "sneezy"

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         concatArray("email", as=servers)

Concatenates the values of fields email[0], email[1] and so on and returns the results in a field named servers. 

  3. Event Result set.




##### Summary and Results

The query is used to concatenate (join) two or more arrays into a new array. Concatenation is useful in programming and computing because it allows you to store and combine multiple pieces of data when needed. 

Sample output from the incoming example data: 

email[0]| email[1]| email[2]| email[3]| email[4]| servers  
---|---|---|---|---|---  
dopey| sleepy| doc| happy| sneezy| dopeysleepydochappysneezy  
  
#### Concatenate Values in Arrays Using Pipe Separation

**Concatenate values in flat arrays using pipe separation between the concatenated values**

##### Query

logscale
    
    
    concatArray(server, separator=" | ")

##### Introduction

In this example, the [`concatArray()`](functions-concatarray.html "concatArray\(\)") function concatenates the values of all fields with the same name into pipe separated values in a new field. 

Example incoming data might look like this: 
    
    
    server[0] := "dopey"
    server[1] := "sleepy"
    server[2] := "doc"
    server[3] := "happy"
    server[4] := "sneezy"

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         concatArray(server, separator=" | ")

Concatenates the values of fields server[0], server[1] and so on and returns the results in a new array with a field named _concatArray where the concatenated values are separated by a pipe. 

  3. Event Result set.




##### Summary and Results

The query is used to concatenate (join) the elements of the array into a new field where the concatenated values are separated by a pipe. Concatenation is useful in programming and computing because it allows you to store and combine multiple pieces of data when needed. 

Sample output from the incoming example data: 

server[0]| server[1]| server[2]| server[3]| server[4]| _concatArray|   
---|---|---|---|---|---|---  
dopey| sleepy| doc| happy| sneezy| dopey| dopey | sleepy | doc | happy | sneezy | dopey  
  
#### Concatenate Values in Arrays With a Defined Prefix and Suffix

**Concatenate values in flat arrays using prefix, suffix and separator**

##### Query

logscale
    
    
    concatArray(server, prefix="[", separator=",", suffix="]")

##### Introduction

In this example, the [`concatArray()`](functions-concatarray.html "concatArray\(\)") function concatenates the values of all fields with the same name and an array suffix into a value in a new field, adding a prefix and a suffix to the generated output result. 

Example incoming data might look like this: 
    
    
    server[0] := "dopey"
    server[1] := "sleepy"
    server[2] := "doc"
    server[3] := "happy"
    server[4] := "sneezy"

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         concatArray(server, prefix="[", separator=",", suffix="]")

Concatenates the values of fields server[0], server[1] and so on and returns the results as a string named _concatArray enclosed in square brackets, and separated by a comma, which is similar to the written array format. 

  3. Event Result set.




##### Summary and Results

This can be useful to summarize or format a list of items for use in another part of the query. 

Sample output from the incoming example data: 

server[0]| server[1]| server[2]| server[3]| server[4]| _concatArray  
---|---|---|---|---|---  
dopey| sleepy| doc| happy| sneezy| [dopey,sleepy,doc,happy,dopey]  
  
#### Concatenate Values of All Fields With Same Name in an Array

**Concatenate values of all fields with same name in a flat array**

##### Query

logscale
    
    
    concatArray(server)

##### Introduction

In this example, the [`concatArray()`](functions-concatarray.html "concatArray\(\)") function concatenates the values of all fields with the same name into a value in a new field. 

Example incoming data might look like this: 

Raw Events

server[0] := "dopey"  
---  
server[1] := "sleepy"  
server[2] := "doc"  
server[3] := "happy"  
server[4] := "sneezy"  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         concatArray(server)

Concatenates the values of fields server[0], server[1] and so on and returns the results in a new array with a field named _concatArray. If no field is defined, the aggregate function always creates a field name beginning with underscore for the returned values. 

  3. Event Result set.




##### Summary and Results

The query is used to concatenate (join) two or more arrays into a new array. Concatenation is useful in programming and computing because it allows you to store and combine multiple pieces of data when needed. 

Sample output from the incoming example data: 

email[0]| email[1]| email[2]| email[3]| email[4]| _concatArray  
---|---|---|---|---|---  
dopey| sleepy| doc| happy| sneezy| dopeysleepydochappysneezy  
  
#### Concatenate a Range of Values in Arrays

**Concatenate values in flat arrays**

##### Query

logscale
    
    
    concatArray(server, from=1, to=3)

##### Introduction

In this example, the [`concatArray()`](functions-concatarray.html "concatArray\(\)") function concatenates the values of all fields with the same name and index between 1 to 3 into a value in a new field. 

Example incoming data might look like this: 
    
    
    server[0] := "dopey"
    server[1] := "sleepy"
    server[2] := "doc"
    server[3] := "happy"
    server[4] := "sneezy"

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         concatArray(server, from=1, to=3)

Concatenates the values of fields server[1], server[2], and server[3], and returns the results in a new array with a field named _concatArray. 

  3. Event Result set.




##### Summary and Results

The query is used to concatenate (join) two or more arrays into a new array. Concatenation is useful in programming and computing because it allows you to store and combine multiple pieces of data when needed. 

Sample output from the incoming example data: 

server[0]| server[1]| server[2]| server[3]| server[4]| _concatArray  
---|---|---|---|---|---  
dopey| sleepy| doc| happy| sneezy| sleepydochappy

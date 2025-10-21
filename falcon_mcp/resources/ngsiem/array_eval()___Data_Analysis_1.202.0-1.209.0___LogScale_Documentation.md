# array:eval() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-eval.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:eval()`](functions-array-eval.html "array:eval\(\)")

Evaluates the [_`function`_](functions-array-eval.html#query-functions-array-eval-function) argument on all values in the array under the [_`array`_](functions-array-eval.html#query-functions-array-eval-array) argument overwriting the array. If the [_`asArray`_](functions-array-eval.html#query-functions-array-eval-asarray) argument is supplied, then [`array:eval()`](functions-array-eval.html "array:eval\(\)") saves the result in an array under the given prefix. This overwrites existing arrays of that name. 

The output array is always compacted, meaning that the array indices are guaranteed to be continuous, for example, `0,1,2,...`. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-eval.html#query-functions-array-eval-array)[a]| string| required |  |  The array name in LogScale [Array Syntax](syntax-array.html "Array Syntax"), for example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents[]`, as in `array:eval(array="incidents[]", ...`.   
[_`asArray`_](functions-array-eval.html#query-functions-array-eval-asarray)|  string| optional[b] | `value passed to the array parameter`|  The output array.   
[_`function`_](functions-array-eval.html#query-functions-array-eval-function)|  non-aggregate function| required |  |  The function to be applied to each element of the array. Must write a value to a field named the same as the output array.   
[_`var`_](functions-array-eval.html#query-functions-array-eval-var)|  string| optional[[b]](functions-array-eval.html#ftn.table-functions-array-eval-optparamfn) | `input array name`|  Name of the variable to be used in the [_`function`_](functions-array-eval.html#query-functions-array-eval-function) argument.   
[a] The parameter name [_`array`_](functions-array-eval.html#query-functions-array-eval-array) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-eval.html#query-functions-array-eval-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:eval("value",function="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:eval(array="value",function="value")
> 
> These examples show basic structure only.

### [`array:eval()`](functions-array-eval.html "array:eval\(\)") Examples

Click + next to an example below to get the full details.

#### Evaluate Function Argument on Values in Array

**Evaluate the[ _`function`_](functions-array-eval.html#query-functions-array-eval-function) argument on all values in a flat array **

##### Query

logscale
    
    
    array:eval("values[]", asArray="squared[]", var="x", function={squared := x*x})

##### Introduction

The [`array:eval()`](functions-array-eval.html "array:eval\(\)") function is used for test purposes. It evaluates the [_`function`_](functions-array-eval.html#query-functions-array-eval-function) argument on all values in the array under the [_`array`_](functions-array-eval.html#query-functions-array-eval-array) argument overwriting the input array. If an [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") argument has been supplied, [`array:eval()`](functions-array-eval.html "array:eval\(\)") will save the result in an array under the supplied prefix. The purpose of this query is to square the value of each item in the array. 

Example incoming data might look like this: 

values[0]| values[1]| values[2]  
---|---|---  
2| 3| 4  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:eval("values[]", asArray="squared[]", var="x", function={squared := x*x})

Squares the value of each item in the array. If input values `(x)` are 2,3,4 then the output values when squared `(x*x)` will be 4,9,16. 

  3. Event Result set.




##### Summary and Results

The query is used to square the value of each item in the array. This is a good example of manipulating array values, for example to format the output before display. 

Sample output from the incoming example data: 

field| value  
---|---  
squared[0]| 4  
squared[1]| 9  
squared[2]| 16  
  
#### Perform Formatting on All Values in an Array

**Perform formatting on all values in a flat array using the[`array:eval()`](functions-array-eval.html "array:eval\(\)") function **

##### Query

logscale
    
    
    array:eval("devices[]",  asArray="upperDevices[]", var=d, function={upperDevices :=upper("d")})

##### Introduction

In this example, the [`array:eval()`](functions-array-eval.html "array:eval\(\)") function is used to convert all values (for example `[Thermostat, Smart Light]`) in an array devices[] from lowercase to uppercase and show the results in a new array. 

Example incoming data might look like this: 

Raw Events

{\"devices\":[\"Thermostat\",\"Smart Plug\"],\"room\":\"Kitchen\"}"  
---  
{\"devices\":[\"Smart Light\",\"Thermostat\",\"Smart Plug\"],\"room\":\"Living Room\"}"  
{\"devices\":[\"Smart Light\",\"Smart Plug\"],\"room\":\"Bedroom\"}"  
{\"devices\":[\"Thermostat\",\"Smart Camera\"],\"room\":\"Hallway\"}"  
{\"devices\":[\"Smart Light\",\"Smart Lock\"],\"room\":\"Front Door\"}"  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:eval("devices[]",  asArray="upperDevices[]", var=d, function={upperDevices :=upper("d")})

Formats all values in the array devices[] to uppercase and returns the results in a new array named upperDevices[]. The values in the original array stay the same: `[Thermostat, Smart Plug, Smart Light]` and the new array contains the returned results: `[THERMOSTAT, SMART PLUG, SMART LIGHT]`

  3. Event Result set.




##### Summary and Results

The query is used to turn values in an array into uppercase. The [`array:eval()`](functions-array-eval.html "array:eval\(\)") function can also be used for squaring a list of numbers in an array. 

Sample output from the incoming example data: 

devices[]| upperDevices[]  
---|---  
Thermostat| THERMOSTAT  
Smart Plug| SMART PLUG  
Smart Light| SMART LIGHT  
  
#### Square Values in an Array

**Square values in an array using the[`array:eval()`](functions-array-eval.html "array:eval\(\)") function **

##### Query

logscale
    
    
    array:eval("values[]", asArray="squared[]", var=element, function={squared :=element*element})

##### Introduction

In this example, the [`array:eval()`](functions-array-eval.html "array:eval\(\)") function is used to square a list of numbers (for example `2`, `3`, and `4`) and show the results in a new array. 

Example incoming data might look like this: 

values [0] = 2  
---  
values [1] = 3  
values [2] = 4  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:eval("values[]", asArray="squared[]", var=element, function={squared :=element*element})

Squares all values in the array values[] and returns the results in a new array named squared[]. The values in the original array stay the same: `[2, 3, 4]` and the new array contains the squared results: `[4, 9, 16]`

  3. Event Result set.




##### Summary and Results

The query is used to square a list of numbers in an array. The [`array:eval()`](functions-array-eval.html "array:eval\(\)") function can also be used for performing formatting on values in an array. 

Sample output from the incoming example data: 

field| value  
---|---  
squared[0]| 4  
squared[1]| 9  
squared[2]| 16

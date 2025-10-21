# objectArray:eval() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-objectarray-eval.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)")

[`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function iterates over the values of a nested array, applies the function on each element, and returns results in a new array field. Currently, the function supports only flat arrays as the output. 

Although [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") can be used on both flat arrays and nested arrays, then for best performance, we recommend using [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") only for nested arrays (for example JSON structures). For flat arrays, the [`array:eval()`](functions-array-eval.html "array:eval\(\)") function is a recommended equivalent. For a list of functions that can be used on flat arrays, see [Array Query Functions](functions-array.html "Array Query Functions"). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-objectarray-eval.html#query-functions-objectarray-eval-array)[a]| string| required |  |  The array name in LogScale [Array Syntax](syntax-array.html "Array Syntax"), for example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents[]`, as in `objectArray:eval(array="incidents[]", ...`.   
[_`asArray`_](functions-objectarray-eval.html#query-functions-objectarray-eval-asarray)|  string| required | `value passed to the array parameter`|  The output array — cannot be the same as the input array.   
[_`function`_](functions-objectarray-eval.html#query-functions-objectarray-eval-function)|  non-aggregate function| required |  |  The function applied to each element of the array. This argument is used to write a value to the same field that is given as the output array in the [_`asArray`_](functions-objectarray-eval.html#query-functions-objectarray-eval-asarray) argument. In [`objectArray:eval()` Examples](functions-objectarray-eval.html#functions-objectarray-eval-examples "objectArray:eval\(\) Examples"), such a field is _mapped.   
[_`var`_](functions-objectarray-eval.html#query-functions-objectarray-eval-var)|  string| optional[b] | `input array name`|  Name of the variable to use in the [_`function`_](functions-objectarray-eval.html#query-functions-objectarray-eval-function) argument.   
[a] The parameter name [_`array`_](functions-objectarray-eval.html#query-functions-objectarray-eval-array) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-objectarray-eval.html#query-functions-objectarray-eval-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     objectArray:eval("value",asArray=value passed to the array parameter,function="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     objectArray:eval(array="value",asArray=value passed to the array parameter,function="value")
> 
> These examples show basic structure only.

### [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") Function Operation

When using this function: 

  * The variable defined by the [_`var`_](functions-objectarray-eval.html#query-functions-objectarray-eval-var) argument is validated to ensure it does not contain object/array access patterns, for example, `[..]` or `.`. 

  * The variable becomes available as a "pseudo-field" (meaning that it's not like a proper field in the event) in the [_`function`_](functions-objectarray-eval.html#query-functions-objectarray-eval-function) argument (see [`objectArray:eval()` Examples](functions-objectarray-eval.html#functions-objectarray-eval-examples "objectArray:eval\(\) Examples")). 

  * The "pseudo-field" can access structured data on the array entries using an array access pattern consisting of `[number]` for array indexing and `.` for sub-selections of object fields. These can be repeated/combined arbitrarily; for example, `x.foo[0].bar.baz` is a valid pattern. 

  * The mapping between input and output array entries is done by the [_`function`_](functions-objectarray-eval.html#query-functions-objectarray-eval-function) argument: for each input array entry, [_`function`_](functions-objectarray-eval.html#query-functions-objectarray-eval-function) maps an output array entry. The output/result value of [_`function`_](functions-objectarray-eval.html#query-functions-objectarray-eval-function) is the value of the same field (without `[]`) given by the [_`asArray`_](functions-objectarray-eval.html#query-functions-objectarray-eval-asarray) argument. 




### [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") Examples

Click + next to an example below to get the full details.

#### Concatenate Multiple Values From Nested Array Elements

**Concatenate multiple values from nested array elements using[`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function with [`concat()`](functions-concat.html "concat\(\)") **

##### Query

logscale
    
    
    objectArray:eval("foo[]", var=x, function={_mapped := concat([x.key.value, "x.key.others[0]", "x.key.others[1]"])}, asArray="_mapped[]")

##### Introduction

In this example, the [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function is used with the [`concat()`](functions-concat.html "concat\(\)") function to concatenate multiple deeply nested arrays of objects values in the array `foo[] ` and return the concatenated values in the output field _mapped[]

Example incoming data might look like this: 

JSON
    
    
    "foo[0].key.value": y
    "foo[0].key.others[0]": 1
    "foo[0].key.others[1]": 2
    "foo[1].nothing": 355

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         objectArray:eval("foo[]", var=x, function={_mapped := concat([x.key.value, "x.key.others[0]", "x.key.others[1]"])}, asArray="_mapped[]")

Notice that a [_`var`_](functions-objectarray-eval.html#query-functions-objectarray-eval-var) parameter can be used to give a different name to the input array variable inside the function argument. This is particularly useful whenever the input array name is very long. 

  3. Event Result set.




##### Summary and Results

The query is used to concatenate multiple deeply nested arrays of objects values. 

Sample output from the incoming example data: 
    
    
    _mapped[0]: y12
    "foo[0].key.value": y
    "foo[0].key.others[0]": 1
    "foo[0].key.others[1]": 2

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

#### Concatenate Values From Nested Array Elements

**Concatenate deeply nested objects and arrays using[`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function with [`concat()`](functions-concat.html "concat\(\)") **

##### Query

logscale
    
    
    objectArray:eval("in[]", asArray="out[]", function={out := concat(["in.a", "in.b.c", "in.others[1].d"])})

##### Introduction

In this example, the [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function is used with the [`concat()`](functions-concat.html "concat\(\)") function to concatenate deeply nested arrays of objects values in the array `in[] ` and return the concatenated values in the output field out[]. 

Example incoming data might look like this: 

JSON
    
    
    in[0].a: 1
    in[0].b.c: 2
    in[0].others[0].d: 3
    in[0].others[1].d: 4

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         objectArray:eval("in[]", asArray="out[]", function={out := concat(["in.a", "in.b.c", "in.others[1].d"])})

Iterates over the array from start to end (or to the first empty index in the array), applies the given function, and returns the concatenated results in a new output array name field out[]. 

  3. Event Result set.




##### Summary and Results

The query is used to concatenate deeply nested arrays of objects. 

Sample output from the incoming example data: 
    
    
    out[0]: 124

#### Concatenate Values From Two Nested Array Elements

**Concatenate values from two nested array elements returning output in flat array**

##### Query

logscale
    
    
    objectArray:eval("arr[]", var=x, function={_mapped := concat([x.a, x.b])}, asArray="_mapped[]")

##### Introduction

In this example, the [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function is used with the variable x to concatenate the values `a` and `b` from each array element. The [`concat()`](functions-concat.html "concat\(\)") function is used to return the concatenated output into a new array. 

Example incoming data might look like this: 

JSON
    
    
    arr[0]: machine
    arr[0].a: a0
    arr[0].b: b0
    arr[1].a: a1
    arr[1].b: b1
    arr[1].c: c1
    arr[2].a: a2
    arr[4].b: b2
    other: abc

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         objectArray:eval("arr[]", var=x, function={_mapped := concat([x.a, x.b])}, asArray="_mapped[]")

Concatenates the values `a` and `b` from each array element and returns the results in a new array named _mapped. In this example, [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") iterates over each element of the array and assigns each element to the variable `x` which is then used as an alias. The new field _mapped is created by concatenating the value using the alias `x` to extract each object value from each element of the array. Notice that the output in this example is a flat array. 

For example, this array element: 

arr[0].a: a0  
---  
arr[0].b: b0  
  
is translated to: 
         
         _mapped[0]: a0b0

  3. Event Result set.




##### Summary and Results

The query is used to concatenate values of two array elements. 

Sample output from the incoming example data, the original values have not been removed: 
    
    
    _mapped[0]: a0b0
    _mapped[1]: a1b1
    _mapped[2]: a2
    _mapped[3]: b2
    
    arr[0]: machine
    
    arr[0].a: a0
    arr[0].b: b0
    
    arr[1].a: a1
    arr[1].b: b1
    
    arr[1].c: c1
    
    arr[2].a: a2
    
    arr[4].b: b2
    
    other: abc

#### Create Single Array from Object Arrays

**Transform one or more objects from object arrays into a single array**

##### Query

logscale
    
    
    "a[0].foo" := "a"
    | "a[0].bar" := "b"
    | "a[1].foo" := "c"
    | "a[1].bar" := "d"
    | objectArray:eval(array="a[]", asArray="output[]", var="x", function={output := x.bar})

##### Introduction

In this example, the [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function is used to extract one object from each element of an array of objects into a new array. 

Example incoming data might look like this: 

a[0].foo: a  
---  
a[0].bar: b  
a[1].foo: c  
a[1].bar: d  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         "a[0].foo" := "a"
         | "a[0].bar" := "b"
         | "a[1].foo" := "c"
         | "a[1].bar" := "d"

  3. logscale
         
         | objectArray:eval(array="a[]", asArray="output[]", var="x", function={output := x.bar})

Iterates (creates a loop) over the array `a[]` and adds the value of the object `.bar` to a new array `output[]`. This is achieved by executing an anonymous function, which sets the value of `output` to the iterated value of `x.bar` from `a[]`. 

The [_`asArray`_](functions-objectarray-eval.html#query-functions-objectarray-eval-asarray) parameter is set to the output[] field, creating an array where each element contains the value of x.bar from the corresponding iteration. 

  4. Event Result set.




##### Summary and Results

The query is used to create an array from compound arrays. This can be useful when you need to collect specific values from nested arrays for further processing, filtering, or analysis. 

Sample output from the incoming example data: 

a[0].foo| a[0].bar| a[1].foo| a[1].bar| output[0]| output[1]  
---|---|---|---|---|---  
a| b| c| d| b| d  
  
#### Format Values From Two Array Elements Using :

**Format Values from Two Array Elements using : as a separator**

##### Query

logscale
    
    
    objectArray:eval("in[]", asArray="out[]", function={out := format("%s:%s", field=[in.key, in.value])})

##### Introduction

In this example, the [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function is used to format the array entries `in[].key ` and `in[].value` separating the concatenated values with a `:` in the output field out[]. The output must be a single field in this example as [`format()`](functions-format.html "format\(\)") is only capable of creating a single value. 

Example incoming data might look like this: 

JSON
    
    
    in[0].key = x
    in[0].value = y
    in[1].key = a
    in[1].value = b

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         objectArray:eval("in[]", asArray="out[]", function={out := format("%s:%s", field=[in.key, in.value])})

Iterates (executes a loop) over the array from start to end (or to the first empty index in the array), applies the given function, and returns the concatenated results in a new output array name field out[]. 

Notice that a [_`var`_](functions-objectarray-eval.html#query-functions-objectarray-eval-var) parameter can be used to give a different name to the input array variable inside the function argument. This is particularly useful whenever the input array name is very long. Example: 

logscale
         
         objectArray:eval("someVeryLongName[]", asArray="out[]",
         var=x, function={out := format("%s:%s", field=[x.key,
         x.value])})

  3. Event Result set.




##### Summary and Results

The query is used to format arrays of objects. 

Sample output from the incoming example data: 
    
    
    out[0] = x:y
    out[1] = a:b

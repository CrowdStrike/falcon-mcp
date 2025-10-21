# Array Syntax | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-array.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

## Array Syntax

The documentation explains array syntax in LogScale, covering both flat and nested arrays, including how arrays are structured, accessed, and manipulated using JSON-like notation with square brackets and dots. It details structured array syntax for working with arrays of objects, array notation rules for field naming, and provides comprehensive examples of array operations using functions like array:contains(), array:eval(), and objectArray:eval(). 

Falcon LogScale operates on both flat arrays and nested arrays. Within LogScale there is no distinct array type, but LogScale is able to operate on array-like objects using syntax similar to manipulating JSON arrays and objects. Within LogScale, an array is an ordered collection of values: each value is called an element, and each element has a numeric position in the array, known as its index. Nested arrays are fields that consist of an array where each element is another array or object, also known as arrays of objects or arrays of arrays. 

Arrays can be parsed from incoming events using the [`splitString()`](functions-splitstring.html "splitString\(\)") or [`parseJson()`](functions-parsejson.html "parseJson\(\)") functions. 

As a part of the CrowdStrike Query Language, there is syntax that applies to array functions, for example [`array:contains()`](functions-array-contains.html "array:contains\(\)"), [`array:eval()`](functions-array-eval.html "array:eval\(\)") and [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") that we refer to as array syntax. Some of the array functions are used on flat arrays, some on nested arrays. The [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function operates on arrays of objects, the nested arrays - note that it can only read the structured array fields, it cannot write to them. 

The array functions operate on fields that follow this specific naming conventions syntax. 

The array syntax is similar to the one used by JSON, where `[` and `]` are used for indexing within arrays and `.` for selecting members in objects. For example: 

json
    
    
    ["jsmith","tmcdonald"]

Is an array with two elements, the first element `username[0]` has the value `jsmith`. 

While the object: 

json
    
    
    {username: "jsmith", name: "Jon Smith"}

The `username` can be extracted using `user.username`. 

The following table compares the JSON and the parsed LogScale form of the same array and object structures. The final column shows the syntax to use when referring to the whole array. 

JSON |  Parsed LogScale event |  array name syntax   
---|---|---  
`["jsmith","tmcdonald"]` |  `username[0]: "jsmith"` `username[1]: "tmcdonald"` |  username[]  
      
    
    [
      {username: "jsmith", name: "Jon Smith"},
      {username: "jdoe", name: "Jane Doe"}
    ]

|  `users[0].user.username: "jsmith"` `users[0].user.name: "Jon Smith"` `users[1].user.username: "jdoe"` `users[1].user.name: "Jane Doe"` |  users[]  
` [ ["a", "b"], ["c", "d"]] ` |  `foo[0][0]: "a"` `foo[0][1]: "b"` `foo[1][0]: "c"` `foo[1][1]: "d"` |  foo[], foo[0][], and foo[1][]  
  
### Structured Array Syntax

Let's start with an example usage: 

logscale Syntax
    
    
    objectArray:eval("in[]", asArray="out[]", function={out := format("%s:%s", field=[in.key, in.value])})
    input:
           in[0].key = x
           in[0].value = y
           in[1].key = a
           in[1].value = b
    output:
           out[0] = x:y
           out[1] = a:b

`objectArray:eval("in[]", asArray="out[]", function=function)` iterates over the array from start to end (or to the first "hole" in the array). 

For each array entry, the given function is applied. 

For each entry, at index `i`, a field out[i] is created if the function writes a value to the output array name field ("out" in this example). 

Within the function, a special pattern to access sub-selections of array entries is supported. 

This pattern is: 

`in` (the input array) followed by: 

  * `.<subselection>`

  * or `[<number>]`

  * or any combination of the above 




Examples: 

  * `in.key`

  * `in.others[0].foo`

  * `in[0][1]`




This pattern is what allows the function to operate on arrays of objects, and arrays of arrays, and other arrays of structured data. 

Semantically, given the input array "in", an array index i, and an access in.<subselection> this will be translated to the field name `in[i].<subselection>`. Similarly, `in[2]` is translated to `in[i][2]`. 

The character sequence could contain another dot. For example `in.foo.bar` becomes `in[i].foo.bar`.

At present, it is only possible to read structured array fields. Writing to them is unsupported, but is a possible future extension. For that reason, at present we disallow modifying the existing array.

The _`var`_ parameter can be used to give a different name to the input array variable inside the function argument. This is particularly useful whenever the input array name is very long. Example: 

`objectArray:eval("someVeryLongName[]", asArray="out[]", var=x, function={out := format("%s:%s", field=[x.key, x.value])})`

### Syntax Array Notation

Fields with names consisting of a valid array-prefix followed by an array entry are treated as entries of an array. The indices must be continuously increasing from 0 and upwards. 

The entire array is referenced within array function using the array-prefix followed by `[]` that indicates the entire range of entries, for example `username[]`. 

Simplified, the valid array-prefix is a sequence of members and array entries. More formally, a valid array-prefix is either: 

  * an identifier — that is, a sequence of alphanumerical characters that starts with a letter, an underscore (`_`), `@`, or `#`. 

If the member name is not an identifier, for example because it starts with a number or contains other special characters, the name needs to be quoted using ``` like this: `user.`e-mail`[]`. 

  * a valid array-prefix followed by a member operator and an identifier — the member operator is a `.`

  * or a valid array-prefix followed by an array entry — the array entry is an index surrounded by square brackets. 




Examples of field names representing entries in an array, and the reference to that array: 

Field names following the array syntax |  How to reference in array functions   
---|---  
`a[0], a[1], a[2]` |  `a[]`  
`a.b[0], a.b[1], a.b[2]` |  `a.b[]`  
`a[0][0], a[0][1]` |  `a[0][]`  
`user.e-mail[0], user.e-mail[1]` |  `user.`e-mail`[]`  
  
### Warning

If the array is a structured array, for example, `a[][0]` or `a[].b`, use the `objectArray:` functions. 

For arrays, use the `array:` functions.

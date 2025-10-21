# lower() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-lower.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`lower()`](functions-lower.html "lower\(\)")

The [`lower()`](functions-lower.html "lower\(\)") function converts text to lower case letters. It can process text from event fields or other sources. By default, it uses the system locale, but it is possible to specify a different language and locale if needed. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-lower.html#query-functions-lower-as)|  string| optional[a] | `_lower`|  The name of the output field.   
[_`field`_](functions-lower.html#query-functions-lower-field)[b]| string| required |  |  The name of the input field with the value to convert to lower case.   
[_`locale`_](functions-lower.html#query-functions-lower-locale)|  string| optional[[a]](functions-lower.html#ftn.table-functions-lower-optparamfn) | `system locale`|  Locale to use, as ISO-639 language and an optional ISO-3166 country (for example, `en` or `en_US`).   
[_`type`_](functions-lower.html#query-functions-lower-type)|  string| optional[[a]](functions-lower.html#ftn.table-functions-lower-optparamfn) |  |  The name of the locale to use as ISO 639 language and an ISO 3166 country. When not specified, it uses the system locale.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-lower.html#query-functions-lower-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-lower.html#query-functions-lower-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     lower("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     lower(field="value")
> 
> These examples show basic structure only.

In addition to providing the field of events to change to all lower-case letters, as well as optionally assigning a name to the resulting field, you can specify the country and language so that conversion is done correctly and without odd characters. 

For the value of type, you can specify just the language, or you can refine that choice by including the country. For instance, you might specify: 

  * `en` for English. 

  * `en_UK` for UK English. 

  * `en_US` for US English. 




Specifying the correct locale is particularly important for languages with non-Latin alphabets, such as Russian with Cyrillic letters. 

### [`lower()`](functions-lower.html "lower\(\)") Examples

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
  
#### Format a String to Upper Case and Lower Case

**Format a string to upper case and lower case using the[`upper()`](functions-upper.html "upper\(\)") and [`lower()`](functions-lower.html "lower\(\)") functions with [`concat()`](functions-concat.html "concat\(\)") **

##### Query

logscale
    
    
    lower(@error_msg[0], as=msg1)
     
    | upper(@error_msg[1], as=msg2)
     
    | concat([msg1, msg2], as=test)

##### Introduction

In this example, [`upper()`](functions-upper.html "upper\(\)") and [`lower()`](functions-lower.html "lower\(\)") functions are used with [`concat()`](functions-concat.html "concat\(\)") to concatenate two fields containing error messages, where one field's result is all lower case letters and the other field's results are all upper case letters. 

If no [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") parameter is set, the fields outputted to is by default named _upper and _lower, respectively. 

In this query, the [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") parameter is used for the [`lower()`](functions-lower.html "lower\(\)") and [`upper()`](functions-upper.html "upper\(\)") functions to label their results. These fields (msg1 and msg2) are then used with the [`concat()`](functions-concat.html "concat\(\)") function, returning the concatenated string into a field named test. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         lower(@error_msg[0], as=msg1)

Formats the first element (index 0) of the @error_msg array to lower case and returns the results in a field named msg1. 

  3. logscale
         
         | upper(@error_msg[1], as=msg2)

Formats the second element (index 1) of the  @error_msg array to upper case and returns the results in a field named msg2. 

  4. logscale
         
         | concat([msg1, msg2], as=test)

Concatenates (combines) the values in field msg1 and field msg2, and returns the concatenated string in a new field named test. 

If using the [`top()`](functions-top.html "top\(\)") function on the test field, like this: 

`| top(test)`

then the top 10 values for the field test is displayed with a count of their occurrences in a field named _count. 

  5. Event Result set.




##### Summary and Results

The query is used to either convert strings to lower case or upper case and return the new concatenated strings/results in a new field. In this example, concatenating error messages. 

The specific labeling of msg1 and msg2 is particularly useful when you have more than one field that use the same query function. 

By converting fields to consistent cases, it helps standardize data for easier analysis and comparison. The concatenation allows you to combine multiple fields into a single field, which can be useful for creating unique identifiers or grouping related information. 

#### Standardize Values And Combine Into Single Field

**Standardize values using the[`upper()`](functions-upper.html "upper\(\)") and [`lower()`](functions-lower.html "lower\(\)") functions and combine into single field with [`concat()`](functions-concat.html "concat\(\)") **

##### Query

logscale
    
    
    lower(#severity, as=severity)
     
    | upper(#category, as=category)
     
    | concat([severity, category], as=test)
     
    | top(test)

##### Introduction

Standardizing the format of fields is useful for consistent analysis. In this example, [`upper()`](functions-upper.html "upper\(\)") and [`lower()`](functions-lower.html "lower\(\)") functions are used with [`concat()`](functions-concat.html "concat\(\)") to concatenate the fields #category and severity, where one field's result is all lower case letters and the other field's results are all upper case letters. 

If no [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") parameter is set, the fields outputted to is by default named _upper and _lower, respectively. 

In this query, the [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") parameter is used for the [`lower()`](functions-lower.html "lower\(\)") and [`upper()`](functions-upper.html "upper\(\)") functions to label their results. These output fields (category and severity) are then used with the [`concat()`](functions-concat.html "concat\(\)") function, returning the concatenated string into a field named test. Finally, it uses the [`top()`](functions-top.html "top\(\)") function, to show which combinations of `severity` and `category` are most common in the data. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         lower(#severity, as=severity)

Converts the values in the #severity field to lower case and returns the results in a field named severity. 

  3. logscale
         
         | upper(#category, as=category)

Converts the values in the #category field to upper case and returns the results in a field named category. 

  4. logscale
         
         | concat([severity, category], as=test)

Concatenates (combines) the values in field category and field severity, and returns the concatenated string in a new field named test. 

  5. logscale
         
         | top(test)

Finds the most common values of the field test — the top of an ordered list of results - along with their count. The result of the count of their occurrences is displayed in a field named _count. 

  6. Event Result set.




##### Summary and Results

The query is used to standardize the format of the values in the fields #category and severity and concatenate the values into a single field, showing which combinations of `severity` and `category` are most common in the data. 

The specific labeling of category and severity is particularly useful when you have more than one field that use the same query function. 

By converting fields to consistent cases, it helps standardize data for easier analysis and comparison. The concatenation allows you to combine multiple fields into a single field, which can be useful for creating unique identifiers or grouping related information. It provides a quick overview of the distribution of events across different `severity-category` combinations. 

Sample output from the incoming example data (showing the first 10 rows only): 

test| _count  
---|---  
infoALERT| 90005  
infoFILTERALERT| 36640  
errorALERT| 17256  
warningGRAPHQL| 14240  
warningALERT| 13617  
warningSCHEDULEDSEARCH| 11483  
infoSCHEDULEDSEARCH| 5917  
warningFILTERALERT| 1646  
errorFILTERALERT| 1487  
infoACTION| 3  
  
Notice how the value of #severity is in lower case letters, and the value of #category is in upper case letters.

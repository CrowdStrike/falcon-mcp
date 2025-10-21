# xml:prettyPrint() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-xml-prettyprint.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`xml:prettyPrint()`](functions-xml-prettyprint.html "xml:prettyPrint\(\)")

'Pretty prints' an XML field. The function formats an XML field for improved readability. This can be an expensive operation. 

It is recommended to apply [`xml:prettyPrint()`](functions-xml-prettyprint.html "xml:prettyPrint\(\)") after filtering your data at the end of the query. This prevents unnecessary formatting of data that will be discarded. 

Default behaviour is as follows: 

  * If the field does not contain valid XML, the unmodified input value is stored in the output field. 

  * If no field is specified, the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field will be formatted. 




Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-as)|  string| optional[a] |  |  The name of the field to store the output in.   
[_`field`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-field)[b]| string| required | `@rawstring`|  The name of the field to format.   
[_`step`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-step)|  integer| optional[[a]](functions-xml-prettyprint.html#ftn.table-functions-xml-prettyprint-optparamfn) | `2`|  The indentation in number of characters.   
[_`strict`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-strict)|  boolean| optional[[a]](functions-xml-prettyprint.html#ftn.table-functions-xml-prettyprint-optparamfn) | `false`|  If set to true only valid XML input produce a value in the output field. By default invalid XML is copied to the output field unmodified.   
[_`width`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-width)|  integer| optional[[a]](functions-xml-prettyprint.html#ftn.table-functions-xml-prettyprint-optparamfn) | `80`|  The width (in number of characters) to fit the output input.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     xml:prettyPrint("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     xml:prettyPrint(field="value")
> 
> These examples show basic structure only.

### [`xml:prettyPrint()`](functions-xml-prettyprint.html "xml:prettyPrint\(\)") Examples

Click + next to an example below to get the full details.

#### Format Only Valid Input XML in Output String

**Format only valid input XML to valid XML in output string using the[`xml:prettyPrint()`](functions-xml-prettyprint.html "xml:prettyPrint\(\)") function **

##### Query

logscale
    
    
    formattedXml := xml:prettyPrint(field=message, strict=true)

##### Introduction

In this example, the [`xml:prettyPrint()`](functions-xml-prettyprint.html "xml:prettyPrint\(\)") function is used to format only the valid XML in the field [message](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) in the output string. 

Setting the [_`strict`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-strict) parameter to `true`, means that only valid XML input produce a value in the output field. By default - if the [_`strict`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-strict) parameter is not set - invalid input XML is copied to the output field unmodified. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         formattedXml := xml:prettyPrint(field=message, strict=true)

Formats and copies valid XML to the output field formattedXml by setting the parameter `strict=true`. 

When [_`strict`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-strict) is set to `true`, only valid XML input produce a value in the output field, therefore, the field formattedXml will not be created for events with invalid XML in message. 

  3. Event Result set.




##### Summary and Results

The query is used to "pretty print" an XML field, in this example the [message](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) field, and to validate the integrity of the XML message as it only outputs if the XML is completely valid. Only the valid input XML is formatted to valid output XML. Invalid input XML is not copied to the output field unmodified. 

The query is useful in cases where XML validity is critical and to ensure XML compliance. 

The [`xml:prettyPrint()`](functions-xml-prettyprint.html "xml:prettyPrint\(\)") function formats an XML field for improved readability. 

#### Format XML String to Certain Line Length and Indentation

**Format XML strings to a certain line length and indentation using the[`xml:prettyPrint()`](functions-xml-prettyprint.html "xml:prettyPrint\(\)") function **

##### Query

logscale
    
    
    formattedXml := xml:prettyPrint(field=payload, step=4, width=100)

##### Introduction

In this example, the [`xml:prettyPrint()`](functions-xml-prettyprint.html "xml:prettyPrint\(\)") function is used with specified _`step`_ and _`width`_ parameters to format the XML content in the payload field (instead of default [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         formattedXml := xml:prettyPrint(field=payload, step=4, width=100)

Formats XML in the field payload to a max line length of `100` and indent by `4` spaces, and returns the formatted XML result in a new field named formattedXml. 

Defining a max line length of 100 characters using the [_`width`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-width) parameter makes it easier to read (allows longer lines before wrapping). 

Larger indentation (4 spaces) provides more visual separation between XML levels. 

  3. Event Result set.




##### Summary and Results

The query is used to format values of a specific field into valid XML of a certain line length and indentation. Defining a max line length makes it easier to read. 

"Pretty printing" XML can be an expensive operation and it is recommended only to perform this after filtering the data (at the end of the query), so that only filtered data is formatted. 

The [`xml:prettyPrint()`](functions-xml-prettyprint.html "xml:prettyPrint\(\)") function formats an XML field for improved readability. 

#### Format XML in @rawstring Field after Filtering Data

**Format XML in @rawstring field after filtering the data using the[`xml:prettyPrint()`](functions-xml-prettyprint.html "xml:prettyPrint\(\)") function **

##### Query

logscale
    
    
    #type=SOAP
    | account=123
    | xml:prettyPrint()

##### Introduction

In this example, the [`xml:prettyPrint()`](functions-xml-prettyprint.html "xml:prettyPrint\(\)") function is used to format the filtered `SOAP` messages in the output string. 

Note that if no field is specified, the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field will be formatted. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #type=SOAP

Filters for all events of the data type `SOAP`. 

  3. logscale
         
         | account=123

Filters for strings where the field account matches the value `123`. It narrows the scope to a specific account's `SOAP` messages. 

  4. logscale
         
         | xml:prettyPrint()

Takes the filtered SOAP messages (which are in XML format), and formats the XML content in the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field for better readability. 

In this example, all the default values for the parameters [_`field`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-field), [_`step`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-step), [_`width`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-width) and [_`strict`_](functions-xml-prettyprint.html#query-functions-xml-prettyprint-strict) are used. 

  5. Event Result set.




##### Summary and Results

The query is used to format rawstrings into valid XML, in this case retrieved `SOAP` messages from `account 123`. This is useful, for example, when analyzing specific `SOAP` messages in detail. 

Note that the [`xml:prettyPrint()`](functions-xml-prettyprint.html "xml:prettyPrint\(\)") function can be used on any XML content - not just limited to SOAP messages, but also REST XML responses, XML configuration files, XML logs and any other XML formatted data. 

"Pretty printing" XML can be an expensive operation and it is recommended only to perform this after filtering the data (at the end of the query), so that only filtered data is formatted.

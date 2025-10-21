# stripAnsiCodes() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-stripansicodes.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`stripAnsiCodes()`](functions-stripansicodes.html "stripAnsiCodes\(\)")

Removes ANSI color codes and movement commands. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-stripansicodes.html#query-functions-stripansicodes-as)|  string| optional[a] |  |  Name of output field, default is to replace contents of input field.   
[_`field`_](functions-stripansicodes.html#query-functions-stripansicodes-field)[b]| string| required | `@rawstring`|  Specifies the field where to remove ANSI escape codes.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-stripansicodes.html#query-functions-stripansicodes-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-stripansicodes.html#query-functions-stripansicodes-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     stripAnsiCodes("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     stripAnsiCodes(field="value")
> 
> These examples show basic structure only.

### [`stripAnsiCodes()`](functions-stripansicodes.html "stripAnsiCodes\(\)") Syntax Examples

Remove the ANSI escape codes from the message field. 

logscale
    
    
    message := "\x1b[93;41mColor"
    | stripAnsiCodes(message)
    | @display := message

Remove all ANSI escape codes from @rawstring 

logscale
    
    
    stripAnsiCodes()

### [`stripAnsiCodes()`](functions-stripansicodes.html "stripAnsiCodes\(\)") Examples

Click + next to an example below to get the full details.

#### Remove ANSI Escape Codes From Text

**Clean text containing ANSI color codes using the[`stripAnsiCodes()`](functions-stripansicodes.html "stripAnsiCodes\(\)") function **

##### Query

logscale
    
    
    message := "\x1b[93;41mColor"
    stripAnsiCodes(message)
    @display := message

##### Introduction

In this example, the [`stripAnsiCodes()`](functions-stripansicodes.html "stripAnsiCodes\(\)") function is used to clean a text field containing ANSI color codes and assign the result to a display field. 

Example incoming data might look like this: 

@timestamp| message  
---|---  
2025-08-06T10:15:30.000Z| \x1b[93;41mColor  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         message := "\x1b[93;41mColor"

Creates a variable [message](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) containing text with ANSI escape codes. The sequence `\x1b[93;41m` sets bright yellow text (93) on a red background (41). 

  3. logscale
         
         stripAnsiCodes(message)

Removes all ANSI escape sequences from the content of the [message](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) field, leaving only the plain text. 

  4. logscale
         
         @display := message

Assigns the cleaned text to the @display field for output. 

  5. Event Result set.




##### Summary and Results

The query is used to clean text by removing ANSI escape codes that control color and formatting in terminal output. 

This query is useful, for example, to process log files that contain terminal output or to clean data for display in interfaces that don't support ANSI formatting. 

Sample output from the incoming example data: 

@timestamp| @timestamp.nanos| @timezone| @display| message  
---|---|---|---|---  
1754475330000| 0| Z| Color| \x1b[93;41mColor  
  
#### Remove ANSI Escape Codes from Default Field

**Remove ANSI Escape Codes from Default Field using the[`stripAnsiCodes()`](functions-stripansicodes.html "stripAnsiCodes\(\)") function without parameters **

##### Query

logscale
    
    
    stripAnsiCodes()

##### Introduction

In this example, the [`stripAnsiCodes()`](functions-stripansicodes.html "stripAnsiCodes\(\)") function is used to clean ANSI escape codes from the default field. 

Example incoming data might look like this: 

@timestamp| @rawstring  
---|---  
2025-08-06T10:15:30.000Z| \x1b[93;41mWarning: System overload\x1b[0m  
2025-08-06T10:15:31.000Z| \x1b[32mStatus: Normal\x1b[0m  
2025-08-06T10:15:32.000Z| \x1b[31mError: Connection failed\x1b[0m  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         stripAnsiCodes()

Removes all ANSI escape sequences from the default field. When no field is specified, the function processes the [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field, removing color codes and other ANSI formatting sequences while preserving the plain text content. 

  3. Event Result set.




##### Summary and Results

The query is used to clean text by removing ANSI escape codes that control color and formatting in terminal output, operating on the default field. 

This query is useful, for example, to process raw log data that contains terminal output with color coding, making the text suitable for analysis and display in any context. 

Sample output from the incoming example data: 

@timestamp| @timestamp.nanos| @timezone| @rawstring  
---|---|---|---  
1754475330000| 0| Z| Warning: System overload  
1754475331000| 0| Z| Status: Normal  
1754475332000| 0| Z| Error: Connection failed

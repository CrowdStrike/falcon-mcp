# parseCsv() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-parsecsv.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`parseCsv()`](functions-parsecsv.html "parseCsv\(\)")

Parse a CSV-encoded field into known columns. It can parse values of the form: 

  * `value 1, value 2, value 3`

  * `"value 1", "value 2", value 3` (Quoted values. Quotes are optional.) 

  * `"value 1"; "value 2"; value 3` (Using ; as delimiter. Delimiter is configurable.) 




Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`columns`_](functions-parsecsv.html#query-functions-parsecsv-columns)|  string or array| required |  |  Names of columns to extract from field.   
[_`delimiter`_](functions-parsecsv.html#query-functions-parsecsv-delimiter)|  string| optional[a] | `,`|  Delimiter character to split records by.   
[_`excludeEmpty`_](functions-parsecsv.html#query-functions-parsecsv-excludeempty)|  boolean| optional[[a]](functions-parsecsv.html#ftn.table-functions-parsecsv-optparamfn) | `false`|  If the value of a column is empty, exclude the field.   
[_`field`_](functions-parsecsv.html#query-functions-parsecsv-field)[b]| string| required | `@rawstring`|  Field that holds the input in CSV form.   
[_`trim`_](functions-parsecsv.html#query-functions-parsecsv-trim)|  boolean| optional[[a]](functions-parsecsv.html#ftn.table-functions-parsecsv-optparamfn) | `false`|  Allows to ignore whitespace before and after values. If the value is quoted, the quotes can start after the spaces. Useful for parsing data created by sources that do not adhere to the CSV standard.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-parsecsv.html#query-functions-parsecsv-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-parsecsv.html#query-functions-parsecsv-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     parseCsv("value",columns="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     parseCsv(field="value",columns="value")
> 
> These examples show basic structure only.

### [`parseCsv()`](functions-parsecsv.html "parseCsv\(\)") Syntax Examples

For a log line like this: 

ini
    
    
    2017-02-22T13:14:01.917+0000 [main thread] INFO statsModule got result="117,success,27%,3.14"

Using `parseCsv(result, columns=[count, status, completion, precision, sourcetask])` will add these fields: 

count| 117  
---|---  
status| success  
completion| 27%  
precision| 3.14  
  
sourcetask will not get assigned a value, as there were too few columns in the input for that. 

Use the (unnamed) _`field`_ parameter to specify which field should be CSV parsed. Specify [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) to parse the rawstring. 

### [`parseCsv()`](functions-parsecsv.html "parseCsv\(\)") Examples

Click + next to an example below to get the full details.

#### Parse String as CSV

**Parse a CSV-encoded field into known columns using[`parseCsv()`](functions-parsecsv.html "parseCsv\(\)") function **

##### Query

logscale
    
    
    kvParse()
    | parseCsv(result, columns=[count, status,
              completion, precision, sourcetask])

##### Introduction

The [`parseCsv()`](functions-parsecsv.html "parseCsv\(\)") function can be used to parse a CSV-encoded field into known columns. 

Example incoming data might look like this: 

Raw Events

2017-02-22T13:14:01.917+0000 [main thread] INFO statsModule got result="117 ,success ,27% ,3.14"  
---  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         kvParse()

Parses the string into key value pairs. 

  3. logscale
         
         | parseCsv(result, columns=[count, status,
                   completion, precision, sourcetask])

CSV parses the result field from a log line (extracted by the [`kvParse()`](functions-kvparse.html "kvParse\(\)") function) and adds the following fields to the event: count with the value `117`, status with the value `success`, completion with the value `27%`, and precision with the value `3.14`. 

  4. Event Result set.




##### Summary and Results

The query is used to parse a string as CSV. 

Sample output from the incoming example data: 

completion| count| precision| result| status  
---|---|---|---|---  
27% | 117 | 3.14 | 117 ,success ,27% ,3.14 | success   
  
#### Parse String as CSV - Example 2

**Parse a CSV-encoded field into known columns using[`parseCsv()`](functions-parsecsv.html "parseCsv\(\)") function and trim parameter defined **

##### Query

logscale
    
    
    parseCsv(columns=[status, hosts, rest], trim=true)

##### Introduction

The [`parseCsv()`](functions-parsecsv.html "parseCsv\(\)") function can be used to parse a CSV-encoded field into known columns. In this example, the [`parseCsv()`](functions-parsecsv.html "parseCsv\(\)") function is used to parse a log line with spaces and quotes and trim the output. Trimming the output is done by setting the [_`trim`_](functions-parsecsv.html#query-functions-parsecsv-trim) parameter to `true`. When `true` and using quotes with trim, the spaces inside the quotes are not removed, but the quotes may come after spaces. 

Example incoming data might look like this: 

csv
    
    
    117, " crowdstrike.com, logscale.com ", 3.14

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         parseCsv(columns=[status, hosts, rest], trim=true)

CSV parses the columns field from a log line and adds the following fields to the event: status with the value `117, `, hosts with the value `" crowdstrike.com, logscale.com \"`, rest with the value ` 3.14"`. 

  3. Event Result set.




##### Summary and Results

The query is used to parse a string as CSV. 

Note that if you use quotes with _`trim`_ the behavior is as follows: 

  * When [_`trim`_](functions-parsecsv.html#query-functions-parsecsv-trim) set to `true`, spaces around the separation character (for example a comma) are ignored, but retained within quoted columns. For example: 

csv
        
        117 , " crowdstrike.com, humio.com " , 3.14

Would identify three columns: 

csv
        
        117," crowdstrike.com, humio.com ",3.14

Retaining the spaces at the beginning and end of a quoted column. 

  * Without trim ([_`trim=false`_](functions-parsecsv.html#query-functions-parsecsv-trim)), the spaces around the character separated would be included in the values. For example: 
        
        117 , " crowdstrike.com, humio.com " , 3.14

Would identify the following three columns, as the quotation mark after the space does not start a quoted value, which means that the ',' between the two host names is interpreted as a separator: 

csv
        
        117 , " crowdstrike.com, humio.com  "

In the preceding example, there are spaces after and before columns due to the spaces around the comma separator. 




#### Parse a CSV-encoded Field Into Known Columns

**Parse a CSV-encoded Field into known columns and add it to the event using the parseCsv() function **

##### Query

logscale
    
    
    parseCsv(result, columns=[count, status, completion, precision, sourcetask])

##### Introduction

In this example, the parseCsv() function is used to parse a log line. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         parseCsv(result, columns=[count, status, completion, precision, sourcetask])

Parses a CSV-encoded field into known columns. 

In this example, where the parsed field is from a log line, using `parseCsv(result, columns=[count, status, completion, precision, sourcetask])` will add these fields to the event: 

     * `count: 117`

     * `status: success`

     * `completion: 27%`

     * `precision: 3.14`

  3. Event Result set.




##### Summary and Results

The query is used to parse a CSV-encoded field into known columns. CSV files are often used to exchange data between systems.

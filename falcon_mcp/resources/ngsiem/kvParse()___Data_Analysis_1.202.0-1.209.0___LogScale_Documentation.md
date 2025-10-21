# kvParse() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-kvparse.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Jan 28, 2025

## [`kvParse()`](functions-kvparse.html "kvParse\(\)")

Parse events encoded with key/value pairs into individual fields and values. This function can run an extra key/value parser on events. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-kvparse.html#query-functions-kvparse-as)|  string| optional[a] |  |  Prefix for all resolved field keys.   
[_`excludeEmpty`_](functions-kvparse.html#query-functions-kvparse-excludeempty)|  array of strings| optional[[a]](functions-kvparse.html#ftn.table-functions-kvparse-optparamfn) | `false`|  If the value of a key is empty, exclude the field.   
[_`field`_](functions-kvparse.html#query-functions-kvparse-field)[b]| array of strings| optional[[a]](functions-kvparse.html#ftn.table-functions-kvparse-optparamfn) | `@rawstring`|  Fields that should be key-value parsed.   
[_`onDuplicate`_](functions-kvparse.html#query-functions-kvparse-onduplicate)|  string| optional[[a]](functions-kvparse.html#ftn.table-functions-kvparse-optparamfn) | [`keepLast`](functions-kvparse.html#query-functions-kvparse-onduplicate-option-keeplast)|  Set the value for duplicate keys that exist in the event.   
|  |  | **Values**  
|  |  | [`keepFirst`](functions-kvparse.html#query-functions-kvparse-onduplicate-option-keepfirst)| Keep the first duplicate value  
|  |  | [`keepLast`](functions-kvparse.html#query-functions-kvparse-onduplicate-option-keeplast)| Keep the last duplicate value  
[ _`override`_](functions-kvparse.html#query-functions-kvparse-override)|  boolean| optional[[a]](functions-kvparse.html#ftn.table-functions-kvparse-optparamfn) | `false`|  Override existing values for keys that already exist in the event.   
[_`prefix`_](functions-kvparse.html#query-functions-kvparse-prefix)|  string| optional[[a]](functions-kvparse.html#ftn.table-functions-kvparse-optparamfn) |  |  Prefix for all resolved field keys. Alias of the [_`as`_](functions-kvparse.html#query-functions-kvparse-as) parameter.   
[_`separator`_](functions-kvparse.html#query-functions-kvparse-separator)|  string| optional[[a]](functions-kvparse.html#ftn.table-functions-kvparse-optparamfn) | `=`|  The token that separates the key from the value — a single char only.   
[_`separatorPadding`_](functions-kvparse.html#query-functions-kvparse-separatorpadding)|  string| optional[[a]](functions-kvparse.html#ftn.table-functions-kvparse-optparamfn) | [`unknown`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-unknown)|  Help the function recognize unquoted empty values and parse them by specifying whether there is a whitespace around the key-value separator (typically `=`). For a list of interpretations, see [kvParse() separatorPadding argument handling](functions-kvparse.html#table_functions-kvparse-examples-separatorpadding).   
|  |  | **Values**  
|  |  | [`no`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-no)| Assumes the source does not have a whitespace around the key-value separator, as in `a=1, b=2`  
|  |  | [`unknown`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-unknown)| Whether the source has a padding (whitespace) around values is not recognized.  
|  |  | [`yes`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-yes)| Indicates the source has a whitespace around the key-value separator, as in `a = 1, b = 2`  
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-kvparse.html#query-functions-kvparse-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-kvparse.html#query-functions-kvparse-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     kvParse(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     kvParse(field=["value"])
> 
> These examples show basic structure only.

### [`kvParse()`](functions-kvparse.html "kvParse\(\)") Function Operation

The [`kvParse()`](functions-kvparse.html "kvParse\(\)") function is used to parse key/values of the form: 

  * `key=value`

  * `key="value"`

  * `key='value'`

  * `key = value`




Both key and value can be either quoted using `"` or `'`, or unquoted. If using quotes, the quotes must be terminated. 

For a log line like this: 

ini
    
    
    2017-02-22T13:14:01.917+0000 [main thread] INFO UserService - creating new user id=123, name='john doe' email=john@doe

The key/value parser extracts the fields: 

  * id=123

  * name=john doe

  * email=john@doe




Use the parameter [_`field`_](functions-kvparse.html#query-functions-kvparse-field) to specify which fields should be key/value parsed. Specify [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) to key/value parse the rawstring. 

### [`kvParse()`](functions-kvparse.html "kvParse\(\)") Syntax Examples

  * Key/value parse the log line: 




ini
    
    
    creating new user id=123, name='john doe' email=john@doe.

This will add the fields id=123, name='john doe' and email=john@doe to the event: 

logscale
    
    
    kvParse()

  * Key/value parse the log line: 




ini
    
    
    creating new user id=123, name='john doe' email=john@doe loglevel=ERROR.

Assuming the event already has a loglevel field, replacing the value of that field with `ERROR` requires parameter [_`override=true`_](functions-kvparse.html#query-functions-kvparse-override): 

logscale
    
    
    kvParse(override=true)

  * Key/value parse a nested field. In this example we will use JSON input: 




json
    
    
    {
      "service": "paymentService",
      "type": "payment",
      "metadata": "host=server5,transactionID=123,processingTime=100"
    }

and parse out the key/values in the metadata field: 

logscale
    
    
    parseJson()
    | kvParse(metadata)

  * Key/value parse the log line and export fields with a prefix: 




ini
    
    
    creating new user id=123, name='john doe' email=john@doe.

The following query will add the fields user.id=123, user.name='john doe' and user.email=john@doe to the event: 

logscale
    
    
    kvParse(as="user")

Alternatively, you can obtain the same result by using the [_`prefix`_](functions-kvparse.html#query-functions-kvparse-prefix) parameter: 

logscale
    
    
    kvParse(prefix="user")

  * Key/value parse the log line: 




ini
    
    
    firstname = John middlename = lastname = Doe

This will add the fields firstname=John, middleName= (empty value) and lastname=Doe to the event with a whitespace around the key-value separator (`=`): 

logscale
    
    
    kvParse(separatorPadding="yes")

  * When parsing a key/value line, the impact of spacing between the key, value and equals sign can lead to interpretation differences. The [_`separatorPadding`_](functions-kvparse.html#query-functions-kvparse-separatorpadding) parameter controls this by defining how different patterns are interpreted with and without spacing, as follows: 

**Raw Data** |  **separatorPadding** |  **Field _a_ Value** |  **Field _b_ Value** |  **Notes**  
---|---|---|---|---  
a = b = c |  [`unknown`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-unknown) |  b |  |  c dropped   
a = b = c |  [`yes`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-yes) |  (Empty) |  c |   
a = b = c |  [`no`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-no) |  (Empty) |  (Empty) |  c dropped   
a=b=c |  [`unknown`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-unknown) |  b=c |  |   
a=b=c |  [`yes`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-yes) |  b=c |  |   
a=b=c |  [`no`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-no) |  b=c |  |   
a = b=c |  [`unknown`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-unknown) |  b=c |  |   
a = b=c |  [`yes`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-yes) |  b=c |  |   
a = b=c |  [`no`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-no) |  (Empty) |  c |  c dropped   
a=b = c |  [`unknown`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-unknown) |  b |  |   
a=b = c |  [`yes`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-yes) |  (Empty) |  (Empty) |  c dropped   
a=b = c |  [`no`](functions-kvparse.html#query-functions-kvparse-separatorpadding-option-no) |  b |  |   
  



  * Keep the first value for duplicated keys. 

ini
        
        name='john doe' name='jane doe'

By default [`kvParse()`](functions-kvparse.html "kvParse\(\)") will keep the last seen value. To keep the first value instead, set as follows: 

logscale
        
        kvParse(onDuplicate=keepFirst)

name  
---  
john doe  
  
  * Keep the first value for duplicated keys, with a preset field: if name is set to `alice` beforehand, then _`onDuplicate=keepFirst`_ parameter has no effect and name will keep such preset value. If you want to ignore the preset value, use the [_`override`_](functions-kvparse.html#query-functions-kvparse-override) parameter. 

ini
        
        name='john doe' name='jane doe'

logscale
        
        kvParse(onDuplicate=keepFirst, override=true)

name  
---  
john doe  
  
  * Keep the last value for duplicated keys, with a preset field: if name is set to `alice` beforehand, then the _`onDuplicate=Last`_ parameter has no effect and name will keep such preset value. If you want to ignore the preset value, use the [_`override`_](functions-kvparse.html#query-functions-kvparse-override) parameter. 

ini
        
        name='john doe' name='jane doe'

logscale
        
        kvParse(onDuplicate=keepLast, override=true)

name  
---  
jane doe  
  



### [`kvParse()`](functions-kvparse.html "kvParse\(\)") Examples

Click + next to an example below to get the full details.

#### Parse Key-Value Pairs With Override

**Extract key-value pairs from text allowing field overrides using the[`kvParse()`](functions-kvparse.html "kvParse\(\)") function with [_`override`_](functions-kvparse.html#query-functions-kvparse-override) parameter **

##### Query

logscale
    
    
    kvParse(field=message, override=true)

##### Introduction

In this example, the [`kvParse()`](functions-kvparse.html "kvParse\(\)") function is used with the [_`override`_](functions-kvparse.html#query-functions-kvparse-override) parameter to extract key-value pairs from a message field, with the ability to override any existing fields that have matching names. 

Example incoming data might look like this: 

@timestamp| source| status| message  
---|---|---|---  
2025-08-06T10:00:00Z| webserver1| 200| user=john.doe status=active role=admin sessionID=12345  
2025-08-06T10:00:01Z| webserver2| 404| user=jane.smith status=inactive role=user sessionID=67890  
2025-08-06T10:00:02Z| webserver1| 500| user=bob.wilson status=blocked role=guest sessionID=11111  
2025-08-06T10:00:03Z| webserver3| 200| user=alice.jones status=active role=admin sessionID=22222  
2025-08-06T10:00:04Z| webserver2| 200| user=mike.brown status=pending role=user sessionID=33333  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         kvParse(field=message, override=true)

Parses key-value pairs from the [message](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) field containing key-value formatted text. 

The [_`field`_](functions-kvparse.html#query-functions-kvparse-field) parameter specifies which field contains the key-value pairs to parse. The [_`override`_](functions-kvparse.html#query-functions-kvparse-override) parameter set to `true` allows the parsed values to overwrite any existing fields with matching names. Without the [_`override`_](functions-kvparse.html#query-functions-kvparse-override) parameter, the function would skip creating fields that already exist in the event. 

  3. Event Result set.




##### Summary and Results

The query is used to extract structured fields from key-value formatted text while allowing the new values to replace existing field values. 

This query is useful, for example, to parse log messages containing key-value pairs where the extracted values should take precedence over existing fields, or when reprocessing events where field values need to be updated from the message content. 

Sample output from the incoming example data: 

@timestamp| source| message| user| status| role| sessionID  
---|---|---|---|---|---|---  
2025-08-06T10:00:00Z| webserver1| user=john.doe status=active role=admin sessionID=12345| john.doe| active| admin| 12345  
2025-08-06T10:00:01Z| webserver2| user=jane.smith status=inactive role=user sessionID=67890| jane.smith| inactive| user| 67890  
2025-08-06T10:00:02Z| webserver1| user=bob.wilson status=blocked role=guest sessionID=11111| bob.wilson| blocked| guest| 11111  
2025-08-06T10:00:03Z| webserver3| user=alice.jones status=active role=admin sessionID=22222| alice.jones| active| admin| 22222  
2025-08-06T10:00:04Z| webserver2| user=mike.brown status=pending role=user sessionID=33333| mike.brown| pending| user| 33333  
  
Note that the original [status](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-aggregatealert-alert.html) field values are overwritten by the parsed values from the message, and new fields ([user](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-permissionassignment-userassignments.html), role, sessionID) are created from the parsed key-value pairs. 

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

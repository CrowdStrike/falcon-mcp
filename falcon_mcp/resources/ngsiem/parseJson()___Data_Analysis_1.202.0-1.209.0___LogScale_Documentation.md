# parseJson() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-parsejson.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`parseJson()`](functions-parsejson.html "parseJson\(\)")

Parses data or a field as JSON, converting the data into named fields and arrays within the event. Use `parseJson(field=@rawstring)` to parse the original ingested rawstring into JSON. Use the [_`prefix`_](functions-parsejson.html#query-functions-parsejson-prefix) parameter to prefix the names of the extracted fields. 

Furthermore, to exclude some of the extracted fields, use the [_`exclude`_](functions-parsejson.html#query-functions-parsejson-exclude) parameter to specify the JSON object structure to be excluded. For example, use `parseJson(field=input,exclude=a.b.c)` to exclude `c` and all of its descendants (a path-based exclusion) or use `parseJson(field=input,exclude="a.b[*].c")` to exclude all `c` inside the array `b` (array-based exclusion). Note that all non-nested fields are also excluded. 

Use the [_`include`_](functions-parsejson.html#query-functions-parsejson-include) parameter if you need to keep certain descendants of an otherwise excluded path or an excluded non-nested field in the output. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`exclude`_](functions-parsejson.html#query-functions-parsejson-exclude)|  array of strings| optional[a] | `[]`|  Removes specified JSON fields from the output. Use on fields that should be excluded from the result. Supports dot-pathing and array wildcards. If used with prefix, the excluded fields will use the specified prefix. The exclusion works as a wildcard match for the given field; for example, the value `query` will match both nested fields (like query.string) and similarly non-nested named fields (like queryString, [queryStart](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-aggregatealert-alert.html), and [queryEnd](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-aggregatealert-alert.html)). To retain specific fields while excluding others, use the [_`include`_](functions-parsejson.html#query-functions-parsejson-include) parameter.   
[_`excludeEmpty`_](functions-parsejson.html#query-functions-parsejson-excludeempty)|  boolean| optional[[a]](functions-parsejson.html#ftn.table-functions-parsejson-optparamfn) | [`false`](functions-parsejson.html#query-functions-parsejson-excludeempty-option-false)|  Whether to exclude if the field is empty.   
|  |  | **Values**  
|  |  | [`false`](functions-parsejson.html#query-functions-parsejson-excludeempty-option-false)| Do not exclude the field, even if the value is empty  
|  |  | [`true`](functions-parsejson.html#query-functions-parsejson-excludeempty-option-true)| Exclude the field if the value is empty  
[ _`field`_](functions-parsejson.html#query-functions-parsejson-field)[b]| string| required | `@rawstring`|  Fields that should be parsed as JSON.   
[_`handleNull`_](functions-parsejson.html#query-functions-parsejson-handlenull)|  string| optional[[a]](functions-parsejson.html#ftn.table-functions-parsejson-optparamfn) | [`keep`](functions-parsejson.html#query-functions-parsejson-handlenull-option-keep)|  How null values are handled.   
|  |  | **Values**  
|  |  | [`discard`](functions-parsejson.html#query-functions-parsejson-handlenull-option-discard)| Discard the null value and field null value with an empty string `""`  
|  |  | [`empty`](functions-parsejson.html#query-functions-parsejson-handlenull-option-empty)| Replaces a null value with an empty string `""`  
|  |  | [`keep`](functions-parsejson.html#query-functions-parsejson-handlenull-option-keep)| Converts the value to the `"null"` string  
[ _`include`_](functions-parsejson.html#query-functions-parsejson-include)|  array of strings| optional[[a]](functions-parsejson.html#ftn.table-functions-parsejson-optparamfn) | `[]`|  Retains specific descendants of excluded paths. Use on fields that should be included, even if they had been previously excluded by use of [_`exclude`_](functions-parsejson.html#query-functions-parsejson-exclude). Supports dot-pathing and array wildcards. If used with [_`prefix`_](functions-parsejson.html#query-functions-parsejson-prefix), the include fields will also use the specified prefix.   
[_`prefix`_](functions-parsejson.html#query-functions-parsejson-prefix)|  string| optional[[a]](functions-parsejson.html#ftn.table-functions-parsejson-optparamfn) | `blank`|  Prefix the name of the extracted JSON fields with the value of this parameter.   
[_`removePrefixes`_](functions-parsejson.html#query-functions-parsejson-removeprefixes)|  array of strings| optional[[a]](functions-parsejson.html#ftn.table-functions-parsejson-optparamfn) | `[]`|  Prefixes that should be removed from the names of the extracted JSON fields; supports dot-pathing. If multiple prefixes are supplied, the longest matching prefix will be used.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-parsejson.html#query-functions-parsejson-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-parsejson.html#query-functions-parsejson-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     parseJson("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     parseJson(field="value")
> 
> These examples show basic structure only.

### [`parseJson()`](functions-parsejson.html "parseJson\(\)") Function Operation

When parsing JSON, the following apply: 

  * When [_`excludeEmpty=true`_](functions-parsejson.html#query-functions-parsejson-excludeempty) is used, the key/value pairs will be discarded completely whenever the original json contains `foo: ""`

  * When the JSON contains `foo: null`, using [_`handleNull=discard`_](functions-parsejson.html#query-functions-parsejson-handlenull) then the entire key/value pair is discarded, regardless of the setting for [_`excludeEmpty`_](functions-parsejson.html#query-functions-parsejson-excludeempty)




### [`parseJson()`](functions-parsejson.html "parseJson\(\)") Syntax Examples

If the whole event sent to LogScale is JSON like: 

javascript
    
    
    {"service": "userService", "timestamp": "2017-12-18T20:39:35Z", "msg": "user with id=47 logged in"}

logscale
    
    
    parseJson()
    | parseTimestamp(field=timestamp)

If a field in the incoming event contains JSON like: 

Raw Events

2017-12-18T20:39:35Z user id=47 logged in details="{"name": "Peter", "email": "peter@test.com", "id":47}"  
---  
  
In the example below the details field is extracted using the [`kvParse()`](functions-kvparse.html "kvParse\(\)") function and then parseJson is used to parse the JSON inside the details field. 

logscale
    
    
    /(?<timestamp>\S+)/
    | parseTimestamp(field=timestamp)
    | kvParse()
    | parseJson(field=details)

It is possible to prefix names of the extracted JSON fields. This can be useful for avoiding collisions with existing fields with the same name. For example the input line: 

logscale
    
    
    details="{"email": "foo@test.com", "name": "Peter"}"

Could be parsed into these fields: `user.email=foo@test.com`, `user.name=Peter`. 

logscale
    
    
    kvParse()
    | parseJson(field=details, prefix="user.")

It is possible to remove prefixes as well. For example the input line: 

logscale
    
    
    details="{"a": { "b": { "c": { "d": "e", "f": "g"}, "h": "i" }, "j": "k" } }"

If the JSON object is expanded: 

json
    
    
    {
       "a" : {
          "b" : {
             "c" : {
                "d" : "e",
                "f" : "g"
             },
             "h" : "i"
          },
          "j" : "k"
       }
    }

Would be parsed into these fields with the following function if the `a` prefix is removed: `b.c.d=e`, `b.c.f=g`, `b.h=i`, `j=k`. 

logscale
    
    
    kvParse()
    | parseJson(field=details, removePrefixes=a.)

It is possible to exclude extracted fields. This can be useful for removing sensitive data or, for example, large arrays. For example, the input line: 

logscale
    
    
    details="{"a": { "b": { "c": { "d": "e", "f": "g"}, "h": "i" }, "j": "k" } }"

If the raw JSON is formatted: 

json
    
    
    {
       "a" : {
          "b" : {
             "c" : {
                "d" : "e",
                "f" : "g"
             },
             "h" : "i"
          },
          "j" : "k"
       }
    }

The JSON string would be parsed into these fields: `a.b.h=i`, `a.j=k` but not, for example, `a.b.c.d=e`

logscale
    
    
    kvParse()
    | parseJson(field=details, exclude=a.b.c)

It is also possible to exclude extracted fields within arrays. For example the input line: 

logscale
    
    
    details="{"a": { "b": [{ "c": { "d": 1 }, "e": "f" }, { "c": { "d": 2 }, "e": "h" }] } }"

As a formatted JSON string: 

json
    
    
    {
       "a" : {
          "b" : [
             {
                "c" : {
                   "d" : 1
                },
                "e" : "f"
             },
             {
                "c" : {
                   "d" : 2
                },
                "e" : "h"
             }
          ]
       }
    }

Would be parsed into these fields: `a.b[0].e=f`, `a.b[1].e=h` but not, for example, `a.b[0].c.d=1`. 

logscale
    
    
    kvParse()
    | parseJson(field=details, exclude="a.b[*].c")

It is possible to include fields that had previously been excluded. For example the input line: 

logscale
    
    
    details="{"a": { "b": { "c": { "d": 1, "e": 2} } } }"

Would be parsed into these fields: `a.b.c.e=2`. 

logscale
    
    
    kvParse()
    | parseJson(field=details, exclude=a.b.c, include=a.b.c.e)

If includes and excludes are used with prefix, you need to prefix the includes and excludes as well. For example the input line: 

logscale
    
    
    details="{"a": { "b": { "c": { "d": 1, "e": 2} } } }"

Would be parsed into these fields: `x.a.b.c.e=2`. 

logscale
    
    
    kvParse()
    | parseJson(field=details, prefix=x., exclude=x.a.b.c, include=x.a.b.c.e)

### [`parseJson()`](functions-parsejson.html "parseJson\(\)") Examples

Click + next to an example below to get the full details.

####  Parse JSON Content With Specific Parameters 

**Parse JSON content with specific parameters while excluding the actual query content using the[`parseJson()`](functions-parsejson.html "parseJson\(\)") **

##### Query

logscale
    
    
    #type=audit-log
    | /"type":"alert.update"/
    | parseJson(exclude="query", include="queryStart")

##### Introduction

In this example, the [`parseJson()`](functions-parsejson.html "parseJson\(\)") function is used to search audit logs for alert update events, specifically looking at the queryStart field (timestamp), while excluding the actual query content (query.xxx). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #type=audit-log

Filters for all events from repository `audit-log`. 

  3. logscale
         
         | /"type":"alert.update"/

Filters for events (audit logs) where the @rawstring field contains the string `/"type":"alert.update"/`. 

  4. logscale
         
         | parseJson(exclude="query", include="queryStart")

With specific parameters set, parses the JSON content excluding the query field and including only the queryStart field. 

The exclusion works as a wildcard match for the given field; for example, the value `query` will match both nested fields (like query.string) and similarly non-nested named fields (like queryString, queryStart, and queryEnd). In this example, to retain the specific non-nested field queryStart while excluding the others, the [_`include`_](functions-parsejson.html#query-functions-parsejson-include) parameter is used. 

  5. Event Result set.




##### Summary and Results

The query is used to search audit logs for alert update events, specifically looking at the non-nested queryStart field, while excluding the actual query content (query.xxx). The query is useful if, for example, you want to review alert activity without the overhead of full query contents, track temporal patterns in alert updates, or investigate alert timing issues further. 

#### Create Two Temporary Events for Troubleshooting - Example 2

**Create two temporary events for testing or troubleshooting using the[`createEvents()`](functions-createevents.html "createEvents\(\)") function with [`parseJson()`](functions-parsejson.html "parseJson\(\)") **

##### Query

logscale
    
    
    createEvents(["{\"animal\":{\"kind\":\"dog\", \"weight\":7.0}}", "{\"animal\":{\"kind\":\"cat\", \"weight\":4.2}}"])
    | parseJson()

##### Introduction

In this example, the [`createEvents()`](functions-createevents.html "createEvents\(\)") function is combined with [`parseJson()`](functions-parsejson.html "parseJson\(\)") to parse @rawstring as JSON. 

Example incoming data might look like this: 

json
    
    
    [
    {"animal":{"kind":"dog", "weight":7.0}},
    {"animal":{"kind":"cat", "weight":4.2}}
    ]

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         createEvents(["{\"animal\":{\"kind\":\"dog\", \"weight\":7.0}}", "{\"animal\":{\"kind\":\"cat\", \"weight\":4.2}}"])

Creates two temporary events. An event with `dog` and an event with `cat`. 

  3. logscale
         
         | parseJson()

Parses specified fields as JSON. 

  4. Event Result set.




##### Summary and Results

The query is used to create temporary events and parse the @rawstring as JSON. 

Sample output from the incoming example data: 

@timestamp| animal.kind| animal.weight  
---|---|---  
1733311547717| dog| 7.0  
1733311547717| cat| 4.2  
  
#### Create Two Temporary Events for Troubleshooting - Example 3

**Create two temporary events for testing or troubleshooting using the[`createEvents()`](functions-createevents.html "createEvents\(\)") function with [`kvParse()`](functions-kvparse.html "kvParse\(\)") **

##### Query

logscale
    
    
    createEvents(["animal=dog weight=7.0", "animal=cat weight=4.2"])
    | kvParse()

##### Introduction

In this example, the [`createEvents()`](functions-createevents.html "createEvents\(\)") function is combined with [`kvParse()`](functions-kvparse.html "kvParse\(\)") to parse @rawstring as JSON. 

Example incoming data might look like this: 

animal=dog weight=7.0  
---  
animal=cat weight=4.2  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         createEvents(["animal=dog weight=7.0", "animal=cat weight=4.2"])

Creates two temporary events. An event with `dog` and an event with `cat`. 

  3. logscale
         
         | kvParse()

Parses the string into key value pairs. 

  4. Event Result set.




##### Summary and Results

The query is used to create temporary events and parse the @rawstring as key value pairs. 

Sample output from the incoming example data: 

animal| weight  
---|---  
dog| 7.0  
cat| 4.2

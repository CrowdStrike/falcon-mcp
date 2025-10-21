# wildcard() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-wildcard.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Mar 4, 2024

## [`wildcard()`](functions-wildcard.html "wildcard\(\)")

Performs a wildcard pattern search with optional case insensitivity. 

The primary purpose is to make it easier to do case insensitive searching across fields and events using a wildcard pattern instead of a regular expression. This is especially useful for users unfamiliar with regular expressions. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`field`_](functions-wildcard.html#query-functions-wildcard-field)|  array of strings| optional[a] |  |  Determines which fields the pattern should search in. When no fields are given, all fields of the original, unmodified event will be searched.   
[_`ignoreCase`_](functions-wildcard.html#query-functions-wildcard-ignorecase)|  boolean| optional[[a]](functions-wildcard.html#ftn.table-functions-wildcard-optparamfn) | `false`|  Allows for case-insensitive searching.   
[_`includeEverythingOnAsterisk`_](functions-wildcard.html#query-functions-wildcard-includeeverythingonasterisk)|  boolean| optional[[a]](functions-wildcard.html#ftn.table-functions-wildcard-optparamfn) | `false`|  Allows to output all events (even those missing the fields specified in [_`field`_](functions-wildcard.html#query-functions-wildcard-field)) if [_`pattern`_](functions-wildcard.html#query-functions-wildcard-pattern) is set to `*`.   
[_`pattern`_](functions-wildcard.html#query-functions-wildcard-pattern)[b]| string| required |  |  Wildcard (glob) pattern to search for.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`pattern`_](functions-wildcard.html#query-functions-wildcard-pattern) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`pattern`_](functions-wildcard.html#query-functions-wildcard-pattern) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     wildcard("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     wildcard(pattern="value")
> 
> These examples show basic structure only.

Hide negatable operation for this function

Show negatable operation for this function

> Negatable Function Operation
> 
> This function is negatable, implying the inverse of the result. For example:
> 
> logscale Syntax
>     
>     
>     !wildcard()
> 
> Or:
> 
> logscale Syntax
>     
>     
>     not wildcard()
> 
> For more information, see [Negating the Result of Filter Functions](syntax-operators.html#syntax-operators-negate "Negating the Result of Filter Functions").

### [`wildcard()`](functions-wildcard.html "wildcard\(\)") Function Operation

Depending on the [_`field`_](functions-wildcard.html#query-functions-wildcard-field) and [_`ignoreCase`_](functions-wildcard.html#query-functions-wildcard-ignorecase) arguments, the [`wildcard()`](functions-wildcard.html "wildcard\(\)") behavior can vary: 

  * Whenever _`ignoreCase`_ is `true`: 

    * the search will be case-insensitive; for example, if the given pattern is `*http*` then this will match any upper/lower-case combination of HTTP. 

    * the search is equivalent to a case-insensitive regex, either on the given fields, or as an unanchored freetext regex that searches the entire, original, unmodified event — see the example below [Search Fields Through a Given Pattern - Example 5](functions-wildcard.html#functions-wildcard-examples-wildcard-5 "Search Fields Through a Given Pattern - Example 5"). 

  * Whenever [_`ignoreCase`_](functions-wildcard.html#query-functions-wildcard-ignorecase) is `false`, the search is equivalent to a wildcard-search, either on the given fields, or as an unanchored, freetext search on the entire, original, unmodified event. 




To sum up: 

**Table: wildcard() behavior**

[_`ignoreCase`_](functions-wildcard.html#query-functions-wildcard-ignorecase) Parameter |  field is `[]` or not specified |  field is specified as `[field1, field2, …, ]`  
---|---|---  
`ignoreCase = false` |  `*<pattern>*` |  `field1=<pattern>` OR `field2=<pattern> `OR …   
`ignoreCase = true` |  `/<patternAsRegex>/i` |  `field1=/<patternAsRegex>/i` OR `field2=/<patternAsRegex>/i` OR …(as unanchored regexes)   
  
  


The [_`includeEverythingOnAsterisk`_](functions-wildcard.html#query-functions-wildcard-includeeverythingonasterisk) argument can also affect the [`wildcard()`](functions-wildcard.html "wildcard\(\)") behavior: 

  * Whenever [_`includeEverythingOnAsterisk`_](functions-wildcard.html#query-functions-wildcard-includeeverythingonasterisk) is `true` and [_`pattern`_](functions-wildcard.html#query-functions-wildcard-pattern) is set to `*`, all events are returned — even events that are missing the field specified in [_`field`_](functions-wildcard.html#query-functions-wildcard-field). 

  * Whenever [_`includeEverythingOnAsterisk`_](functions-wildcard.html#query-functions-wildcard-includeeverythingonasterisk) is `false` or omitted, the behavior does not change that is, events without the field specified in [_`field`_](functions-wildcard.html#query-functions-wildcard-field) are excluded. See [Include All Fields with Any Given Pattern](functions-wildcard.html#functions-wildcard-examples-wildcard-8 "Include All Fields with Any Given Pattern") for an example. 




### Note

For performance reasons, only set _`ignoreCase`_ to `true` if necessary; the case-insensitive search might be up to 2x slower than having this parameter set to `false` — depending on the search pattern and the data. 

The following query: 

logscale
    
    
    wildcard(field=myField, pattern="*foobar*")

can be written as: 

logscale
    
    
    myField =~ wildcard("*foobar*")

This is because _`pattern`_ is the implicit parameter, and parameters named _`field`_ can be used with the _`=~`_ shorthand syntax in general in the query language. 

`wildcard(...)` can be negated by using `not wildcard(...)`, this finds all events that did not match the given pattern. 

### [`wildcard()`](functions-wildcard.html "wildcard\(\)") Examples

Click + next to an example below to get the full details.

#### Drop Events Based on Specific Field Values or Patterns

**Drop events based on specific field values or patterns during normal searching using the[`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function with case statement **

##### Query

logscale
    
    
    case {
    fielda = badresult | dropEvent();
    fieldb = badresult | dropEvent();
    wildcard("badip", field[fieldc, fieldd] | dropEvent())
    }

##### Introduction

In this example, the [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function is used within normal searching with a case statement to drop events based on specific values and patterns. When used within normal searching, the [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function is simply an alias for `false` \- it behaves the same as false. It filters out specific events from the results. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         case {
         fielda = badresult | dropEvent();
         fieldb = badresult | dropEvent();
         wildcard("badip", field[fieldc, fieldd] | dropEvent())
         }

Starts a `case` statement containing the following three conditions: 

If fielda equals `badresult`, drop the event. 

If fieldb equals `badresult`, drop the event. 

If either fieldc or fieldd contains the string `badip` (using wildcard matching), drop the event. 

Each condition uses the [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function as the action to take when the condition is met. The [`wildcard()`](functions-wildcard.html "wildcard\(\)") function is used in the third condition to perform pattern matching with wildcards against multiple fields specified in the array notation `field[fieldc, fieldd]`. 

  3. Event Result set.




##### Summary and Results

This query is used to drop events based on specific field values or patterns. In all three cases, the events that contain the filtered information will be removed from the results. This is useful, for example, for event processing or log filtering. 

#### Find Fields With Data in Class

****

##### Query

**Search Repository:** [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html)

logscale
    
    
    wildcard(field=class,pattern="*Data*")
    | groupBy(class)

##### Introduction

Find all events containing any `Data` string in their class, and count the occurrences for each class that is found. For example, it can be used to get a list of events that have items such as DataIngestRateMonitor, or LocalDatasource. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         wildcard(field=class,pattern="*Data*")

Searches the incoming data to list all events having Data (and everything around it) in their string. 

  3. logscale
         
         | groupBy(class)

Takes the events extracted from the search and groups them by the class field. 

  4. Event Result set.




##### Summary and Results

The result is an aggregated count of all events matching anything with `Data` (with one or more characters before or after), in the class field. 

class| _count  
---|---  
c.h.c.c.ChatterDataMemoryStatusLoggerJob$| 283  
c.h.d.DataIngestRateMonitor$| 7504  
c.h.d.LocalDatasource$| 10352  
c.h.d.q.EmptyIdleDatasourcesCleaner| 3  
c.h.e.e.Datasource$| 3947  
c.h.e.e.Datasources$| 4  
c.h.e.f.DataSnapshotOps$| 662  
c.h.e.f.DataWithGlobal| 7254  
c.h.j.CleanupDatasourceFilesJob| 141  
c.h.j.DataSyncJobImpl$| 46594  
c.h.j.DatasourceRehashingJob$| 32  
c.h.k.ChatterDataDistributionKafka$| 107  
  
#### Find Fields With S3Bucket in Class

****

##### Query

**Search Repository:** [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html)

logscale
    
    
    wildcard(field=class, pattern="*S3Bucket*", ignoreCase=true)
    | groupBy(class)

##### Introduction

Find all events containing any `S3Bucket` item (and all before and after) in their class, and count the occurrences for each class that is found. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         wildcard(field=class, pattern="*S3Bucket*", ignoreCase=true)

Searches the incoming data to list all events having S3Bucket (or everything around it, case-insensitive) in their string. 

  3. logscale
         
         | groupBy(class)

Takes the events extracted from the search and group them by the class field. 

  4. Event Result set.




##### Summary and Results

The result is an aggregated count of all events matching anything with `S3Bucket`, case-insensitive, in the class field. 

class| _count  
---|---  
c.h.b.s.S3BucketStorageCleaningJob| 197  
c.h.b.s.S3BucketStorageFileUpLoader| 2329  
c.h.b.s.S3BucketStorageUploadJob| 3869  
  
![Searching S3Bucket with wildcard\(\)](images/query-functions/wildcard-s3-bucket.png)  
---  
  
**Figure 152. Search S3Bucket With wildcard()**

  


#### Include All Fields with Any Given Pattern

****

##### Query

logscale
    
    
    wildcard(field=animal, pattern=*, includeEverythingOnAsterisk=true)

##### Introduction

Given the following three events: 

animal = horse  
---  
animal = seahorse  
machine = car  
  
Match all events in the result set — even those missing the animal field specified in [_`field`_](functions-wildcard.html#query-functions-wildcard-field). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         wildcard(field=animal, pattern=*, includeEverythingOnAsterisk=true)

Set [_`pattern`_](functions-wildcard.html#query-functions-wildcard-pattern) to `*` and include the [_`includeEverythingOnAsterisk`_](functions-wildcard.html#query-functions-wildcard-includeeverythingonasterisk) parameter in the query. 

  3. Event Result set.




##### Summary and Results

The result is a list of the following accepted events: 

field| value  
---|---  
animal| horse  
animal| seahorse  
machine| car  
  
Without [_`includeEverythingOnAsterisk`_](functions-wildcard.html#query-functions-wildcard-includeeverythingonasterisk) ([_`includeEverythingOnAsterisk=false`_](functions-wildcard.html#query-functions-wildcard-includeeverythingonasterisk)), only events with `animal` as the argument would match. For example: 

field| value  
---|---  
animal| horse  
animal| seahorse  
  
#### Search Fields Through a Given Pattern - Example 1

****

##### Query

logscale
    
    
    wildcard(field=animal, pattern=horse, ignoreCase=false)

##### Introduction

Given the following events: 

field| value  
---|---  
animal| horse  
animal| Horse  
animal| duck  
animal| HORSES  
animal| crazy hOrSe  
animal| hooorse  
animal| dancing with horses  
  
Finds events where the field animal contains the exact value `horse`, and makes it case-sensitive. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         wildcard(field=animal, pattern=horse, ignoreCase=false)

Searches elements in the field animal that match `horse`. 

  3. Event Result set.




##### Summary and Results

The result is a list of events where field animal has the exact value `horse`. 

The query used is equivalent to `animal="horse"` . 

#### Search Fields Through a Given Pattern - Example 2

****

##### Query

logscale
    
    
    wildcard(field=animal, pattern=horse, ignoreCase=true)

##### Introduction

Given the following events: 

field| value  
---|---  
animal| horse  
animal| Horse  
animal| duck  
animal| HORSES  
animal| crazy hOrSe  
animal| hooorse  
animal| dancing with horses  
  
Finds events where the field animal contains the value `horse`, and makes it case-insensitive. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         wildcard(field=animal, pattern=horse, ignoreCase=true)

Searches elements in the field animal that match `horse`, case-insensitive. 

  3. Event Result set.




##### Summary and Results

The result is a list of events where field animal contains any capitalization of `horse` (`HORSE`, `hOrsE`, `Horse`, etc.). 

The query used is equivalent to `animal=/\Ahorse\z/i`. 

Note that it is anchored. 

#### Search Fields Through a Given Pattern - Example 3

****

##### Query

logscale
    
    
    wildcard(field=animal, pattern=*h*rse*, ignoreCase=true)

##### Introduction

Given the following events: 

field| value  
---|---  
animal| horse  
animal| Horse  
animal| duck  
animal| HORSES  
animal| crazy hOrSe  
animal| hooorse  
animal| dancing with horses  
  
Finds events where field animal matches the given pattern, and it's case-insensitive: 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         wildcard(field=animal, pattern=*h*rse*, ignoreCase=true)

Searches elements in the field animal that match `*h*rse*`. 

  3. Event Result set.




##### Summary and Results

The result is a list of the following accepted events: 

animal  
---  
horse  
Horse  
HORSES  
crazy hOrSe  
dancing with horses  
hooorse  
  
The query used is equivalent to: `animal=/h.*rse/i` . 

Note that it is unanchored. 

#### Search Fields Through a Given Pattern - Example 4

****

##### Query

logscale
    
    
    wildcard(pattern=horse, ignoreCase=false)

##### Introduction

Given the following events: 

field| value  
---|---  
animal| horse  
mammal| Horse  
mammal| wild horses  
animal| human  
mammal| HORSES  
animal| duck  
mammal| dog  
animal| dancing with horses  
  
Find events that contain `horse` in any field, case-sensitive: 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         wildcard(pattern=horse, ignoreCase=false)

Searches the original, unmodified event for the string `horse`. 

  3. Event Result set.




##### Summary and Results

The result accepts the events with `horse`, `wild horses` and `dancing with horses`. This query is equivalent to the freetext search `"horse"` . 

#### Search Fields Through a Given Pattern - Example 5

****

##### Query

logscale
    
    
    wildcard(pattern=horse, ignoreCase=true)

##### Introduction

Given the following events: 

field| value  
---|---  
animal| horse  
animal| Horse  
animal| duck  
animal| HORSES  
animal| crazy hOrSe  
animal| hooorse  
animal| dancing with horses  
  
Finds events that contain `horse`, case-insensitive: 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         wildcard(pattern=horse, ignoreCase=true)

Searches the original, unmodified event for the string `horse`, case-insensitive. 

  3. Event Result set.




##### Summary and Results

The result is a list of the following accepted events: 

animal  
---  
horse  
Horse  
HORSES  
crazy hOrSe  
dancing with horses  
  
This query is equivalent to the freetext regex `/horse/i` . 

#### Search Multiple Fields Through a Given Pattern

****

##### Query

logscale
    
    
    wildcard(field=[plant,animal], pattern=horse, ignoreCase=false)

##### Introduction

Given the following events: 

field| value  
---|---  
animal| horse  
animal| Horse  
animal| duck  
animal| HORSES  
animal| crazy hOrSe  
animal| hooorse  
animal| dancing with horses  
plant| daisy  
plant| horseflower  
  
Search multiple fields for a value allows you to find events where the field animal or plant contains the exact value `horse`, and makes it case-sensitive. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         wildcard(field=[plant,animal], pattern=horse, ignoreCase=false)

Searches elements in the fields animal and plant that match `horse`. 

  3. Event Result set.




##### Summary and Results

The result is a list of events where either the field animal or plant has the exact value `horse`. 

The query used is equivalent to `animal="horse" plant="horse"`.

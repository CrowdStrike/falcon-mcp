# text:contains() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-text-contains.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Jul 23, 2025

## [`text:contains()`](functions-text-contains.html "text:contains\(\)")

Tests if a specific substring is present within a given string. It takes two arguments: [_`string`_](functions-text-contains.html#query-functions-text-contains-string) and [_`substring`_](functions-text-contains.html#query-functions-text-contains-substring), both of which can be provided as plain text, field values, or results of an expression. 

Similar to the [`test()`](functions-test.html "test\(\)") function, [`text:contains()`](functions-text-contains.html "text:contains\(\)") returns the events where the condition is met. The function can be negated to find the events, where the substring is not found in the main string. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`string`_](functions-text-contains.html#query-functions-text-contains-string)[a]| expression| required |  |  The string where the search is performed.   
[_`substring`_](functions-text-contains.html#query-functions-text-contains-substring)|  expression| required |  |  The string that is searched for in the [_`string`_](functions-text-contains.html#query-functions-text-contains-string) parameter.   
[a] The parameter name [_`string`_](functions-text-contains.html#query-functions-text-contains-string) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`string`_](functions-text-contains.html#query-functions-text-contains-string) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     text:contains("value",substring="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     text:contains(string="value",substring="value")
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
>     !text:contains()
> 
> Or:
> 
> logscale Syntax
>     
>     
>     not text:contains()
> 
> For more information, see [Negating the Result of Filter Functions](syntax-operators.html#syntax-operators-negate "Negating the Result of Filter Functions").

### [`text:contains()`](functions-text-contains.html "text:contains\(\)") Syntax Examples

  * logscale
        
        text:contains(string=name,substring="download")

name is the name of a field and `download` is the string, and that would be equivalent to: 

logscale
        
        name = /download/

  * logscale
        
        text:contains("foobar", substring="oba")

is true (`oba` does exist in the string) 

logscale
        
        text:contains("foobar", substring="abo")

is false (`abo` does not exist in the string) 

  * Check two fields, for example, thread and class: 

logscale
        
        text:contains(thread, substring="bucket")
        | text:contains(class,substring="Storage")
        | groupBy([thread,class])

which will produce the following output: 

Field thread| Field class| Count  
---|---|---  
bucket-clean-obsoletes-s3| c.h.b.BucketStorageCleaningJob| 432  
bucket-entity-config| c.h.b.BucketStorageEntityConfigLogger| 48  
bucket-storage-download| c.h.b.BucketStorageDownloadJobImpl| 8155  
bucket-storage-prefetch| c.h.b.BucketStoragePrefetchJob| 1436  
bucket-storage-transfer-scheduler| c.h.b.BucketStorageUploadJob| 2666  
bucket-storage-upload| c.h.b.BucketStorageUploadJob| 1333  
delete-bucket-segments| c.h.b.BucketStorageDeleteObsoleteSegmentsJob| 2574  
  
  * As in the previous example, check and count the fields thread and class, but exclude the `download` substring in the field thread. This can be done by negating the function, as in the following query: 

logscale
        
        text:contains(thread, substring="bucket")
        | text:contains(class,substring="Storage")
        | !text:contains(thread, substring="download")
        | groupBy([thread,class])

which will produce this result: 

Field thread| Field class| Count  
---|---|---  
bucket-clean-obsoletes-s3| c.h.b.BucketStorageCleaningJob| 432  
bucket-entity-config| c.h.b.BucketStorageEntityConfigLogger| 48  
bucket-storage-prefetch| c.h.b.BucketStoragePrefetchJob| 1436  
bucket-storage-transfer-scheduler| c.h.b.BucketStorageUploadJob| 2666  
bucket-storage-upload| c.h.b.BucketStorageUploadJob| 1333  
delete-bucket-segments| c.h.b.BucketStorageDeleteObsoleteSegmentsJob| 2574

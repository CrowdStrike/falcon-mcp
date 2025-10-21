# rename() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-rename.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`rename()`](functions-rename.html "rename\(\)")

This function renames one or more fields. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-rename.html#query-functions-rename-as)|  string| optional[a] |  |  The new name of the field; it is used when a single field name is given in _`field`_.   
[_`field`_](functions-rename.html#query-functions-rename-field)[b]| string or array, array of arrays of strings| required |  |  The field to rename, if a new field name is given in [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters"). From v1.106.0, multiple fields can be given using an array of old/new field name pairs: `[[oldName1,newName1], [oldName2,newName2]]`.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-rename.html#query-functions-rename-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-rename.html#query-functions-rename-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     rename("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     rename(field="value")
> 
> These examples show basic structure only.

### Note

When a field is renamed to a field that already exists, the existing field and its content is overwritten by the new field. The same happens when the field is renamed through [field aliasing](searching-data-field-aliasing.html "Field Aliasing"). 

Old fields are removed from the event stream which can add overhead during processing. Copying to a new field using: 

logscale
    
    
    newfield := oldfield

is more efficient, but retains the old field in the event set. 

### [`rename()`](functions-rename.html "rename\(\)") Examples

Click + next to an example below to get the full details.

#### Rename Fields

**Rename fields to more readable names using the[`rename()`](functions-rename.html "rename\(\)") function **

##### Query

logscale
    
    
    rename(field=[[src_ip, source_address], [dst_ip, destination_address], [src_port, source_port], [dst_port, destination_port]])

##### Introduction

In this example, the [`rename()`](functions-rename.html "rename\(\)") function is used to rename multiple fields to more readable names. 

Example incoming data might look like this: 

timestamp| src_ip| dst_ip| src_port| dst_port| protocol| bytes_sent| bytes_received  
---|---|---|---|---|---|---|---  
2025-04-01T07:00:00Z| 192.168.1.100| 10.0.0.50| 52431| 443| TCP| 1024| 2048  
2025-04-01T07:00:01Z| 172.16.0.25| 8.8.8.8| 33221| 53| UDP| 64| 512  
2025-04-01T07:00:02Z| 192.168.1.150| 172.16.0.100| 49223| 80| TCP| 2048| 4096  
2025-04-01T07:00:03Z| 10.0.0.75| 192.168.1.1| 55678| 22| TCP| 512| 1024  
2025-04-01T07:00:04Z| 192.168.1.200| 1.1.1.1| 44556| 53| UDP| 64| 512  
2025-04-01T07:00:05Z| 172.16.0.50| 192.168.1.25| 51234| 3389| TCP| 4096| 8192  
2025-04-01T07:00:06Z| 192.168.1.75| 10.0.0.100| 48751| 445| TCP| 2048| 4096  
2025-04-01T07:00:07Z| 10.0.0.25| 172.16.0.75| 53992| 8080| TCP| 1024| 2048  
2025-04-01T07:00:08Z| 192.168.1.125| 8.8.4.4| 35667| 53| UDP| 64| 512  
2025-04-01T07:00:09Z| 172.16.0.100| 192.168.1.50| 47891| 21| TCP| 512| 1024  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         rename(field=[[src_ip, source_address], [dst_ip, destination_address], [src_port, source_port], [dst_port, destination_port]])

Renames the fields src_ip, dst_ip, src_port, and dst_port to more readable field names. The original field names are replaced with the new field names. 

Since [_`field`_](functions-rename.html#query-functions-rename-field) is the unnamed parameter, the query could also look like this: `rename([[src_ip, source_address], [dst_ip, destination_address], [src_port, source_port], [dst_port, destination_port]])`. 

  3. Event Result set.




##### Summary and Results

The query is used to rename multiple fields in one single operation. Renaming of fields is used for standardisation, normalization, and readability. Normalizing field names across different data sources is, for example, useful for joins. The [`rename()`](functions-rename.html "rename\(\)") function is often used with the [`table()`](functions-table.html "table\(\)") function. 

For renaming existing fields in arrays, see [Rename Existing Fields in Array](https://library.humio.com/examples/examples-array-rename-fields.html). 

Sample output from the incoming example data (only showing renamed fields): 

destination_address| destination_port| source_address| source_port  
---|---|---|---  
10.0.0.50| 443| 192.168.1.100| 52431  
8.8.8.8| 53| 172.16.0.25| 33221  
172.16.0.100| 80| 192.168.1.150| 49223  
192.168.1.1| 22| 10.0.0.75| 55678  
1.1.1.1| 53| 192.168.1.200| 44556  
192.168.1.25| 3389| 172.16.0.50| 51234  
10.0.0.100| 445| 192.168.1.75| 48751  
172.16.0.75| 8080| 10.0.0.25| 53992  
8.8.4.4| 53| 192.168.1.125| 35667  
192.168.1.50| 21| 172.16.0.100| 47891  
  
#### Rename a Single Field - Example 1

**Rename a single field using the[`rename()`](functions-rename.html "rename\(\)") function with the [_`as`_](syntax-fields.html#syntax-fields-from-functions "as Parameters") parameter to define the new name of the field **

##### Query

logscale
    
    
    rename(field=badName, as=goodName)

##### Introduction

The [`rename()`](functions-rename.html "rename\(\)") function is used to rename one or more fields. In this example, only one field is renamed using the [_`as`_](functions-rename.html#query-functions-rename-as) parameter to define the new name of the field. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         rename(field=badName, as=goodName)

Renames the field badName to goodName. 

  3. Event Result set.




##### Summary and Results

The query is used to quickly rename single fields. 

#### Rename a Single Field - Example 2

**Rename a single field using the[`rename()`](functions-rename.html "rename\(\)") function with assignment syntax to define the new name of the field **

##### Query

logscale
    
    
    goodName := rename(badName)

##### Introduction

The [`rename()`](functions-rename.html "rename\(\)") function is used to rename one or more fields. In this example, only one field is renamed using the assignment operator (`:=`). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         goodName := rename(badName)

Renames the badName field to goodName by assigning the new value (variable name) to the field. The value on the right side of the assignment operator is set equal to the value on the left side of it. 

  3. Event Result set.




##### Summary and Results

The query is used to quickly rename single fields.

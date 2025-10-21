# unit:convert() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-unit-convert.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)")

Convert values between different units. Such as, `514 ms` to `0.514` or `sizeInKiB=4` to `size=4096`. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-unit-convert.html#query-functions-unit-convert-as)|  string| optional[a] |  |  The output name of the field to set (defaults to the same as the input field).   
[_`binary`_](functions-unit-convert.html#query-functions-unit-convert-binary)|  boolean| optional[[a]](functions-unit-convert.html#ftn.table-functions-unit-convert-optparamfn) | `false`|  If specified, unit prefixes `kMGTPEZY` will be treated as powers of 1024 instead of 1000.   
[_`field`_](functions-unit-convert.html#query-functions-unit-convert-field)[b]| string| required |  |  The name of the input field.   
[_`from`_](functions-unit-convert.html#query-functions-unit-convert-from)|  string| optional[[a]](functions-unit-convert.html#ftn.table-functions-unit-convert-optparamfn) |  |  If the field contains unitless values, specify this parameter to tell which unit the value should be normalized from.   
[_`keepUnit`_](functions-unit-convert.html#query-functions-unit-convert-keepunit)|  boolean| optional[[a]](functions-unit-convert.html#ftn.table-functions-unit-convert-optparamfn) | `false`|  If specified, the output field will have the normalized unit appended.   
[_`to`_](functions-unit-convert.html#query-functions-unit-convert-to)|  string| optional[[a]](functions-unit-convert.html#ftn.table-functions-unit-convert-optparamfn) |  |  The output field should have the value converted to this unit.   
[_`unit`_](functions-unit-convert.html#query-functions-unit-convert-unit)|  string| optional[[a]](functions-unit-convert.html#ftn.table-functions-unit-convert-optparamfn) |  |  If specified, the field must end with this unit.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-unit-convert.html#query-functions-unit-convert-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-unit-convert.html#query-functions-unit-convert-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     unit:convert("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     unit:convert(field="value")
> 
> These examples show basic structure only.

### [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)") Function Operation

Tip

If the unit begins with a reserved prefix character, try manually setting the unit parameter. 

Any unit is supported and the following unit prefixes are converted: 

Prefix |  Decimal Factor |  Binary Factor |  Prefix |  Typical Value   
---|---|---|---|---  
Y |  1024 |  10248 (280) |  Yotta- (Yobi-) |  Bytes   
Z |  1021 |  10247 (270) |  Zetta- (Zebi-) |  Bytes   
E |  1018 |  10246 (260) |  Exa- (Exbi-) |  Bytes   
P |  1015 |  10245 (250) |  Peta- (Pebi-) |  Bytes   
T |  1012 |  10244 (240) |  Tera- (Tebi-) |  Bytes   
G |  109 |  10243 (230) |  Giga- (Gibi-) |  Bytes   
M |  106 |  10242 (220) |  Mega- (Mebi-) |  Bytes   
k |  103 |  1024 (210) |  Kilo- (Kibi-) |  Metric, Bytes   
h |  102 |  |  Hect- |  Metric   
da |  10 |  |  Deca- |  Metric   
d |  10-1 |  |  Deci- |  Metric   
c |  10-2 |  |  Centi- |  Metric   
m |  10-3 |  |  Milli- |  Metric, Seconds   
u, µ |  10-6 |  |  Micro- |  Metric, Seconds   
n |  10-9 |  |  Nano |  Metric, Seconds   
p |  10-12 |  |  Pico |  Metric, Seconds   
f |  10-15 |  |  Femto |  Metric, Seconds   
a |  10-18 |  |  Atto |  Metric, Seconds   
z |  10-21 |  |  Zepto |  Metric, Seconds   
y |  10-24 |  |  Yocto |  Metric, Seconds   
Yi |  |  10248 (280) |  Yobi- |  Bytes   
Zi |  |  10247 (270) |  Zebi- |  Bytes   
Ei |  |  10246 (260) |  Exbi- |  Bytes   
Pi |  |  10245 (250) |  Pebi- |  Bytes   
Ti |  |  10244 (240) |  Tebi- |  Bytes   
Gi |  |  10243 (230) |  Gibi- |  Bytes   
Mi |  |  10242 (220) |  Mebi- |  Bytes   
Ki |  |  1024 (210) |  Kibi- |  Metric, Bytes   
  
Tip

Units can be expressed as SI units or binary units. An example of a base unit is `2Gi bytes`. We use the standard SI-units K, M, G, and P to denote 1000-based kilo, mega, giga and peta; whereas Ki, Mi, Gi, and Pi designate the binary multiple 1024n style. See the National Institute of Standards & Technology's [Reference on Prefixes for Binary Multiples](http://physics.nist.gov/cuu/Units/binary.html) for a detailed explanation. 

If a field contains a value such as 5 kB that should be treated as 5 KiB, set the binary flag. 

When the unit is a rate, such as MB/min the rate will be normalized to per second, for example, B/s. 

The following rate conversions are supported: `s`, `sec`, `m`, `min`, `h`, `hour`, `d`, `day`, `w`, `week`. 

### [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)") Syntax Examples

Parses a value into a number by removing the unit. An input event with the field size with the value 5 MB results in the field size having the value `5000000`. 

logscale
    
    
    unit:convert(size)

Parses a value into a number by removing the unit. An input event with the field size with the value 5 MiB results in the field size having the value `5242880`. 

logscale
    
    
    unit:convert(size)

Parses a value into a number by removing the unit. An input event with the field size with the value 5 MB results in the field size having the value `5242880`. 

logscale
    
    
    unit:convert(size, binary=true)

Parses a value into a number by removing the unit. An input event with the field duration with the value `514` us results in the field duration having the value `0.000514`. 

logscale
    
    
    unit:convert(duration)

Parses a unit less value into a number by manually specifying the input unit. An input event with the field size with the value `234.567` results in the field size having the value `234567`. 

Internally the value is parsed as `{size} {from}`, just as if the field had contained the value `234.567 k`. 

logscale
    
    
    unit:convert(size, from="k")

Parses a value into a number by removing the unit. An input event with the field rate with the value `120 hits/min` results in the field rate having the value `2`. 

### Note

Since the unit in this case starts with a letter `h` from the supported prefixes, it will be interpreted as the prefix `h` (102) and unit `hits`. To enforce that the unit is actually hits, specify the unit parameter. 

logscale
    
    
    unit:convert(rate, as="rate", unit="hits")

Converts a number into a value with a unit. An input event with the field size with the value `19886168` results in the field rate having the value `19.886168`. 

logscale
    
    
    unit:convert(rate, as="rate", to="M")

### [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)") Examples

Click + next to an example below to get the full details.

#### Convert Rate Values

**Convert rate values to hits using the[`unit:convert()`](functions-unit-convert.html "unit:convert\(\)") function **

##### Query

logscale
    
    
    | unit:convert(rate, as="rate", unit="hits")

##### Introduction

In this example, the [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)") function is used to convert rate values to hits. The function parses a value into a number by removing the unit. 

Example incoming data might look like this: 

@timestamp| service| rate  
---|---|---  
2023-08-06T10:00:00Z| api| 150hits/min  
2023-08-06T10:01:00Z| api| 25hits/s  
2023-08-06T10:02:00Z| api| 3600hits/h  
2023-08-06T10:03:00Z| api| 80hits/min  
2023-08-06T10:04:00Z| api| 40hits/s  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         | unit:convert(rate, as="rate", unit="hits")

Converts the values in the rate field to hits. The [_`as`_](functions-unit-convert.html#query-functions-unit-convert-as) parameter specifies that it is a conversion of a rate type measurement, and the [_`unit`_](functions-unit-convert.html#query-functions-unit-convert-unit) parameter with value `hits` enforces that the desired output unit is actually hits. 

Note that since the unit in this case starts with a letter `h` from the supported prefixes, it will be interpreted as the prefix `h` (102) and unit `hits`. 

  3. Event Result set.




##### Summary and Results

The query is used to convert rate values from different time units (per second, per minute, per hour) to a standardized hits per second format. 

This query is useful, for example, to normalize different rate measurements for consistent monitoring and analysis. 

Note that any unit is supported in LogScale. 

Sample output from the incoming example data: 

@timestamp| service| rate  
---|---|---  
2023-08-06T10:00:00Z| api| 2.5  
2023-08-06T10:01:00Z| api| 25  
2023-08-06T10:02:00Z| api| 1  
2023-08-06T10:03:00Z| api| 1.33  
2023-08-06T10:04:00Z| api| 40  
  
#### Convert Values Between Units

**Convert file size and transfer time units using the[`unit:convert()`](functions-unit-convert.html "unit:convert\(\)") function **

##### Query

logscale
    
    
    unit:convert(field=file_size, from="B", to="MB")
    | unit:convert(field=transfer_time, from="ms", to="s")
    | table([file_size, transfer_time])

##### Introduction

In this example, the [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)") function is used to convert file sizes and transfer times units. The [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)") function automatically handles the mathematical conversion between units, making it easier to work with different measurement scales in the event set. 

Note that any unit is supported in LogScale. 

Example incoming data might look like this: 

timestamp| file_name| file_size| transfer_time| status  
---|---|---|---|---  
2025-05-15 05:30:00| doc1.pdf| 1048576| 3500| complete  
2025-05-15 05:31:00| img1.jpg| 2097152| 4200| complete  
2025-05-15 05:32:00| video1.mp4| 5242880| 12000| complete  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         unit:convert(field=file_size, from="B", to="MB")

Converts file sizes from Bytes (B) to Megabytes (MB). 

  3. logscale
         
         | unit:convert(field=transfer_time, from="ms", to="s")

Converts transfer times from milliseconds (ms) to seconds (s) 

  4. logscale
         
         | table([file_size, transfer_time])

Displays the result of the fields file_size and transfer_time in a table. 

  5. Event Result set.




##### Summary and Results

The query is used to convert file sizes and transfer times units. A table showing file sizes and transfer times is, for example, useful to spot unusually large file transfers, to identify slow transfers or bottlenecks (for debugging). 

The [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)") function is useful to standardize the units for better comparison and make data more readable. 

Note that any unit is supported in LogScale. For more examples, see [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)"). 

Sample output from the incoming example data: 

file_name| file_size| transfer_time  
---|---|---  
doc1.pdf| 1.0| 3.5  
img1.jpg| 2.0| 4.2  
video1.mp4| 5.0| 12.0

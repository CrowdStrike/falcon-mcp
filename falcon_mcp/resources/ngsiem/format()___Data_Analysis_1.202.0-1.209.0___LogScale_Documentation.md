# format() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-format.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`format()`](functions-format.html "format\(\)")

The [`format()`](functions-format.html "format\(\)") function creates formatted strings using `printf` style. This function adds the formatted string to a new field. The input parameters or fields can be one field or an array of fields. To format multiple fields, separate them with commas inside square brackets. For datetime formatting, the input fields must contain milliseconds since epoch (for example, `1 January 1970 00:00:00 UTC`). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-format.html#query-functions-format-as)|  string| optional[a] | `_format`|  The output name of the formatted field.   
[_`field`_](functions-format.html#query-functions-format-field)|  array of strings| required |  |  The fields to format. For multiple fields, enter within square brackets, separated by commas.   
[_`format`_](functions-format.html#query-functions-format-format)[b]| string| required |  |  The formatting codes for formatting the given string or strings.   
[_`timezone`_](functions-format.html#query-functions-format-timezone)|  string| optional[[a]](functions-format.html#ftn.table-functions-format-optparamfn) |  |  The timezone when formatting dates and times. See [Supported Time Zones](syntax-time-timezones.html "Supported Time Zones") for a list of supported timezones.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`format`_](functions-format.html#query-functions-format-format) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`format`_](functions-format.html#query-functions-format-format) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     format("value",field=["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     format(format="value",field=["value"])
> 
> These examples show basic structure only.

### [`format()`](functions-format.html "format\(\)") Syntax Examples

Since there are several fields and types of fields that may be given with the [`format()`](functions-format.html "format\(\)") query function, this section provides several examples of how to use the query function. 

As a first example, suppose you want to calculate a numeric value and want to format the results so that it shows only two decimal places. You would do that like this: 

logscale
    
    
    avg(field=cputime)
    | format("%,.2f", field=_avg, as=_avg)

In this example, the query is averaging the field containing the CPU value. This number is then piped to the [`format()`](functions-format.html "format\(\)") function, which gives a formatting code — how the field value should be formatted; in the example, it formats the number to two decimal places, using `,` as the thousands separator. 

_avg  
---  
288.582  
  
Other examples of using the [`format()`](functions-format.html "format\(\)") can be: 

Concatenate two fields with a comma as separator: 

logscale
    
    
    format(format="%s,%s", field=[a, b], as="combined")
    | table(combined)

Get the hour of day out of the event [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp): 

logscale
    
    
    format("%tm", field=@timestamp, as=hour)
    | table(hour)

To format an integer adding a thousands separator: 

logscale
    
    
    count()
    | format("%,i", field=_count, as=_count)

Produces 

_count|  |   
---|---|---  
3| 886| 817  
  
Create a link with title based on the extracted content: 

logscale
    
    
    $extractRepo()
    | top(repo)
    | format("[Link](https://example.com/%s)", field=repo, as=link)

### Important

Do not include a newline if the format specification for a link, even for readability. The link will not be identified correctly and may not create a link in the generated event list. 

### Format Specifiers

### Deprecated:1.58

The format specifiers `%a`, `%A` and `%S` were deprecated in 1.58 and removed completely in 1.70. 

A format specifier is formed like this: 
    
    
    %[argument_index][flags][width][.precision][length]type[modifiers]

Sections in square brackets, for example, `[flags]`, are optional and can be omitted. 

### Important

The resulting format specifier may be a two-letter code where type identifies the type, and a second letter (the modifier) identifies the specific format. For example, with the time specifier, `%t` only identifies the field to be formatted as a date or time value. The output formate must use a letter from [Date/Time](functions-format.html#functions-format-specifiers-datetime "Date/Time") to indicate the actual format. For example: 

logscale
    
    
    parseTimestamp(field=@timestamp)
    | timeonly := format("%tr",field=[@timestamp])

Formats the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) using `%tr` which is the equivalent of the [`formatTime()`](functions-formattime.html "formatTime\(\)") specifier `%r`, which outputs a full natrual time value, for example, as `%tI:%tM:%tS %Tp`, for example, 1:30:00 PM 

#### Supported Types

The supported type specifiers are the following. 

Type |  Output   
---|---  
d or i |  Signed decimal integer   
b or B |  Boolean (uppercase and lowercase, respectively)   
o |  Signed octal   
x or X |  Unsigned hexadecimal integer (lowercase and uppercase, respectively)   
f or F |  Decimal floating point   
e or E |  Scientific-notation (exponential) floating point   
g or G |  Scientific or decimal floating point   
t or T |  Date/Time (lowercase or uppercase, respectively)   
c or C |  Single character (lowercase or uppercase, respectively)   
s |  String of characters   
n |  Newline character   
% |  The format specifier %% will produce a single %   
  
#### Numbers

Type |  Output   
---|---  
d or i |  Signed decimal integer   
o |  Unsigned octal   
x or X |  Signed hexadecimal integer   
f or F |  Decimal floating point   
e or E |  Scientific-notation (exponential) floating point   
g or G |  Scientific or decimal floating point (depending on input)   
  
A number is a field that contains only an integer or a real number, with no grouping, for example, `1,000` is not a number. Scientific notation, for example, `1.74587E100` is supported. 

If a field is not a number following the above description, the output of format given any of the above type specifiers is `null`. 

##### Octal Formatting

Type specifier `o`, does not support negative numbers. If the given field is a negative integer, the output in undefined. 

##### Hexadecimal Formatting

Type specifiers `x` and `X` expect the corresponding field to be that of a 64-bit signed integer and produce the same integer in the [Hexadecimal numeral system](https://en.wikipedia.org/wiki/Hexadecimal) stripped of any leading zeros. For instance, if a field num contains the value 42, running: 

logscale
    
    
    format("%X", field=[num])

The [`format()`](functions-format.html "format\(\)") function creates the field _format = 2A. Notice that [`format()`](functions-format.html "format\(\)") does not add the common denomination of `0x` (from the C programming language) to the produced output unless given the `#` flag. Likewise, `0x` can be added explicitly to the format string as: 

logscale
    
    
    format("0x%X", field=[num])

This would produce the field _format = 0x2A. 

Hexadecimal formatting is closely related to the binary representation of the integer, which is in [Two's complement](https://en.wikipedia.org/wiki/Two%27s_complement) representation. This has the adverse effect that the hexadecimals produced for negative integers can have a large amount of leading `F` characters. If your input is a signed 32-bit integer, you can shorten the output of [`format()`](functions-format.html "format\(\)") down to only display output corresponding to 32-bits, using the length specifiers. 

##### Floating Point Formatting

Type specifiers `f` and `F` format the given field as a real number with the specified precision. They only work on floating point values up to `1e9` (one billion). See [Supported Precision](functions-format.html#functions-format-specifiers-supported-precision "Supported Precision") for more information. 

Type specifiers `e` and `E` formats the given field as a real number in scientific notation, lowercase and uppercase respectively. For instance, `176.54` formatted using `%e` becomes `1.765400e+02`. 

For type specifiers `g` and `G` the specified precision represents the amount of significant figures, instead of the number of digits after the decimal point. If the integer part of the number is larger than the specified amount of significant digits, `g` and `G` behave like `e` and `E` respectively, otherwise they behave like `f` and `F`. Notice that the minimum precision is 6 and the maximum precision is 9. 

#### Booleans (true and false)

Type |  Output   
---|---  
b or B |  Boolean   
  
On type specifier `b` or `B`, if the corresponding field is `false`, then the result is `false` or `FALSE` respectively. Otherwise, the result is `true` or `TRUE`, respectively. 

#### Strings

Type |  Output   
---|---  
c or C |  Single character (lowercase or uppercase, respectively)   
s |  String of characters   
n |  Newline character   
  
A string is any sequence of length `>= 1` consisting of unicode characters. Any field will match this description. 

On type specifier `c`, the first character of the string is output. Type specifier `s` outputs the specified field. 

#### Date/Time

For dates and times, the format specifier `t` or `T` is a prefix for the value specific format, as supported by the [`formatTime()`](functions-formattime.html "formatTime\(\)") and [`formatDuration()`](functions-formatduration.html "formatDuration\(\)") functions. 

For example, to format the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field to show the time in `HOUR:MINUTE` format using [`format()`](functions-format.html "format\(\)") function, it would need the format specifier `%tH:%tM`: 

logscale
    
    
    parseTimestamp(field=@timestamp)
    | timeonly := format("%tH:%tM",field=[@timestamp,@timestamp])

In the above example, note as well that the source field [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) must be provided twice to be decoded by each format specifier. 

This is equivalent to using [`formatTime()`](functions-formattime.html "formatTime\(\)"): 

logscale
    
    
    parseTimestamp(field=@timestamp)
    | timeonly := formatTime("%H:%M",field=@timestamp)

For more information, see [`formatTime()`](functions-formattime.html "formatTime\(\)")

Fields can only be used as date/time values if they are in milliseconds since the beginning of the Unix epoch, 1 January 1970 00:00:00 UTC. If the field is anything else, format outputs `null`. 

All Date/Time type specifiers must be followed by a Date/Time modifier. 

The following time modifiers are available: 

Modifier |  Output   
---|---  
`H` |  Hour of the day for the 24-hour clock, formatted as two digits with a leading zero as necessary, (00 - 23)   
`I` |  Hour of the day for the 12-hour clock, formatted as two digits with a leading zero as necessary, (01 - 12)   
`k` |  Hour of the day for the 24-hour clock, (0 - 23)   
`l` |  Hour of the day for the 12-hour clock, (1 - 12)   
`M` |  Minutes within the hour formatted as two digits with a leading zero as necessary, (00 - 59)   
`S` |  Seconds within the minute, formatted as two digits with a leading zero as necessary, that is 00 - 60 ('60' is a special value required to support leap seconds).   
`L` |  Milliseconds within the second formatted as three digits with leading zeros as necessary, (000 - 999)   
`N` |  Nanoseconds within the second, formatted as nine digits with leading zeros as necessary, (000000000 - 999999999)   
`p` |  Locale-specific morning or afternoon marker in lower case, for example 'am' or 'pm'. Use of the prefix 'T' forces this output to upper case.   
`z` |  RFC 822 style numeric time zone offset from GMT, for example -0800. This value will be adjusted as necessary for Daylight Saving Time. May depend on locale.   
`Z` |  A string representing the abbreviation for the time zone. This value will be adjusted as necessary for Daylight Saving Time. May depend on locale.   
`s` |  Seconds since the beginning of the epoch starting at 1 January 1970 00:00:00 UTC, (`Long.MIN_VALUE/1000` to `Long.MAX_VALUE/1000`, where `Long` is a 64-bit signed integer.   
`Q` |  Milliseconds since the beginning of the epoch starting at 1 January 1970 00:00:00 UTC, (`Long.MIN_VALUE` to `Long.MAX_VALUE`, where `Long` is a 64-bit signed integer.   
  
The following date modifiers are available: 

Modifier |  Output   
---|---  
`Y` |  Year, formatted as at least four digits with leading zeros as necessary, for example, 0092 equals 92 CE for the Gregorian calendar.   
`y` |  Last two digits of the year, formatted with leading zeros as necessary, that is 00 - 99.   
`j` |  Day of year, formatted as three digits with leading zeros as necessary, for example, 001 - 366 for the Gregorian calendar.   
`m` |  Month, formatted as two digits with leading zeros as necessary, that is 01 - 13.   
`d` |  Day of month, formatted as two digits with leading zeros as necessary, that is 01 - 31.   
`e` |  Day of month, formatted as two digits, that is 1 - 31.   
`a` |  Locale-specific short name of the day of the week.   
`A` |  Locale-specific full name of the day of the week.   
`b` |  Locale-specific abbreviated month name.   
`B` |  Locale-specific full month name.   
`C` |  Four-digit year divided by 100, formatted as two digits with leading zero as necessary.   
  
Furthermore, the following special date/time modifiers are available: 

Modifier |  Output   
---|---  
`R` |  Time formatted for the 24-hour clock as `H:M`.   
`T` |  Time formatted for the 24-hour clock as `H:M:S`.   
`r` |  Time formatted for the 12-hour clock as `I:M:S p`. The location of the morning or afternoon marker (`p`) may be locale-dependent.   
`D` |  Date formatted as `m/d/y`.   
`F` |  ISO 8601 complete date formatted as `Y-m-d`.   
`c` |  Date and time formatted as `%ta %tb %td %tT %tZ %tY`.   
  
#### Other

Type |  Output   
---|---  
% |  The format specifier `%%` will produce a single %   
  
#### Supported Argument Index Specifiers

The argument index is a decimal integer indicating the position of the argument in the fields list. The first argument is referenced by `1$`, the second by `2$`, and so on. Another way to reference arguments by position is to use the `'<'(\u003c)` flag, which causes the argument for the previous format specifier to be re-used. For example, the following two statements produce identical strings: 
    
    
    format("Event date: %1$Tm/%1$Te/%1$TY", field=[@timestamp], timezone="Europe/Copenhagen")
    format("Event date: %1$Tm/%<Te/%<TY", field=[@timestamp], timezone="Europe/Copenhagen")

If no argument index is specified, the first format specifier refers to the first argument of the fields list, the second format specifier refers to the second argument and so on. 

#### Supported Flags

Flags |  Description   
---|---  
-sign |  Left-justify within the given field width; Right justification is the default.   
+sign |  Forces preceding the result with a plus or minus sign (+ or -) even for positive numbers. By default, only negative numbers are preceded with a -sign.   
(space) |  If no sign is written, a blank space is inserted before the value.   
# |  Used with o, b, x or X type specifiers the value is preceded with 0, 0b, 0x or 0X respectively for values different than zero. Used with f or F it forces the written output to contain a decimal point even if no more digits follow. By default, if no digits follow, no decimal point is written.   
0 |  Left-pads the number with zeros (0) instead of spaces when padding is specified (see width sub-specifier).   
, |  Groups the output in thousands, for instance 10000 becomes 10,000.   
  
#### Supported Width

Width |  Description   
---|---  
(number) |  Minimum number of characters to be printed. If the value to be printed is shorter than this number, the result is padded with blank spaces. The value is not truncated even if the result is larger.   
  
#### Supported Precision

Precision |  Description   
---|---  
.number |  For integer specifiers (d, i, o, u, x, X): precision specifies the minimum number of digits to be written. If the value to be written is shorter than this number, the result is padded with leading zeros. The value is not truncated even if the result is longer. A precision of 0 means that no character is written for the value 0. For f and F specifiers: this is the number of digits to be printed after the decimal point. **By default, this is 6, maximum is 9**. For 'g' and 'G' specifiers: this is number of significant digits with which to display the number. For s: this is the maximum number of characters to be printed. By default all characters are printed until the ending null character is encountered. If the period is specified without an explicit value for precision, 0 is assumed.   
  
#### Supported Length

The length argument specifies the length with which to interpret the given fields' data type. 

In general, [`format()`](functions-format.html "format\(\)") interprets any number that is not a floating point number to be that of a 64-bit signed integer and formats any such integer with leading zeros removed. For instance, converting 42 to hexadecimal with the format string `0x%X` produces the string `0x2A` and not one with 62 leading zeros. However, conversions of negative numbers to hexadecimal are represented using [Two's complement](https://en.wikipedia.org/wiki/Two%27s_complement) which entails a large number of leading `F` characters. For example, the number `-1` is by default represented using all 64-bits, hence the above format string produces `0xFFFFFFFFFFFFFFFF`. This can for example be brought down to `0xFFFFFFFF` by specifying the `h` length argument. 

Length |  Description   
---|---  
(none) |  Signed 64-bit integer   
h |  Signed 32-bit integer   
  
### [`format()`](functions-format.html "format\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate the Mean of CPU Time

**Calculate the sum of all numbers (mean) of the CPU time**

##### Query

logscale
    
    
    avg(field=cputimeNanos)
    | cputime := (_avg/1000000)
    | format("%,.2f", field=_avg, as=_avg)

##### Introduction

CPU time is the exact amount of time that the CPU has spent processing data for a specific program or process. In this example the [`avg()`](functions-avg.html "avg\(\)") function is used to calculate the sum of all numbers; the mean of the CPU Time. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         avg(field=cputimeNanos)

Calculates the mean of the field cputimeNanos. This can be run in the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) system repository to get the average time spent in nanoseconds for different activities. The mean is calculated by summing all of the values in the cputimeNanos field and dividing by the number of values across all events. 

  3. logscale
         
         | cputime := (_avg/1000000)

Calculates the average CPU time to milliseconds to make it easier to read. 

  4. logscale
         
         | format("%,.2f", field=_avg, as=_avg)

Overwrites the field _avg to contain the _avg field to show only two decimals. 

  5. Event Result set.




##### Summary and Results

The query is used to averaging the field containing the CPU value. This value is then piped to the [`format()`](functions-format.html "format\(\)") function, which provides a formatting code — how the field value should be formatted. In this example, it formats the value to two decimal. Calculation of CPU times is useful to determine processing power - for example if troubleshooting a system with high CPU usage. 

Sample output from the incoming example data: 

_avg  
---  
0.14  
  
#### Combine Values of Multiple Fields

**Create a new field by combining values from multiple fields using the[`format()`](functions-format.html "format\(\)") function **

##### Query

logscale
    
    
    format(format="%s,%s", field=[a, b], as="combined")
    table(combined)

##### Introduction

In this example, the [`format()`](functions-format.html "format\(\)") function is used to combine values from two fields a and b into a single field combined using a comma as a separator. 

Example incoming data might look like this: 

@timestamp| a| b  
---|---|---  
1686048000000000000| John| Smith  
1686048001000000000| Jane| Doe  
1686048002000000000| Bob| Johnson  
1686048003000000000| Alice| Brown  
1686048004000000000| Mike| Davis  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         format(format="%s,%s", field=[a, b], as="combined")

Creates a new field named combined by combining the values from fields a and b using a comma as separator. The [_`format`_](functions-format.html#query-functions-format-format) parameter specifies the format string where each `%s` is replaced with the corresponding field value in the order specified in the [_`field`_](functions-format.html#query-functions-format-field) parameter. 

  3. logscale
         
         table(combined)

Displays the results in a table showing only the newly created combined field. 

  4. Event Result set.




##### Summary and Results

The query is used to merge values from multiple fields into a single field using a specified format pattern. 

This query is useful, for example, to create concatenated values for reporting, to prepare data for export, or to simplify complex multi-field data structures into a single field. 

Sample output from the incoming example data: 

combined  
---  
John,Smith  
Jane,Doe  
Bob,Johnson  
Alice,Brown  
Mike,Davis  
  
#### Concatenate Fields and Strings Together

****

##### Query

logscale
    
    
    format("%s/%s",field=[dirname,filename],as=pathname)

##### Introduction

The [`concat()`](functions-concat.html "concat\(\)") is not able to concatenate fields and strings together. For example to create a pathname based on the directory and filename it is not possible to do: 

logscale
    
    
    concat([dirname,"/",filename],as=pathname)

This will raise an error. Instead, we can use [`format()`](functions-format.html "format\(\)"). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         format("%s/%s",field=[dirname,filename],as=pathname)

Formats a value separating the two by a forward slash, creating the field pathname

  3. Event Result set.




##### Summary and Results

The [`format()`](functions-format.html "format\(\)") function provides a flexible method of formatting data, including encapsulating or combining strings and fields together. 

#### Convert Decimal Numbers to Hexadecimal Format

**Transform decimal numbers to their hexadecimal representation using the[`format()`](functions-format.html "format\(\)") function **

##### Query

logscale
    
    
    format("%X", field=[num])

##### Introduction

In this example, the [`format()`](functions-format.html "format\(\)") is used to convert decimal numbers to uppercase hexadecimal format. The `%X` format specifier converts integers to hexadecimal with uppercase letters A-F. 

Example incoming data might look like this: 

@timestamp| event_type| num| description  
---|---|---|---  
2025-06-10T13:00:00Z| status| 255| max byte value  
2025-06-10T13:01:00Z| status| 16| small number  
2025-06-10T13:02:00Z| status| 4096| memory page  
2025-06-10T13:03:00Z| status| 65535| max word value  
2025-06-10T13:04:00Z| status| 10| decimal value  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         format("%X", field=[num])

Converts the decimal numbers in the num field to their hexadecimal representation. 

The [_`field`_](functions-format.html#query-functions-format-field) parameter specifies which field to format, and the `%X` format specifier indicates uppercase hexadecimal conversion. The result is stored in a new field named _format by default. 

The `%X` format specifier will convert the decimal number to hexadecimal using uppercase letters (A-F). For example, decimal `255` becomes `FF`, and `4096` becomes `1000`. 

  3. Event Result set.




##### Summary and Results

The query is used to convert decimal numbers to their hexadecimal representation, which is particularly useful when working with binary data, memory addresses, or color codes. 

This query is useful, for example, to analyze network packets, debug memory dumps, or work with data that is commonly represented in hexadecimal format. 

Sample output from the incoming example data: 

_format| description| event_type| num  
---|---|---|---  
FF| max byte value| status| 255  
10| small number| status| 16  
1000| memory page| status| 4096  
FFFF| max word value| status| 65535  
A| decimal value| status| 10  
  
Note that the hexadecimal values are displayed in uppercase letters, and leading zeros are not included in the output. The original decimal values are preserved in the num field while the hexadecimal representations are stored in the _format field. 

#### Convert Decimal Numbers to Prefixed Hexadecimal Format

**Transform decimal numbers to hexadecimal with 0x prefix using the[`format()`](functions-format.html "format\(\)") function **

##### Query

logscale
    
    
    format("0x%X", field=[num])

##### Introduction

In this example, the [`format()`](functions-format.html "format\(\)") is used to convert decimal numbers to uppercase hexadecimal format with the `0x` prefix. The `%X` format specifier converts integers to hexadecimal with uppercase letters A-F. 

Example incoming data might look like this: 

@timestamp| event_type| num| description  
---|---|---|---  
2025-06-10T13:00:00Z| memory| 255| page boundary  
2025-06-10T13:01:00Z| memory| 16| offset value  
2025-06-10T13:02:00Z| memory| 4096| page size  
2025-06-10T13:03:00Z| memory| 65535| segment limit  
2025-06-10T13:04:00Z| memory| 10| base address  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         format("0x%X", field=[num])

Converts the decimal numbers in the num field to their hexadecimal representation with the `0x` prefix. 

The [_`field`_](functions-format.html#query-functions-format-field) parameter specifies which field to format, and the format string `0x%X` adds the prefix to the hexadecimal conversion. The result is stored in a new field named _format by default. 

The `%X` format specifier will convert the decimal number to hexadecimal using uppercase letters (A-F). For example, decimal `255` becomes `0xFF`, and `4096` becomes `0x1000`. The `0x` prefix makes it clear that the number is in hexadecimal format, which is a common convention in programming and debugging. 

  3. Event Result set.




##### Summary and Results

The query is used to convert decimal numbers to their hexadecimal representation with the standard `0x` prefix, making the output immediately recognizable as hexadecimal values. 

This query is useful, for example, to format numbers for programming contexts, debug memory addresses, or analyze system-level logs where hexadecimal values are commonly prefixed with `0x`. 

Sample output from the incoming example data: 

_format| description| event_type| num  
---|---|---|---  
0xFF| page boundary| memory| 255  
0x10| offset value| memory| 16  
0x1000| page size| memory| 4096  
0xFFFF| segment limit| memory| 65535  
0xA| base address| memory| 10  
  
Note that each hexadecimal value is prefixed with `0x`, making it clear that these are hexadecimal representations. The original decimal values are preserved in the num field while the formatted hexadecimal representations are stored in the _format field. 

#### Convert Timestamp Values Into Formatted Strings

**Converting epoch timestamp to hour format using the[`format()`](functions-format.html "format\(\)") function with a format specifier **

##### Query

logscale
    
    
    format("%tH", field=@timestamp, as=hour)
    table(hour)

##### Introduction

In this example, the [`format()`](functions-format.html "format\(\)") function is used to format the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field (containing milliseconds since epoch) to show the time in `HOUR` format using the format specifier `%tH`. 

Example incoming data might look like this: 

@timestamp| action| user| status  
---|---|---|---  
1686837825000| login| john| success  
1686839112000| logout| john| success  
1686840753000| login| alice| success  
1686842415000| download| alice| completed  
1686844522000| login| bob| failed  
1686845745000| login| bob| success  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         format("%tH", field=@timestamp, as=hour)

Extracts the hour (in 24-hour format) from the epoch timestamp in [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field using the format specifier `%tH` and returns the formatted results in a new field named hour. The parameter [_`field`_](functions-format.html#query-functions-format-field) specifies the input field containing the epoch timestamp (in milliseconds), and [_`as`_](functions-format.html#query-functions-format-as) defines the name of the output field. The pattern `%tH` specifically formats the hour in 24-hour format (00-23). 

Note that fields can only be used as date/time values if they are in milliseconds since the beginning of the Unix epoch, 1 January 1970 00:00:00 UTC. If the field is anything else, format outputs null. 

  3. logscale
         
         table(hour)

Displays the result of the hour field in a table. 

  4. Event Result set.




##### Summary and Results

The query is used to convert epoch timestamps to readable hour format. 

Sample output from the incoming example data: 

hour  
---  
14  
15  
16  
  
The hours are displayed in 24-hour format (00-23). 

#### Create Frequency Count With Formatted Links

**Transform field values into clickable links with occurrence count using the[`top()`](functions-top.html "top\(\)") function with [`format()`](functions-format.html "format\(\)") **

##### Query

logscale
    
    
    top(repo)
    | format("[Link](https://example.com/%s)", field=repo, as=link)

##### Introduction

In this example, the [`top()`](functions-top.html "top\(\)") is used to count occurrences of repository names in the field [repo](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html), followed by the [`format()`](functions-format.html "format\(\)") function to create clickable links for each repository. 

Example incoming data might look like this: 

@timestamp| repo| action| user  
---|---|---|---  
2023-06-15T10:00:00Z| frontend-app| push| alice  
2023-06-15T10:05:00Z| backend-api| clone| bob  
2023-06-15T10:10:00Z| frontend-app| pull| charlie  
2023-06-15T10:15:00Z| database-service| push| alice  
2023-06-15T10:20:00Z| frontend-app| pull| bob  
2023-06-15T10:25:00Z| backend-api| push| alice  
2023-06-15T10:30:00Z| monitoring-tool| clone| charlie  
2023-06-15T10:35:00Z| frontend-app| push| bob  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         top(repo)

Groups events by the [repo](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html) field and counts their occurrences. Creates a result set with two fields: the repository name ([repo](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html)) and _count. Results are automatically sorted by count in descending order. If no limit is specified, the [`top()`](functions-top.html "top\(\)") function returns all unique values. 

  3. logscale
         
         | format("[Link](https://example.com/%s)", field=repo, as=link)

Creates formatted markdown-style links based on repository values in [repo](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html) and returns the results in a new field named link. 

The [_`field`_](functions-format.html#query-functions-format-field) parameter specifies to use the [repo](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html) field value in the formatting string (represented by `%s`). 

  4. Event Result set.




##### Summary and Results

The query is used to analyze the frequency of repository interactions and create clickable links for each repository. 

This query is useful, for example, to create interactive reports showing which repositories are most actively used, or to build dashboards where users can quickly access frequently accessed repositories. 

Sample output from the incoming example data: 

repo| _count| link  
---|---|---  
frontend-app| 4| [Link](https://example.com/ frontend-app)  
backend-api| 2| [Link](https://example.com/ backend-api)  
monitoring-tool| 1| [Link](https://example.com/ monitoring-tool)  
database-service| 1| [Link](https://example.com/ database-service)  
  
Note that the results are automatically sorted by count in descending order, showing the most frequently accessed repositories first. The original field value is preserved in the [repo](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html) field while the formatted link is available in the link field. 

#### Format Values From Two Array Elements Using :

**Format Values from Two Array Elements using : as a separator**

##### Query

logscale
    
    
    objectArray:eval("in[]", asArray="out[]", function={out := format("%s:%s", field=[in.key, in.value])})

##### Introduction

In this example, the [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function is used to format the array entries `in[].key ` and `in[].value` separating the concatenated values with a `:` in the output field out[]. The output must be a single field in this example as [`format()`](functions-format.html "format\(\)") is only capable of creating a single value. 

Example incoming data might look like this: 

JSON
    
    
    in[0].key = x
    in[0].value = y
    in[1].key = a
    in[1].value = b

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         objectArray:eval("in[]", asArray="out[]", function={out := format("%s:%s", field=[in.key, in.value])})

Iterates (executes a loop) over the array from start to end (or to the first empty index in the array), applies the given function, and returns the concatenated results in a new output array name field out[]. 

Notice that a [_`var`_](functions-objectarray-eval.html#query-functions-objectarray-eval-var) parameter can be used to give a different name to the input array variable inside the function argument. This is particularly useful whenever the input array name is very long. Example: 

logscale
         
         objectArray:eval("someVeryLongName[]", asArray="out[]",
         var=x, function={out := format("%s:%s", field=[x.key,
         x.value])})

  3. Event Result set.




##### Summary and Results

The query is used to format arrays of objects. 

Sample output from the incoming example data: 
    
    
    out[0] = x:y
    out[1] = a:b

#### Perform Formatting on All Values in an Array

**Perform formatting on all values in a flat array using the[`array:eval()`](functions-array-eval.html "array:eval\(\)") function **

##### Query

logscale
    
    
    array:eval("devices[]",  asArray="upperDevices[]", var=d, function={upperDevices :=upper("d")})

##### Introduction

In this example, the [`array:eval()`](functions-array-eval.html "array:eval\(\)") function is used to convert all values (for example `[Thermostat, Smart Light]`) in an array devices[] from lowercase to uppercase and show the results in a new array. 

Example incoming data might look like this: 

Raw Events

{\"devices\":[\"Thermostat\",\"Smart Plug\"],\"room\":\"Kitchen\"}"  
---  
{\"devices\":[\"Smart Light\",\"Thermostat\",\"Smart Plug\"],\"room\":\"Living Room\"}"  
{\"devices\":[\"Smart Light\",\"Smart Plug\"],\"room\":\"Bedroom\"}"  
{\"devices\":[\"Thermostat\",\"Smart Camera\"],\"room\":\"Hallway\"}"  
{\"devices\":[\"Smart Light\",\"Smart Lock\"],\"room\":\"Front Door\"}"  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:eval("devices[]",  asArray="upperDevices[]", var=d, function={upperDevices :=upper("d")})

Formats all values in the array devices[] to uppercase and returns the results in a new array named upperDevices[]. The values in the original array stay the same: `[Thermostat, Smart Plug, Smart Light]` and the new array contains the returned results: `[THERMOSTAT, SMART PLUG, SMART LIGHT]`

  3. Event Result set.




##### Summary and Results

The query is used to turn values in an array into uppercase. The [`array:eval()`](functions-array-eval.html "array:eval\(\)") function can also be used for squaring a list of numbers in an array. 

Sample output from the incoming example data: 

devices[]| upperDevices[]  
---|---  
Thermostat| THERMOSTAT  
Smart Plug| SMART PLUG  
Smart Light| SMART LIGHT  
  
#### Rounding to n Decimal Places

****

##### Query

logscale
    
    
    format("%.2f", field=value)

##### Introduction

To round a number to a specific number of decimal points, use [`format()`](functions-format.html "format\(\)") rather than [`round()`](functions-round.html "round\(\)"). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         format("%.2f", field=value)

Rounds the field value to two decimal places. 

  3. Event Result set.




##### Summary and Results

When using [`format()`](functions-format.html "format\(\)"), rounding is performed using standard math rules. The [`format()`](functions-format.html "format\(\)") rounds a number to a specific decimal accuracy. 

### Note

To round a number to the nearest integer, use [`round()`](functions-round.html "round\(\)"). See [Basic Rounding](https://library.humio.com/examples/examples-functions-round-basic.html).

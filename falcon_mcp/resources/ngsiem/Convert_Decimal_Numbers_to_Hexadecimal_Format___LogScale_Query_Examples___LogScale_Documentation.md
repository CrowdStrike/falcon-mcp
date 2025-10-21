# Convert Decimal Numbers to Hexadecimal Format | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-format-decimal-to-hex.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Convert Decimal Numbers to Hexadecimal Format

Transform decimal numbers to their hexadecimal representation using the [`format()`](https://library.humio.com/data-analysis/functions-format.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    format("%X", field=[num])

### Introduction

The [`format()`](https://library.humio.com/data-analysis/functions-format.html) function can be used to format values according to specified patterns, including converting decimal numbers to their hexadecimal representation using the `%X` format specifier. 

In this example, the [`format()`](https://library.humio.com/data-analysis/functions-format.html) is used to convert decimal numbers to uppercase hexadecimal format. The `%X` format specifier converts integers to hexadecimal with uppercase letters A-F. 

Example incoming data might look like this: 

@timestamp| event_type| num| description  
---|---|---|---  
2025-06-10T13:00:00Z| status| 255| max byte value  
2025-06-10T13:01:00Z| status| 16| small number  
2025-06-10T13:02:00Z| status| 4096| memory page  
2025-06-10T13:03:00Z| status| 65535| max word value  
2025-06-10T13:04:00Z| status| 10| decimal value  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         format("%X", field=[num])

Converts the decimal numbers in the num field to their hexadecimal representation. 

The [_`field`_](https://library.humio.com/data-analysis/functions-format.html#query-functions-format-field) parameter specifies which field to format, and the `%X` format specifier indicates uppercase hexadecimal conversion. The result is stored in a new field named _format by default. 

The `%X` format specifier will convert the decimal number to hexadecimal using uppercase letters (A-F). For example, decimal `255` becomes `FF`, and `4096` becomes `1000`. 

  3. Event Result set.




### Summary and Results

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

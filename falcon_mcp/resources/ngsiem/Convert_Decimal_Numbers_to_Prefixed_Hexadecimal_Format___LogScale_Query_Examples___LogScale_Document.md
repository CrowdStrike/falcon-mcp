# Convert Decimal Numbers to Prefixed Hexadecimal Format | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-format-decimal-to-hex-prefix.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Convert Decimal Numbers to Prefixed Hexadecimal Format

Transform decimal numbers to hexadecimal with 0x prefix using the [`format()`](https://library.humio.com/data-analysis/functions-format.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Function)] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    format("0x%X", field=[num])

### Introduction

The [`format()`](https://library.humio.com/data-analysis/functions-format.html) function can be used to format values according to specified patterns, including converting decimal numbers to their hexadecimal representation with a standard `0x` prefix commonly used in programming. 

In this example, the [`format()`](https://library.humio.com/data-analysis/functions-format.html) is used to convert decimal numbers to uppercase hexadecimal format with the `0x` prefix. The `%X` format specifier converts integers to hexadecimal with uppercase letters A-F. 

Example incoming data might look like this: 

@timestamp| event_type| num| description  
---|---|---|---  
2025-06-10T13:00:00Z| memory| 255| page boundary  
2025-06-10T13:01:00Z| memory| 16| offset value  
2025-06-10T13:02:00Z| memory| 4096| page size  
2025-06-10T13:03:00Z| memory| 65535| segment limit  
2025-06-10T13:04:00Z| memory| 10| base address  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Function)] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         format("0x%X", field=[num])

Converts the decimal numbers in the num field to their hexadecimal representation with the `0x` prefix. 

The [_`field`_](https://library.humio.com/data-analysis/functions-format.html#query-functions-format-field) parameter specifies which field to format, and the format string `0x%X` adds the prefix to the hexadecimal conversion. The result is stored in a new field named _format by default. 

The `%X` format specifier will convert the decimal number to hexadecimal using uppercase letters (A-F). For example, decimal `255` becomes `0xFF`, and `4096` becomes `0x1000`. The `0x` prefix makes it clear that the number is in hexadecimal format, which is a common convention in programming and debugging. 

  3. Event Result set.




### Summary and Results

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

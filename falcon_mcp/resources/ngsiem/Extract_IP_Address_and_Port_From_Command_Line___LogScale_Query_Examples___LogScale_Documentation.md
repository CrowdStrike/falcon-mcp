# Extract IP Address and Port From Command Line | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-regex-extract-ip-port.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract IP Address and Port From Command Line

Extract IP address and port from a command line string using the [`regex()`](https://library.humio.com/data-analysis/functions-regex.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    | regex("(?<ip>[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3})\\:(?<port>\\d{2,5})", field=CommandLine)

### Introduction

The [`regex()`](https://library.humio.com/data-analysis/functions-regex.html) function can be used to extract patterns from strings using regular expressions with named capture groups. It creates new fields containing the captured values. 

Note that characters in strings require escaping when using the [`regex()`](https://library.humio.com/data-analysis/functions-regex.html) function. 

In this example, the [`regex()`](https://library.humio.com/data-analysis/functions-regex.html) function is used to extract an IP address and port number from a command line string using named capture groups with properly escaped special characters. 

Example incoming data might look like this: 

@timestamp| CommandLine| ProcessId  
---|---|---  
2025-08-06T10:15:30.000Z| netstat -an | findstr 192.168.1.100:8080| 1234  
2025-08-06T10:15:31.000Z| curl http://10.0.0.50:443/api/status| 1235  
2025-08-06T10:15:32.000Z| ping 172.16.0.1:22| 1236  
2025-08-06T10:15:33.000Z| invalid command string| 1237  
2025-08-06T10:15:34.000Z| connect to 192.168.0.1:3389| 1238  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | regex("(?<ip>[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3})\\:(?<port>\\d{2,5})", field=CommandLine)

Applies a regular expression pattern to the CommandLine field to extract IP addresses and port numbers. The pattern uses two named capture groups separated by an escaped colon: 

     * `(?<ip>)` captures only the IP address pattern (four groups of 1-3 digits separated by escaped dots). 

     * An escaped colon `\\:` serves as the delimiter between IP and port. 

     * `(?<port>)` captures the port number pattern (2-5 digits). 

The matched values are returned in new fields named ip and port respectively. 

The double backslashes are required to properly escape the special characters (dots and colon) in the regular expression pattern. This structure ensures that the colon is not included in either the IP or port capture groups, resulting in cleaner extracted values. Events that do not match the pattern will not have these fields. 

  3. Event Result set.




### Summary and Results

The query is used to extract IP addresses and port numbers from command line strings using regular expression pattern matching. 

This query is useful, for example, to analyze network connections, monitor command line activities involving specific IP addresses and ports, or track connection attempts to specific services. 

Sample output from the incoming example data: 

CommandLine| ProcessId| ip| port  
---|---|---|---  
netstat -an | findstr 192.168.1.100:8080| 1234| 192.168.1| 8080  
curl http://10.0.0.50:443/api/status| 1235| 10.0.0| 443  
ping 172.16.0.1:22| 1236| 172.16.0| 22  
connect to 192.168.0.1:3389| 1238| 192.168.0| 3389  
  
Note that the event with the invalid command string is not included in the results as it did not match the regex pattern. 

Also pay attention to the importance of placing the parentheses correctly to avoid unexpected behavior. If doing the regex like this (the closing parenthesis is placed at the end of the string and not before the colon as in the above example): 

` | regex("(?<ip>[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\:(?<port>\\d{2,5}))", field=CommandLine) `

then the output field ip will also contain the colon and port value `192.168.1.100:8080`, and the output field port the value `8080`.

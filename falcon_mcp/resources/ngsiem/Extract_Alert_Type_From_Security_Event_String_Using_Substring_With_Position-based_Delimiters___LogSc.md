# Extract Alert Type From Security Event String Using Substring With Position-based Delimiters | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-substring-extract-alert-field.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract Alert Type From Security Event String Using Substring With Position-based Delimiters

Extract alert type from a security event string using the [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) function with [`text:positionOf()`](https://library.humio.com/data-analysis/functions-text-positionof.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    alertType := text:substring(securityEvent, begin=text:positionOf(securityEvent, character=",", occurrence=1) + 1, end=text:positionOf(securityEvent, character=",", occurrence=2))

### Introduction

The [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) function can be used to extract a portion of text from a string based on specified start and end positions. The [`text:positionOf()`](https://library.humio.com/data-analysis/functions-text-positionof.html) function helps locate specific characters within a string and returns their position, which can be used as input for substring operations. 

In this example, the [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) and [`text:positionOf()`](https://library.humio.com/data-analysis/functions-text-positionof.html) functions work together to extract the alert type from a security event string. The [`text:positionOf()`](https://library.humio.com/data-analysis/functions-text-positionof.html) function finds the positions of comma delimiters, which are then used by [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) to extract the text between them. 

Example incoming data might look like this: 

@rawstring| @timestamp  
---|---  
securityEvent="ALERT,malware_detected,endpoint123,trojan.exe,high_risk"| 1757568587006  
securityEvent="ALERT,brute_force_attempt,server456,ssh_service,medium_risk"| 1757568587006  
securityEvent="ALERT,suspicious_process,endpoint789,unusual_powershell,medium_risk"| 1757568587006  
securityEvent="ALERT,data_exfiltration,endpoint234,large_upload,high_risk"| 1757568587006  
securityEvent="ALERT,ransomware_behavior,endpoint567,encryption_activity,critical_risk"| 1757568587006  
securityEvent="ALERT,privilege_escalation,server789,sudo_abuse,high_risk"| 1757568587006  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         alertType := text:substring(securityEvent, begin=text:positionOf(securityEvent, character=",", occurrence=1) + 1, end=text:positionOf(securityEvent, character=",", occurrence=2))

Extracts the second field from the security event string using two functions: 

     * The [`text:positionOf()`](https://library.humio.com/data-analysis/functions-text-positionof.html) function is used twice on the securityEvent field: 

       * First to find the position of the first comma by setting [_`occurrence`_](https://library.humio.com/data-analysis/functions-text-positionof.html#query-functions-text-positionof-occurrence)=1 

       * Then to find the position of the second comma by setting [_`occurrence`_](https://library.humio.com/data-analysis/functions-text-positionof.html#query-functions-text-positionof-occurrence)=2 

     * The [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) function then extracts the text between these positions: 

       * The [_`begin`_](https://library.humio.com/data-analysis/functions-text-substring.html#query-functions-text-substring-begin) parameter is set to the position after the first comma (adding 1 to skip the comma) 

       * The [_`end`_](https://library.humio.com/data-analysis/functions-text-substring.html#query-functions-text-substring-end) parameter is set to the position of the second comma 

The results are returned in a new field named alertType that contains the actual alert type (such as `malware_detected` or `brute_force_attempt`) extracted from the securityEvent field. 

Alternatively, the string could also be: `| alertType := text:substring(securityEvent, begin=text:positionOf(securityEvent, character=",") + 1, end=text:positionOf(securityEvent, character=",", occurrence=2))`. The difference is, that the string in the example makes it possible to extract, for example, `malware_detected,endpoint123` by using `occurrence=1` and `occurrence=3`. 

  3. Event Result set.




### Summary and Results

The query is used to extract the specific alert type from a security event string by finding the positions of the delimiter characters and then extracting the text between them. 

This query is useful, for example, to parse specific alert types from security event strings where the data is embedded in a single field with comma-separated values. This is common in security logs where multiple pieces of information are combined into a single event string. 

Sample output from the incoming example data: 

alertType| securityEvent  
---|---  
malware_detected| ALERT,malware_detected,endpoint123,trojan.exe,high_risk  
brute_force_attempt| ALERT,brute_force_attempt,server456,ssh_service,medium_risk  
suspicious_process| ALERT,suspicious_process,endpoint789,unusual_powershell,medium_risk  
data_exfiltration| ALERT,data_exfiltration,endpoint234,large_upload,high_risk  
ransomware_behavior| ALERT,ransomware_behavior,endpoint567,encryption_activity,critical_risk  
privilege_escalation| ALERT,privilege_escalation,server789,sudo_abuse,high_risk  
  
Note that the extracted values in the alertType field contains the actual alert types, making it easier to analyze and categorize different types of security incidents. 

To extract other parts of the security event string, you could create similar queries with different [_`occurrence`_](https://library.humio.com/data-analysis/functions-text-positionof.html#query-functions-text-positionof-occurrence) values. For example, to get the affected endpoint, use `occurrence=2` and `occurrence=3`, or for the risk level, use the last two comma positions.

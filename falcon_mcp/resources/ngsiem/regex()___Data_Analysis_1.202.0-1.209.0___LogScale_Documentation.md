# regex() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-regex.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`regex()`](functions-regex.html "regex\(\)")

The [`regex()`](functions-regex.html "regex\(\)") provides a method for executing regular expressions on events to: 

  * Filter incoming events that match the regular expression 

  * Capture (extract) data using regex-based field extraction, and then filtering the events 

  * Capturing (extracting) data without filtering (when using the _`strict`_ mode to the [_`strict`_](functions-regex.html#query-functions-regex-strict) parameter 

  * Repeated or iteractive capture of data from events 




The regular expression syntax is the same as the [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters") syntax, but operates on specific fields or [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`field`_](functions-regex.html#query-functions-regex-field)|  string| optional[a] | `@rawstring`|  Specifies the field to run the regular expression against.   
[_`flags`_](functions-regex.html#query-functions-regex-flags)|  string| optional[[a]](functions-regex.html#ftn.table-functions-regex-optparamfn) | [`m`](functions-regex.html#query-functions-regex-flags-value-m)|  Specifies regex modifier flags.   
|  |  | **Values**  
|  |  | [`F`](functions-regex.html#query-functions-regex-flags-value-f)| Use the LogScale Regex Engine v2  
|  |  | [`d`](functions-regex.html#query-functions-regex-flags-value-d)| Period (.) also includes newline characters  
|  |  | [`i`](functions-regex.html#query-functions-regex-flags-value-i)| Ignore case for matched values  
|  |  | [`m`](functions-regex.html#query-functions-regex-flags-value-m)| Multi-line parsing of regular expressions  
[ _`limit`_](functions-regex.html#query-functions-regex-limit)|  integer| optional[[a]](functions-regex.html#ftn.table-functions-regex-optparamfn) | `100`|  Defines the maximum number of events to produce. A warning is produced if this limit is exceeded, unless the parameter is specified explicitly.   
[_`regex`_](functions-regex.html#query-functions-regex-regex)[b]| string| required |  |  Specifies a regular expression. The regular expression can contain one or more named capturing groups. Fields with the names of the groups will be added to the events.   
[_`repeat`_](functions-regex.html#query-functions-regex-repeat)|  boolean| optional[[a]](functions-regex.html#ftn.table-functions-regex-optparamfn) | [`false`](functions-regex.html#query-functions-regex-repeat-option-false)|  If set to true, multiple matches yields multiple events.   
|  |  | **Values**  
|  |  | [`false`](functions-regex.html#query-functions-regex-repeat-option-false)| Match at most one event  
|  |  | [`true`](functions-regex.html#query-functions-regex-repeat-option-true)| Match multiple events  
[ _`strict`_](functions-regex.html#query-functions-regex-strict)|  boolean| optional[[a]](functions-regex.html#ftn.table-functions-regex-optparamfn) | [`true`](functions-regex.html#query-functions-regex-strict-option-true)|  Specifies if events not matching the regular expression should be filtered out of the result set.   
|  |  | **Values**  
|  |  | [`false`](functions-regex.html#query-functions-regex-strict-option-false)| Events not matching the regular expression are not filtered out then the regex matches.  
|  |  | [`true`](functions-regex.html#query-functions-regex-strict-option-true)| Events not matching the regular expression are filtered out of the result set.  
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`regex`_](functions-regex.html#query-functions-regex-regex) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`regex`_](functions-regex.html#query-functions-regex-regex) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     regex("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     regex(regex="value")
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
>     !regex()
> 
> Or:
> 
> logscale Syntax
>     
>     
>     not regex()
> 
> For more information, see [Negating the Result of Filter Functions](syntax-operators.html#syntax-operators-negate "Negating the Result of Filter Functions").

### [`regex()`](functions-regex.html "regex\(\)") Function Operation

Regular expressions in LogScale allow you search (filter) and extract information and are a very common part of the LogScale language and syntax. 

LogScale uses JitRex which closely follows — but does not entirely replicate — the syntax of RE2J regular expressions, which is very close to Java's regular expressions. See [Regular Expression Syntax](syntax-regex.html "Regular Expression Syntax") for more information. 

### Note

To ensure compatibility, it is recommended to always test your regular expressions inside LogScale, instead of a 3rd party regex tool. 

#### Escaping Characters

Care needs to be taken when escaping characters in the regular expression submitted to the [`regex()`](functions-regex.html "regex\(\)") function. The functions uses the `\` backslash character to indicate when an individual character needs to be escaped, which is used in many common situations to indicate the original character. This works for all characters except the backslash itself. Within [`regex()`](functions-regex.html "regex\(\)") you must double-escape the backslash; this is because it needs to be escaped for definition within the string, and then again when the regular expressed is parsed. 

This can cause complexities when looking for filenames that use the backslash (for example, Windows filename `\Windows\tmp\myfile.txt`). The following regular expression will not work as expected: 

logscale Syntax
    
    
    regex("\\(?<file_name>[^\\]+$)")

The regular expression is trying to identify all the text between the `\` characters. However, because we are submitting a string to the [`regex()`](functions-regex.html "regex\(\)"), the regular expression will instead sse: 

logscale Syntax
    
    
    \(?<file_name>[^\]+$)

Because the backslash is only escaped once the expression will fail. Instead, escape the backslash twice: 

logscale
    
    
    regex("\\\\(?<file_name>[^\\\\]+$)")

Two alternatives exist to avoid this: 

  * Use the ASCII character code (`\x5c`) to specify the backslash: 

logscale
        
        regex("\x5c\x5c(?<file_name>[^\x5c\x5c]+$)")

  * Use the `/regex` which is only parsed once and so only needs to be escaped once: 

logscale Syntax
        
        /\\(?<file_name>[^\\]+$)




#### Comparing [`regex()`](functions-regex.html "regex\(\)") and [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters") Syntax

The operation of [`regex()`](functions-regex.html "regex\(\)") and [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters") are summarized in the table below: 

Operation |  [`regex()`](functions-regex.html "regex\(\)") |  [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters")  
---|---|---  
Default search |  [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) |  All defined or parsed fields and [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) (not tags, [@id](searching-data-event-fields.html#searching-data-event-fields-metadata-id) or timestamp fields)   
Specific field search |  Using [_`field`_](functions-regex.html#query-functions-regex-field) parameter |  Using `field = /regex/`  
  
Note that: 

  * `foo = /regex/` and `regex("regex", field=foo)` are equivalent; the latter has the benefit that more parameters can be used to refine the search. Specifically, it allows for specifying [_`strict=false`_](functions-regex.html#query-functions-regex-strict). The former has the benefit that the regular expression is not written as a string and therefore there are elements that don't need escaping. 

  * [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters") specifies free-text search which searches all fields. Wehn used in a query it searches exactly the fields as they were in the original event, and it works only before the first aggregator. 

  * If using [`regex()`](functions-regex.html "regex\(\)") and [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) is absent, then the function will work, because there is no field to execute against. 




The difference in search scope between the two regex syntax operations introduces a significant performance difference between the two. Using [`regex()`](functions-regex.html "regex\(\)") searches only the specified field ([@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) by default) and can be significantly more performant than the [`/regex/`](syntax-filters.html#syntax-filters-regex "Regular Expression Filters") syntax depending on the number of fields in the dataset. 

#### Using `g` in [_`flags`_](functions-regex.html#query-functions-regex-flags)

When performing queries, the `g` option — used for global, as in repeating — is allowed in a query, but is not an acceptable option for the [_`flags`_](functions-regex.html#query-functions-regex-flags) parameter. To use one of the parameters for multiple matches, you should instead set the _`repeat`_ parameter to `true`. 

For more information, see [Global (Repeating) Matches](syntax-regex-diffs.html#syntax-regex-diffs-pcre-global). 

### [`regex()`](functions-regex.html "regex\(\)") Syntax Examples

Extract the domain name of the http referrer field. Often this field contains a full url, so we can have many different URLs from the same site. In this case we want to count all referrals from the same domain. This will add a field named refdomain to events matching the regular expression. 

logscale
    
    
    regex("https?://(www.)?(?<refdomain>.+?)(/
    | $)", field=referrer)
    | groupBy(refdomain, function=count())
    | sort(field=_count, type=number, reverse=true)

Extract the user id from the url field. New fields are stored in a field named userid. 

logscale
    
    
    regex(regex="/user/(?<_userid_ >\\S+)/pay", field=url)

Show how to escape `"` in the regular expression. This is necessary because the regular expression is itself in quotes. Extract the user and message from events like: `Peter: "hello"` and `Bob: "good morning"`. 

logscale Syntax
    
    
    regex("(?<name>\\S+): \"(?<msg>\\S+)\"")

### Note

There are no default flags for a regular expression. For example: 

logscale Syntax
    
    
    @rawstring=/expression/

Is syntactically equivalent to: 

logscale Syntax
    
    
    regex("expression")

Or: 

logscale Syntax
    
    
    regex("expression", flags="")

When using flags: 

logscale Syntax
    
    
    @rawstring=/expression/m

Is syntactically equivalent to: 

logscale Syntax
    
    
    regex("expression", flags="m")

### [`regex()`](functions-regex.html "regex\(\)") Examples

Click + next to an example below to get the full details.

#### Extract Components from Fixed-Length Data

**Extract Components from Variable Length Data using the[`text:substring()`](functions-text-substring.html "text:substring\(\)") function with regex **

##### Query

logscale
    
    
    data = /^(?<id>\d{2})(?<payloadLength>\d{4})(?<remaining>.+)$/
    payload := text:substring(remaining, end=payloadLength)
    transactionID := text:substring(remaining, begin=payloadLength)

##### Introduction

In this example, the [`text:substring()`](functions-text-substring.html "text:substring\(\)") function is used with a regular expression to break down variable-length data strings into their component parts based on predefined positions and lengths. 

Example incoming data might look like this: 

@timestamp| data  
---|---  
2025-08-06T10:15:00.000Z| 6800091A3C5B78F4468  
2025-08-06T10:15:01.000Z| 420004E2E228930  
2025-08-06T10:15:02.000Z| 7800123ABC45DE6789  
2025-08-06T10:15:03.000Z| 910007DEFG89HI1234  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         data = /^(?<id>\d{2})(?<payloadLength>\d{4})(?<remaining>.+)$/

Uses a regular expression to parse the data field with these capture groups: 

     * id: `^` matches the start of the string, followed by `\d{2}` which captures exactly two digits. 

     * payloadLength: `\d{4}` captures exactly four digits after the id. 

     * remaining: `.+` captures one or more of any character until `$` (end of string). 

The regex pattern ensures that the entire string matches this format with no additional characters before or after, due to the `^` (start) and `$` (end) anchors. 

  3. logscale
         
         payload := text:substring(remaining, end=payloadLength)

Extracts a substring from the remaining field starting at position 0 and ending at the position specified by payloadLength (extracted by the regular expression in the previous line) and returns the result in a new field named payload. 

The [_`end`_](functions-text-substring.html#query-functions-text-substring-end) parameter specifies the exclusive end position of the substring. 

  4. logscale
         
         transactionID := text:substring(remaining, begin=payloadLength)

Extracts a substring from the remaining field starting at the position specified by payloadLength until the end of the string and returns the result in a new field named transactionID. 

The [_`begin`_](functions-text-substring.html#query-functions-text-substring-begin) parameter specifies the inclusive start position of the substring. 

  5. Event Result set.




##### Summary and Results

The query is used to parse variable-length data strings where different portions of the string represent specific pieces of information in a predefined format. 

This query is useful, for example, to process type-length-value like data formats, which are common in network protocols, or any variable-length formatted messages where different segments of the data have specific meanings based on their position and length. 

Sample output from the incoming example data: 

data| id| payload| payloadLength| remaining| transactionID  
---|---|---|---|---|---  
6800091A3C5B78F4468| 68| 1A3C5B78F| 0009| 1A3C5B78F4468| 4468  
420004E2E228930| 42| E2E2| 0004| E2E228930| 28930  
7800123ABC45DE6789| 78| 3ABC45DE6789| 0012| 3ABC45DE6789| <no value>  
910007DEFG89HI1234| 91| DEFG89H| 0007| DEFG89HI1234| I1234  
  
Note that the payloadLength field determines exactly how many characters to extract for the payload field. When the payloadLength equals the length of remaining, then the transactionID field will be empty. 

Also note that the payload and transactionID fields together make up the complete remaining field. 

#### Extract IP Address and Port From Command Line

**Extract IP address and port from a command line string using the[`regex()`](functions-regex.html "regex\(\)") function **

##### Query

logscale
    
    
    | regex("(?<ip>[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3})\\:(?<port>\\d{2,5})", field=CommandLine)

##### Introduction

In this example, the [`regex()`](functions-regex.html "regex\(\)") function is used to extract an IP address and port number from a command line string using named capture groups with properly escaped special characters. 

Example incoming data might look like this: 

@timestamp| CommandLine| ProcessId  
---|---|---  
2025-08-06T10:15:30.000Z| netstat -an | findstr 192.168.1.100:8080| 1234  
2025-08-06T10:15:31.000Z| curl http://10.0.0.50:443/api/status| 1235  
2025-08-06T10:15:32.000Z| ping 172.16.0.1:22| 1236  
2025-08-06T10:15:33.000Z| invalid command string| 1237  
2025-08-06T10:15:34.000Z| connect to 192.168.0.1:3389| 1238  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         | regex("(?<ip>[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3})\\:(?<port>\\d{2,5})", field=CommandLine)

Applies a regular expression pattern to the CommandLine field to extract IP addresses and port numbers. The pattern uses two named capture groups separated by an escaped colon: 

     * `(?<ip>)` captures only the IP address pattern (four groups of 1-3 digits separated by escaped dots). 

     * An escaped colon `\\:` serves as the delimiter between IP and port. 

     * `(?<port>)` captures the port number pattern (2-5 digits). 

The matched values are returned in new fields named ip and port respectively. 

The double backslashes are required to properly escape the special characters (dots and colon) in the regular expression pattern. This structure ensures that the colon is not included in either the IP or port capture groups, resulting in cleaner extracted values. Events that do not match the pattern will not have these fields. 

  3. Event Result set.




##### Summary and Results

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

#### Extract URL Page Names and Find Most Common Pages

**Extract page names from URLs and count their frequency using[`regex()`](functions-regex.html "regex\(\)") function with [`top()`](functions-top.html "top\(\)") **

##### Query

logscale
    
    
    regex(regex="/.*/(?<url_page>\S+\.page)", field=url)
    | top(url_page, limit=12, rest=others)

##### Introduction

In this example, the [`regex()`](functions-regex.html "regex\(\)") function is used to extract page names from URLs, and then [`top()`](functions-top.html "top\(\)") is used to identify the most frequently accessed pages. 

Example incoming data might look like this: 

@timestamp| url| status_code| user_agent  
---|---|---|---  
2023-08-06T10:00:00Z| https://example.com/products/item1.page| 200| Mozilla/5.0  
2023-08-06T10:01:00Z| https://example.com/about/company.page| 200| Chrome/90.0  
2023-08-06T10:02:00Z| https://example.com/products/item2.page| 404| Safari/14.0  
2023-08-06T10:03:00Z| https://example.com/products/item1.page| 200| Firefox/89.0  
2023-08-06T10:04:00Z| https://example.com/contact/support.page| 200| Chrome/90.0  
2023-08-06T10:05:00Z| https://example.com/about/company.page| 200| Safari/14.0  
2023-08-06T10:06:00Z| https://example.com/products/item3.page| 200| Mozilla/5.0  
2023-08-06T10:07:00Z| https://example.com/products/item1.page| 200| Chrome/90.0  
2023-08-06T10:08:00Z| https://example.com/about/company.page| 200| Firefox/89.0  
2023-08-06T10:09:00Z| https://example.com/products/item2.page| 404| Safari/14.0  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         regex(regex="/.*/(?<url_page>\S+\.page)", field=url)

Extracts the page name including the `.page` extension from the url field using a regular expression with a named capture group url_page. The pattern matches any characters up to the last forward slash (`.*`), followed by any non-whitespace characters (`\S+`) ending with `.page`. 

  3. logscale
         
         | top(url_page, limit=12, rest=others)

Groups the results by the extracted url_page field and counts their occurrences. The [_`limit`_](functions-top.html#query-functions-top-limit) parameter is set to show the top 12 results, and the [_`rest`_](functions-top.html#query-functions-top-rest) parameter combines all remaining values into a group named `others`. 

  4. Event Result set.




##### Summary and Results

The query is used to analyze the most frequently accessed pages on a website by extracting page names from URLs and counting their occurrences. 

This query is useful, for example, to identify popular content, monitor user behavior patterns, or detect potential issues with specific pages that receive high traffic. 

Sample output from the incoming example data: 

url_page| _count  
---|---  
item1.page| 3  
company.page| 3  
item2.page| 2  
support.page| 1  
item3.page| 1  
  
Note that the results are automatically sorted in descending order by count, showing the most frequently accessed pages first. 

#### Extract the Top Most Viewed Pages of a Website

****

##### Query

logscale
    
    
    regex(regex="/.*/(?<url_page>\S+\.page)", field=url)
    | top(url_page, limit=12, rest=others)

##### Introduction

Your LogScale repository is ingesting log entries from a web server for a photography site. On this site there are several articles about photography. The URL for articles on this site ends with the extension, `.page` instead of `.html`. 

You want to extract the page users viewed and then list the top most viewed pages. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         regex(regex="/.*/(?<url_page>\S+\.page)", field=url)

Extracts the page viewed by users by returning the name of the file from the url field and storing that result in a field labeled, url_page. 

  3. logscale
         
         | top(url_page, limit=12, rest=others)

Lists the top most viewed pages. The first parameter given is that url_page field coming from the first line of the query. The second parameter is to limit the results to the top twelve — instead of the default limit of ten. Because we're curious of how many pages were viewed during the selected period that were not listed in the top twelve, the rest parameter is specified with the label to use. 

  4. Event Result set.




##### Summary and Results

The table displays the matches from the most viewed pages during the selected period to the least — limited to the top twelve. 

url_page| _count  
---|---  
home.page| 51  
index.page| 21  
home-studio.page| 10  
a-better-digital-camera.page| 7  
is-film-better.page| 6  
leica-q-customized.page| 6  
student-kit.page| 4  
focusing-screens.page| 4  
changing-images-identity.page| 2  
others| 27  
  
#### Filter Out Based on a Non-Matching Regular Expression (Function Format)

****

##### Query

logscale
    
    
    responsesize > 2000
    | not regex("/falcon-logscale-.*/",field=url)

##### Introduction

This example searches weblog data looking for large log entries that are larger than a specified size but not in a specific directory. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         responsesize > 2000

Fine 

  3. logscale
         
         | not regex("/falcon-logscale-.*/",field=url)

Negates the regular expression match, here filtering out any filename that contains the prefix `falcon-logscale`, but returning all other matching URLs. 

  4. Event Result set.




##### Summary and Results

For example, given the following events: 

@timestamp| #repo| #type| @id| @ingesttimestamp| @rawstring| @timestamp.nanos| @timezone| client| httpversion| method| responsesize| statuscode| url| userid  
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6401_1719982743| 2024-07-03T04:59:41| 192.168.1.240 - - [03/07/2024:04:59:03 +0000] "GET /js/htmllinkhelp.js HTTP/1.1" 200 23| 0| Z| 192.168.1.240| HTTP/1.1| GET| 23| 200| /js/htmllinkhelp.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6400_1719982743| 2024-07-03T04:59:41| 192.168.1.24 - - [03/07/2024:04:59:03 +0000] "GET /data-analysis-1.100/css-images/external-link.svg HTTP/1.1" 200 1072| 0| Z| 192.168.1.24| HTTP/1.1| GET| 1072| 200| /data-analysis-1.100/css-images/external-link.svg| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6399_1719982743| 2024-07-03T04:59:41| 192.168.1.209 - - [03/07/2024:04:59:03 +0000] "GET /js/htmllinkhelp.js HTTP/1.1" 304 -| 0| Z| 192.168.1.209| HTTP/1.1| GET| -| 304| /js/htmllinkhelp.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6398_1719982743| 2024-07-03T04:59:41| 192.168.1.39 - - [03/07/2024:04:59:03 +0000] "GET /data-analysis/js/java.min.js HTTP/1.1" 304 -| 0| Z| 192.168.1.39| HTTP/1.1| GET| -| 304| /data-analysis/js/java.min.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6397_1719982743| 2024-07-03T04:59:41| 192.168.1.62 - - [03/07/2024:04:59:03 +0000] "GET /falcon-logscale-cloud/js/php.min.js HTTP/1.1" 200 6397| 0| Z| 192.168.1.62| HTTP/1.1| GET| 6397| 200| /falcon-logscale-cloud/js/php.min.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6396_1719982743| 2024-07-03T04:59:41| 192.168.1.206 - - [03/07/2024:04:59:03 +0000] "GET /integrations/js/theme.js HTTP/1.1" 200 14845| 0| Z| 192.168.1.206| HTTP/1.1| GET| 14845| 200| /integrations/js/theme.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6395_1719982743| 2024-07-03T04:59:41| 192.168.1.1 - - [03/07/2024:04:59:03 +0000] "GET /data-analysis/js/json.min.js HTTP/1.1" 200 496| 0| Z| 192.168.1.1| HTTP/1.1| GET| 496| 200| /data-analysis/js/json.min.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_0_6394_1719982743| 2024-07-03T04:59:41| 192.168.1.252 - - [03/07/2024:04:59:03 +0000] "GET /falcon-logscale-cloud/js/java.min.js HTTP/1.1" 200 2739| 0| Z| 192.168.1.252| HTTP/1.1| GET| 2739| 200| /falcon-logscale-cloud/js/java.min.js| -  
  
Might return the following values: 

@timestamp| #repo| #type| @id| @ingesttimestamp| @rawstring| @timestamp.nanos| @timezone| client| httpversion| method| responsesize| statuscode| url| userid  
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_2_6541_1719982743| 2024-07-03T05:03:48| 192.168.1.231 - - [03/07/2024:04:59:03 +0000] "GET /logscale-repo-schema/js/corp.js HTTP/1.1" 200 18645| 0| Z| 192.168.1.231| HTTP/1.1| GET| 18645| 200| /logscale-repo-schema/js/corp.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_2_6538_1719982743| 2024-07-03T05:03:48| 192.168.1.69 - - [03/07/2024:04:59:03 +0000] "GET /data-analysis-1.100/images/dashboards.png HTTP/1.1" 200 152590| 0| Z| 192.168.1.69| HTTP/1.1| GET| 152590| 200| /data-analysis-1.100/images/dashboards.png| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_2_6535_1719982743| 2024-07-03T05:03:47| 192.168.1.154 - - [03/07/2024:04:59:03 +0000] "GET /integrations/js/theme.js HTTP/1.1" 200 14845| 0| Z| 192.168.1.154| HTTP/1.1| GET| 14845| 200| /integrations/js/theme.js| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_2_6534_1719982743| 2024-07-03T05:03:47| 192.168.1.58 - - [03/07/2024:04:59:03 +0000] "GET /integrations/images/extrahop.png HTTP/1.1" 200 10261| 0| Z| 192.168.1.58| HTTP/1.1| GET| 10261| 200| /integrations/images/extrahop.png| -  
2024-07-03T04:59:03| weblogs| httpsimp| MqHKxw2QoBPZyNqbJRRs4ECC_2_6527_1719982743| 2024-07-03T05:03:47| 192.168.1.164 - - [03/07/2024:04:59:03 +0000] "GET /integrations/images/zeek.png HTTP/1.1" 200 4392| 0| Z| 192.168.1.164| HTTP/1.1| GET| 4392| 200| /integrations/images/zeek.png| -  
  
#### Filter Out Based on a Non-Matching Regular Expression (Syntax)

****

##### Query

logscale
    
    
    method != /(PUT
    | POST)/

##### Introduction

This example searches weblog data looking for events where the method does not match a specified value. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         method != /(PUT
         | POST)/

This line performs a negative regular expression match, returning only the events where the method does not match either `PUT` or `POST`. 

  3. Event Result set.




##### Summary and Results

This format of the query can be a simple way to perform a negative regular expression match, or more specifically, returning a list of the events that do not match the given regular expression. 

#### Get Integer Part of Number

**Get the integer part of a number using the[`regex()`](functions-regex.html "regex\(\)") function and regex capturing groups **

##### Query

logscale
    
    
    regex("(?<b>\\d+)\\..*",field=a)

##### Introduction

In this example, regex pattern matching with a named capturing group is used to look at a filename and find something after the backslash, then store it in a new field named b, leaving the original field a unchanged. 

See also alternative method mentioned under the summary. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         regex("(?<b>\\d+)\\..*",field=a)

Looks for a sequence of characters in a capturing group and replaces the character with a digit (number): \\\ backslash (\\) \d+ one or more digits \\\ backslash (\\) . any character .* zero or more characters. If the sequence of characters in an event looks like this `\folder58\` instead of `\folder58\a` , then there is no filename as nothing comes after the `\`. 

  3. Event Result set.




##### Summary and Results

The query with regex pattern matching and named capturing group is used to get the integer part of a number, storing the replacement (the matched value) automatically in a new field named b. This is useful when searching for specific filenames. 

The query using the [`regex()`](functions-regex.html "regex\(\)") function is primarily used for pattern matching and extraction as regex is generally very concise for simple extraction tasks. 

Alternative

There is another way of achieving the same end result using the [`replace()`](functions-replace.html "replace\(\)") function in a query like this: `replace("(\\d+)\\..*", with="$1", field=a, as=b)`. This query uses the replace function with numbered references to perform substitution, whereas the first one uses regex pattern matching with a named capture group. 

The query using [`replace()`](functions-replace.html "replace\(\)") captures digits before the decimal point in an unnamed group, and explicitly creates a new field b with the result (\\\d+). 

This query using the [`replace()`](functions-replace.html "replace\(\)") function is more used for string manipulation and transformation in a replacement operation. 

#### Replace Word or Substring With Another

**Replace a word or substring with another in an event set using the[`replace()`](functions-replace.html "replace\(\)") function with a regular expression **

##### Query

logscale
    
    
    replace(regex=propperties, with=properties)

##### Introduction

In this example, the [`replace()`](functions-replace.html "replace\(\)") function is used to correct a spelling mistake. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         replace(regex=propperties, with=properties)

Replaces the word `propperties` with the word `properties`. 

  3. Event Result set.




##### Summary and Results

The query is used to correct spelling mistakes in an event set. Changing words or other substrings like this with a regular expression is useful in many situations, where it is necessary to make quick changes of field values. 

#### Search for Command Line String

**Search for command line string after`/` and before `@` using a regular expression **

##### Query

logscale
    
    
    #event_simpleName=ProcessRollup2
    | CommandLine=/@/
    | CommandLine=/\/.*@/

##### Introduction

A regular expression can be used to run a query that looks for command line strings containing any characters after `/` and before `@`. It is important to perform as much filtering as possible to not exceed resource limits. 

In this example, a regular expression is used to filter and search for specific process events in the CrowdStrike Falcon platform. Note that the query filters on the `@` alone first to perform as much filtering as possible. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #event_simpleName=ProcessRollup2

Filters for events of the type `ProcessRollup2` in the #event_simpleName field. 

  3. logscale
         
         | CommandLine=/@/

Filters for any command line containing the `@` symbol. 

  4. logscale
         
         | CommandLine=/\/.*@/

Uses a regular expression to search the returned results for command lines that contain a forward slash (`/`) followed by any number of characters, and then a `@` symbol. 

  5. Event Result set.




##### Summary and Results

The query is used to search for command line strings that contain any characters after `/` and before `@`. The query could, for example, be used to help security analysts identify potentially suspicious processes that might be interacting with email addresses or using email-like syntax in their command lines. 

#### Truncate a String or Message

**Truncate a string or message to exact 100 characters using[`replace()`](functions-replace.html "replace\(\)") function and regex capturing groups **

##### Query

logscale
    
    
    replace("^(.{100}).*", with="$1", field=message, as="truncated_message")

##### Introduction

In this example, the [`replace()`](functions-replace.html "replace\(\)") function together with regex capturing group, is used to truncate a string, chop of last part of a message, to only show the first `100` characters, replace the last character with a digit (number) at the end of the line. and then store the truncated string in the new field truncated_message, leaving the field message untouched. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         replace("^(.{100}).*", with="$1", field=message, as="truncated_message")

Captures group that matches exactly 100 characters of any type starting from the beginning of the line and replaces the last character at the end of the truncated string with a digit, then returns the truncated version in a new field named truncated_message. The original message field remains unchanged. 

`with="$1"` means that it replaces the entire match with the defined number of characters, in this case 100 characters. 

  3. Event Result set.




##### Summary and Results

The query is used to truncate strings. 

Truncation can, for example, be used to speed up download times and complete searches faster. In file systems, the truncate operation is used to reduce the size of a file by removing data from the end. This can be helpful when you need to reclaim storage space or when dealing with log files that need to be periodically truncated. 

Another advantage of truncation is, that it allows you to search for a word that could have multiple endings. This way it will broaden the results and look for variations of words. 

Truncation of numbers is also useful to shorten digits past a certain point in the number.

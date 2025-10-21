# urlDecode() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-urldecode.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`urlDecode()`](functions-urldecode.html "urlDecode\(\)")

URL-decodes the contents of a string field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-urldecode.html#query-functions-urldecode-as)|  string| optional[a] | `_urldecode`|  Name of output field.   
[_`field`_](functions-urldecode.html#query-functions-urldecode-field)[b]| string| required |  |  Name of input field that contains the value for URL decoding.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-urldecode.html#query-functions-urldecode-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-urldecode.html#query-functions-urldecode-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     urlDecode("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     urlDecode(field="value")
> 
> These examples show basic structure only.

### [`urlDecode()`](functions-urldecode.html "urlDecode\(\)") Syntax Examples

With an event with a field Bar=https%3A%2F%2Fwww.example.com, you get `https://www.example.com` in the _urldecode field: 

logscale
    
    
    urlDecode("Bar")

With an event with a field Bar=https%3A%2F%2Fwww.example.com, you get `https://www.example.com` in the Foo field: 

logscale
    
    
    Foo:=urlDecode("Bar")

With an event with a field Bar=https%3A%2F%2Fwww.example.com, you get `https://www.example.com` in the Foo field: 

logscale
    
    
    urlDecode("Bar", as="Foo")

### [`urlDecode()`](functions-urldecode.html "urlDecode\(\)") Examples

Click + next to an example below to get the full details.

#### Decode Redirect URLs in Authentication Logs

**Decode Redirect URLs in Authentication Logs to analyze authentication flows using the urlDecode() function with[ _`as`_](functions-urldecode.html#query-functions-urldecode-as) parameter **

##### Query

logscale
    
    
    redirect_url = *
    | urlDecode(field=redirect_url, as=decoded_redirect)
    | auth_status="success"

##### Introduction

In this example, the [`urlDecode()`](functions-urldecode.html "urlDecode\(\)") function is used to decode URL-encoded redirect URLs in authentication logs to analyze user authentication flows and potential security issues. Using the [_`as`_](functions-urldecode.html#query-functions-urldecode-as) parameter, you can specify a custom field name for the decoded result. 

Example incoming data might look like this: 

@timestamp| auth_status| redirect_url| user_id| source_ip  
---|---|---|---|---  
1683000000000| success| https%3A%2F%2Fapp.example.com%2Fdashboard%3Ftoken%3Dabc123| user1| 10.0.0.1  
1683000001000| failed| https%3A%2F%2Fmalicious.com%2Fphish%3Ftoken%3Dxyz789| user2| 192.168.1.100  
1683000002000| success| https%3A%2F%2Fapp.example.com%2Freports%3Fid%3D456%26view%3Dfull| user3| 10.0.0.2  
1683000003000| success| https%3A%2F%2Fapp.example.com%2Fsettings%3Fmode%3Dadmin| user4| 10.0.0.3  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         redirect_url = *

Filters for events containing the redirect_url field. 

  3. logscale
         
         | urlDecode(field=redirect_url, as=decoded_redirect)

Decodes the URL-encoded values in the redirect_url field and stores the result in a new field named decoded_redirect using the [_`as`_](functions-urldecode.html#query-functions-urldecode-as) parameter. 

  4. logscale
         
         | auth_status="success"

Filters to include only successful authentication attempts. 

  5. Event Result set.




##### Summary and Results

The query is used to analyze post-authentication redirect patterns by decoding redirect URLs from authentication logs. 

This query is useful, for example, to monitor authentication flows, detect suspicious redirect patterns, or track which application areas users access after authentication. 

Sample output from the incoming example data: 

@timestamp| auth_status| decoded_redirect| redirect_url| source_ip| user_id  
---|---|---|---|---|---  
1.683E+12| success| https://app.example.com/dashboard?token=abc123| https%3A%2F%2Fapp.example.com%2Fdashboard%3Ftoken%3Dabc123| 10.0.0.1| user1  
1.683E+12| success| https://app.example.com/reports?id=456&view=full| https%3A%2F%2Fapp.example.com%2Freports%3Fid%3D456%26view%3Dfull| 10.0.0.2| user3  
1.683E+12| success| https://app.example.com/settings?mode=admin| https%3A%2F%2Fapp.example.com%2Fsettings%3Fmode%3Dadmin| 10.0.0.3| user4  
  
Note that the decoded URL is stored in the specified field decoded_redirect and special characters (&, =, ?) are properly decoded. 

#### Decode Referrer URLs in Web Access Logs

**Decode Referrer URLs in Web Access Logs to analyze traffic sources using the[`urlDecode()`](functions-urldecode.html "urlDecode\(\)") function with assignment operator **

##### Query

logscale
    
    
    referrer = *
    | decodedUrl := urlDecode(field=referrer)
    | conversion=true

##### Introduction

In this example, the [`urlDecode()`](functions-urldecode.html "urlDecode\(\)") function is used to decode URL-encoded referrer URLs to analyze traffic sources and marketing campaign effectiveness. Using the assignment operator (:=), you can specify a custom field name for the decoded result. 

Example incoming data might look like this: 

@timestamp| referrer| campaign_id| conversion| revenue  
---|---|---|---|---  
1683000000000| https%3A%2F%2Fwww.google.com%2Fsearch%3Fq%3Dbest%20cloud%20security| camp_001| true| 199.99  
1683000001000| https%3A%2F%2Fwww.facebook.com%2Fads%3Fcampaign%3Dsecurity2023| camp_002| false| 0.00  
1683000002000| https%3A%2F%2Ftwitter.com%2Fstatus%3Fpromo%3Dspring50| camp_003| true| 299.99  
1683000003000| https%3A%2F%2Fwww.google.com%2Fsearch%3Fq%3Dantivirus%20enterprise| camp_001| false| 0.00  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         referrer = *

Filters for events containing the referrer field. 

  3. logscale
         
         | decodedUrl := urlDecode(field=referrer)

Decodes the URL-encoded values in the referrer field and assigns the result to a new field named decodedUrl. 

  4. logscale
         
         | conversion=true

Filters to include only successful conversions. 

  5. Event Result set.




##### Summary and Results

The query is used to analyze traffic sources that led to successful conversions by decoding referrer URLs. 

This query is useful, for example, to track which search terms or social media campaigns are driving successful conversions, or to analyze the effectiveness of different marketing channels. 

Sample output from the incoming example data: 

@timestamp| campaign_id| conversion| decodedUrl| referrer| revenue  
---|---|---|---|---|---  
1.683E+12| camp_001| TRUE| https://www.google.com/search?q=best cloud security| https%3A%2F%2Fwww.google.com%2Fsearch%3Fq%3Dbest%20cloud%20security| 199.99  
1.683E+12| camp_003| TRUE| https://twitter.com/status?promo=spring50| https%3A%2F%2Ftwitter.com%2Fstatus%3Fpromo%3Dspring50| 299.99  
  
Note that the original encoded referrer field remains unchanged. 

#### Decode URL-Encoded Strings

**Decode URL-Encoded Web Request Parameters using the[`urlDecode()`](functions-urldecode.html "urlDecode\(\)") function **

##### Query

logscale
    
    
    request_url = *
    | urlDecode(field=request_url)
    | status_code=200

##### Introduction

In this example, the [`urlDecode()`](functions-urldecode.html "urlDecode\(\)") function is used to decode URL-encoded parameters from web requests to analyze user interactions. When used without specifying an output field, the decoded result is automatically stored in a field named _urldecode. 

Example incoming data might look like this: 

@timestamp| request_url| status_code| bytes_sent| response_time  
---|---|---|---|---  
1683000000000| /products?category=electronics&filter=price%3E100%20AND%20brand%3DApple| 200| 2048| 0.23  
1683000001000| /search?q=wireless%20headphones%20with%20noise%20cancelling| 200| 1536| 0.15  
1683000002000| /products?id=12345&return_url=%2Fcart%3Fcheckout%3Dtrue| 500| 512| 1.45  
1683000003000| /search?q=bluetooth%20speakers%20under%20%24100| 200| 1024| 0.  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         request_url = *

Filters for events containing the request_url field. 

  3. logscale
         
         | urlDecode(field=request_url)

Decodes the URL-encoded values in the request_url field, and returns the result in the default output field _urldecode. 

  4. logscale
         
         | status_code=200

Filters to include only successful requests with status code `200`. 

  5. Event Result set.




##### Summary and Results

The query is used to decode URL-encoded web request parameters to analyze user behavior and application patterns. 

This query is useful, for example, to monitor user search patterns, analyze product filtering preferences, or troubleshoot issues with specific URL parameters. 

Sample output from the incoming example data: 

@timestamp| _urldecode| bytes_sent| request_url| response_time| status_code  
---|---|---|---|---|---  
1.683E+12| /products?category=electronics&filter=price>100 AND brand=Apple| 2048| /products?category=electronics&filter=price%3E100%20AND%20brand%3DApple| 0.23| 200  
1.683E+12| /search?q=wireless headphones with noise cancelling| 1536| /search?q=wireless%20headphones%20with%20noise%20cancelling| 0.15| 200  
1.683E+12| /search?q=bluetooth speakers under $100| 1024| /search?q=bluetooth%20speakers%20under%20%24100| 0.18| 200  
  
Note that special characters (>, $, spaces) are properly decoded and failed requests (`status_code != 200`) are excluded.

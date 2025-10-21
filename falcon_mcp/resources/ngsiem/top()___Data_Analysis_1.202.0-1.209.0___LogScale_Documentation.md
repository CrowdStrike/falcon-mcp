# top() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-top.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`top()`](functions-top.html "top\(\)")

Use this query function to find the most common values of a field in a set of events — the top of an ordered list of results. It's also possible to find the occurrences of a field using the value of another field. 

The [`top()`](functions-top.html "top\(\)") query function is a more succinct and powerful way to execute the [`groupBy()`](functions-groupby.html "groupBy\(\)") query in conjunction with [`count()`](functions-count.html "count\(\)") and [`sort()`](functions-sort.html "sort\(\)"): 

logscale
    
    
    groupBy([*fields*], function=count())
    | sort(_count)

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-top.html#query-functions-top-as)|  string| optional[a] | `_count or _sum`|  The optional name of the output field.   
[_`error`_](functions-top.html#query-functions-top-error)|  number| optional[[a]](functions-top.html#ftn.table-functions-top-optparamfn) | `5`|  The error threshold in percentage for displaying a warning message when not precise enough.   
[_`field`_](functions-top.html#query-functions-top-field)[b]| array of strings| required |  |  The fields on which to group and count. An event is not counted if fields are not present.   
[_`limit`_](functions-top.html#query-functions-top-limit)|  number| optional[[a]](functions-top.html#ftn.table-functions-top-optparamfn) | `10`|  Sets the number of results to find.   
|  | **Minimum**| `1`|   
[ _`max`_](functions-top.html#query-functions-top-max)|  string| optional[[a]](functions-top.html#ftn.table-functions-top-optparamfn) |  |  This changes the function used from [`count()`](functions-count.html "count\(\)") to find the max value of a max field (for example, `groupBy([*fields*], function=max(*max*)) | sort(_max)`).   
[_`percent`_](functions-top.html#query-functions-top-percent)|  boolean| optional[[a]](functions-top.html#ftn.table-functions-top-optparamfn) | `false`|  Will add a column named `percent` containing the count in percentage of total.   
[_`rest`_](functions-top.html#query-functions-top-rest)|  string| optional[[a]](functions-top.html#ftn.table-functions-top-optparamfn) |  |  Will add an extra row containing the count of all the other values not included.   
[_`sum`_](functions-top.html#query-functions-top-sum)|  string| optional[[a]](functions-top.html#ftn.table-functions-top-optparamfn) |  |  This changes the function used from [`count()`](functions-count.html "count\(\)") to [`sum()`](functions-sum.html "sum\(\)") (for example, like `groupBy([*fields*], function=sum(*sum*)) | sort(_sum)`).   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-top.html#query-functions-top-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-top.html#query-functions-top-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     top(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     top(field=["value"])
> 
> These examples show basic structure only.

### [`top()`](functions-top.html "top\(\)") Function Operation

LogScale's [`top()`](functions-top.html "top\(\)") function uses an approximative algorithm from [DataSketches](https://datasketches.apache.org/) to compute the most frequent items. This algorithm is guaranteed to be exact for up to `0.75* maxMapSize` items, where `maxMapSize` is `32768` items in historical queries and `8192` items in live queries. 

The algorithm provides an upper bound for the error. By default, a warning is issued if the guaranteed precision is less than five percent; such error threshold can be modified using the [_`error`_](functions-top.html#query-functions-top-error) parameter. See [Frequent Items, Error Threshold Table](https://datasketches.apache.org/docs/Frequency/FrequentItemsErrorTable.html) for more information. 

[`top()`](functions-top.html "top\(\)") only returns events that are guaranteed to be in the top k events — that is to say, that are not false positives. 

When the [`top()`](functions-top.html "top\(\)") function is executed, if there are more fields other than those grouped and counted, the [_`rest`_](functions-top.html#query-functions-top-rest) parameter will return an extra row containing a count of all the remaining values — those values that were not included in the top results. To enable it, set the parameter to whatever you want the row to be labeled. 

### [`top()`](functions-top.html "top\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Query Costs by User and Repository in a Single Field

**Calculate query costs by user across multiple repositories, showing the repository/user as a single field**

##### Query

logscale
    
    
    #type=humio #kind=logs class=c.h.j.RunningQueriesLoggerJob message="Highest Cost query"
    | repoUser:= format("%s/%s", field=[dataspace, initiatingUser])
    | top(repoUser, sum=deltaTotalCost, as=cost)
    |table([cost, repoUser], sortby=cost)

##### Introduction

In this example, the query filter events in the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) repository that are tagged with `kind` equal to `logs` and then returns the events where the class field has values containing `c.h.j.RunningQueriesLoggerJob`, searching for the specific value `Highest Cost query`. The query then combines the results in a new field repoUser. The query then uses [`top()`](functions-top.html "top\(\)") and [`table()`](functions-table.html "table\(\)") functions to aggregate and display the results. 

Example incoming data might look like this: 

#type| #kind| class| message| timestamp| dataspace| initiatingUser| totalLiveCost| totalStaticCost| deltaTotalCost| repo  
---|---|---|---|---|---|---|---|---|---|---  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:30:00Z| production| john.doe| 1500| 800| 2300| security-logs  
humio| logs c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:31:00Z| development| jane.smith| 2000| 1200| 3200| app-logs|   
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:32:00Z| staging| bob.wilson| 1000| 500| 1500| infra-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:33:00Z| production| john.doe| 1800| 900| 2700| security-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:34:00Z| development| jane.smith| 2500| 1300| 3800| app-logs  
humio| logs| c.h.j.RunningQueriesLoggerJob| Highest Cost query| 2025-03-26T09:35:00Z| staging| alice.cooper| 1200| 600| 1800| infra-logs  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         #type=humio #kind=logs class=c.h.j.RunningQueriesLoggerJob message="Highest Cost query"

Filters for Humio internal logs containing `c.h.j. RunningQueriesLoggerJob` in the class field and where the value in the message field is equal to `Highest Cost query`. 

  3. logscale
         
         | repoUser:= format("%s/%s", field=[dataspace, initiatingUser])

Combines the fields dataspace and initiatingUser with a `/` separator, and then assigns the combined value to a new field named repoUser. Example of combined value: `dataspace/username`. 

  4. logscale
         
         | top(repoUser, sum=deltaTotalCost, as=cost)

Finds the most common values in the field repoUser, makes a sum of the field deltaTotalCost, and returns the results in a new field named cost. 

  5. logscale
         
         |table([cost, repoUser], sortby=cost)

Displays the results in a table with fields `cost` and `repoUser`, sorted by the column `cost`. 

  6. Event Result set.




##### Summary and Results

The query is used to search across multiple repositories and calculate query costs per user, by combining costs and showing the repository/user as a single field. 

Sample output from the incoming example data: 

cost| repoUser  
---|---  
3200| development/jane.smith  
2300| production/john.doe  
1500| staging/bob.wilson  
  
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
  
#### Find Most Common URLs Returning 404 Errors

**Identify frequently failing URLs using filtering with the[`top()`](functions-top.html "top\(\)") function **

##### Query

logscale
    
    
    statuscode = "404"
    | top(url, limit=20)

##### Introduction

In this example, the [`top()`](functions-top.html "top\(\)") function is used to identify the most common URLs that are returning HTTP 404 (Not Found) errors. 

Example incoming data might look like this: 

@timestamp| url| statuscode| client_ip| user_agent  
---|---|---|---|---  
2023-08-06T10:00:00Z| /products/old-item.html| 404| 192.168.1.100| Mozilla/5.0  
2023-08-06T10:01:00Z| /about/team.html| 200| 192.168.1.101| Chrome/90.0  
2023-08-06T10:02:00Z| /products/old-item.html| 404| 192.168.1.102| Safari/14.0  
2023-08-06T10:03:00Z| /blog/2022/post1.html| 404| 192.168.1.103| Firefox/89.0  
2023-08-06T10:04:00Z| /contact.html| 200| 192.168.1.104| Chrome/90.0  
2023-08-06T10:05:00Z| /products/old-item.html| 404| 192.168.1.105| Safari/14.0  
2023-08-06T10:06:00Z| /images/banner.jpg| 404| 192.168.1.106| Mozilla/5.0  
2023-08-06T10:07:00Z| /blog/2022/post1.html| 404| 192.168.1.107| Chrome/90.0  
2023-08-06T10:08:00Z| /products/old-item.html| 404| 192.168.1.108| Firefox/89.0  
2023-08-06T10:09:00Z| /images/banner.jpg| 404| 192.168.1.109| Safari/14.0  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         statuscode = "404"

Filters the events to include only those where the statuscode field equals `404`, representing HTTP Not Found errors. 

  3. logscale
         
         | top(url, limit=20)

Groups the filtered results by the url field and counts their occurrences. The [_`limit`_](functions-top.html#query-functions-top-limit) parameter is set to show the top 20 most frequent URLs. If no [_`rest`_](functions-top.html#query-functions-top-rest) parameter is specified, any additional URLs beyond the limit are excluded from the results. 

  4. Event Result set.




##### Summary and Results

The query is used to identify which URLs most frequently return 404 errors, helping to pinpoint broken links or missing resources on a website. 

This query is useful, for example, to prioritize which broken links to fix first, identify outdated links in external references, or detect potential website structure issues after content migration. 

Sample output from the incoming example data: 

url| _count  
---|---  
/products/old-item.html| 4  
/blog/2022/post1.html| 2  
/images/banner.jpg| 2  
  
Note that the results are automatically sorted in descending order by count, showing the URLs with the most 404 errors first. 

#### List URLs Not Found

****

##### Query

logscale
    
    
    statuscode = "404"
    | top(url, limit=20)

##### Introduction

You want to get a list of URLs that users attempted to view, but the web server could not find them. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         statuscode = "404"

Filters only events in which the statuscode is 404: that is the HTTP code which indicates that the requested URL was not found. 

  3. logscale
         
         | top(url, limit=20)

Pipe the events to the [`top()`](functions-top.html "top\(\)") function to group the results on the value of the urlurl field and to list the top twenty. 

  4. Event Result set.




##### Summary and Results

The results show a few attempts to access pages like `wp-login.php` and similar pages. These are attempts to log into WordPress, Drupal, and other content management systems. Since this particular web server does not use a CMS, these pages don't exist on the server and are indications of failed hacker attempts. 

url| _count  
---|---  
/.env| 962  
/favicon.ico| 67  
/api/.env| 22  
/core/.env| 25  
/backend/.env| 25  
/info.php| 19  
/admin/.env| 19  
/user/login| 18

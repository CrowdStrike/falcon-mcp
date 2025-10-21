# Data Management & Analysis | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/data-analysis-docs.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

# Data Management & Analysis

This manual provides a guide to parsing, searching and analysing in Falcon LogScale 1.202.0-1.209.0. Since these are essentials of LogScale, these pages of the documentation apply to both Cloud and Self-Hosted deployments. 

Below are links to the major sections, with descriptions of each. They're listed somewhat from the most basic, key aspects to the more advanced and useful tools. They're grouped, though, by related topics. 

Data Storage & Sifting 

You may have an administrator who installed LogScale, as well as set up log shippers on your servers to send data to LogScale — making it easier for you to focus on the data itself. 

As a data analyst, to start you'll need to know your tools (i.e., the UI), as well as understand the repositories where the data is stored and how to parse that data, properly. These topics are covered in sections below. 

> **[_LogScale Web Interface_](ui.html "LogScale Web Interface")**
> 
> Most people utilize LogScale with the web-based user interface. Through the UI, you can access your repositories containing server logs and metrics. It's where you can view and search data, create and see charts of server activities. Here you'll learn about the LogScale UI. In a way, for most, it all starts with the UI. 
> 
> **[_Manage Repositories and Views_](repositories.html "Manage Repositories and Views")**
> 
> The main storage entity within LogScale is the repository. It's where log shippers on your servers send server log entries and other server metrics, known as events. Events are converged and stored in repositories. It's where you can manage and query and monitor the data accumulated. This section of the documentation is where you can learn about repositories, the heart of LogScale. 
> 
> **[_Parse Data_](parsers.html "Parse Data")**
> 
> LogScale without parsers is raw data; it's chaos. Parsers bring order and sanity to data. They take events and break them into useful and manageable components. It discerns dates from IP addresses, user names from file names, and much more. This section on parsers shows you how to assemble and organize data so that you can query that data. 

Using Data 

With the data parsed and stored in your repositories, you'll want to be able to search it, to be able to get answers to questions you may have about activities on your servers. How to do this is covered in the sections listed here, some basic and some to more indepth levels. 

> **[_Search Data_](searching-data.html "Search Data")**
> 
> This is where you can learn how to get information from LogScale that you can actually use — in making decisions about your servers, about your security, and about your business. This section explains the basics of how to search your repositories, how to query the data through the user interface. 
> 
> **[_Write Queries_](writing-queries.html "Write Queries")**
> 
> The previous section explains how to use the UI to search data. This section provides much more details on how to write queries using the LogScale query language to search data. These queries may be used within the query field of the UI, or with API interfaces. That may seem more advanced: while it can be, it's primarily more of an intermediate level. 
> 
> **[_Query Language Syntax_](syntax.html "Query Language Syntax")**
> 
> The previous sections cover the more common ways to query a repository. This section provides much more details; it's a full language syntax guide for writing queries. It includes using operators, conditional statements, regular expressions. 
> 
> **[_Query Functions_](functions.html "Query Functions")**
> 
> LogScale has an elaborate list of powerful functions for querying repositories. Functions have specific syntax requirements, parameters allowed, and how data is returned using various data types. Here you'll find all of the details for all LogScale functions used for parsing and executing queries. 

Visualization & Automation 

To streamline queries you often use, and to make data available to others without your skills or permissions, such as business managers and clients, the sections below explain how to save favorite and useful queries, as well as how to display them in meaningful ways. 

> **[_Dashboards_](dashboards.html "Dashboards")** **[_Widgets_](widgets.html "Widgets")**
> 
> Dashboards and widgets provide graphical views of your event data. They can be configured using different graphs and display formats, such as pie charts, line graphs, as well as listing relevant text. These can be useful for you and others to monitor easily server usage and activity. This is all explained here. 
> 
> **[_Automation_](automated.html "Automation")**
> 
> Being able to monitor data with dashboards is great, but you can't review them constantly: you have other things to do and can't work twenty-four hours a day, every day. LogScale has a variety of ways to check automatically your repositories, using your queries. If certain events happen, if criteria you set are met or exceeded, an alert can be triggered and you or others in your organization can be notified — by email or telephone text message.

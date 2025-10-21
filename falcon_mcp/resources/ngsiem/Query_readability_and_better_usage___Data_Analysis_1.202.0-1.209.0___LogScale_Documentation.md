# Query readability and better usage | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/writing-queries-usage-best-practice.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Write Queries](writing-queries.html)

## Query readability and better usage

Sifting through the data can range from quite simple searches to very complex queries. Reading, using or reusing a query can be easier if the query is written according to some basic recommendations. 

### Multi-line queries

Queries can be split over multiple lines, with the convention of using the pipe operator as the break point, to chain the different expressions within. For example, the following query: 

logscale
    
    
    #host=github #parser=json | repo.name=docker | groupBy(repo.name, function=count()) | sort()

is identical to: 

logscale
    
    
    #host=github #parser=json
    | repo.name=docker
    | groupBy(repo.name, function=count())
    | sort()

but the latter is easier to read. 

### Tip

Press `Shift` \+ `Enter` to insert a line break within the query. 

### Comments

The CrowdStrike Query Language (CQL) supports // single-line and /* multi-line */ comments. 

Single-line comments should be used at the end of a line, for example: 

logscale
    
    
    #host=github #parser=json
    | // Search for host and parser
    repo.name=docker/*
    | groupBy(repo.name, function=count())
    | sort()

Multi-line comments are useful to provide a deeper description or documentation for a search. For example: 

logscale
    
    
    /* Search for killed processes
       Set the <signal> type and <process> name */
    ?{signal="*" }
    | ?{process="*"}
    | /Service exited due to (?<signal>\S+)/
    | signal = ?signal
    | /sent by (?<process>\S+)\[\d+\]/
    | process = ?process

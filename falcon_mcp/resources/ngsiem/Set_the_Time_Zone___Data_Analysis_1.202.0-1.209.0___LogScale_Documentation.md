# Set the Time Zone | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-set-timezone.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

Content was updated:Aug 13, 2024

## Set the Time Zone

Data is stored as _Unix Time_ by LogScale (see [Parsing Timestamps](parsers-parsing-timestamps.html "Parsing Timestamps") for details), but by default displayed in the local time zone according to the OS on which your browser runs. 

It is possible to change the default time zone, or change it temporarily during a search. 

### Changing the Default Time Zone

By default, all users within an organization will use the browser local time as their timezone. 

As a user, you can adjust the default time zone to a specific, preferred zone, as follows. 

  1. Click the User Icon menu → Manage your account and under Account settings → `General`. 

  2. Under Timezone, select the relevant time zone from the list. 

  3. Click Save to confirm your changes. You can always revert the value back to browser default. 




As an administrator, you can adjust the default time zone at organization level, and set the timezone for all users: 

  1. Click the User Icon menu → Organization settings and under Organization → `User defaults`. 

  2. Under Timezone, select a time zone for all users. 

  3. Click Save to confirm your changes. You can always reset the value back to browser default. 




  * Users can override the organization-level setting from their Account settings section. 

  * The organization-level setting will not change existing user-level overrides. 




### Changing the Time Zone Temporarily

You can change the default time zone from the UI temporarily and run the search on different time zones. This is useful when working with a colleague situated in another time zone, and both wish to see timestamps with the same value. 

  1. From the Search page, enter a query in the Query editor. 

  2. Click the arrow next to the Time Zone dropdown field, and select the desired time zone from the list. It is also possible to select a time zone by starting typing in Time Zone dropdown field, for example **`Cop`** for +02:00 Copenhagen

  3. Click Run in the query editor, or press **Enter** to start the query running. The new time zone is supported in the search link and is retained if the URL is copied in a new tab. 

  4. Click the  (revert) icon to reset the time zone to default. 




![Change Time Zone from Search](images/search-data/search-time-zone-new.png)  
---  
  
**Figure 104. Change Time Zone from Search**

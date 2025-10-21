# Grant permissions for saved queries | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/writing-queries-manage-asset-sharing.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Write Queries](writing-queries.html)

/ [Query management](writing-queries-manage.html)

### Grant permissions for saved queries

##### Security Requirements and Controls

  * [ _`Change user access`_](https://library.humio.com/falcon-logscale-self-hosted/security-authorization-role-permissions.html#security-user-permissions-change-user-access) permission




Sometimes you might want to collaborate with another user on a saved query, but that user does not have permission to saved queries in the view. If you have permissions to do so, you can grant permissions to that user to edit and delete a particular saved query in a view. For more information about asset permissions, see [Asset permissions](https://library.humio.com/falcon-logscale-cloud/security-authorization.html#security-authorization-asset-permissions). 

If you do **not** have [_`Change user access`_](https://library.humio.com/falcon-logscale-self-hosted/security-authorization-role-permissions.html#security-user-permissions-change-user-access) permission on the repository, you will see a list of users only (no groups) that already have at least Read permissions on the repository. You can select from these users and give them more permissions (up to the same permissions you have). 

To grant access to edit or delete a saved query to another user or group: 

Asset creator/Regular user

> The creator of an asset and regular users can share the same permissions that they have to the asset with users who already have read access to the view. You cannot share access with users who do not have read access to the view. You cannot share access with groups at all. 
> 
>   1. Click Details next to the saved query you want to share and click Asset sharing. 
> 
> ![](images/queries/saved-query-asset-sharing.png)  
> ---  
>   
>   2. In the Users and groups with access window you see users who currently have access to the dashboard and what access they have. 
> 
> ![](images/queries/saved-query-asset-sharing-reg-user.png)  
> ---  
>   
>   3. Click Share saved query. 
> 
>   4. Click to select the user to get additional permissions. Note that you can only see users who already have read permission to the view. Click Next. 
> 
> ![](images/queries/saved-query-permissions-reg-user-add-user.png)  
> ---  
>   
>   5. Select the appropriate permissions to assign. Click Grant permissions. 
> 
> ![](images/queries/saved-query-permissions-reg-user-add-user-permission.png)  
> ---  
>   
> 


You have Change user access permission

> With [_`Change user access`_](https://library.humio.com/falcon-logscale-self-hosted/security-authorization-role-permissions.html#security-user-permissions-change-user-access) permission, you can grant permission to users, including read permission if the user does not have that, and permissions that you do not have yourself. You can also see groups and group members and what permissions they have in the Groups tab, but you cannot change the permissions for the group in the Groups tab. To be able to change the permissions directly from the group tab, you must have [_`Change organization permissions`_](https://library.humio.com/falcon-logscale-self-hosted/security-authorization-organization-roles.html#security-manager-permissions-changeorgperm) permission. 
> 
> To grant additional permissions to a user that already has read access to the view: 
> 
>   1. Click Details next to the saved query you want to share and click Asset sharing. 
> 
> ![](images/queries/saved-query-asset-sharing.png)  
> ---  
>   
>   2. In the Users and groups with access window you see users who currently have access to the saved query and what access they have. 
> 
> ![](images/queries/saved-query-asset-sharing-list.png)  
> ---  
>   
>   3. Click the  button next to the user or group in the list. 
> 
>   4. Click to assign the permissions. Click Save changes. 
> 
>   5. Click Close. 
> 
> 

> 
> If you have the [_`Change user access`_](https://library.humio.com/falcon-logscale-self-hosted/security-authorization-role-permissions.html#security-user-permissions-change-user-access) permission and you want to share permissions to the action with a user or group **not** in the list, or you want to give a group that **is** in the list additional permissions: 
> 
>   1. Click Share saved query. 
> 
>   2. Click to select the group or user who should get additional permissions. Click Next. 
> 
> ![](images/queries/saved-query-asset-sharing-new-user.png)  
> ---  
>   
>   3. Select the appropriate permissions to assign. Be aware of the message that the user or group gets Read access to all assets in the repository automatically when assigning asset permissions for one asset in the repository. Click Next. 
> 
> ![](images/queries/saved-query-asset-sharing-new-user-permissions.png)  
> ---  
>   
>   4. Confirm that you understand that you are granting Read access to all assets in the repository by adding the asset permission for the user or group. Click Grant data read access. 
> 
> ![](images/automated/actions-management-permissions-dataread-confirmation.png)  
> ---  
>   
>   5. Click Grant permissions. 
> 
>

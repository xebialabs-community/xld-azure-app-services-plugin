# XL Deploy plugin for Azure App Services #

## CI status ##

[![Build Status][xld-azure-app-services-plugin-travis-image] ][xld-azure-app-services-plugin-travis-url]
[![Codacy][xld-azure-app-services-plugin-codacy-image] ][xld-azure-app-services-plugin-codacy-url]
[![Code Climate][xld-azure-app-services-plugin-code-climate-image] ][xld-azure-app-services-plugin-code-climate-url]
[![License: MIT][xld-azure-app-services-plugin-license-image] ][xld-azure-app-services-plugin-license-url]
[![Github All Releases][xld-azure-app-services-plugin-downloads-image] ]()


[xld-azure-app-services-plugin-travis-image]: https://travis-ci.org/xebialabs-community/xld-azure-app-services-plugin.svg?branch=master
[xld-azure-app-services-plugin-travis-url]: https://travis-ci.org/xebialabs-community/xld-azure-app-services-plugin
[xld-azure-app-services-plugin-codacy-image]: https://api.codacy.com/project/badge/Grade/dac4a5ff98784e8487216b7d3f26761a
[xld-azure-app-services-plugin-codacy-url]: https://www.codacy.com/app/joris-dewinne/xld-azure-app-services-plugin
[xld-azure-app-services-plugin-code-climate-image]: https://codeclimate.com/github/xebialabs-community/xld-azure-app-services-plugin/badges/gpa.svg
[xld-azure-app-services-plugin-code-climate-url]: https://codeclimate.com/github/xebialabs-community/xld-azure-app-services-plugin
[xld-azure-app-services-plugin-license-image]: https://img.shields.io/badge/License-MIT-yellow.svg
[xld-azure-app-services-plugin-license-url]: https://opensource.org/licenses/MIT
[xld-azure-app-services-plugin-downloads-image]: https://img.shields.io/github/downloads/xebialabs-community/xld-azure-app-services-plugin/total.svg


## Overview ##

The Azure App Service plugin is an XL Deploy plugin that has the ability to deploy to the Azure App Service backend. 

## Features ##

* Supports the discovery of resource groups and web apps for a given subscription
* Supports Azure Web App deployments
	* Application Settings
	* Connection Strings
* Supports webjobs
	* Triggered
	* Continuous
* Define Application Service Plan
* Resource Group creation via control task


## Requirements ##

* **XLD Server** 6+
		

## Installation ##

Plugin can be downloaded directly from the plugin's repository on [Github](https://github.com/xebialabs-community/xld-azure-app-services-plugin/releases).

Place the plugin XLDP file into __&lt;xld-home&gt;/plugins__ directory.

## Azure Connection Information ##

Azure connection settings are defined in an __azure.Subscription__ configuration item under the **Infrastructure** node in the XL Deploy repository.

| Property | Description |
| -------- | ----------- |
| subscriptionId   | Azure subscription |
| tenantId | Tenant Id |
| clientId | Client Id |
| clientKey | Client Key |
| ftpUser | Ftp User |
| ftpPassword | Ftp Password |


Please refer to the [Create an Azure Active Directory application](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal#create-an-azure-active-directory-application)  section in [Create Service Principal](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal
) documentation for setting up and obtaining a *Client Id*, *Client Key* and *Tenant Id*

For information on setting up FTP credentials, please refer to [Deployment Credentions](https://github.com/projectkudu/kudu/wiki/Deployment-credentials)


## Discovery ##

__azure.Subscription__ supports XL Deploy's discovery feature. Discovery of the following types are supported :

* Resource Group (__azure.ResourceGroup__)
* Web App (__azure.WebAppModule__)



## Deployable Types ##

| Deployable | Target Container |
| -------- | ----------- | 
| azure.AppServicePlanSpec   | azure.ResourceGroup | 
| azure.WebApp   | azure.ResourceGroup | 
| azure.TriggeredWebJobModule   | azure.ResourceGroup | 
| azure.ContinuousWebJobModule   | azure.ResourceGroup | 





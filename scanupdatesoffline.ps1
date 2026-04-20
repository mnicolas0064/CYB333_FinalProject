
<#PSScriptInfo
 
.VERSION 1.0
 
.GUID 7f1cf7cf-7a86-4124-9b20-8228ad7b13b2
 
.AUTHOR Andrei Stoica astoica@microsoft.com
 
.COMPANYNAME Microsoft
 
.COPYRIGHT
 
.TAGS
 
.LICENSEURI https://opensource.org/licenses/MIT
 
.PROJECTURI
 
.ICONURI
 
.EXTERNALMODULEDEPENDENCIES
 
.REQUIREDSCRIPTS
 
.EXTERNALSCRIPTDEPENDENCIES
 
.RELEASENOTES VBS version: https://docs.microsoft.com/en-us/previous-versions/windows/desktop/aa387290(v=vs.85)
 
 
#>

<#
 
.DESCRIPTION
 Using WUA to Scan for Updates Offline with PowerShell
 
#> 
Param()
 
$UpdateSession = New-Object -ComObject Microsoft.Update.Session 
$UpdateServiceManager  = New-Object -ComObject Microsoft.Update.ServiceManager 
$UpdateService = $UpdateServiceManager.AddScanPackageService("Offline Sync Service", "c:\temp\wsusscn2.cab", 1) 
$UpdateSearcher = $UpdateSession.CreateUpdateSearcher()  
 
Write-Output "Searching for updates... `r`n" 
 
$UpdateSearcher.ServerSelection = 3 #ssOthers

$UpdateSearcher.IncludePotentiallySupersededUpdates = $true # good for older OSes, to include Security-Only or superseded updates in the result list, otherwise these are pruned out and not returned as part of the final result list
 
$UpdateSearcher.ServiceID = $UpdateService.ServiceID.ToString() 
 
$SearchResult = $UpdateSearcher.Search("IsInstalled=0") # or "IsInstalled=0 or IsInstalled=1" to also list the installed updates as MBSA did
 
$Updates = $SearchResult.Updates 
 
if($Updates.Count -eq 0){ 
    Write-Output "There are no applicable updates." 
    return $null 
} 
 
Write-Output "List of applicable items on the machine when using wssuscan.cab: `r`n" 
 
$i = 0 
foreach($Update in $Updates){  
    Write-Output "$($i)> $($Update.Title)" 
    $i++ 
}
if (((Get-NetFirewallProfile | select name,enabled) | where { $_.Enabled -eq $True } | measure ).Count -eq 3)
{
    $output = "0 Windows-Firewall - Windows-Firewall ist aktiviert"
}
else
{
    $output = "2 Windows-Firewall - Windows-Firewall ist deaktiviert"
}
Write-Output $output

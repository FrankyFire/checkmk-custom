# aktualisiert den Nagios-Agenten auf allen Windows-PCs, die in hostliste.txt definiert sind
# geschrieben von Andreas Döhler am 13.01.2017, editiert von Sebastian Arndt am 07.07.2020
# hostliste definiert (durch Zeilenumbruch getrennt) die Zielcomputer
$computers = Get-Content -path hostliste.txt

foreach ($i in $computers){
  Write-Host $i
  $DestPath = "\\"+"$i"+"\c$\temp\"
  # prüft ob der Zielpfad existiert
  if (!( Test-Path $DestPath ))
   {
     # falls nicht wird er angelegt
     New-Item $DestPath -ItemType Dir
   }
  Copy-Item -Path C:\Install\Deploy\check_mk_agent.msi -Destination $DestPath -Recurse -Force
  PsExec.exe \\$i -d -s cmd /c "msiexec.exe /i C:\temp\check_mk_agent.msi /quiet /norestart"
}

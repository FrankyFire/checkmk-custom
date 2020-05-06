# Wiki-Sync for CheckMK

Dies ist ein Tool zum Synchronisieren von Wiki-Seiten, die auf mehrere Sites verteilt sind.
Der Grundgedanke ist simpel: Von einem zentralen Service Desk aus werden mehrere Kundensysteme überwacht. Gibt es bekannte Probleme, können sowohl Kunden als auch Service-Desk-Mitarbeiter Einträge erstellen und bearbeiten. Wisyn übernimmt hierbei die Synchronisation zwischen den Sites und bietet gleichzeitig die Möglichkeit kundenspezifische Präfixe anzufügen.


# Installation

Voraussetzungen:
- SSH-Keys für die Verbindung zu Remote-Sites sind installiert.
- Python3 und Pakete json, os und commands sind vorhanden.
- RSync ist installiert
- Wird auf einem Linux-System ausgeführt
- Script wird als Site-User ausgeführt, der die Rechte hat im eigenen und im Wikiordner zu lesen und schreiben.

## Konfiguration
Die Konfiguration geschieht über die config.json Datei. Hier gibt es 2 Abschnitte (_kursive_ Felder müssen nicht ausgefüllt, jedoch zumindest als leerer String vorhanden sein):
- "lokal": Eigenschaften der Master-Site
    * "wiki-pfad": Lokaler Ordner, in welchen die Sites synchronisiert werden
    * _"prefix-separator"_: Falls das Kundeprefix vom Hostnamen mit einem Zeichen getrennt werden soll
- "kunden": Alle Kundensysteme
    * _"name"_: Name des Kunden. Derzeit nicht verwendet, dient hauptsächlich der Übersichtlichkeit.
    * _"prefix"_: Präfix, welches vor den Hostnamen angehangen werden soll -> Wird gleichzeitig als Unterordner im lokalen Wiki verwendet
    * "wiki-pfad": Pfad des Wiki auf dem Kundensystem
    * "host": Das Kundensystem, auf dem sich das Wiki befindet -> SSH-Key muss importiert sein!
    * "benutzer": Benutzername, mit dem sich auf dem Kundensystem angemeldet wird. Dies sollte der Site-User sein.
    
## Verwendung
Es reicht, das Tool per Python auszuführen.

    python wisyn.py
    
Innerhalb des eigenen Ordners sucht das Script nach der "config.json" und den dazugehörigen Einträgen.
Für eine regelmäßige Überprüfung nach Änderungen, muss der Befehl als Cronjob hinterlegt werden.

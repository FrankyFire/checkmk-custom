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

## SSH Konfigurieren
Wurde auf dem System noch kein Schlüssel generiert, muss dies zuerst geschehen:

    ssh-keygen -t rsa -b 4096
Anschließend ist der Schlüssel des jeweiligen Kunden zu speichern (-p nur, wenn der Port von Standard abweicht):
    
    ssh-copy-id "siteuser@hostname.domain -p <port-number>"
Nun ist die Verbindung gespeichert und kann ohne Benutzerinteraktion gestartet werden.

## CheckMK Konfigurieren
Zu jeder CheckMK Instanz wird ein Dokuwiki mitgelifert.
Dieses ist unter https://hostname.domain/sitename/wiki/doku.php zu finden.
Über die URL werden auch Informationen zur jeweiligen Wiki-Seite übergeben, inbdem "?id=" und die Seite an die URL angehangen wird.

Zuerst müssen im Wato unter _Global Settings -> User Interface -> Custom icons and actions_ neue Actions definiert werden.
Nach Vergabe einer sinnvollen ID (idealerweise den Kundennamen vorn anhängen), Name und Icon wird in die Action die URL zur Wiki-Seite eingetragen.
Um hierbei automatisch Host- und Servicename einzufügen, wird folgende Action benötigt:

    https://hostname.domain/sitename/wiki/doku.php?id=kundenprefix:$HOSTNAME$:$SERVICEDESC$

Wisyn verwendet das Kundenprefix als Unterordner im Wiki-Verzeichnis.
So kann ausgeschlossen werden, dass Kunden Informationen sehen, die nicht zu ihrer Site gehören.

Anschließend ist zu konfigurieren, in welchem Kontextmenü die Action auftauchen soll.
Hierzu muss unter _Host & Service Parameters -> Monitoring Configuration -> Various -> Custom icons or actions for hosts/services in status GUI_ eine neue Regel angelegt werden.
Hier wird die Action sowie der Kundenordner ausgewählt.
Die Wiki-Seiten sind nun über das Kontextmenü neben Host oder Service abrufbar.

Damit die Kunden jeweils auf ihr eigenes Wiki zugreifen, müssen die Globalen Einstellungen der jeweiligen Site angepasst werden.
Dies geschieht unter _Distributed Monitoring -> Site Specific Global Configuration [Chip Symbol] -> User Interface -> Custom icons and actions_
Hier dann den Host- und Sitenamen des jewiligen Kunden eintragen.

## Wisyn Konfigurieren
Die Konfiguration des Tools geschieht über die config.json Datei.
Hier gibt es 2 Abschnitte (_kursive_ Felder müssen nicht ausgefüllt, jedoch zumindest als leerer String vorhanden sein):
- "lokal": Eigenschaften der Master-Site
    * _"wiki-pfad"_: Lokaler Ordner, in welchen die Sites synchronisiert werden. Wenn leer, wird der Default verwendet.
        >~/var/dokuwiki/data/pages/
    * _"prefix-separator"_: Falls das Kundeprefix vom Hostnamen mit einem Zeichen getrennt werden soll
- "kunden": Alle Kundensysteme
    * _"name"_: Name des Kunden. Derzeit nicht verwendet, dient hauptsächlich der Übersichtlichkeit und benutzerfreundlichen Fehlermeldung.
    * _"prefix"_: Präfix, welches vor den Hostnamen angehangen werden soll -> Wird gleichzeitig als Unterordner im lokalen Wiki verwendet
    * _"wiki-pfad"_: Pfad des Wiki auf dem Kundensystem. Wenn leer, wird der Default verwendet.
        >~/var/dokuwiki/data/pages/
    * "host": Das Kundensystem, auf dem sich das Wiki befindet -> SSH-Key muss importiert sein!
    * "benutzer": Benutzername, mit dem sich auf dem Kundensystem angemeldet wird. Dies sollte der Site-User sein.
    
## Verwendung
Es reicht, das Tool per Python auszuführen.

    python wisyn.py
    
Innerhalb des eigenen Ordners sucht das Script nach der "config.json" und den dazugehörigen Einträgen.
Für eine regelmäßige Überprüfung nach Änderungen, muss der Befehl als Cronjob hinterlegt werden.

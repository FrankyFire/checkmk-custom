#! python
# coding=utf-8

#######################################################################################
################################### _ #################################################
######################### __      _(_)___ _   _ _ __ ##################################
######################### \ \ /\ / / / __| | | | '_ \ #################################
########################## \ V  V /| \__ \ |_| | | | | ################################
########################### \_/\_/ |_|___/\__, |_| |_| ################################
######################################### |___/ #######################################
#######################################################################################
#######################    Wiki-Sync for Service Desks   ##############################
#######################################################################################
#                                                                                     #
# H4x0r: Sebastian Arndt                                                              #
# D4t3: Mai 2020                                                                      #
# D0cum3nt4t10n:                                                                      #
# https://github.com/FrankyFire/checkmk-custom/tree/master/tools/wiki-sync/readme.md  #
#                                                                                     #
#######################################################################################

####################################
# Skript zur Ausführung im Service #
# Desk.                            #
# Dient der gelmäßigen Synchronisa-#
# tion der Wiki-Seiten von Kunden- #
# zu lokalen CheckMK Instanzen.    #
####################################

import sys, os      #Grundlegende OS-Funktionen
import json         #Intepretieren der Konfigurationsdatei
import commands     #Zum ausführen von Kommdos auf der Shell, hier zur Prüfung auf Existenz der SSH-Credentials

customers = []

# Standard-Werte:
separator = ''
confDir = os.path.join(os.path.dirname(sys.argv[0]), 'config.json')
wikiDir = os.path.expanduser('~/var/dokuwiki/data/pages/')	#Expanduser ersetzt ~ mit der Home-Directory

# Eine Klasse Kunde, in der alle Kunden, welche in der Konfiguration angegeben wurden, hinterlegt werden.
class Customer:
    def __init__(self, name, prefix, dir, host, user):
        self.name = name                                                  # Kundenname
        self.prefix = prefix                                              # Prefix in lokalem CheckMK
        if dir != '':
            self.dir = dir                                                # Wiki-Ordner im Kundensystem
        else:                                                             # Default-Wert
            self.dir = os.path.expanduser('~/var/dokuwiki/data/pages/')

        self.host = host                                                  # IP/Hostname des Kundensystems
        self.credentials = user + '@' + self.host                         # Anmeldedaten für Remote-Host (benutzer@remote-host)
        if self.prefix != '':
            self.tmp = os.path.join(os.path.dirname(sys.argv[0]), (self.prefix + '/'))     # TMP-Ordner und Kundenordner werden nach dem Präfix des Kunden benannt.
        else:
            self.tmp = os.path.join(os.path.dirname(sys.argv[0]), 'tmp/')                  # TMP-Ordner und Kundenordner werden 'tmp' genannt.


    def translate(self, to_temp):
        
        ##################################################
        # Zweck: Anfügen/Entfernen der Kundenpräfixe     #
        # Parameter:                                     #
        # - to_temp[Bool]: Übersetzungsrichtung          #
        #   1: Eingehende Synchronisation                #
        #   0: Ausgehende Synchronisation                #
        # Rückgabewerte:                                 #
        # - 1: Fehler!                                   #
        # - 0: Erfolg.                                   #
        ##################################################
        
        if to_temp: # Wenn in lokale wikiDir geschrieben wird (eingehende Synchronisation)...
            for path, subdirs, files in os.walk(os.path.normpath(self.tmp)):    # Alle Dateien in Pfad, inklusive Unterordner, durchsuchen
                for curpath in subdirs:                                         # Unterordner umbenennen (Präfix anfügen)
                    newsubpath = os.path.join(path, (self.prefix + separator + curpath))
                    curpath = os.path.join(path, curpath)

                    os.rename(curpath, newsubpath)
                for name in files:                                              # Dateien umbenennen (Präfix anfügen)
                    print(path)
                    old_name = os.path.join(path, os.path.basename(name))
                    new_name = os.path.join(path, (self.prefix + separator + name))

                    if os.path.isfile(old_name):                                # Um Zeitstempel beizubehalten wird cp -p verwendet.
                        os.system('cp -p ' + old_name + ' ' + new_name)         # Präfix anfügen
                        os.system('rm ' + old_name)
            if self.prefix != '':
                os.system('cp -R -p ' + self.tmp + ' ' + wikiDir)               # Kopieren der Wiki-Einträge aus tmp in den realen Wiki-Ordner
            else:
                os.system('cp -R -p ' + self.tmp + '* ' + wikiDir)              # Variante für leeres Präfix
            return 1
        else: # Wenn in Temp geschrieben wird...
            os.system('mkdir ' + self.tmp)
            search_string = self.prefix + separator	                            # Der Kundenpräfix, welcher gesucht und vor der synchronisation entfernt werden soll
            prefix_size = len(search_string)

            for path, subdirs, files in os.walk(wikiDir):                       # Alle Dateien in Pfad, inklusive Unterordnern, durchsuchen
                for curpath in subdirs:
                    if curpath[:prefix_size] == search_string:                  # Wenn der Dateiname das Präfix des Kunden enthält...
                        if os.path.isdir(os.path.join(path, curpath)):		    # Wenn aktuelles Element ein Pfad ist...
                            # Kopiere den gesamten Pfad und benenne dabei um...
                            os.system('cp -R -p ' + os.path.join(path, curpath) + ' ' + self.tmp + curpath[prefix_size:]) # Kopieren der Wiki-Einträge nach tmp
                        else:
                            # ...sonst nur die jeweilige Datei kopieren und dabei umbenennen.
                            os.system('cp -p ' + os.path.join(path, curpath) + ' ' + self.tmp + curpath[prefix_size:])
                for name in files:
                    if name[:prefix_size] == search_string and os.path.isfile(os.path.join(path, name)):
                        os.system('cp -p ' + os.path.join(path, name) + ' ' + self.tmp + name[prefix_size:])
            return 1

        return 0

    def sync(self):
        ##################################################
        # Zweck: Prüfen auf Unterschiede der Dateien     #
        # Rückgabewerte:                                 #
        # - 1: Fehler!                                   #
        # - 0: Erfolg. (Dateien sind bereits gleich oder #
        #               wurden synchronisiert)           #
        ##################################################

        # Hiermit wird geprüft, ob die Anmeldedaten bereits gespeichert sind, um automatisch auf den Host zugreifen zu können.
        known_host = str(commands.getstatusoutput('ssh-keygen -H -F ' + self.host))

        # Hierfür muss er in der Rückgabe des ssh-keygen aufruf gefunden werden.
        if known_host.find('# Host ' + self.host + ' found') == -1:
            print('Please authenticate the host for SSH first. Use:\n ssh-copy-id ' + self.credentials)
            return 1
        
        # Bidirektionale synchronisation, erst vom Kunden zum ServiceDesk, danach umgekehrt.
        if len(self.prefix) > 0:
            cust.translate(0) # Temp-Ordner befüllen, um Änderungen von beiden Seiten zu akzeptieren.
            os.system('rsync --numeric-ids -aruz' + ' ' + self.credentials + ':' + self.dir + ' ' + self.tmp)
            os.system('rsync --numeric-ids -aruz' + ' ' + self.tmp + ' ' + self.credentials + ':' + self.dir)
            cust.translate(1)
            os.system('rm -R ' + self.tmp)
        else:
            os.system('rsync --numeric-ids -aruz' + ' ' + self.credentials + ':' + self.dir + ' ' + wikiDir)
            os.system('rsync --numeric-ids -aruz' + ' ' + wikiDir + ' ' + self.credentials + ':' + self.dir)

        return 0

def readConfig():
    
    ##################################################
    # Zweck: Liest die Konfigurationsdatei und       #
    #        erstellte Kunden.                       #
    # Rückgabewerte:                                 #
    # - 1: Fehler!                                   #
    # - 0: Erfolg.                                   #
    ##################################################
    
    try:
        with open(confDir) as config:
            # Zugriff auf die globalen Variablen
            global separator
            global wikiDir

            content = json.load(config)

            # Lokale Konfiguration - nur übernehmen wenn nicht leer
            if content['lokal']['prefix-separator'] != '':
                separator = content['lokal']['prefix-separator']

            if content['lokal']['wiki-pfad'] != '':
                wikiDir = os.path.expanduser(content['lokal']['wiki-pfad'])		#Expanduser ersetzt ~ mit der Home-Directory

            # Kundenkonfiguration: Für jeden Kunden...
            for company in content['kunden']:
                # ...wird die Liste erweitert mit den gefundenen Paramtern der Konfigurationsdatei.
                customers.append(Customer(company['name'],company['prefix'],company['wiki-pfad'],company['host'],company['benutzer']))
    except IOError:
        print('ERROR: Config file inaccessible.')
        return 1
    except:
        print('ERROR: Could not interpret Config file. Please check for typos.')
        return 1
    return 0

if __name__ == '__main__':
    ##################################################
    # Ablauf:                                        #
    #  1. Configdatei lesen                          #
    #  2. Alle konfigurierten Remote-Systeme         #
    #     synchronisieren.                           #
    #  3. Re-Check.                                  #
    ##################################################
    
    if readConfig():
        exit()
    
#    try:
    for cust in customers:                
        if cust.sync():
            exit('ERROR: Could not sync ' + cust.name + ' to local directory.\nProgram will still try to sync other customers.')
#    except:
#        exit('ERROR: Not able to sync files. Please check your customers directory and your config.')
    
    print('\nSuccess!\n')

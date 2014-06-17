#!/usr/bin/python
# coding: utf-8

"""
.. module:: Configure

Modulo che gestisce la Configurazione dell'intero progetto. 
Contiene medoti per il salvataggio e il caricamento delle impostazioni dei principali parametri.

"""

import os
import tempfile
import ConfigParser

#-------------------------------------------------------------------------------

ConfigFile 	= None # Percorso del file di configurazione correntemente utilizzato
ExcludeServer 	= None # Indica se nei grafici bisogna considerare anche i dati del server
MaxNodes 	= None # Numero massimo di nodi consentiti di Worker
LocalhostOnly 	= None # Indica se i Worker eseguono esclusivamente su localhost
TimeStep 	= None # Indica il numero di intervalli rappresentati sui grafici temporali
Interval	= None # Indica la durata di ogni intervallo nei grafici temporali

#-------------------------------------------------------------------------------

def CheckStr(value):
	"""
	Funzione che controlla la validità di una stringa.

	:param value: Il valore di cui va effettuato il type-checking.
	:returns: ``value`` stesso, se il valore è del tipo corretto.
	:raises: ``TypeError`` se il tipo non è corretto.
	"""
	if (not isinstance(value, str)): raise TypeError, "Argomento ""--conf"" non valido."
	else: return value

def SaveConfig(Reset=False, NewFile=""):
	"""
	Funzione che salva le impostazioni su file specificato.

	:param Reset: Indica se è necessario salvare le impostazioni di default all'interno del file specificato.
	:param NewFile: Il percorso del file di configurazione in cui salvare i dati.
	:returns: *nulla*.

	"""
	global ConfigFile, ExcludeServer, MaxNodes, LocalhostOnly, TimeStep, Interval
	if(NewFile!=""): ConfigFile = CheckStr(NewFile)

	if(Reset):
		ExcludeServer = 0
		MaxNodes = 4
		LocalhostOnly = 1
		TimeStep = 20
		Interval = 1

	Config = ConfigParser.ConfigParser()
	CFile = open(ConfigFile, 'w')
	Config.add_section("Monitor")
	Config.set("Monitor", "excludeserver", ExcludeServer)
	Config.set("Monitor", "maxnodes", MaxNodes)
	Config.set("Monitor", "localhost", LocalhostOnly)
	Config.set("Monitor", "timestep", TimeStep)
	Config.set("Monitor", "interval", Interval)
	Config.write(CFile)
	CFile.close()

def LoadConfig(CF=None):
	"""
	Funzione che carica le impostazioni da file specificato.

	:param CF: Il percorso del file di configurazione in cui salvare i dati. Se lasciato su ``None`` verrà utilizzato il percorso correntemente utilizzato, altrimenti quest'ultimo verrà sostituito dal nuovo percorso specificato.
	:returns: *nulla*.

	"""
	global ConfigFile, ExcludeServer, MaxNodes, LocalhostOnly, TimeStep, Interval

	if(CF!=None): ConfigFile = CF

	Config = ConfigParser.ConfigParser()

	if(ConfigFile==""):
		# Se non viene specificato alcun file, viene utilizzato il percorso di default /tmp/MonitorTemp.ini
		ConfigFile = os.path.join(tempfile.gettempdir(), "MonitorTemp.ini")
		if(not os.path.exists(ConfigFile)):
			SaveConfig(Reset=True)
	else:
		if(not os.path.exists(ConfigFile)):
			print("\n### ATT: Unable to find the required file\n defaults will be stored in a file with the same name.")
			SaveConfig(Reset=True)

		Config.read(ConfigFile)
		ExcludeServer = int(Config.get("Monitor", "excludeserver"))
		MaxNodes = 	int(Config.get("Monitor", "maxnodes"))
		LocalhostOnly = int(Config.get("Monitor", "localhost"))
		TimeStep = 	int(Config.get("Monitor", "timestep"))
		Interval = 	int(Config.get("Monitor", "interval"))

#-------------------------------------------------------------------------------

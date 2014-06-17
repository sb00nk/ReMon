#!/usr/bin/python
# coding: utf-8

"""
.. module:: Server

Modulo che fa da back-end per l'utente, gestisce la comunicazione tra il Client e le Probes tramite PyRO

"""

import sys, os, subprocess, time

import Pyro.core
import Pyro.naming
from Pyro.errors import NamingError

from optparse import OptionParser

import threading, thread

from Queue import Queue

import Configure

#-------------------------------------------------------------------------------

ConfigFile = None # Percorso del file di configurazione correntemente utilizzato
Interval = 1
RunNumb = 0

#-------------------------------------------------------------------------------

class ProbeManager(Pyro.core.ObjBase):

	"""
	Classe ProbeManager che contiene i metodi necessari alla gestione delle comunicazioni tra le Probes ed il Client.
	
	In particolare le Probes richiedono i parametri per effettuare le misure al Server, e gli forniscono i risultati.
 	Quando il Client lo richiede, gli vengono spediti tutti i risultati in possesso del Server, che li azzera localmente e ricomincia.

	"""

	def __init__(self):

		print "### Starting the ProbeManager..."
		Pyro.core.ObjBase.__init__(self)
	
		self.ProbeList = []
		self.AliveProbe = {}
		self.StressWork = {}
		self.ResultList=[]
		self.Token = "ZOMBIE-"
		self.KillProbe = -10
	
	def ShutDown(self):
		"""
		Metodo per terminare in automatico il ProbeManager.

		:returns: *nulla*.
		"""
		global RunNumb
		RunNumb = self.KillProbe
		time.sleep(2*Interval)
		#mando il KeyboardInterrupt al Main, provocando la chiusura
		thread.interrupt_main()

	def SetStress(self, index, flag1, flag2):
		"""
		Metodo per modificare i flag di carico su CPU e MEM.

		:param index: indice nella ProbeList della Probe interessata.
		:param value: nuovi valori da assegnare ai flag.
		:returns: *nulla*.
		"""
		#print "ricevuta richiesta di stress per ", index, flag1, flag2
		self.StressWork[self.ProbeList[index]] = [flag1, flag2]

	def GetStress(self, index):
		"""
		Metodo per modificare i flag di carico su CPU e MEM.

		:param index: indice nella ProbeList della Probe interessata.
		:returns: i valori degli StressFlags della specifica Probe.
		"""
		return(self.StressWork[self.ProbeList[index]])

	def PutResult(self, item):
		"""
		Metodo che inserisce nella coda dei Risultati un nuovo oggetto.

		:param item: l'oggetto da aggiungere alla coda.
		:returns: *nulla*.
		"""
		global Interval
		#vado a prelevare l'ultimo elemento, cioè il tempo in cui è iniziato il monitoraggio
		stop = time.time()
		start = item.pop()
		#lo confronto con il tempo attuale e sottraggo Interval, ottenendo la latenza che rimetto in fondo ad item
		#traduco il risultato in millisecondi e lo approssimo ad NDecimal cifre decimali
		NDecimal = 2
		item.append(round(1000*(stop-start-Interval),NDecimal))
		#print "Ricevuti risultati monitoraggio",item[0],item[1],self.AliveProbe[item[0]]
		self.AliveProbe[item[0]] = item[1]
		self.ResultList.append(item)

	def GetWork(self, ProbeID):
		"""
		Metodo per comunicare tra la Probe remota ed il Server.

		:param ProbeID: identificativo della Probe.
		:returns: Una tupla contenente tutte le informazioni per il monitoraggio da parte della Probe.
		"""
		global RunNumb, Interval

		global ConfigFile
		Configure.LoadConfig(ConfigFile)

		stressCPU, stressMEM = self.StressWork[ProbeID][0], self.StressWork[ProbeID][1]
		self.StressWork[ProbeID][0], self.StressWork[ProbeID][1] = False, False
		#rilevo una probe in eccesso
		if (len(self.ProbeList) > Configure.MaxNodes) and (ProbeID == self.ProbeList[-1]) : 
			print ">> Terminated a OverFlowed-Probe",self.ProbeList.pop(self.ProbeList.index(ProbeID))
			return(self.KillProbe, Interval, time.time(), False, False)
		#il server sta spegnendo le probe
		elif (RunNumb < 0):
			print ">> Shutting down Probe",self.ProbeList.pop(self.ProbeList.index(ProbeID))
			return(self.KillProbe, Interval, time.time(), False, False)
		#composizione del work normale
		else: return(RunNumb, Interval, time.time(), stressCPU, stressMEM)

	def GetResult(self):
		"""
		Metodo per ottenere la lista dei risultati ottenuti dalle Probe. Dopo questa operazione, la lista viene svuotata.

		:returns: La lista dei risultati.
		"""
		#ogni volta che il client richiama questa funzione, è passato un interval e comincia una nuova Run
		global RunNumb
		RunNumb += 1
		Copy = self.ResultList[:]
		self.ResultList = []
		return (Copy)

	def GetProbe(self):
		"""
		Metodo per ottenere la lista dalle Probe.

		:returns: La lista degli identificativi delle Probe.
		"""
		#una controllata alla lista prima di passarla al chiamante
		self.CheckList()
		return (self.ProbeList)

	def GetToken(self):
		"""
		Metodo per ottenere il nome utilizzato come Token.

		:returns: L'elemento Token.
		"""
		#una controllata alla lista prima di passarlo al chiamante
		self.CheckList()
		return (self.Token)

	def CheckList(self):
		"""
		Metodo per controllare se le Probe sono ancora attive, basandosi sul loro ultimo risultato sottomesso. Modifica self.ProbeList

		:returns: *nulla*.
		"""
		global RunNumb
		Toll = 10 # Cercare di essere severi, altrimenti gli zombies scappano
		for item in self.ProbeList:
			if not (item.startswith(self.Token)) and RunNumb >= 0:
				ItemRun = self.AliveProbe[item]
				if (ItemRun < RunNumb - Toll) or (ItemRun > RunNumb + Toll):
					print ">> Detected a ZOMBIE-Probe", item, "(since", RunNumb-ItemRun, "runs)"
					#si fonda sulla convinzione che nessuna probe abbia lo stesso pid
					self.ProbeList.insert(self.ProbeList.index(item), self.Token+item[-4:])
					self.ProbeList.remove(item)

	def SearchPlaceholder(self):
		"""
		Metodo per controllare se nella ProbeList ci sono delle occorrenze di placeholder ZOMBIE

		:returns: indice dell'elemento placeholder se trovato.
		:returns: valore -1 altrimenti.
		"""
		for item in self.ProbeList:
			if (item.startswith(self.Token)):
				return(self.ProbeList.index(item))
		return (-1)

	def ACKNode(self, ProbeID):
		"""
		Metodo che gestisce l'acknowledgement di nuove Probe al Server.

		In questo modo è possibile tenere traccia delle Probes a cui è stato dato il permesso di lavorare
		ed è possibile controllare il *numero massimo consentito* di Probes in monitoring.

		:returns: ``True`` se il Server ha acconsentito all'introduzione del nuovo Worker.
		:returns: ``False`` se il Server ha raggiunto il numero massimo di Worker consentito.
		"""
		global ConfigFile, RunNumb
		Configure.LoadConfig(ConfigFile)
		print ">>",ProbeID,"request to connect"

		#una controllata alla lista prima di cercare d'inserire una nuova probe
		self.CheckList()


		if (str(ProbeID) in self.ProbeList):
			print ">>> Rejected duplicate probe",ProbeID
			return False
		else:
			firstPlaceholder = self.SearchPlaceholder()
			if (firstPlaceholder >= 0):
				self.ProbeList.pop(firstPlaceholder)
				self.ProbeList.insert(firstPlaceholder,str(ProbeID))
				self.StressWork[str(ProbeID)] = [False,False]
				self.AliveProbe[ProbeID] = RunNumb
				print ">>> Connected new probe replacing ZOMBIE one",ProbeID
				return True

			elif (len(self.ProbeList) < Configure.MaxNodes):
				self.ProbeList.append(str(ProbeID))
				self.StressWork[str(ProbeID)] = [False,False]
				self.AliveProbe[ProbeID] = RunNumb
				print ">>> Connected new probe",ProbeID
				return True

			else:
				print ">>> Rejected new probe",ProbeID
				return False

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

def CheckStr(value):
	"""
	Funzione che controlla la validità di una stringa.

	:param value: Il valore di cui va effettuato il type-checking.
	:returns: ``value`` stesso, se il valore è del tipo corretto; altrimenti solleva una eccezione ``TypeError``

	"""
	if (not isinstance(value, str)): raise TypeError, "Argomento ""--conf"" non valido."
	else: return value

#-------------------------------------------------------------------------------

def Main():

	"""
	Funzione Main del Server.

	Legge le opzioni che gli passa il Client quando lo lancia, nel caso modifica il file hosts (locale) e fa partire il server PyRo che si mette in ascolto.
	"""

	global ConfigFile

	parser = OptionParser()
	parser.add_option("-c", "--conf", dest="FILE", default="", metavar="FILE", help="Specifica il file di configurazione da utilizzare.")
	parser.add_option("-l", "--localhost", dest="localhost", action="store_true", help="Indica che il software verra utilizzato solo sulla macchina locale.")
	parser.add_option("--quiet", dest="quiet", action="store_true", help="Indica al software che non deve utilizzare lo stdout.")

	(options, args) = parser.parse_args()
	ConfigFile = CheckStr(options.FILE.strip())
	LocalHost = options.localhost
	QuietMode = options.quiet

	if(LocalHost and not QuietMode):
		# Se il monitor viene eseguito in locale, viene automaticamente modificato il file /etc/hosts (se presenti i permessi di root), in modo tale da non applicare come indirizzo di ascolto l'indirizzo di loopback, ma l'indirizzo attuale della scheda di rete presente.
		print "### Properly setting /etc/hosts file..."

		os.system("grep -q \"Linguaggi Dinamici\" /etc/hosts && sudo cp /etc/hosts.bak /etc/hosts || sudo cp /etc/hosts /etc/hosts.bak")
		os.system("echo \"$(sed 's/^127\.0\..*\('\"$(hostname)\"'\|localhost\)/#\\0/g' /etc/hosts)\\n\\n###  lines below added automatically by a script  ###\\n\\n$(hostname -i)\\t$(hostname)\\n$(hostname -i)\\tlocalhost\" > /etc/hosts")
		
	IPAddr = str(subprocess.check_output("hostname -I", shell=True)) # Metodo per ottenere l'indirizzo IP della scheda di rete, senza l'utilizzo di ifconfig
	threading.Thread(target=Pyro.naming.main, args=[['-n', IPAddr, '-v']]).start() # Lancia il NameServer in ascolto sull'indirizzo della scheda di rete

        Pyro.core.initServer() # Inizializza il server PyRO

	while(True):
		try:
			ns = Pyro.naming.NameServerLocator().getNS() # Viene ottenuto il nameserver
			break
		except:	pass

	d = Pyro.core.Daemon(host=IPAddr)
        d.useNameServer(ns)

	try: ns.createGroup(":LDServer")
	except NamingError: pass

	try: ns.unregister(":LDServer.ProbeManager")
	except NamingError: pass

	w = ProbeManager()

        d.connect(w, ':LDServer.ProbeManager')
	print "### ProbeManager server ready."

        try:
		threading.Thread(target=d.requestLoop()).start() # Il server rimane in ascolto all'infinito
	except KeyboardInterrupt:
		print "### Shutting down daemon, disconnecting objects..."
		d.disconnect(w)
		d.shutdown()
		print "### Server stopped gracefully."
		os._exit(0)

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == "__main__":
	Main()

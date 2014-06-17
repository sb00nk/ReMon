#!/usr/bin/python
# coding: utf-8

"""
.. module:: Probe

Modulo che gestisce il codice che deve eseguire ogni nodo, ovvero la richiesta dei dati dal Server e l'applicazione del monitoraggio sul sistema ospite.

"""

import os, socket, time, sys, gc

import Pyro.core, Pyro.errors

import threading
import numpy
from random import randrange

#cerco di importare psutil, se non riesco lo importo dai miei moduli
try:
	import psutil
except ImportError:
	#includo i moduli dalla cartella ../extra/modules/
	import inspect
	cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],"../extra/modules/psutil")))
	if cmd_subfolder not in sys.path:
    		sys.path.insert(0, cmd_subfolder)
finally:
	import psutil

#-------------------------------------------------------------------------------

ProbeManager = None
ProbeID = None

#-------------------------------------------------------------------------------

def StressCPU():

	"""
	Funzione per mettere sotto sforzo la CPU

	Calcola numerosi interi random intorno ad un intervallo fissato (Order) per mostrare il consumo di CPU

	:returns: *nulla*.
	"""
	Order = 150000 #magic number rilevato con test in laboratorio

	Numb = randrange(70000,Order)
	for i in range(Numb):
		carico = randrange((Order-1000),(Order+1000))
		

#-------------------------------------------------------------------------------

def StressMEM():

	"""
	Funzione per mettere sotto sforzo la Memoria

	Alloca Order locazioni di memoria di dimensione fissata per mostrare il consumo di Memoria

	:returns: *nulla*.
	"""
	Order = 5000 #magic number rilevato con test in laboratorio
	count = 0
	MemoryList = []
	MemoryList2 = []
	MemoryList3 = []
	MemoryList4 = []
	gc.disable()
	while (count < Order):
		MemoryList.append(numpy.ones((Order/100,Order/100)))
		MemoryList2.append(numpy.ones((Order/100,Order/100)))
		MemoryList3.append(numpy.ones((Order/100,Order/100)))
		MemoryList4.append(numpy.ones((Order/100,Order/100)))
		time.sleep(0.001) #mi serve rallentare un po' la pendenza, altrimenti non si vede bene
		count += 1
	del (MemoryList)
	del (MemoryList2)
	del (MemoryList3)
	del (MemoryList4)
	gc.enable()
#-------------------------------------------------------------------------------

def CatchCPU(RunNumb, Interval, TimeStart):

	"""
	Funzione per catturare i dati della CPU

	Cattura il numero delle CPUs del nodo sul quale gira, la percentuale di utilizzo media nell'intervallo richiesto
	 e li impacchetta per formare la risposta.

	:param RunNumb: Il numero della Run corrente (al momento in cui è stato richiesto il lavoro al server)
	:param Interval: Intervallo tra un campionamento e l'altro.
	:param TimeStart: Tempo di avvio di questo campionamento, lo restituisco in uscita per poter calcolare la latenza.
	:returns: Una tupla contenente i dati rilevati nel Interval.
	"""
	ProbeManager.PutResult([ProbeID, RunNumb, "CPU", float(psutil.NUM_CPUS), psutil.cpu_percent(interval=Interval), TimeStart])

#-------------------------------------------------------------------------------

def CatchMEM(RunNumb, Interval, TimeStart):

	"""
	Funzione per catturare i dati della Memoria

	Cattura le percentuali di utilizzo della memoria e della swap medie nell'intervallo richiesto
	 e le impacchetta per formare la risposta.

	:param RunNumb: Il numero della Run corrente (al momento in cui è stato richiesto il lavoro al server)
	:param Interval: Intervallo tra un campionamento e l'altro.
	:param TimeStart: Tempo di avvio di questo campionamento, lo restituisco in uscita per poter calcolare la latenza.
	:returns: Una tupla contenente i dati rilevati nel Interval.
	"""
	#selettori per andare a selezionare la percentuale di memoria utilizzata nelle rispettive liste ritornate da psutil
	SelPerc = 3

	Average_MEM, Average_SWP = 0, 0
	for i in range(Interval):
		Average_MEM += psutil.phymem_usage()[SelPerc]/(Interval+1)
		Average_SWP += psutil.virtmem_usage()[SelPerc]/(Interval+1)
		time.sleep(1)

	Average_MEM += psutil.phymem_usage()[SelPerc]/(Interval+1)
	Average_SWP += psutil.virtmem_usage()[SelPerc]/(Interval+1)
	ProbeManager.PutResult([ProbeID, RunNumb, "MEM", Average_MEM, Average_SWP, TimeStart])
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------

def Main():

	"""
	Funzione Main della Probe.

	All'inizio la Probe si occupa di contattare il Server e di registrarsi presso di lui. Dopodichè comincia a chiedere lavoro al server, cioè una lista contenente le indicazioni delle misure che deve fare e se ha dei carichi extra.

	:returns: *nulla*.
	"""
	global ProbeManager, ProbeID
	Pyro.core.initClient()
	# Ci si connette al Server
	ProbeManager = Pyro.core.getProxyForURI("PYRONAME://:LDServer.ProbeManager") 
	print "### Connected to ProbeManager server"
	# Si costruisce l'identificatore univoco del Worker sottoforma di stringa
	ProbeID = socket.gethostname().upper() + "-" + str(os.getpid())
	print ">> PROBE ID: " + ProbeID
	print "### Requesting acknowledgement from ProbeManager server..."
	if(ProbeManager.ACKNode(ProbeID)):
		print "### Receiving work from ProbeManager server..."
	else:
		print "### ERR: Connection refused from ProbeManager server... KILLED."
		os._exit(0)

	while(True):
		#recupero dal server una lista di informazioni riguardanti i lavori che dovrà svolgere questa particolare probe
		#mappo: numero_run, time_step, time_start, cpu_stress_flag, mem_stress_flag
		KeyList=["RunNumb", "Interval", "TimeStart", "CPUStressFlag", "MEMStressFlag"]
		TestInfo=dict(zip(KeyList,ProbeManager.GetWork(ProbeID)))	
		#print "Info ricevute dal server",ProbeManager.GetWork(ProbeID)
		#print "Info mappate localmente",TestInfo

		#chiusura comandata dal server
		if (TestInfo["RunNumb"] < 0):
			print "### Probe terminated by ProbeManager server.. KILLED."
			os._exit(0)

		#ed in base a questi, lanciare il lavoro per questa run
		if (TestInfo["CPUStressFlag"]):
			CPU = threading.Thread(target=StressCPU)
			CPU.daemon = True
			CPU.start()
		if (TestInfo["MEMStressFlag"]):
			MEM = threading.Thread(target=StressMEM)
			MEM.daemon = True
			MEM.start()
		#nota: so esattamente quando una probe comincia e finisce un lavoro -> posso misuare il delay(dal SERVER)
		threading.Thread(target=CatchCPU(TestInfo["RunNumb"],TestInfo["Interval"],TestInfo["TimeStart"])).start()
		threading.Thread(target=CatchMEM(TestInfo["RunNumb"],TestInfo["Interval"],TestInfo["TimeStart"])).start()

		#il thread principale può dormire un Interval mentre gli altri lavorano
		time.sleep(TestInfo["Interval"])
		

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

if __name__=="__main__":
	Main()

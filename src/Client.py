#!/usr/bin/python
# coding: utf-8

"""
.. module:: Client

Modulo che fa da front-end per l'utente, lancia il server oppure l'interfaccia grafica e le Probes a seconda della modalità.

"""

import os, sys, socket
import threading, getpass, time, numpy, operator
import Configure
import Interface

import Pyro.naming, Pyro.core
from Pyro.errors import ConnectionClosedError, ProtocolError

from optparse import OptionParser
from subprocess import STDOUT
from itertools import ifilter
from collections import defaultdict

#includo i moduli dalla cartella ../extra/modules/
import inspect
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],"../extra/modules/cairoplot")))
if cmd_subfolder not in sys.path:
	sys.path.insert(0, cmd_subfolder)
import cairoplot

cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],"../extra/modules/lockfile")))
if cmd_subfolder not in sys.path:
	sys.path.insert(0, cmd_subfolder)
from lockfile import FileLock,LockTimeout

#cerco di importare fabric, se non riesco lo importo dai miei moduli
try:
	from fabric.api import *
	from fabric.network import disconnect_all
except ImportError:
	cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0],"../extra/modules/fabric")))
	if cmd_subfolder not in sys.path:
		sys.path.insert(0, cmd_subfolder)
finally:
	from fabric.api import *
	from fabric.network import disconnect_all

#-------------------------------------------------------------------------------
Interval,TimeStep = None,None
ConfigFile = None
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

class Client():

	def __init__(self, Manager):
		global Interval, TimeStep
		Interval = Configure.Interval
		TimeStep = Configure.TimeStep

		self.ProbeManager = Manager
		self.AskPass = True

		print "### Setting up Probes..."
		self.SetupMonitoring()

		# if per i settaggi del test, coprono anche una possibile "chiamata irregolare"
		if Manager is not None :
			print "### Starting GUI..."
			threading.Thread(target=Interface.Main,
args=(self.RemoteStartMonitoring, self.SetupMonitoring, self.ProbeManager)).start()
#-------------------------------------------------------------------------------

	def GatherResults(self):
		"""
		Recupera i risultati del monitoraggio dal Server.

		:returns: Una lista contenente tutti i dati raccolti dalle Probe.
		"""
		Results = self.ProbeManager.GetResult()

		#ordino i risultati in base alla run prima di restituirli
		Results.sort(key=lambda ele: (ele[1]))
		return Results
#-------------------------------------------------------------------------------

	def MakeLegend(self, FileName):
		"""
		Funzione che produce un'immagine con la legenda.

		:param FileName: Nome file da assegnare al risultato.
		:returns: *nulla*

		"""
		global Interval
		FileName = 'extra/MonitorGraph/'+FileName
		FakeValues = range(len(self.ProbeList))

		#ogni volta cerca di acquisire il lock per creare una nuova immagine, se non riesce, rompe il lock
		TempLock = FileLock(FileName)
		try:
			TempLock.acquire(timeout=Interval)
		except LockTimeout:
			TempLock.break_lock()
		else:
			cairoplot.dot_line_plot(FileName, dict(zip(self.ProbeList,FakeValues)), 200, 10*len(self.ProbeList)+50, 
axis=False, grid=False, series_legend=True,series_colors=self.Colors)
			TempLock.release()
#-------------------------------------------------------------------------------

	def MakeGraph(self, Data, FileName):
		"""
		Funzione che produce un grafico temporale.

		:param Data: Serie di dati da dover graficare.
		:param FileName: Nome file da assegnare al grafico prodotto.
		:returns: *nulla*

		"""
		global Interval,TimeStep

		Markers=[]
		FileName = 'extra/MonitorGraph/'+FileName

		for x in range((TimeStep-1)*Interval,-1,-Interval): Markers.append(str(x))

		#ogni volta cerca di acquisire il lock per creare una nuova immagine, se non riesce, rompe il lock
		TempLock = FileLock(FileName)
		try:
			TempLock.acquire(timeout=Interval)
		except LockTimeout:
			TempLock.break_lock()
		else:
			cairoplot.dot_line_plot(FileName, dict(zip(self.ProbeList,Data[:])), 
600, 200, axis=True, grid=True, series_legend=False, x_labels=Markers, series_colors=self.Colors)
			TempLock.release()
#-------------------------------------------------------------------------------

	def MakeGraphPercent(self, Data, FileName):
		"""
		Funzione che produce un grafico percentuale sotto forma di pieplot.

		:param Data: Dato da dover graficare.
		:param FileName: Nome file da assegnare al grafico prodotto.
		:returns: *nulla*

		"""
		global Interval
		Labels = ["%IN USO","TOT"]
		FileName = 'extra/MonitorGraph/'+FileName

		#print "**Data Graph**"
		#print Data

		#selezione della combinazione di colori per i grafici percentuali, a soglie [0,33],[34,66],[67,100]
		if  (Data <= 33): PercentColors = ["lime","gray"]
		elif (Data <= 66): PercentColors = ["yellow","light_gray"]
		else : PercentColors = ["red","white"]
		Data = [int(Data),100-int(Data)]

		#ogni volta cerca di acquisire il lock per creare una nuova immagine, se non riesce, rompe il lock
		TempLock = FileLock(FileName)
		try:
			TempLock.acquire(timeout=Interval)
		except LockTimeout:
			TempLock.break_lock()
		else:
			cairoplot.pie_plot(FileName, dict(zip(Labels,Data)), 185, 130, colors = PercentColors)
			TempLock.release()
#-------------------------------------------------------------------------------

	def MakeGraphTop3(self, Data, FileName):
		"""
		Funzione che produce un grafico dei nodi a maggiore latenza sotto forma di istogram.

		:param Data: Serie di dati da dover graficare.
		:param FileName: Nome file da assegnare al grafico prodotto.
		:returns: *nulla*

		"""
		global Interval
		FileName = 'extra/MonitorGraph/'+FileName

		ordered = sorted(Data.iteritems(), key=operator.itemgetter(1), reverse=True)
		first3 = []
		colors3 = []
		for item in ordered:
			if (len(first3) < 3) and (item[0] in self.ProbeList):
				colors3.append(self.Colors[sorted(self.ProbeList).index(item[0])])
				first3.append(item[1])

		#ogni volta cerca di acquisire il lock per creare una nuova immagine, se non riesce, rompe il lock
		TempLock = FileLock(FileName)
		try:
			TempLock.acquire(timeout=Interval)
		except LockTimeout:
			TempLock.break_lock()
		else:
			cairoplot.vertical_bar_plot(FileName, first3, 170, 130, display_values=True, colors=colors3)
			TempLock.release()
#-------------------------------------------------------------------------------

	def SetupMonitoring(self):
		"""
		Funzione preparatoria per il setup del sistema di monitoraggio.

		:returns: *nulla*.
		"""
		print "### Setup Monitoring..."
		global ConfigFile,TimeStep,Interval
		Configure.LoadConfig(ConfigFile) # Carica la configurazione.
		self.NumbNodes = Configure.MaxNodes

		# if per i settaggi del test, coprono anche una possibile "chiamata irregolare"
		if self.ProbeManager is not None : self.ProbeList = self.ProbeManager.GetProbe()
		else :
			self.ProbeList = []
			self.NumbNodes = 0
		self.NumbProbe = len(self.ProbeList)

		if(Configure.LocalhostOnly):
			for i in range(self.NumbProbe,self.NumbNodes):
				print ">> Start Probe #",i
				threading.Thread(target=os.system, args=["gnome-terminal -e \"python src/Probe.py\""]).start()
			if self.ProbeManager is not None : token = self.ProbeManager.GetToken()
			for i,item in enumerate(self.ProbeList):
				if(item.startswith(token)):
					print ">> Refresh Probe #",i
					threading.Thread(target=os.system, args=["gnome-terminal -e \"python src/Probe.py\""]).start()
		else:
			if (self.AskPass):
				self.user = raw_input("\tUsername:")
				self.passwd = getpass.getpass("\tPassword:")
				self.AskPass = False

			ClientID = str(socket.gethostname()).upper()

			hosts = ",".join([ line.rstrip() for (i,line) in enumerate(open("./extra/fabric/hosts.txt"))
			                   if (i <= self.NumbNodes
			                       and not(line.startswith(ClientID)) 
			                       and not any(item.startswith(line.rstrip()) for item in self.ProbeList)) ])

			# Vengono ottenuti i primi "MaxNodes" dalla lista degli hosts per fabric, escludendo l'host Client

			print ">> Loaded host list from Fabric :", hosts
			if (len(hosts) >= 1):
				os.system("cd ./extra/fabric; fab --hide ALL --hosts " + hosts + " -u " + self.user + " -p " + self.passwd + " load_probes > /dev/null")
				print ">> Starting Probes..."
				sys.stdout.flush()
				probe = threading.Thread(target=os.system, args=["cd ./extra/fabric; fab --hide ALL --hosts " + hosts + " -u " + self.user + " -p " + self.passwd + " start_probes"])
				probe.daemon = True
				probe.start()
				sys.stdout.flush()

		TimeStep = Configure.TimeStep
		Interval = Configure.Interval

		self.CPUData = [[0 for x in xrange(TimeStep)] for x in xrange(self.NumbNodes)] 
		self.MEMData = [[0 for x in xrange(TimeStep)] for x in xrange(self.NumbNodes)]
		self.SWPData = [[0 for x in xrange(TimeStep)] for x in xrange(self.NumbNodes)]
		self.LATData = [[0 for x in xrange(TimeStep)] for x in xrange(self.NumbNodes)]
#-------------------------------------------------------------------------------

	def RemoteStartMonitoring(self):
		"""
		Funzione di appoggio per la GUI, per fare partire un tread di Monitoring

		:returns: *nulla*.
		"""
		threading.Thread(target=self.Monitoring).start()
#-------------------------------------------------------------------------------

	def Monitoring(self):
		"""
		Funzione principale del Client, dove recupera i dati dal server e li usa per disegnare i grafici.

		:returns: *nulla*.
		"""
		global Interval
		LATStat = defaultdict(lambda: Interval)

		#carico la lista con i miei colori, per essere sicuro di associare sempre lo stesso colore ad una certa probe
		MyColors = [	"orange",	"lime",		"cyan",		"maroon",	"navy",		"yellow",
		                    "magenta",	"green",	"red",		"blue",		"black",	"gray",
		                    "custom-0",	"custom-1",	"custom-2",	"custom-3",	"custom-4",	"custom-5",
		                    "custom-6",	"custom-7",	"custom-8",	"custom-9",	"custom-10",	"custom-11",
		                    "custom-12",	"custom-13",	"custom-14",	"custom-15",	"custom-16",	"custom-17"	]

		CPUStat,MEMStat,SWPStat = [],[],[]

		print "### Start Monitoring..."

		while (True):
			try :
				self.ProbeList = self.ProbeManager.GetProbe()
				self.NumbProbe = len(self.ProbeList)

				self.Token = self.ProbeManager.GetToken()
				self.NumbPlaceHolder = 0
				#print self.Token,self.NumbProbe,self.ProbeList

				for item in self.ProbeList:
					if item.startswith(self.Token):
						self.NumbPlaceHolder += 1

				#creazione della lista dei colori secondo l'ordine alfabetico
				self.Colors = []
				for item in sorted(self.ProbeList):
					genertedColor = MyColors[self.ProbeList.index(item)]
					self.Colors.append(genertedColor)

				#print ">> Drawing legend..."
				self.MakeLegend("legenda.png")
				#print ">> Collecting results from Probes..."
				Results = self.GatherResults()

				#selettori per andare a prelevare i valori giusti nella lista che rappresenta i risultati
				SelProbe,SelTag,SelValue1,SelValue2,SelValue3=0,2,3,4,5
				for num in range(self.NumbProbe):
					if (self.ProbeList[num].startswith(self.Token)):
						LATStat[self.ProbeList[num]] += Interval

					for element in ifilter(lambda ele:ele[SelProbe]==self.ProbeList[num], Results):
						if (element[SelTag]=="CPU"):
							#trattamento dati per grafico temporale CPU
							self.CPUData[num].pop(0)
							self.CPUData[num].append(element[SelValue2])
							#trattamento dati per grafico statistica CPU
							CPUStat.append(element[SelValue2])
							#trattamento dati per il grafico latenza CPU
							self.LATData[num].pop(0)
							self.LATData[num].append(element[SelValue3])
							#trattamento dati per grafico statistica Lat
							LATStat[element[SelProbe]] = element[SelValue3]
						elif (element[SelTag]=="MEM"):
							#trattamento dati per grafico temporale MEM
							self.MEMData[num].pop(0)
							self.MEMData[num].append(element[SelValue1])
							#trattamento dati per grafico statistica MEM
							MEMStat.append(element[SelValue1])
							#trattamento dati per grafico temporale SWP
							self.SWPData[num].pop(0)
							self.SWPData[num].append(element[SelValue2])
							#trattamento dati per grafico statistica SWP
							SWPStat.append(element[SelValue2])
				#creazione Grafici Temporali
				self.MakeGraph(self.CPUData, "cpu.png")
				self.MakeGraph(self.MEMData, "mem.png")
				self.MakeGraph(self.SWPData, "swp.png")
				self.MakeGraph(self.LATData, "lat.png")

				#le statistiche considerano solo i dati istantanei
				#se non sono presenti è meglio evitare di invocare le funzioni
				#creazione Grafici Percentuali
				#print "**CPUStat**"
				#print CPUStat,self.NumbProbe,self.NumbPlaceHolder
				if (len(CPUStat) >= self.NumbProbe-self.NumbPlaceHolder
				    and len(CPUStat) > 0): 
					self.MakeGraphPercent(numpy.mean(CPUStat), "cpu_stat.png")
					CPUStat = []
				#print "**MEMStat**"
				#print MEMStat
				if (len(MEMStat) >= self.NumbProbe - self.NumbPlaceHolder
				    and len(MEMStat) > 0):
					self.MakeGraphPercent(numpy.mean(MEMStat), "mem_stat.png")
					MEMStat = []
				#print "**SWPStat**"
				#print SWPStat
				if (len(SWPStat) >= self.NumbProbe - self.NumbPlaceHolder
				    and len(SWPStat) > 0):
					self.MakeGraphPercent(numpy.mean(SWPStat), "swp_stat.png")
					SWPStat = []

				#creazione Grafici Top 3
				if (len(LATStat) > 0): 
					self.MakeGraphTop3(LATStat, "lat_stat.png")				

				if (self.NumbProbe == 0):
					sys.stdout.flush()
					raise ConnectionClosedError

				#sleep alla fine				
				time.sleep(Interval)

			except IndexError:
				pass

			except ConnectionClosedError:
				print "### Cleaning and Closing..."

				#pulizia delle macchine Probe
				if(not Configure.LocalhostOnly):

					ClientID = str(socket.gethostname()).upper()
					hosts = ",".join([ line.rstrip() for (i,line) in enumerate(open("./extra/fabric/hosts.txt"))
					                   if (i <= self.NumbNodes
					                       and not(line.startswith(ClientID)) 
					                       and not any(item.startswith(line.rstrip()) for item in self.ProbeList)) ])

					print ">> Loaded host for remote cleaning :", hosts
					if (len(hosts) >= 1):
						os.system("cd ./extra/fabric; fab --hide ALL --hosts " + hosts + " -u " + self.user + " -p " + self.passwd + " clean > /dev/null")
					disconnect_all()

				#pulizia della macchina Client
				print "### Cleaning up locally..."
				os.system("find ./extra/MonitorGraph/ -type f -not -name 'def*' | xargs rm -f")
				print "### Client terminated by ProbeManager server... SHUTDOWN."
				os._exit(0)

			except Exception:
				raise ConnectionClosedError

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
	Funzione **Main**

	Il punto di partenza del programma, analizza le opzioni richieste e lancia il Server oppure Client, GUI e Probes a seconda della modalità.
	"""

	parser = OptionParser(usage="Client.py [-a] [-g/-s] [-l] [-c FILE]\n\n\t --> ReMon - Remote Monitor <--")
	parser.add_option("-g", "--startgui", dest="startgui", default=False, action="store_true", help="Avvia l'interfaccia grafica.")
	parser.add_option("-s", "--startserver", dest="startserver", default=False, action="store_true", help="Avvia il programma come istanza Server.")
	parser.add_option("-c", "--conf", dest="FILE", default="", metavar="FILE", help="Specifica il file di configurazione da utilizzare.")
	parser.add_option("-l", "--localhost", dest="localhost", default=False, action="store_true", help="Indica che il software verra utilizzato solo sulla macchina locale.")
	parser.add_option("-a", "--autostart", dest="autostart", default=False, action="store_true", help="Avvia il Server ed il Client sulla stessa macchina in automatico.")

	(options, args) = parser.parse_args()
	ServerMode = options.startserver
	StartGui = options.startgui
	AutoStart = options.autostart
	global ConfigFile
	ConfigFile = CheckStr(options.FILE)
	LocalHost = options.localhost

	Configure.LoadConfig(ConfigFile) # Carico la configurazione da file

	if(ConfigFile==""):
		print "### ATT: No configuration file in input.\n	Defaults will be loaded."
		Configure.SaveConfig(True)
		ConfigFile = Configure.ConfigFile

	if(ServerMode):
		print "### Running mode: SERVER"
		if(StartGui): print("### ATT: Can't set both -g AND -s flags, use -a instead.")
		ServerString = "python src/Server.py -c " + ConfigFile
		if(LocalHost): ServerString += " -l"
		os.system(ServerString)		
		sys.exit(0)

	elif(StartGui):
		print "### Running mode: CLIENT"
		Pyro.core.initClient()
		C = Client(Pyro.core.getProxyForURI("PYRONAME://:LDServer.ProbeManager"))

	elif(AutoStart):
		print "### Running mode: AUTOSTART"
		ServerString = "python src/Server.py --quiet -c " + ConfigFile
		if(LocalHost): ServerString += " -l"
		server = threading.Thread(target=os.system, args=[ServerString + " > /dev/null"])
		server.daemon = True
		server.start()

		while(True):
			try:
				#concedo un secondo (alla volta) al server per partire
				time.sleep(1)
				Pyro.core.initClient()
				C = Client(Pyro.core.getProxyForURI("PYRONAME://:LDServer.ProbeManager"))
				break
			except:
				pass

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

if __name__ == "__main__":
	Main()

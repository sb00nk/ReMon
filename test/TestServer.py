#!/usr/bin/python
# coding: utf-8

"""
Modulo che effettua il processo di Testing sul codice del progetto.

"""

import sys
import unittest

from src.Server import *
from src.Configure import *

#-------------------------------------------------------------------------------

class TestServer(unittest.TestCase):
	"""
	Classe che controlla il modulo di Server

	"""
	def setUp(self):
		"""
		Funzione preparatoria per il testing del Modulo

		"""
		self.probe = "TestProbe-0001" #nome compatibile con quelli realmente adottati
		self.result = [self.probe, 2, "CPU", 2, 53, 1.111111] #dati compatibili con un vero result
		self.flags = [True, True] #lo stato normale dei flag stress è False, False
		self.M = ProbeManager()

	def testObj(self):
		"""
		Funzione che controlla la correttezza degli oggetti del Modulo

		"""
		self.assertTrue(isinstance(self.M, ProbeManager), "M non è una istanza di ProbeManager.")

	def testMeth(self):
		"""
		Funzione che controlla la completezza della implementazione dei metodi all'interno del Modulo

		"""
		def testMeth(self):
			self.assertTrue(callable(self.M.ShutDown), 	    "Metodo ""ShutDown"" inesistente.")
			self.assertTrue(callable(self.M.SetStress),	    "Metodo ""SetStress"" inesistente.")
			self.assertTrue(callable(self.M.GetStress), 	    "Metodo ""GetStress"" inesistente.")
			self.assertTrue(callable(self.M.PutResult), 	    "Metodo ""PutResult"" inesistente.")
			self.assertTrue(callable(self.M.GetWork),	    "Metodo ""GetWork"" inesistente.")
			self.assertTrue(callable(self.M.GetResult), 	    "Metodo ""GetResult"" inesistente.")
			self.assertTrue(callable(self.M.GetProbe), 	    "Metodo ""GetProbe"" inesistente.")
			self.assertTrue(callable(self.M.GetToken), 	    "Metodo ""GetToken"" inesistente.")
			self.assertTrue(callable(self.M.CheckList), 	    "Metodo ""CheckList"" inesistente.")
			self.assertTrue(callable(self.M.SearchPlaceholder), "Metodo ""SearchPlaceholder"" inesistente.")
			self.assertTrue(callable(self.M.ACKNode), 	    "Metodo ""ACKNode"" inesistente.")

	def testStr(self):
		"""
		Funzione che controlla la correttezza del tipo immesso da una opzione

		"""
		self.assertRaises(TypeError, CheckStr, 1)

	def testPutGetResult(self):
		"""
		Funzione che controlla la coerenza tra un Probe inserito e ottenuto dalla lista

		"""
		self.M.PutResult(self.result)
		self.assertTrue(self.result in self.M.GetResult())

	def testNodeACK(self):
		"""
		Funzione che controlla la corretta esclusione di un numero troppo elevato di nodi

		"""
		SaveConfig(True, NewFile="/tmp/config.ini") # Crea un nuovo file di configurazione temporaneo

		Configure.MaxNodes = 0 # Imposta il numero massimo di nodi nel file di configurazione
		SaveConfig() # Salva la configurazione
		self.assertFalse(self.M.ACKNode(self.probe))

		Configure.MaxNodes = 1 # Provo anche con una probe
		SaveConfig()
		self.assertTrue(self.M.ACKNode(self.probe))

	def testSetGetStress(self):
		"""
		Funzione che controlla la corretta configurazione dei flag di stress

		"""
		SaveConfig(True, NewFile="/tmp/config.ini") # Crea un nuovo file di configurazione temporaneo

		Configure.MaxNodes = 1 # Imposta il numero massimo di nodi nel file di configurazione
		SaveConfig() # Salva la configurazione
		self.M.ACKNode(self.probe)
		self.M.SetStress(0, self.flags[0], self.flags[1])
		self.assertEqual(self.flags, self.M.GetStress(0))

	def testGetCheckProbe(self):
		"""
		Funzione che controlla la coerenza tra le Probes inserite e la lista ottenuta

		"""
		SaveConfig(True, NewFile="/tmp/config.ini") # Crea un nuovo file di configurazione temporaneo

		Configure.MaxNodes = 1 # Imposta il numero massimo di nodi nel file di configurazione
		SaveConfig() # Salva la configurazione
		self.M.ACKNode(self.probe) # Notifica la Probe al server
		self.assertTrue(self.probe in self.M.GetProbe()) # Controlla se la Probe risulta tra quelle valide
		self.assertEqual(-1, self.M.SearchPlaceholder()) # Controlla che non ci siano Probe ZOMBIE

		for i in range(20): self.M.GetResult() # Incrementa il RunNumb del Server fino a rendere invalida la Probe di test

		self.assertNotEqual(self.probe, self.M.GetProbe())

		tokenProbe = self.M.GetToken()+self.probe[-4:] # Creo il nome della Probe secondo le regole del server
		self.assertTrue(tokenProbe in self.M.GetProbe()) # Controllo che risulti ZOMBIE
		self.assertFalse(self.M.SearchPlaceholder()) # Ora SearchPlaceholder mi dovrebbe ritornare 0

	def tearDown(self):
		"""
		Funzione di uscita del Modulo

		"""
		del self.result
		del self.M

	def suite(self):
		"""
		Funzione per definire la suite di test del Modulo

		"""
		return unittest.TestLoader().loadTestsFromTestCase(TestServer)

#-------------------------------------------------------------------------------

if __name__ == '__main__':
	unittest.main()

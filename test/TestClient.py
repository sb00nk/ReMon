#!/usr/bin/python
# coding: utf-8

"""
Modulo che effettua il processo di Testing sul codice del progetto.

"""

import sys
import unittest
sys.path.append(".") # Imposta il PYTHONPATH

from src.Configure import *
from src.Client import *
from src.Server import *

#-------------------------------------------------------------------------------

class TestClient(unittest.TestCase):
	"""
	Classe che controlla il modulo di Client

	"""
	def setUp(self):
		"""
		Funzione preparatoria per il testing del Modulo

		"""
		self.C = Client(None)

	def testObj(self):
		"""
		Funzione che controlla la correttezza degli oggetti del Modulo

		"""
		self.assertTrue(isinstance(self.C, Client), "C non è una istanza di Client.")

	def testMeth(self):
		"""
		Funzione che controlla la completezza della implementazione dei metodi all'interno del Modulo

		"""
		def testMeth(self):
			self.assertTrue(callable(self.C.ToggleContinue),	"Metodo ""ToggleContinue"" inesistente.")
			self.assertTrue(callable(self.C.GatherResults), 	"Metodo ""GatherResults"" inesistente.")
			self.assertTrue(callable(self.C.MakeLegend),		"Metodo ""MakeLegend"" inesistente.")
			self.assertTrue(callable(self.C.MakeGraph), 		"Metodo ""MakeGraph"" inesistente.")
			self.assertTrue(callable(self.C.MakeGraphPercent), 	"Metodo ""MakeGraphPercent"" inesistente.")
			self.assertTrue(callable(self.C.MakeGraphTop3), 	"Metodo ""MakeGraphTop3"" inesistente.")
			self.assertTrue(callable(self.C.SetupMonitoring), 	"Metodo ""SetupMonitoring"" inesistente.")
			self.assertTrue(callable(self.C.RemoteStartMonitoring), "Metodo ""RemoteStartMonitoring"" inesistente.")
			self.assertTrue(callable(self.C.Monitoring), 		"Metodo ""Monitoring"" inesistente.")

	def testStr(self):
		"""
		Funzione che controlla la correttezza del tipo immesso da una opzione

		"""
		self.assertRaises(TypeError, CheckStr, 1)

	def tearDown(self):
		"""
		Funzione di uscita del Modulo

		"""
		del self.C

	def suite(self):
		"""
		Funzione per definire la suite di test del Modulo

		"""
		return unittest.TestLoader().loadTestsFromTestCase(TestClient)

#-------------------------------------------------------------------------------

if __name__ == '__main__':
	unittest.main()

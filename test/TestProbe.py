#!/usr/bin/python
# coding: utf-8

"""
Modulo che effettua il processo di Testing sul codice del progetto.

"""

import sys
import unittest
sys.path.append(".") # Imposta il PYTHONPATH

from src.Probe import *

#-------------------------------------------------------------------------------

class TestProbe(unittest.TestCase):
	"""
	Classe che controlla il modulo di Client

	"""
	def setUp(self):
		"""
		Funzione preparatoria per il testing del Modulo

		"""
		global ProbeManager
		self.P = Main()

		ProbeManager = None
	def testObj(self):
		"""
		Funzione che controlla la correttezza degli oggetti del Modulo

		"""
		self.assertTrue(isinstance(self.P, Probe), "P non è una istanza di Probe.")

	def testMeth(self):
		"""
		Funzione che controlla la completezza della implementazione dei metodi all'interno del Modulo

		"""
		def testMeth(self):
			self.assertTrue(callable(self.P.StressCPU), "Metodo ""StressCPU"" inesistente.")
			self.assertTrue(callable(self.P.StressMEM), "Metodo ""StressMEM"" inesistente.")
			self.assertTrue(callable(self.P.CatchCPU),  "Metodo ""CatchCPU"" inesistente.")
			self.assertTrue(callable(self.P.CatchMEM),  "Metodo ""CatchMEM"" inesistente.")

	def tearDown(self):
		"""
		Funzione di uscita del Modulo

		"""
		del self.P

	def suite(self):
		"""
		Funzione per definire la suite di test del Modulo

		"""
		return unittest.TestLoader().loadTestsFromTestCase(TestProbe)

#-------------------------------------------------------------------------------

if __name__ == '__main__':
	unittest.main()

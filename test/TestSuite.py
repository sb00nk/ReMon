#!/usr/bin/python
# coding: utf-8

import sys
import unittest

sys.path.append(".") # Imposta il PYTHONPATH

from TestConfigure import *
from TestClient import *
from TestServer import *

# Definisco una suite di test per ciascuno
# dei moduli che intendo verificare
# - TestConfigure
# - TestClient
# - TestServer

ts_configure = TestConfigure("testMeth").suite()
ts_client = TestClient("testObj").suite()
ts_server = TestServer("testObj").suite()

# Istanzio un oggetto di tipo TestSuite
ts = unittest.TestSuite()

# Inserisco nell'oggetto TestSuite le test suite
# dei singoli moduli che intendo eseguire
ts.addTest(ts_configure)
ts.addTest(ts_client)
ts.addTest(ts_server)

# Istanzio un oggetto di tipo TextTestRunner, che eseguirà
# la test suite ts con l'opportuna configurazione
# - scrittura su stdout
# - livello di verbosità pari a 2
trun = unittest.TextTestRunner(sys.stdout, verbosity=2)

# Eseguo la suite di test
res = trun.run(ts)

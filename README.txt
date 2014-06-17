                                                                       
RRRRRRRRRRRRRRRRR                       MMMMMMMM               MMMMMMMM
R::::::::::::::::R                      M:::::::M             M:::::::M
R::::::RRRRRR:::::R                     M::::::::M           M::::::::M
RR:::::R     R:::::R                    M:::::::::M         M:::::::::M
  R::::R     R:::::R    eeeeeeeeeeee    M::::::::::M       M::::::::::M   ooooooooooo   nnnn  nnnnnnnn  
  R::::R     R:::::R  ee::::::::::::ee  M:::::::::::M     M:::::::::::M oo:::::::::::oo n:::nn::::::::nn 
  R::::RRRRRR:::::R  e::::::eeeee:::::eeM:::::::M::::M   M::::M:::::::Mo:::::::::::::::on::::::::::::::nn 
  R:::::::::::::RR  e::::::e     e:::::eM::::::M M::::M M::::M M::::::Mo:::::ooooo:::::onn:::::::::::::::n
  R::::RRRRRR:::::R e:::::::eeeee::::::eM::::::M  M::::M::::M  M::::::Mo::::o     o::::o  n:::::nnnn:::::n
  R::::R     R:::::Re:::::::::::::::::e M::::::M   M:::::::M   M::::::Mo::::o     o::::o  n::::n    n::::n
  R::::R     R:::::Re::::::eeeeeeeeeee  M::::::M    M:::::M    M::::::Mo::::o     o::::o  n::::n    n::::n
  R::::R     R:::::Re:::::::e           M::::::M     MMMMM     M::::::Mo::::o     o::::o  n::::n    n::::n
RR:::::R     R:::::Re::::::::e          M::::::M               M::::::Mo:::::ooooo:::::o  n::::n    n::::n
R::::::R     R:::::R e::::::::eeeeeeee  M::::::M               M::::::Mo:::::::::::::::o  n::::n    n::::n
R::::::R     R:::::R  ee:::::::::::::e  M::::::M               M::::::M oo:::::::::::oo   n::::n    n::::n
RRRRRRRR     RRRRRRR    eeeeeeeeeeeeee  MMMMMMMM               MMMMMMMM   ooooooooooo     nnnnnn    nnnnnn
  
					---> ReMon, Remote Monitor <---

Istruzioni:

aprire una shell bash, e posizionare il prompt all'interno della cartella "project".
Eseguire le seguenti azioni:

- Lanciare il Server:

	python src/Client -s -c config.ini
	
	seguire le istruzioni a video per l'inserimento dei dati di login

	attendere che compaia la scritta : "### ProbeManager server ready."

- Lanciare il Client:

	python src/Client -g -c config.ini

	per impostare i parametri di monitoraggio andare in:
	Menu -> Impostazioni -> Configurazione
	(i settaggi di default sono già presenti, ma sono modificabili a piacere)
	una volta terminato premere "Conferma" per rendere effettivi i valori immessi, 
	eventualmente si può scegliere di salvare le impostazioni su di un file differente da quello 
	iniziale

	per avviare il monitoraggio andare in:
	Menu -> Monitor -> Avvia
	
	quando si desidera interrompere il monitoraggio è sufficente chiudere la finestra principale del
	programma, il segnale di chiusura verrà propagato automaticamente anche al Server ed alle Probes

--------------------------------------------------------------------------------
Variazioni:

Se si desidera lanciare il programma in locale basterà aggiungere l'opzione "-l" alle chiamate python
le chiamate risulteranno ad esempio:
	Per il Server			python src/Client.py -s -l -c config.ini
	Per il Client			python src/Client.py -g -l -c config.ini

Se non si vuole indicare un file di configurazione specifico ed utilizzare quello standard sarà sufficente
omettere l'opzione "-c nomefile" nelle chiamate python, che risulteranno ad esempio:
	Per il Server			python src/Client.py -s
	Per il Client			python src/Client.py -g

Se si desidera utilizzare l'opzione autostart per lanciare automaticamente sia il server che il client
nella stessa macchina, la chiamata diviene unica ed è ad esempio:
					python src/Client.py -a -l
Questo comando richiede che il file hosts sia già stato configurato per l'utilizzo in locale.

Se si vuole richiamare l'help per l'invocazione del programma basterà specificare l'opzione "-h" nelle
chiamate principali di python, per esempio:
	Per il Server			python src/Server.py -h
	Per il Client			python src/Client.py --help

--------------------------------------------------------------------------------
Gerarchia dei Menù:

:Monitor
 ::::::: Avvia
	Da inizio alla raccolta dei dati di monitoraggio e crea i grafici.
 ::::::: Istantanea Grafici
	Raccoglie tutti i grafici dentro ad un archivio posizionato nella cartella
	extra/UserOutput con il nome SnapshotYYYYMMDD-hhmm.tar dove:
		YYYY = anno corrente
		  MM = mese corrente
		  DD = giorno corrente
		  hh = ora attuale
		  mm = minuti attuali
 ::::::: Mostra Legenda
	Visualizza una finestra secondaria che mostra la corrispondenza tra
	nomi delle Probe e colori utilizzati nei grafici.

:Impostazioni
 :::::::::::: Configurazione
	Apre una finestra secondaria che permette di regolare i parametri del
	monitoraggio e li scrive nel ini file indicato in fondo alla finestra
	stessa, se non si specifica un percorso sarà salvato in extra/UserOutput.
 :::::::::::: Risveglia Sonde
	Fa riattivare o rimpiazza le sonde riconosciute come ZOMBIE, prelevando
	i nomi dei possibili host dal file extra/fabric/host.txt
 :::::::::::: Carica Sonda
	Apre una finestra secondaria per inviare un Carico di lavoro (per la
	CPU, la MEM od entrambe) in modo da poter visualizzare il picco di lavoro
	nei relativi grafici. Viene considerata una singola Probe alla volta.

:Help
 :::: Documentazione
	Apre la documentazione creata con Sphinx nel browser predefinito.
 :::: About
	Visualizza il dialog contenente le informazioni circa la versione del
	programma, l'autore, la licenza ed il sito web.

--------------------------------------------------------------------------------
Altri tool:

Se si vuole invece lanciare la suite di testing, digitare:
	python test/TestSuite.py

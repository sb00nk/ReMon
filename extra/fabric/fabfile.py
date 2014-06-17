from fabric.api import *

env.skip_bad_hosts = True
env.warn_only = True
env.parallel = True
env.timeout = 5
env.eagerly_disconnect = True

@parallel
def load_probes():
	run("mkdir -p ~/Monitor/src")
	run("mkdir -p ~/Monitor/extra/modules/psutil")
	put("../../src/Probe.py", "~/Monitor/src/Probe.py")
	put("../modules/psutil/*", "~/Monitor/extra/modules/psutil/")	

@parallel
def start_probes():
	run("python ~/Monitor/src/Probe.py")

@parallel
def clean():
	run("rm -r ~/Monitor")

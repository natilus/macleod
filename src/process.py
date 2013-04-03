import os, signal, time, subprocess, logging, re
import process, filemgt
import multiprocessing
from multiprocessing import Queue
from multiprocessing import Event

class ReasonerProcess(multiprocessing.Process):
	
	def __init__(self, command, result_queue, log_queue):
		multiprocessing.Process.__init__(self)

		self.command = command
		self.result_queue = result_queue
		self.log_queue = log_queue
		self.exit = multiprocessing.Event()
		self.done = multiprocessing.Event()

	def isDone (self):
		return self.done.is_set()

	def shutdown (self):
		record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.DEBUG, None, None, "RECEIVED ABORT SIGNAL: "  + self.name + ", command = " + self.command, None, None))
		self.log_queue.put(record)
		self.exit.set()
		
	def terminate (self):
		record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "TERMINATING: " + self.name + ", command = " + self.command, None, None))
		self.log_queue.put(record)
		self.shutdown()
		time.sleep(1)
		multiprocessing.Process.terminate (self)
				
	def run (self):
		record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "STARTING: " + self.name + ", command = " + self.command, None, None))
		self.log_queue.put(record)
		sp = process.startSubprocess(self.command, True)
		while sp.poll() is None and not self.exit.is_set():		
			#logging.getLogger(__name__).info("WAITING: " + self.command)
			time.sleep(1)
		if self.exit.is_set():
			# interrupted
			record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.DEBUG, None, None, "ABORTING: "  + self.name + ", command = " + self.command, None, None))
			self.log_queue.put(record)
#			print "RECEIVED ABORT SIGNAL"
			(p, stdoutdata) = process.terminateSubprocess(sp)
			if stdoutdata:
				stdoutdata = re.sub(r'[^\w]', ' ', stdoutdata)
				stdoutdata = ' '.join(stdoutdata.split())
				record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "STDOUT from "  + self.name + ": " + str(stdoutdata), None, None))
				self.log_queue.put(record)
#			(stdoutdata, _) = sp.communicate()
#			if stdoutdata:
#				print stdoutdata.__class__.__name__
#				stdoutdata = re.sub(r'[^\w]', ' ', stdoutdata)
#				stdoutdata = ' '.join(stdoutdata.split())
#				record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "STDOUT from "  + self.name + ": " + str(stdoutdata), None, None))
#				self.log_queue.put(record)
			self.result_queue.put((self.command, sp.returncode, stdoutdata))
			record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "ABORTED: "  + self.name + ", command = " + self.command, None, None))
			self.log_queue.put(record)
			#print "+++ HERE +++"
			self.done.set()
			return True
		# finished
		stdoutdata = sp.stdout.read()
		if sp.stderr:
			stdoutdata += sp.stderr.read()
		stdoutdata = re.sub(r'[^\w]', ' ', stdoutdata)
		stdoutdata = ' '.join(stdoutdata.split())
		record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "STDOUT from "  + self.name + ": " + str(stdoutdata), None, None))
		self.log_queue.put(record)
		self.result_queue.put((self.command, sp.returncode, stdoutdata))
		record = filemgt.format(logging.LogRecord(self.__class__.__name__, logging.INFO, None, None, "FINISHED: "  + self.name + ", command = " + self.command, None, None))
		self.log_queue.put(record)
		self.done.set()
		return True
	
		

def startSubprocess(command, piping = False):
	"""Start a new subprocess, but does not wait for the subprocess to complete. 
	This method uses the os.setsid in Linux, which is not available in Windows"""
	if os.name == 'nt':
		# Windows
		if piping:
			#logging.getLogger(__name__).debug(command.split()[0] +  "redirecting STDERR to STDOUT")
			p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		else:
			#logging.getLogger(__name__).debug(command.split()[0] + " -- no piping")
			#logging.getLogger(__name__).info("STARTING: " + command)
			p = subprocess.Popen(command, shell=True, stderr=subprocess.STDOUT)
	else:
		# Linux (and others)
		if piping:
			p = subprocess.Popen(command, shell=True, preexec_fn=os.setsid, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		else:
			logging.getLogger(__name__).info("STARTING: " + command)
			p = subprocess.Popen(command, shell=True, preexec_fn=os.setsid, close_fds=True)
	
	#print p.__class__
	return p


def startInteractiveProcess():
	"""Start a process whose output (STDOUT) is written to the return value."""
	if os.name == 'nt':
		# Windows
		p = subprocess.Popen(command, shell=True, close_fds=True, 
								stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	else:
		# Linux (and others)
		p = subprocess.Popen(command, shell=True, close_fds=True, preexec_fn=os.setsid, 
								stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	return p
	
			

def executeSubprocess(command, piping = False):
	"""start a new subprocess and wait for it to terminate"""
	p = process.startSubprocess(command, piping=piping)
	p.wait()
	time.sleep(0.1)
	return p
		

def terminateSubprocess (process):
	"""terminate a sub process."""
	def terminate_win (process):
		p = startSubprocess("taskkill /F /T /PID " + str(process.pid), piping=True)
		(stdout, _ ) = process.communicate()
		(stdout2, _ ) = p.communicate()
		#print "TYPE = " + stdout.__class__.__name__
		time.sleep(0.2)
		if not stdout:
			stdout = ""
		if not stdout2:
			stdout2 = ""
		re.sub(r'[^\w]', '', stdout)
		stdoutdata = ' '.join(stdout.split())
		return (process.returncode, stdout+stdout2)  

	def terminate_nix (process):
		#os.kill(process.pid, signal.SIGINT)
		return_value = process.terminate()
		(stdout, _ ) = process.communicate()
		if process.is_alive():
			return_value = os.kill(process.pid, signal.SIGINT)
			time.sleep(0.2)
		if not stdout:
			stdout = ""
		re.sub(r'[^\w]', '', stdout)
		stdoutdata = ' '.join(stdout.split())
		return (return_value, stdoutdata)

		#return os.waitpid(process.pid, os.WNOHANG)

	terminate_default = terminate_nix
	
	handlers = {
		"nt": terminate_win, 
		"linux": terminate_nix
	}

	return handlers.get(os.name, terminate_default)(process)


def raceProcesses (reasoners):
	"""run a set of theorem provers and a set of model finders in parallel.
	If one terminates successfully, all others are immediately terminated.
	
	Keyword arguments:
	provers -- dictionary of theorem provers to execute where the key is the command and the value a set of return codes that indicate success.
	modelfinders -- dictionary of modelfinders to execute where the key is the command and the value a set of return codes that indicate success.
	"""
	time.sleep(0.1)
	
	results = Queue()

	processLogs = []
	
	reasonerProcesses = []
	
	# start all processes
	for r in reasoners:
		log = Queue()
		p = ReasonerProcess(r.getCommand(),results,log)
		reasonerProcesses.append(p)
		processLogs.append(log)
		#p = multiprocessing.Process(name=r.identifier, target=executeSubprocess, args=(r.getCommand(),results,))
		p.start()
		time.sleep(0.1)
		#i += 1

	num_running = len(reasonerProcesses)
	success = False
	
	time.sleep(0.1)
	#active=multiprocessing.active_children()
	while num_running>0:	
		while results.empty():
			merged_log = merge(processLogs)
			if len(merged_log)>0:
				filemgt.add_to_subprocess_log(merged_log)
				#print "\n\n" + l + "\n\n"
			time.sleep(1.0)
			#active=multiprocessing.active_children()	# poll for active processes
		# at least one process has terminated
		while not results.empty():
			num_running += - 1
			(name, code, stdout) = results.get()
			logging.getLogger(__name__).debug("STDOUT from " + name.split()[0] + ": " + ("".join([s.strip("\n") for s in stdout])))
			#name = proverDict[name]		# mapping the number back to the real command name
			#print str(name) + " returned with " + str(code)
			
			#print name + " finished; positive returncodes are " + str(provers[name])
			r = reasoners.getByCommand(name)
			r.setReturnCode(code)
			#print str(r.return_code) + " ++++ CODES: " + str(r.positive_returncodes)
			if r.terminatedSuccessfully():
				success = True
				if r.isProver():
					logging.getLogger(__name__).info(name + " found a proof/inconsistency")
				else:
					logging.getLogger(__name__).info(name + " found a counterexample/model")
				
		if success:
			for p in reasonerProcesses:
				logging.getLogger(__name__).debug("SENDING ABORT SIGNAL to " + p.command)				
				p.shutdown()
				while not p.isDone():
					time.sleep(0.1)
			logging.getLogger(__name__).debug("Final processing of subprocess log queue")
			time.sleep(0.1)
			merged_log = merge(processLogs)
			filemgt.add_to_subprocess_log(merged_log)
			merged_log = []
		break

	return reasoners

		#num_running = len(active)
#		print(str(num_running) + " active processses")
#		time.sleep(0.5)
#		for p in reasonerProcesses:
#			if p not in active:
#				print p
#				if p.returncode in p.provers[p.name()]:
#					success = True
#		for p in finderProcesses:
#			if p not in active:
#				print p
#				if p.returncode in p.finders[p.name()]:
#					success = True

#	for r in reasonerProcesses:
#		provers[r.name()]=r.returncode
#	for finder in finderProcesses:
#		modelfinders[finder.name()]=find.returncode

def merge(logs):
	""" simple sort algorithm for merging the log queues from multiple processes"""

	#for log in logs:
	#	if not log.empty():
	#		print "Log ENTRY found\n\n"
	
	merged_log = []

	# combine everything into a single list
	for i in range(0,len(logs)):
		while not logs[i].empty():
			merged_log.append(logs[i].get())
	return sorted(merged_log)

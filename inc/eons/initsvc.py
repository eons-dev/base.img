import eons
import os
import time
import logging
from pathlib import Path

class initsvc(eons.StandardFunctor):
	def __init__(this, name="Initialize Services"):
		super().__init__(name)

		this.functionSucceeded = True
		this.enableRollback = False

		this.optionalKWArgs["retry_count"] = 10
		this.optionalKWArgs["retry_wait"] = 1


	def GetServiceNameFromFileName(this, file):
		fileSplit = file.split("_")
		if (len(fileSplit) > 1 and fileSplit[0].isnumeric()):
			file = "_".join(fileSplit[1:])
		return file


	def WriteRCConf(this):
		rcconf = this.CreateFile("/etc/rc.conf")
		rcconf.write("rc_logger=\"YES\"\n")


	def WriteRCService(this, name, command, dependencies=[]):
		# command_name = command.split(" ")[0]
		# command_args = " ".join(command.split(" ")[1:])
		command_args = command
		if (command_args.endswith('\n')):
			command_args = command_args[:-1]

		command_args.replace('"', '\\"')
		command_args.replace("'", "\\'")
		command_args = f"-c '. /.env; rm -f /var/run/{name}.exitcode; {command_args}; echo $? > /var/run/{name}.exitcode'"

		kvs = {
			"name": name,
			"command": "/bin/bash",
			"command_args": command_args,
			"command_user": "root:root",
			"command_background": "true",
			"pidfile": f"/var/run/{name}.pid",
			"output_log": f"/var/log/{name}.out.log",
			"error_log": f"/var/log/{name}.err.log",
		}
		
		serviceFilePath = f"/etc/init.d/{name}"
		serviceFile = this.CreateFile(serviceFilePath)
		serviceFile.write(f"#!/sbin/openrc-run\n")
		for key, value in kvs.items():
			serviceFile.write(f"{key}=\"{value}\"\n")

		serviceFile.write(f'''
status() {{
	if [ -f /var/run/{name}.exitcode ]; then
		return $(cat /var/run/{name}.exitcode)
	fi
	pid=$(cat /var/run/{name}.pid)
	if [ -z "$pid" ]; then
		return ps -p $pid > /dev/null 2>&1
	fi
	return 1
}}
''')

		if (len(dependencies)):
			serviceFile.write("depend() {\n")
			serviceFile.write("".join([f"\tafter {dep}\n" for dep in dependencies]))
			serviceFile.write("}\n")

		serviceFile.close()
		Path(serviceFilePath).chmod(0o755)

	
	def Function(this):
		this.WriteRCConf()

		launchFiles = sorted(os.listdir("/launch.d"))
		for i, file in enumerate(launchFiles):
			dependencies = []
			with open(f"/launch.d/{file}", "r") as f:
				if (i):
					dependencies.append(launchFiles[i-1])
				this.WriteRCService(this.GetServiceNameFromFileName(file), f.read(), dependencies=dependencies)
		
		# maybe necessary?
		# https://github.com/gliderlabs/docker-alpine/issues/437#issuecomment-667456518
		this.RunCommand("rc-status")

		for file in launchFiles:
			service = this.GetServiceNameFromFileName(file)
			this.RunCommand(f"rc-service {service} start")
			code = -1
			attempts = 1
			while code != 0:
				possibleExitCodeFile = f"/var/run/{service}.exitcode"
				if (os.path.exists(possibleExitCodeFile)):
					with open(possibleExitCodeFile, "r") as f:
						code = int(f.read())
				else:
					code = this.RunCommand(f"rc-service {service} status", raiseExceptions=False)
				
				if (code != 0):
					logging.debug(f"Waiting for {service} to start...")
					time.sleep(this.retry_wait)
				attempts += 1
				if (attempts >= this.retry_count):
					errorFile = f"/var/log/{service}.err.log"
					error = ""
					if (os.path.exists(errorFile)):
						with open(errorFile, "r") as f:
							error = f.read()
					raise Exception(f"Failed to start {service} after {attempts} attempts. Errors (if any): {error}")




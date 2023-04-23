import eons
import os

class initsvc(eons.StandardFunctor):
	def __init__(this, name="Initialize Services"):
		super().__init__(name)

		this.functionSucceeded = True
		this.enableRollback = False


	def WriteRCConf(this):
		rcconf = this.CreateFile("/etc/rc.conf")
		rcconf.write("rc_logger=\"YES\"\n")


	def WriteRCService(this, name, command, dependencies=[]):
		command_name = command.split(" ")[0]
		command_args = " ".join(command.split(" ")[1:])

		kvs = {
			"name": name,
			"command": command_name,
			"command_args": command_args,
			"command_user": "root:root",
			"command_background": "true",
			"pidfile": f"/var/run/{name}.pid",
			"output_log": f"/var/log/{name}.out.log",
			"error_log": f"/var/log/{name}.err.log",
		}
		
		serviceFile = this.CreateFile(f"/etc/init.d/{name}")
		serviceFile.write(f"#!/sbin/openrc-run\n")
		for key, value in kvs:
			serviceFile.write(f"{key}=\"{value}\"\n")

		if (len(dependencies)):
			serviceFile.write(f'''depend() {{
{"".join([f"    after {dep}\n" for dep in dependencies])}
}}
'''
		serviceFile.close()

	
	def Function(this):
		this.WriteRCConf()

		launchFiles = sorted(os.listdir("/launch.d"))
		for i, file in enumerate(launchFiles):
			dependencies = []
			with open(f"/launch.d/{file}", "r") as f:
				if (i):
					dependencies.append(launchFiles[i-1])
				this.WriteRCService(file, f.read(), dependencies=dependencies)
		
		# maybe necessary?
		# https://github.com/gliderlabs/docker-alpine/issues/437#issuecomment-667456518
		this.RunCommand("rc-status")

		for file in launchFiles:
			this.RunCommand(f"rc-service {file} start")


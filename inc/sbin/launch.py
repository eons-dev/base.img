#!/usr/bin/env python3

import eons

executor = eons.Executor()
executor()
executor.RegisterAllClassesInDirectory("/eons")

startup = [
	"initsvc",
]

for start in startup:
	executor.Execute(start)
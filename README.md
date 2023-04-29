# Base Image
This Docker image provides all standard utilities used in other eons and downstream images.

## Big

This image is big. It includes pip and other utilities that make development easy. You'll likely want to strip these when shipping your image to production.

For example, add to your dockerfile or ebbs script:
```
RUN apk del build-base py3-pip python3-dev
```

## Utilities

### Init System

Eons container images occasionally need to run multiple processes (e.g. a vpn connection and a service). Instead of having each image implement it's own means of doing this, we provide a standardized process through the use of [OpenRC](https://github.com/OpenRC/openrc). While this does necessitate larger images for all downstream workloads, any efficiency improvements, features, security patches, etc. made here will be applied to all downstream images. It is our opinion that Docker should support multiple entrypoints; however, we're happy to build our own hacks in lieu of official support (if this feature becomes available, someone please let us know!).

To facilitate an easier means of "just running something", we've added our own launch script that kicks off openrc & then tails the logs of all processes. This launch script does the heavy lifting of writing the openrc service files for you. However, you are, of course, free to write your own service files if you prefer. While doing so is not yet supported, it shouldn't be hard.

**IMPORTANT NOTE: Your commands must run in the foreground!**

It is okay if your command exits with status 0 (i.e. oneshots are supported).

The Launch Script provides a `/launch.d` directory. Any executable files (or symlinks) in this directory will be managed by the init system. You can use init.d standard numeric prefix notation to establish initialization order. Sorting occurs to the `sort` standard with locale setting `LC_ALL=C` (run `info sort` for all the details).

An example launch script could be the file `/launch.d/apache` with the contents:
```shell
apachectl -D FOREGROUND
```
Such a file gets stored in /etc/init.d/apache as:
```shell
name="apache"
command="apachectl"
command_args="-D FOREGROUND"
command_user="root:root"
command_background="true"
pidfile="/var/run/apache.pid"
output_log="/var/log/apache.out.log"
error_log="/var/log/apache.err.log"
```

We really want to try not to reinvent the wheel nor revisit old grudges. While developing this base.img, we do our best to keep in mind the goals and history of [init freedom](https://www.devuan.org/os/init-freedom).

### EBBS Docker Launch Directive

To take advantage of our init system in [EBBS](https://github.com/eons-dev/bin_ebbs), specify `launch` in the build json for your docker build step.
See the [EBBS Docker Builder](https://github.com/eons-dev/build_docker) for more info.

### EMI

[EMI](https://github.com/eons-dev/bin_emi) is the Eons package manager. Since we intend to use emi in all of our projects, it is best included here. As with everything we do, emi is configurable and modular, so you can make it work for you: the way you want.

### Honorable Mentions

#### Supervisor
[Supervisor](http://supervisord.org) is the [recommended way of running multiple processes in a Docker container](https://docs.docker.com/config/containers/multi-service_container/). However, it does not currently support dependencies and is not a suitable init system for PID 1.
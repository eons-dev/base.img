# Base Image
This Docker image provides all standard utilities used in other eons and downstream images.

## Utilities

### Supervisor

Eons Docker images occasionally need to run multiple processes (e.g. a vpn connection and a service). Instead of having each image implement it's own means of doing this, we provide a standardized process through the use of [Supervisor](http://supervisord.org). While this does necessitate larger images for all downstream workloads, any efficiency improvements, features, security patches, etc. made here will be applied to all downstream images. It is our opinion that Docker should support multiple entrypoints; however, we're happy to build our own hacks in lieu of official support (if this feature becomes available, someone please let us know!).

[Supervisor](http://supervisord.org) is the [recommended way of running multiple processes in a Docker container](https://docs.docker.com/config/containers/multi-service_container/). Instead of relying on Supervisor's `[include]` directive, we've shimmed in a bash script that creates the Supervisor config on container startup. This allows us to have a standard process for creating all dependent images while retaining the ability to swap out Supervisor with a different init system at some later time.

The Launch Script provides a `/launch.d` directory. Any executable files (or symlinks) in this directory will be managed by Supervisor. You can use init.d standard numeric prefix notation to establish initialization order. Sorting occurs to the `sort` standard with locale setting `LC_ALL=C` (run `info sort` for all the details).

An example launch script could be the file `/launch.d/apache` with the contents:
```shell
apachectl -D FOREGROUND
```
Such a file gets stored in the supervisord.conf as:
```shell
[program:apache]
command=apachectl -D FOREGROUND
```

The general form is (per the launch file) is:
```shell
[program:$file]
command=$(cat /launch.d/$file)
```

This means you can add other Supervisor configs on newlines below the command (though this is untested).

We really want to try not to reinvent the wheel nor revisit old grudges. While developing this, we will do our best to keep in mind the goals and history of [init freedom](https://www.devuan.org/os/init-freedom).
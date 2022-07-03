# Base Image
This Docker image provides all standard utilities used in other eons and downstream images.

## Utilities

### Supervisor

Eons Docker images occasionally need to run multiple processes (e.g. a vpn connection and a service). Instead of having each image implement it's own means of doing this (which would produce smaller images), we provide a standardized process here instead. Any efficiency improvements, features, security patches, etc. made here will be applied to all downstream images. It is our opinion that Docker should support multiple entrypoints; however, we're happy to build our own hacks in lieu of official support (if this feature becomes available, someone please let us know!).

[Supervisor](http://supervisord.org) is the [recommended way of running multiple processes in a Docker container](https://docs.docker.com/config/containers/multi-service_container/). However, Supervisor requires a single configuration file. This obviously doesn't scale when each downstream client needs to provide the services from its base image in addition to its own. To remedy this, we've shimmed in a bash script that creates the Supervisor config on container startup.

The Launch Script provides a `/launch.d` directory. Any executable files (or symlinks) in this directory will be managed by Supervisor. You can use init.d standard numeric prefix notation to establish initialization order. Sorting occurs to the `sort` standard with locale setting `LC_ALL=C` (run `info sort` for all the details).

We really want to try not to reinvent the wheel nor revisit old grudges. While developing this, we will do our best to keep in mind the goals and history of [init freedom](https://www.devuan.org/os/init-freedom).
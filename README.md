# Base Image
This Docker image provides all standard utilities used in other eons and downstream images.

## Big

This image is big. It includes pip and other utilities that make development easy. You'll likely want to strip these when shipping your image to production.

For example, add to your dockerfile or ebbs script:
```
RUN apk del build-base py3-pip python3-dev
```

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

### EBBS Docker Launch Directive

To take advantage of our Supervisor init system in [EBBS](https://github.com/eons-dev/bin_ebbs), specify `launch` in the build json for your docker build step.
See the [EBBS Docker Builder](https://github.com/eons-dev/build_docker) for more info.

### EMI

[EMI](https://github.com/eons-dev/bin_emi) is the eons package manager. Since we intend to use emi in all of our projects, it is best included here. As with everything we do, emi is configurable and modular, so you can make it work for you: the way you want.

Unfortunately, EMI is currently built in python (as is the rest of our E___ products). Once [Biology](https://develop.bio) is stable, we will rewrite emi to remove the python dependency in this base image.
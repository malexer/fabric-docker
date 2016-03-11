fabric-docker
=============

Docker-engine command-line tool wrapper for Fabric.

Can be used both in local and remote modes (via subprocess or ssh).

Method names and options try to use the same names as related docker-engine
commands and options.

So, it is mainly a helper to write:

.. code-block:: python

    docker.ps(all=True, size=True)

instead of:

.. code-block:: python

    run('docker ps --all --size')

With some nice use cases:

.. code-block:: python

    # remove dangling images "<none>:<none>"
    docker.rmi(docker.none_images())

    # remove images by some filter
    images = [
        image['image id'] for image in docker.images()
        if image['tag'] != 'latest'
    ]
    docker.rmi(images)


Requirements
------------

* Docker (local or remote - depending the mode you use)
* Fabric
* pyyaml


Supported commands
------------------

Only limited set of commands and options are supported now:

* cli - run arbitrary Docker command. i.e. ``docker.cli('ps -a')``
* images
* ps
* restart
* rm
* rmi
* run - limited set of options
* start
* stop
* version
* none_images - helper method to get "dangling" images


Usage
-----

Create instance to use locally with sudo:

.. code-block:: python

    import fabric_docker

    docker = fabric_docker.DockerCli(local=True, use_sudo=True)
    # any command can override this default settings by suppling
    # "local" and "sudo" key-value arguments

List all local containers:

.. code-block:: python

    docker.ps(all=True)

Remove latest container:

.. code-block:: python

    docker.rm(docker.ps(latest=True))

List remote images (override default local flag):

.. code-block:: python

    docker.images(no_truncate=True, local=False)

Run remote container:

.. code-block:: python

    docker.run(
        detach=True,
        restart='always',
        publish={'8080':'80'},
        volume={'/host/dir': '/container/dir', '/host/dir2': '/container/dir2'},
        name='name_of_container',
        image='image_name:tag',
    )

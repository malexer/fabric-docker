from fabric import api
from fabric.context_managers import settings
from fabric.utils import warn
import yaml

from .parse import parse_table
from .util import assemble_flag_arguments, assemble_mapping_arguments, \
    assemble_multivalue_arguments


class ParameterError(Exception):
    pass


class _DockerWrapper(object):
    """Low-level helper methods for wrapping docker-engine command-line tool.
    """

    def _run(self, command, local=None, use_sudo=None, capture=False):
        local = local if local is not None else self._local
        use_sudo = use_sudo if use_sudo is not None else self._use_sudo

        with settings(warn_only=True):
            if local:
                prefix = 'sudo ' if use_sudo else ''
                output = api.local(prefix + command, capture=capture)
            else:
                execute = api.sudo if use_sudo else api.run
                output = execute(command)

            return output if output.succeeded else output.stderr


class DockerCli(_DockerWrapper):
    """Fabric wrapper for docker-engine command-line tool.

    Supports both remote (default) and local modes, with or without sudo.

    .. note::
        Every command can override local/sudo mode by using arguments ``local``
        and ``use_sudo``.
    """

    def __init__(self, local=False, use_sudo=False):
        self._local = local
        self._use_sudo = use_sudo

    def _start_stop(self, cmd, container, time=None, **kwargs):
        args = ''
        if time is not None:
            if not isinstance(time, int):
                raise ParameterError('"time" argument is not of integer value')
            args = '--time=%d' % time

        container = assemble_multivalue_arguments(container)

        cmd = '{command} {arg} {containers}'.format(
            command=cmd, arg=args, containers=container)

        return self.cli(cmd, **kwargs)

    def cli(self, command_and_args, capture=True, **kwargs):
        """Execute arbitrary command with custom arguments.

        :param command_and_args: command with args, i.e. "ps -q -l"
        :type command_and_args: str
        """

        cmd = 'docker %s' % command_and_args
        return self._run(cmd, capture=capture, **kwargs)

    # Standard docker commands

    def images(self, all=False, quiet=False, no_truncate=False, filter=None,
               **kwargs):
        """docker images - list images"""

        args = assemble_flag_arguments({
            '--all': all,
            '--quiet': quiet,
            '--no-trunc': no_truncate,
        })

        if filter is not None:
            args += ' --filter="%s"' % filter

        output = self.cli('images %s' % args, **kwargs)

        if quiet:
            return str.splitlines(output)
        else:
            return list(parse_table(output))

    def ps(self, all=False, size=False, quiet=False, no_truncate=False,
           latest=False, **kwargs):
        """docker ps - list containers."""

        args = assemble_flag_arguments({
            '--all': all,
            '--size': size,
            '--quiet': quiet,
            '--no-trunc': no_truncate,
            '--latest': latest,
        })

        output = self.cli('ps %s' % args, **kwargs)

        if quiet:
            result = str.splitlines(output)
        else:
            result = list(parse_table(output))

        if latest:
            if result:
                return result[0]
            else:
                return None
        else:
            return result

    def restart(self, container, time=None, **kwargs):
        """docker restart - restart running container(s).

        :param container: container(s) id
        :type container: str or list
        """

        return self._start_stop('restart', container, time, **kwargs)

    def rm(self, container, force=False, link=False, volumes=False, **kwargs):
        """docker rm - remove container(s)"""

        args = assemble_flag_arguments({
            '--force': force,
            '--link': link,
            '--volumes': volumes,
        })
        container = assemble_multivalue_arguments(container)

        output = self.cli('rm %s %s' % (args, container), **kwargs)

        deleted = [line for line in str.splitlines(output) if ' ' not in line]
        messages = [line for line in str.splitlines(output) if ' ' in line]

        for msg in messages:
            warn('Docker: %s' % msg)

        return deleted

    def rmi(self, image, force=False, **kwargs):
        """docker rmi - remove image(s)"""

        args = assemble_flag_arguments({'--force': force})
        image = assemble_multivalue_arguments(image)

        output = self.cli('rmi %s %s' % (args, image), **kwargs)

        deleted = [
            line.split(':')[2]
            for line in str.splitlines(output)
            if line.startswith('Deleted:')
        ]
        messages = [
            line for line in str.splitlines(output)
            if not line.startswith('Deleted:')
        ]

        for msg in messages:
            warn('Docker: %s' % msg)

        return deleted

    def run(self, image, raw_options=None, command=None, detach=False,
            name=None, publish=None, restart=None, rm=None, volume=None,
            **kwargs):
        """docker run - run command in a new container.

        :param image: image name
        :param raw_options: supply any supported options as a custom string
        :param command: command which is used to start container
        :param detach: run container in background, id will be returned
        :param name: assign name to container
        :param publish: dict of port mappings {host: container, ...}
        :param restart: restart policy
        :param rm: autoremove on container exit
        :param volume: dict of mount mappings {host: container, ...}
        """

        flag_args = assemble_flag_arguments({
            '--detach': detach,
            '--rm': rm,
        })

        mapping_args = assemble_mapping_arguments({
            '-p': publish,
            '-v': volume,
        })

        name = '--name=%s' % name if name else ''
        restart = '--restart=%s' % restart if restart else ''

        cmd = 'run {options} {other_options} {image} {command}'.format(
            options=' '.join([flag_args, mapping_args, name, restart]),
            other_options=raw_options or '',
            image=image,
            command=command or '',
        )
        output = self.cli(cmd, **kwargs)

        if detach:
            return output

    def start(self, container, **kwargs):
        """docker start - start stopped container(s).

        :param container: container(s) id
        :type container: str or list
        """

        return self._start_stop('start', container, **kwargs)

    def stop(self, container, time=None, **kwargs):
        """docker stop - stop running container(s).

        :param container: container(s) id
        :type container: str or list
        """

        return self._start_stop('stop', container, time, **kwargs)

    def version(self, **kwargs):
        """docker version - get Docker version"""

        output = self.cli('version', **kwargs)
        return yaml.safe_load(output)

    # usefull helpers

    def none_images(self):
        return self.images(quiet=True, filter='dangling=true')

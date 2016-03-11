def assemble_flag_arguments(args):
    """Assemble dict of flag arguments into string."""

    return ' '.join([name for name, use in args.items() if use])


def assemble_multivalue_arguments(argument):
    """Assemble single string or list of strings into string."""

    if isinstance(argument, (list, tuple)):
        argument = ' '.join(argument)

    return argument


def assemble_mapping_arguments(arguments):
    """Assemble mapping arguments into string.

    :param arguments: mapping arguments with values. Example:
                        {
                            '-v': {
                                '/host/dir': '/container/dir',
                                '/host/dir2': '/container/dir2',
                                ...
                            },
                            '-p': {...},
                            ...
                        }
    :return: string with all unfolded mapping arguments
    """

    string_arguments = []
    for name, mappings in arguments.items():
        if isinstance(mappings, dict):
            string_arguments.append(
                ' '.join([
                    '{0} {1}:{2}'.format(name, host, container)
                    for host, container in mappings.items()
                ])
            )

    return ' '.join(string_arguments)

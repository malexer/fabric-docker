from operator import itemgetter


TWO_WORDS_FIELD_NAMES = (
    'CONTAINER ID',
    'IMAGE ID',
)


def get_fields(line):
    """Parse header line and extract field names, start & end positions index.
    """

    def get_field_start_positions(field_names):
        start_positions = [line.index(f) for f in field_names]

        fields = zip(field_names, start_positions)
        fields = sorted(fields, key=itemgetter(1))

        field_names, start_positions = zip(*fields)
        return field_names, start_positions

    header = line
    field_names = []

    for name in TWO_WORDS_FIELD_NAMES:
        if name in header:
            field_names.append(name)
            header = header.replace(name, '', 1)

    field_names += header.split()

    field_names, field_start_positions = get_field_start_positions(field_names)

    field_positions = zip(
        field_start_positions,
        list(field_start_positions[1:]) + [None]
    )
    field_names = map(str.lower, field_names)

    return dict(zip(field_names, field_positions))


def parse_table(table_output):
    """Parse table output from Docker CLI into list of dicts.

    :param table_output: text table from docker-engine output.
    :type table_output: str
    :return: table with rows as dicts.
    :rtype: list
    """

    lines = str.splitlines(table_output)

    if len(lines) < 2:
        raise StopIteration()

    fields = get_fields(lines[0])

    for line in lines[1:]:
        item = {
            field: line[pos_start:pos_stop].rstrip()
            for field, (pos_start, pos_stop) in fields.items()
        }
        yield item

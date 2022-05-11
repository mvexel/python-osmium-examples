import osmium
import click
from datetime import datetime
from pandas import DataFrame

MAIN_HIGHWAY_KEYS = [
    'motorway',
    'motorway_link',
    'trunk',
    'trunk_link',
    'primary',
    'primary_link',
    'secondary',
    'secondary_link', 
    'tertiary',
    'tertiary_link']


class MapperCounterHandler(osmium.SimpleHandler):

    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.mappers = []

    def way(self, w):
        if 'highway' in w.tags and any(elem in w.tags['highway'] for elem in MAIN_HIGHWAY_KEYS):
            if w.user not in self.mappers:
                self.mappers.append(w.user)


class HighwayCounterHandler(osmium.SimpleHandler):

    def __init__(self, mappers, all_versions, after, before):
        osmium.SimpleHandler.__init__(self)
        self.result = DataFrame(0, columns=MAIN_HIGHWAY_KEYS, index=mappers)
        self._all_versions = all_versions
        self._way_ids = []
        self.after = after
        self.before = before

    def way(self, w):
        if 'highway' in w.tags and w.tags['highway'] in MAIN_HIGHWAY_KEYS:
            if self.after and self.after > w.timestamp:
                return
            if self.before and self.before < w.timestamp:
                return
            if self._all_versions or w.id not in self._way_ids:
                self.result.at[w.user, w.tags['highway']] += 1
                self._way_ids.append(w.id)

@click.command()
@click.option('-a', '--all-versions', is_flag=True, help='Count all previous versions (if reading a full history file)')
@click.option('--before', default=None, is_flag=False, help='Only record changes before this date/time (ISO 8601 format). Example: --before "2022-01-01"')
@click.option('--after', default=None, is_flag=False, help='Only record changes after this date/time (ISO 8601 format). Example: --after "2020-01-01"')
@click.argument('osmfile', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
def cli(osmfile, output, all_versions, after, before):
    if after:
        after = datetime.fromisoformat(after)
        # Convert the argment to local time if no timezone is passed.
        if after.tzinfo is None or after.tzinfo.utcoffset(after) is None:
            after = after.astimezone()
    if before:
        before = datetime.fromisoformat(before)
        # Convert the argment to local time if no timezone is passed.
        if before.tzinfo is None or before.tzinfo.utcoffset(before) is None:
            before = before.astimezone()
    click.echo("processing {}".format(osmfile))
    click.echo("Stage 1: Counting Unique Highway Mappers")
    mch = MapperCounterHandler()
    mch.apply_file(osmfile)
    click.echo("Done, {} mappers counted.".format(len(mch.mappers)))

    click.echo("Stage 2: Counting Highway Edits")
    hch = HighwayCounterHandler(mappers=mch.mappers, all_versions=all_versions, after=after, before=before)
    hch.apply_file(osmfile)
    hch.result.to_csv(output)
    click.echo("Done. Result written to {}".format(
        output
    ))

if __name__ ==  '__main__':
    cli()

import osmium
import click
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
    
    def __init__(self, mappers, all_versions):
        osmium.SimpleHandler.__init__(self)
        self.result = DataFrame(0, columns=MAIN_HIGHWAY_KEYS, index=mappers)
        self.all_versions = all_versions
        self.way_ids = []
        self.edits_count = 0

    def way(self, w):
        if 'highway' in w.tags and w.tags['highway'] in MAIN_HIGHWAY_KEYS:
            # click.echo("id {} version {} visibe {} tags {}".format(w.id, w.version, w.visible, w.tags['highway']))
            if self.all_versions or w.id not in self.way_ids:
                self.result.at[w.user, w.tags['highway']] += 1
                self.way_ids.append(w.id)
                self.edits_count += 1                

@click.command()
@click.option('-a', '--all-versions', is_flag=True, help='Count all previous versions (if reading a full history file)')
@click.argument('osmfile', type=click.Path(exists=True))
@click.argument('output', type=click.Path())
def cli(osmfile, output, all_versions):
    click.echo("processing {}".format(osmfile))
    click.echo("Stage 1: Counting Unique Highway Mappers")
    mch = MapperCounterHandler()
    mch.apply_file(osmfile)
    click.echo("Done, {} mappers counted.".format(len(mch.mappers)))

    click.echo("Stage 2: Counting Highway Edits")
    hch = HighwayCounterHandler(mappers=mch.mappers, all_versions=all_versions)
    hch.apply_file(osmfile)
    click.echo("Done. {} highway edits counted. Result written to {}".format(
        hch.edits_count,
        output
    ))
    hch.result.to_csv(output)

if __name__ ==  '__main__':
    cli()
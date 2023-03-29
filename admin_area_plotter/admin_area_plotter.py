import osmium
import click
import shapely
from shapely.plotting import plot_polygon, plot_points
from matplotlib import pyplot as plt
from admin_area_plotter.utils import get_boundary_nodes_from_members


class AdminLevelArea:
    def __init__(self, name):
        self.name = name
        self.members = []
        self.polygon = None

class AdminLevelManager:
    '''
    This class is a wrapper to get geometries from a osm file by iterating over the file two times.
    To actually get geometries from osm without the area call the first iteration needs to extract all the needed relation object and cache the reference of the members (ways).
    In the second iteration the saved references are used to extract all the nodes that actually define the geometry.
    '''
    def __init__(self, admin_level_list):
        self.adlr = AdminLevelRelationHandler(admin_level_list)
        self.adlw = AdminLevelWaysHandler()
        self.polygons = None

    def run_on_file(self, file):
        click.echo("Stage 1: Run osm handler to get all relations with the admin_level tag.")
        self.adlr.apply_file(file, locations=True)
        click.echo("Stage 2: Run osm handler again to get the nodes from all ways which were referenced in the relations with the admin_level tag.")
        self.adlw.members = self.adlr.members
        self.adlw.admin_level_areas = True
        self.adlw.apply_file(file, locations=True)

    def assemble_shapely_polygons(self):
        for admin_area in self.adlr.admin_level_areas:
            try:
                nodes = get_boundary_nodes_from_members(self.adlw.nodes, admin_area.members)
            except KeyError as e:
                # sometimes the members (ways) of a relation go over borders.
                # so the polygon shape is not fully inside of the loaded map.
                continue
            admin_area.polygon = shapely.Polygon(nodes)

class AdminLevelWaysHandler(osmium.SimpleHandler):
    def __init__(self):
        super(AdminLevelWaysHandler, self).__init__()
        self.nodes = {}
        self.members = set()

    def way(self, w):
        if w.id in self.members and not self.nodes.get(w.id):
            for node in w.nodes:
                self.nodes.setdefault(w.id, []).append((node.x, node.y))

class AdminLevelRelationHandler(osmium.SimpleHandler):
    def __init__(self, admin_level_list):
        super(AdminLevelRelationHandler, self).__init__()
        self.admin_level_areas = []
        self.admin_level_list = admin_level_list
        self.members = set()

    def relation(self, r):
        if 'admin_level' in r.tags and r.tags['admin_level'] in self.admin_level_list:
            admin_level_area = AdminLevelArea(r.tags["name"])
            for member in r.members:
                if member.role == 'outer':
                    self.members.add(member.ref)
                    admin_level_area.members.append(member.ref)
            self.admin_level_areas.append(admin_level_area)

@click.command()
@click.argument('osmfile', type=click.Path(exists=True))
def cli(osmfile):
    click.echo("processing {}".format(osmfile))
    alm = AdminLevelManager(['8'])
    alm.run_on_file(osmfile)
    click.echo("Stage 3: Try to assemble shapely polygons.")
    alm.assemble_shapely_polygons()
    fig = fig = plt.figure(1, dpi=90)
    ax = fig.add_subplot(111)
    ax = plt.gca()
    plt.axis('off')
    plt.title("Liechtenstein")
    ax.set_aspect('equal', adjustable='box')
    for area in alm.adlr.admin_level_areas:
        if area.polygon:
            plot_polygon(area.polygon, add_points=False, ax=ax, color=(0,0,1))
    plt.show()
if __name__ ==  '__main__':
    cli()
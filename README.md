# Python Osmium Examples

This is a set (currently of size 1) of examples showing practical usage of PyOsmium, a thin wrapper around the osmium library. 

If you have other useful scripts, please submit a pull request to include them. If you do, please also update `setup.py` accordingly. See the [Click documentation](https://click.palletsprojects.com/en/8.0.x/setuptools/#setuptools-integration) for information.

## How to install

```bash
git clone git@github.com:mvexel/python-osmium-examples.git
cd python-osmium-examples
python3 -m venv venv
source venv/bin/activate
pip install .
```

## The Scripts

You can get basic syntax help by calling the script with `--help`.

### highway_mappers

Counts edits to major highways by user. The result is written as a CSV file with one row per mapper and one column per highway value.

The highway tag values to include are hard-coded in the script.

To see options and arguments use:
```
python3 highway_mappers.py --help
```

The data used as input for this script are OSM history files (`.osh.pbf`) that contain all change or OSM files (`.osm.pbf`) that only contain the most recent state and change. These files can be downloaded from https://osm-internal.download.geofabrik.de/ , but please note the GDPR restrictions on use of user-data.

To count edits by users over time rather than just recording the user behind the most recent change, run the script the `--all-versions` flag against an OSM history file (`*.osh.pbf`).

Additional `--after <date>` and `--before <date>` filters can be passed to scope the changeset date range.

import duckdb
import logging

duckdb.load_extension("spatial")
logger = logging.getLogger(__name__)


def read_wkt_data(files, cls):
    """Reads all given Parquet files in the data/ sub-package creates the library's
    database of Well-Known Locations, indexed by their name and all aliases.

    The source data is expected to have four columns:
      - ID
      - accessor name (like 'us.ca.san_francisco')
      - comma-separated list of aliases
      - geometry
    """
    database = {}
    for file in files:
        logger.debug("Loading WKT data from %s...", file.name)
        df = duckdb.sql(f"SELECT geom_id, name, aliases, ST_AsText(geom) AS geom FROM '{file}'").df()
        for line in df.itertuples():
            item = cls(line.name, line.geom)
            database[line.name] = item
            if line.aliases:
                for alias in filter(None, line.aliases.split(',')):
                    database[alias] = item
    logger.debug(
        "Read data from %d file(s); %d item(s) in database.",
        len(files),
        len(database),
    )
    return database

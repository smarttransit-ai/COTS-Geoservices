# Commercial-off-the-shelf Geoservices
This is a repository for several commercial, free and open source geoservices that we regularly use in the lab. The default configuration followed in this readme is for the state of Tennessee.

- [Open Source Routing Machine (OSRM)](#osrm)
- [Vehicle Routing Open-source Optimization Machine (VROOM)](#vroom)
- [OpenTripPlanner (OTP)](#otp)
- [photon](#photon)
- [Overpass](#Overpass)
- [Nominatim](#Nominatim)

## Setup and Deployment
1. Install docker desktop or docker on the server.
0. `git clone git@github.com:smarttransit-ai/COTS-Geoservices.git`
1. `cd COTS-Geoservices`
3. Download and place the pbf file into the `./data/shared` folder.
    `curl https://download.geofabrik.de/north-america/us/tennessee-latest.osm.pbf -o ./data/shared/tn.osm.pbf`
3. Generate speeds.csv: `touch ./data/osrm/speeds.csv`
2. `mkdir nominatim`
1. `docker compose build`
2. `docker compose --profile init up`
4. ```
   docker compose exec --user postgres nominatim \
   psql -U postgres -d nominatim -c "ALTER USER nominatim WITH ENCRYPTED PASSWORD 'mysecretpassword';"
   ```
5. `docker compose --profile init up`
6. `docker compose up -d`
3. `docker exec -it overpass bash -lc 'set -e && chmod 755 /db /db/db && stat -c "%A %U:%G %n" /db /db/db'`
7. Maybe you need to up serve-otp again.
8. Verify: `python scripts/verify_deployment.py`

## Docker
Follow the instructions [here](https://docs.docker.com/get-started/get-docker/).

# Containers
## OSRM
This uses a custom build that increases the potential alternative routes for any given query. See this [dockerhub](https://hub.docker.com/repository/docker/linusmotu/osrm-more-alt-linux) for more information.

This is built from a Dockerfile that, if provided a proper speeds.csv, will modify the edge speeds of the network. For more information on modifying or generating the speeds.csv, checkout [custom osrm speeds](https://github.com/smarttransit-ai/custom_osrm_speeds).

## VROOM
This uses the latest version of Vroom as of writing (v1.14.0) and the included config.yml file will point directly to the OSRM instance (included here) on the same docker network. For our particular use case, **ensure that your depots are on a road** or at least you have used the other tools to project your locations to the nearest road.

> Note, the environment variable VROOM_ROUTER has precedence over the router setting in config.yml.

## Valhalla
The advantages of Valhalla is in its ability to mark exclude locations and the capability of adding time aware speeds to its roads. More information on the Docker image is [here](https://github.com/valhalla/valhalla/tree/master/docker). We are using scripted image for this repo. It lets the user configure the whole tile build parameters using environment variables..

## OTP
This is different from the two planners/solvers/routing machines, instead this relies on the osm map and a gtfs. The limitation is it requires a single GTFS file no matter how many agencies you are trying to use and it will only set the date for a single day (so your queries need to be set to that day). To do this, we have to first merge the different files.
> Also this is not timezone naive.

### Merging GTFS files
Since these have different timezones and OTP only supports single timezones, we will also modify it to be all `America/Chicago` or Central Time.
0. `mkdir -p ./scripts/data/input`
1. Place all zipped GTFS files in `./scripts/data`.
    > These GTFS have been in no way cleaned and processed for mistakes, these are as is and are the latest versions as of 08-14-2025 and based on what is available from [Transitland](https://www.transit.land/).

    ```bash
    curl -L --fail --retry 3 "https://data.trilliumtransit.com/gtfs/jackson-tn-us/jackson-tn-us.zip?utm_source=transitland" -o ./scripts/data/input/jta.zip && \
    curl -L --fail --retry 3 "https://gtfs.mata.cadavl.com/MATA/GTFS/GTFS_MATA.zip" -o ./scripts/data/input/mata.zip && \
    curl -L --fail --retry 3 "https://www.gocarta.org/wp-content/uploads/2025/05/GTFS-1.zip?utm_source=transitland" -o ./scripts/data/input/carta.zip && \
    curl -L --fail --retry 3 "https://www.wegotransit.com/GoogleExport/Google_Transit.zip" -o ./scripts/data/input/wego.zip && \
    curl -L --fail --retry 3 -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)" \
    "https://knoxville.syncromatics.com/gtfs?utm_source=transitland" -o ./scripts/data/input/kat.zip
    ```
2. For a special handmade BlueOval City GTFS:
    ```bash
    curl -L --fail --retry 3 -o boc_gtfs.zip 'https://www.dropbox.com/scl/fi/86f760nfqgddv459oibjj/boc_gtfs.zip?rlkey=hsob65d3ddnjm639itrj1k87y&st=7bc8ebbh&dl=1'
    ```
2. `docker run -it --rm --name my-running-script -v "$PWD/scripts":/usr/src/myapp -w /usr/src/myapp python:3.10 bash -c "pip install --no-cache-dir -r requirements.txt && python main.py"`
5. Move or copy the new zipped gtfs `sciprts/data/temp_output/MERGED_gtfs.zip` to `./data/shared/gtfs_feeds`.

## photon
photon is an open source geocoder built for OpenStreetMap data. It is based on elasticsearch/OpenSearch - an efficient, powerful and highly scalable search platform.
photon was started by komoot who also provide the public demo server at photon.komoot.io.

## Overpass
The Overpass API is a read-only API that serves up custom selected parts of the OSM map data. It acts as a database over the web: the client sends a query to the API and gets back the data set that corresponds to the query. 

## Nominatim
Nominatim (from the Latin, 'by name') is a tool to search OpenStreetMap data by name and address (geocoding) and to generate synthetic addresses of OSM points (reverse geocoding). An instance with up-to-date data can be found at https://nominatim.openstreetmap.org. Nominatim is also used as one of the sources for the Search box on the OpenStreetMap home page.

## Verify
This is setup for the default location of tennessee.
1. Run `python scripts/verify_deployment.py`
2. You might need to install `python-dotenv`
2. The results should show:
```bash
Verifying deployment...
OSRM URL: localhost:8080/nearest/v1/driving/
OTP URL: http://localhost:8083
VROOM URL: http://localhost:3000
VALHALLA URL: http://localhost:8002/status
NOMINATIM URL: http://localhost:8081
PHOTON URL: http://localhost:2322
OVERPASS URL: http://localhost:1234/api
Success: http://localhost:8080/nearest/v1/driving/-86.9024502,35.9067283 is reachable.
Success: http://localhost:8083 is reachable.
Success: http://localhost:3000/health is reachable.
Success: http://localhost:8002/status is reachable.
Success: http://localhost:8081/search?q=Memphis&format=json is reachable.
Success: http://localhost:2322/api?q=Nashv&limit=1 is reachable.
Success: http://localhost:1234/api is reachable
```

## Things to do
1. Create sample commands for the services.
2. Link to APIs.

# References
* [Valhalla](https://github.com/valhalla/valhalla/tree/master/docker)
* [time accurate routing](https://github.com/smarttransit-ai/valhalla/tree/main)


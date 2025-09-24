# Commercial-off-the-shelf Solvers
- [Open Source Routing Machine (OSRM)](#osrm)
- [Vehicle Routing Open-source Optimization Machine (VROOM)](#vroom)
- [OpenTripPlanner (OTP)](#otp)
- [Valhalla](#valhalla)

This is a repository for several commercial, free and open source solvers and planners that we regularly use in the lab.  
The default configuration is for the state of Tennessee with included GTFS for the following transit agencies:
* [WeGo](http://www.nashvillemta.org/GoogleExport/google_transit.zip)
* [MATA](https://www.matatransit.com/how-do-you-travel/route-schedules/gtfs-feed/)
* [KAT](https://knoxville.syncromatics.com/gtfs)
* [JTA](https://data.trilliumtransit.com/gtfs/jackson-tn-us/jackson-tn-us.zip) 
* [CARTA](https://www.gocarta.org/wp-content/uploads/2025/05/GTFS-1.zip)
> These GTFS have been in no way cleaned and processed for mistakes, these are as is and are the latest versions as of 08-14-2025 and based on what is available from [Transitland](https://www.transit.land/).

# Setup
`git clone git@github.com:smarttransit-ai/COTS_SOLVERS.git`

## Docker
Follow the instructions [here](https://docs.docker.com/get-started/get-docker/).

# Containers
## OSRM
This uses a custom build that increases the potential alternative routes for any given query. See this [dockerhub](https://hub.docker.com/repository/docker/linusmotu/osrm-more-alt-linux) for more information.

This is built from a Dockerfile that, if provided a proper speeds.csv, will modify the edge speeds of the network. For more information on modifying or generating the speeds.csv, checkout [custom osrm speeds](https://github.com/smarttransit-ai/custom_osrm_speeds).

## VROOM
This uses the latest version of Vroom as of writing (v1.14.0) and the included config.yml file will point directly to the OSRM instance (included here) on the same docker network.

## OTP
This is different from the two planners/solvers/routing machines, instead this relies on the osm map and a gtfs. The limitation is it requires a single GTFS file no matter how many agencies you are trying to use and it will only set the date for a single day (so your queries need to be set to that day). To do this, we have to first merge the different files.
> Also this is not timezone naive.

### Merging GTFS files
Since these have different timezones and OTP only supports single timezones, we will also modify it to be all `America/Chicago` or Central Time.
0. `mkdir -p ./scripts/data/input`
1. Place all zipped GTFS files in `./scripts/data`.
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

## Setup and Deployment
1. Install docker desktop or docker on the server.
3. Download and place the pbf file into the `./data/shared` folder.
    `curl https://download.geofabrik.de/north-america/us/tennessee-latest.osm.pbf -o ./data/shared/osm.pbf`
3. Generate speeds.csv: `touch ./data/osrm/speeds.csv`
2. Ensure that the `./data` folder has the following contents:
    ```bash.
    ├── opentripplanner
    ├── osrm
    │   └── speeds.csv # for setting up edge weights on OSRM
    ├── shared
    │   ├── merged_gtfs.zip # for OTP/Valhalla, GTFS you want to use
    │   ├── merged_gtfs #unzipped gtfs folder for valhalla
    │   └── osm.pbf # tiles used for OSRM and OTP
    ├── valhalla # Mounted to Valhalla
    └── vroom
        └── config.yml # used by VROOM to point to OSRM/Valhalla services
    ```
    > Ensure that the gtfs, osm and speeds all point to the same area and have some overlap
3. `docker compose -f docker-compose.yml --env-file .env build`
3. `docker compose -f docker-compose.yml --env-file .env up`


## Verify
This is setup for the default location of tennessee.
1. Run `python scripts/verify_deployment.py`
2. The results should show:
```bash
Verifying deployment...
OSRM URL: localhost:8080/nearest/v1/driving/
OTP URL: http://localhost:8081
VROOM URL: http://localhost:3000
Valhalla URL: http://localhost:8002
Success: http://localhost:8080/nearest/v1/driving/-86.9024502,35.9067283 is reachable.
Success: http://localhost:8081 is reachable.
Success: http://localhost:3000/health is reachable.
Success: http://localhost:8002/status is reachable.
```

## Things to do
1. Create sample commands for the services.
2. Link to APIs.

# References
* [Valhalla](https://github.com/valhalla/valhalla/tree/master/docker)
* [time accurate routing](https://github.com/smarttransit-ai/valhalla/tree/main)
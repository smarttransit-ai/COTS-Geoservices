# Commercial-off-the-shelf Solvers
- [Open Source Routing Machine (OSRM)](#osrm)
- [Vehicle Routing Open-source Optimization Machine (VROOM)](#vroom)
- [OpenTripPlanner (OTP)](#otp)

This is a repository for several commercial, free and open source solvers and planners that we regularly use in the lab.  
The default configuration is for the state of Tennessee with included GTFS for the following transit agencies:
* [WeGo](http://www.nashvillemta.org/GoogleExport/google_transit.zip)
* [MATA](https://www.matatransit.com/how-do-you-travel/route-schedules/gtfs-feed/)
* [KAT](https://knoxville.syncromatics.com/gtfs)
* [JTA](https://data.trilliumtransit.com/gtfs/jackson-tn-us/jackson-tn-us.zip) 
* [CARTA](https://www.gocarta.org/wp-content/uploads/2025/05/GTFS-1.zip)
> These GTFS have been in no way cleaned and processed for mistakes, these are as is and are the latest versions as of 08-14-2025 and based on what is available from [Transitland](https://www.transit.land/).

## Clone
`git clone git@github.com:smarttransit-ai/COTS_SOLVERS.git`

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
    cd ./scripts/data/input && \
    curl https://data.trilliumtransit.com/gtfs/jackson-tn-us/jackson-tn-us.zip?utm_source=transitland -o jta.zip && \
    curl https://gtfs.mata.cadavl.com/MATA/GTFS/GTFS_MATA.zip -o mata.zip && \
    curl https://www.gocarta.org/wp-content/uploads/2025/05/GTFS-1.zip?utm_source=transitland -o carta.zip && \
    curl https://www.wegotransit.com/googleexport/google_transit.zip?utm_source=transitland -o wego.zip && \
    curl https://knoxville.syncromatics.com/gtfs?utm_source=transitland -o kat.zip
    ```
2. `docker run -it --rm --name my-running-script -v "$PWD/scripts":/usr/src/myapp -w /usr/src/myapp python:3.10 bash -c "pip install --no-cache-dir -r requirements.txt && python gtfs_merging.py"`
5. Move or copy the new zipped gtfs `sciprts/data/temp_output/MERGED_gtfs.zip` to `./data`.

## Setup and Deployment
1. Install docker desktop or docker on the server.
3. Download and place the pbf file into the `./data` folder.
    `curl https://download.geofabrik.de/north-america/us/tennessee-latest.osm.pbf -o ./data/osm.pbf`
3. Generate speeds.csv: `touch ./data/speeds.csv`
2. Ensure that the `./data` folder has the following contents:
    ```bash
    └── data 
        ├── conf # for VROOM
        │   └── config.yml # used by VROOM to point to OSRM
        ├── Merged_gtfs.zip # for OTP, GTFS you want to use
        ├── osm.pbf # tiles used for OSRM and OTP
        └── speeds.csv # for setting up edge weights on OSRM
    ```
    > Ensure that the gtfs, osm and speeds all point to the same area and have some overlap
3. `docker compose up -d`

## Verify
This is setup for the default location of tennessee.
1. Run `python scripts/verify_deployment.py`
2. The results should show:
```bash
Verifying deployment...
OSRM URL: localhost:8080/nearest/v1/driving/
OTP URL: http://localhost:8081
VROOM URL: http://localhost:3000
Success: http://localhost:8080/nearest/v1/driving/-86.9024502,35.9067283 is reachable.
Success: http://localhost:8081 is reachable.
Success: http://localhost:3000/health is reachable.
```

## Things to do
1. Create sample commands for the services.
2. Link to APIs.

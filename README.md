# project-thea-api

Welcome to the the project-thea-api!

## Development

Start the containers in dev
```bash
docker compose -f docker-compose-dev.yml up -d
```

You can use the following commands to view the logs
```bash
docker-composer -f docker-compose-[dev,prod].yml logs --follow --tail 10 project-thea-api
```

Add the fixture data to your database
```bash
python manage.py load_all_fixtures
```

The Valhalla service is often distributed as a docker image and the following command can be used to start the container and in our case, also load the Uganda map data
```bash
docker run -dt --name thea_valhalla -p 8002:8002 -v $PWD/custom_files:/custom_files -e tile_urls=https://download.geofabrik.de/africa/uganda-latest.osm.pbf ghcr.io/gis-ops/docker-valhalla/valhalla:latest
```

For more information on the Valhalla docker image and more container customisations, please refer [here](https://github.com/nilsnolde/docker-valhalla)

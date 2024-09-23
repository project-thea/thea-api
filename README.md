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

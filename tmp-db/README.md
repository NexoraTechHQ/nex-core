# run

If it need lastest version or just skip

```sh
sudo docker compose down
```

Then

```sh
sudo docker compose build --no-cache
```

```sh
sudo docker compose up
```

if error with entrypoint

```sh
pip install dos2unix
dos2unix entrypoint.sh
```

In linux run extra scripts

```sh
sudo chown -R 1000:1000 ./pb_data
sudo chmod -R 755 ./pb_data
```

REST API: http://0.0.0.0:8090/api/
Dashboard: http://0.0.0.0:8090/_/

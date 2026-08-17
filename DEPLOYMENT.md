# Deploying with Gunicorn

This project is configured to run its Django WSGI app through Gunicorn.

## 1. Configure production environment variables

Copy `.env.example` to your deployment platform's environment-variable settings and provide real values. At minimum set:

- `SECRET_KEY`: a long, unique secret value.
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`: a comma-separated list of the domains that will serve the app.

Do not upload the local `.env` file or reuse its secret in production.

## 2. Install dependencies

```sh
python -m pip install -r requirements.txt
```

## 3. Use one deploy command

```sh
./deploy.sh
```

This runs database migrations and `collectstatic`, then starts Gunicorn. Gunicorn binds to `0.0.0.0:$PORT`; it uses port `8000` when `PORT` is unset. WhiteNoise serves the collected static assets through the application. Set the platform's single deploy/start command to `./deploy.sh`.

For a traditional server, put Nginx or another reverse proxy in front of Gunicorn to terminate HTTPS. User uploads in `media/` still need persistent object storage or web-server configuration; WhiteNoise is for version-controlled static assets only.

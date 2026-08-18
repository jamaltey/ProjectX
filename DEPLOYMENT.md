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

### Render Free memory limit

Render's Free web service has 512 MB of memory. This project therefore starts one Gunicorn worker by default. Do not set `GUNICORN_WORKERS` above `1` on the Free plan. Workers recycle after 300 requests to release any memory retained by application libraries; override this only with `GUNICORN_MAX_REQUESTS` if required.

For a traditional server, put Nginx or another reverse proxy in front of Gunicorn to terminate HTTPS. User uploads in `media/` still need persistent object storage or web-server configuration; WhiteNoise is for version-controlled static assets only.

## Free Render media uploads with Cloudinary

Cloudinary stores uploaded product images outside Render, so they survive service restarts and deploys without a Render Persistent Disk. Create a Cloudinary account and copy its cloud name, API key, and API secret from the Cloudinary Console. Add these three environment variables to the Render service:

```text
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

Never commit the API secret. The existing `./deploy.sh` command stays unchanged. New Django `ImageField` uploads are sent to Cloudinary and their existing `.url` template usage automatically resolves to Cloudinary URLs. Existing files in the local `media/` directory must be uploaded to Cloudinary separately.

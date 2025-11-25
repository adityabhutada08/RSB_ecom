# Docker Setup Guide

This guide explains how to run the Django e-commerce application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed

## Quick Start

1. **Create a `.env` file** in the root directory with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
DB_NAME=rsb_db
DB_USER=rsb_user
DB_PASSWORD=rsb_password
DB_HOST=db
DB_PORT=5432

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# Razorpay Configuration
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_SECRET_KEY=your-razorpay-secret-key
```

2. **Build and start the containers:**

```bash
docker-compose up --build
```

3. **Create a superuser (in a new terminal):**

```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Access the application:**

- Web application: http://localhost:8000
- Admin panel: http://localhost:8000/admin

## Common Commands

### Start containers in detached mode:
```bash
docker-compose up -d
```

### Stop containers:
```bash
docker-compose down
```

### View logs:
```bash
docker-compose logs -f web
```

### Run Django management commands:
```bash
docker-compose exec web python manage.py <command>
```

### Access Django shell:
```bash
docker-compose exec web python manage.py shell
```

### Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

### Collect static files:
```bash
docker-compose exec web python manage.py collectstatic
```

### Rebuild containers:
```bash
docker-compose up --build --force-recreate
```

## Database

The application uses PostgreSQL in Docker. The database data is persisted in a Docker volume named `postgres_data`.

### Access PostgreSQL shell:
```bash
docker-compose exec db psql -U rsb_user -d rsb_db
```

### Backup database:
```bash
docker-compose exec db pg_dump -U rsb_user rsb_db > backup.sql
```

### Restore database:
```bash
docker-compose exec -T db psql -U rsb_user rsb_db < backup.sql
```

## Volumes

The following volumes are created:
- `postgres_data`: PostgreSQL database data
- `static_volume`: Collected static files
- `media_volume`: User uploaded media files

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in your `.env` file
2. Update `ALLOWED_HOSTS` with your domain
3. Use a strong `SECRET_KEY`
4. Consider using environment-specific settings
5. Set up proper SSL/TLS certificates
6. Configure a reverse proxy (nginx) if needed

## Troubleshooting

### Container won't start:
- Check if port 8000 is already in use
- Verify your `.env` file exists and has all required variables
- Check logs: `docker-compose logs web`

### Database connection errors:
- Ensure the `db` service is healthy: `docker-compose ps`
- Check database credentials in `.env`
- Wait for database to be ready before starting web service

### Static files not loading:
- Run: `docker-compose exec web python manage.py collectstatic`
- Check volume mounts in `docker-compose.yml`


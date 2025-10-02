# Deployment Guide for VnExpress News Scraper API

## Quick Start

Use the deployment script for easy deployment:

```bash
./deploy.sh [option]
```

## Deployment Options

### 1. Local Development (Current)
```bash
./deploy.sh dev
# OR
python main.py
```
- **Pros**: Quick to start, good for development
- **Cons**: Not suitable for production, single-threaded

### 2. Production with Gunicorn (Recommended)
```bash
./deploy.sh gunicorn
```
- **Pros**: Production-ready, multi-worker, better performance
- **Cons**: Requires more system resources
- **Best for**: Production deployments on VPS/dedicated servers

### 3. Docker Deployment
```bash
./deploy.sh docker
# OR manually:
docker build -t vnexpress-api .
docker run -d -p 8000:8000 --name vnexpress-api-container vnexpress-api
```
- **Pros**: Isolated environment, easy to manage, portable
- **Cons**: Requires Docker knowledge
- **Best for**: Containerized environments, cloud deployments

### 4. Docker Compose (Recommended for Docker users)
```bash
./deploy.sh compose
# OR manually:
docker-compose up -d
```
- **Pros**: Easy to manage, includes volume mounting, restart policies
- **Cons**: Requires Docker Compose
- **Best for**: Local development with containers, staging environments

### 5. Systemd Service (Linux Servers)
```bash
./deploy.sh systemd
```
- **Pros**: Auto-starts on boot, process management, logging
- **Cons**: Linux-specific, requires sudo access
- **Best for**: Production Linux servers

## Cloud Platform Deployments

### Railway
1. Connect your GitHub repository to Railway
2. Railway will automatically detect the `Procfile`
3. Set environment variables if needed
4. Deploy automatically

### Render
1. Connect your GitHub repository to Render
2. Use the `Procfile` for build command
3. Set environment variables
4. Deploy

### Heroku
1. Install Heroku CLI
2. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```
3. Deploy:
   ```bash
   git push heroku main
   ```

### DigitalOcean App Platform
1. Connect your GitHub repository
2. Choose Python as runtime
3. Use `gunicorn -c gunicorn.conf.py main:app` as run command
4. Deploy

## Environment Configuration

### Required Environment Variables (Optional)
```bash
# For production deployments, you can set:
export DATABASE_URL="sqlite:///./vnexpress_news.db"
export API_HOST="0.0.0.0"
export API_PORT="8000"
```

### Production Considerations

1. **Database**: Consider using PostgreSQL or MySQL for production:
   ```bash
   pip install psycopg2-binary  # For PostgreSQL
   pip install mysql-connector-python  # For MySQL
   ```

2. **Reverse Proxy**: Use Nginx as a reverse proxy:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **SSL Certificate**: Use Let's Encrypt for HTTPS:
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

4. **Monitoring**: Consider adding:
   - Health checks
   - Logging (structured logs)
   - Metrics collection
   - Error tracking (Sentry)

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   sudo lsof -i :8000
   sudo kill -9 <PID>
   ```

2. **Permission denied**:
   ```bash
   chmod +x deploy.sh
   ```

3. **Dependencies issues**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

4. **Database permissions**:
   ```bash
   chmod 664 vnexpress_news.db
   ```

## Testing Your Deployment

After deployment, test your API:

```bash
# Health check
curl http://localhost:8000/health

# API documentation
curl http://localhost:8000/docs

# Get articles
curl http://localhost:8000/articles?limit=5
```

## Performance Tuning

### Gunicorn Configuration
Adjust `gunicorn.conf.py` based on your server specs:
- **Workers**: Generally `(2 x CPU cores) + 1`
- **Worker connections**: 1000 for most cases
- **Memory**: Monitor and adjust based on usage

### Database Optimization
- Add indexes for frequently queried fields
- Consider connection pooling for high traffic
- Regular database maintenance

## Security Considerations

1. **API Keys**: Use environment variables for sensitive data
2. **Rate Limiting**: Implement rate limiting for public APIs
3. **CORS**: Configure CORS properly for your domain
4. **Firewall**: Restrict access to necessary ports only
5. **Updates**: Keep dependencies updated regularly

## Scaling

For high-traffic scenarios:
1. **Load Balancer**: Use multiple instances behind a load balancer
2. **Database**: Separate database server
3. **Caching**: Implement Redis for caching
4. **CDN**: Use CDN for static content
5. **Microservices**: Split scraping and API into separate services
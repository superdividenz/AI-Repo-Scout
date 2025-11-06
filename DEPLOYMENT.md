# 🚀 Deployment Guide - AI Repo Scout

This guide covers all deployment options for AI Repo Scout, from local development to production hosting.

## 📋 Prerequisites

- Python 3.8+
- Git
- GitHub account (for API access and deployment)

## 🏠 Local Development

### 1. Clone and Setup

```bash
git clone https://github.com/superdividenz/AI-Repo-Scout.git
cd AI-Repo-Scout
chmod +x setup.sh
./setup.sh
```

### 2. Environment Configuration

Create a `.env` file (optional but recommended):

```bash
# .env
GITHUB_TOKEN=your_github_personal_access_token
```

Get a GitHub token from: https://github.com/settings/tokens

### 3. Run Locally

```bash
# Generate a quick report
python src/main.py --timeframe daily --languages python javascript

# Launch dashboard
streamlit run src/dashboard.py

# Continuous monitoring
python src/main.py --continuous --interval 24
```

## ☁️ Cloud Deployment Options

### 1. Streamlit Cloud (Free Dashboard Hosting)

**Perfect for: Interactive dashboards, demos**

1. **Fork this repository** to your GitHub account
2. Visit [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your GitHub account
4. Select your forked repository
5. Set deployment settings:
   - **Main file path**: `src/dashboard.py`
   - **Python version**: 3.9
6. Add secrets in Streamlit Cloud dashboard:
   ```toml
   [github]
   token = "your_github_token_here"
   ```
7. Deploy!

**Result**: Your dashboard will be available at `https://your-app-name.streamlit.app`

### 2. GitHub Pages (Free Report Hosting)

**Perfect for: Static reports, public sharing**

1. **Enable GitHub Pages** in repository settings:

   - Go to Settings → Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages` (created automatically)

2. **Configure GitHub Actions** (already included):

   - Reports generate automatically daily at 6 AM UTC
   - Deploys to GitHub Pages automatically

3. **Add GitHub token** to repository secrets:
   - Go to Settings → Secrets and variables → Actions
   - Add `GITHUB_TOKEN` with your personal access token

**Result**: Reports available at `https://yourusername.github.io/AI-Repo-Scout`

### 3. Google Colab (Free Execution)

**Perfect for: One-off analysis, experimentation**

1. **Open in Colab**:

   ```python
   # In a Colab notebook
   !git clone https://github.com/superdividenz/AI-Repo-Scout.git
   %cd AI-Repo-Scout
   !pip install -r requirements.txt

   # Set your GitHub token
   import os
   os.environ['GITHUB_TOKEN'] = 'your_token_here'

   # Run analysis
   !python src/main.py --timeframe daily --languages python
   ```

2. **Scheduled execution**: Use Colab Pro for scheduled runs

### 4. Heroku (Free Tier Alternative)

**Perfect for: Web apps, APIs, scheduled tasks**

1. **Install Heroku CLI** and login

2. **Create Heroku app**:

   ```bash
   heroku create your-repo-scout-app
   ```

3. **Add Procfile**:

   ```
   web: streamlit run src/dashboard.py --server.port=$PORT --server.address=0.0.0.0
   worker: python src/main.py --continuous --interval 24
   ```

4. **Set environment variables**:

   ```bash
   heroku config:set GITHUB_TOKEN=your_token_here
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

### 5. Railway/Render (Free Alternatives)

**Similar to Heroku, with generous free tiers**

#### Railway:

1. Connect GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `streamlit run src/dashboard.py`
4. Add environment variables

#### Render:

1. Connect GitHub repository
2. Choose "Web Service"
3. Build: `pip install -r requirements.txt`
4. Start: `streamlit run src/dashboard.py`

## 🔄 Automated Workflows

### GitHub Actions (Included)

**Daily Report Generation** (`.github/workflows/generate-reports.yml`):

- Runs daily at 6 AM UTC
- Generates reports for trending repositories
- Deploys to GitHub Pages automatically
- Updates README with latest report link

**Dashboard Deployment** (`.github/workflows/deploy-dashboard.yml`):

- Tests dashboard on code changes
- Validates dependencies
- Prepares for Streamlit Cloud deployment

### Custom Scheduling

For other platforms, use their built-in schedulers:

**Heroku Scheduler**:

```bash
heroku addons:create scheduler:standard
heroku addons:open scheduler
# Add job: python src/main.py --timeframe daily
```

**GitHub Actions (Custom)**:

```yaml
on:
  schedule:
    - cron: "0 6 * * *" # Daily at 6 AM UTC
```

## 🌐 Custom Domain Setup

### GitHub Pages

1. Add `CNAME` file to `reports/` directory:
   ```
   your-domain.com
   ```
2. Configure DNS with your domain provider

### Streamlit Cloud

1. Add custom domain in Streamlit Cloud dashboard
2. Configure DNS records as instructed

## 📊 Monitoring and Analytics

### Built-in Metrics

- Repository analysis logs
- API rate limit monitoring
- Error tracking and recovery

### External Monitoring

- **Uptime monitoring**: UptimeRobot (free)
- **Analytics**: Google Analytics (add to HTML templates)
- **Error tracking**: Sentry (free tier)

## 🔒 Security Best Practices

### API Keys

- **Never commit** API keys to repository
- Use environment variables or secrets management
- Rotate keys regularly

### Rate Limiting

- Implement exponential backoff
- Monitor API usage
- Use caching to reduce API calls

### Dependencies

- Keep dependencies updated
- Use `pip-audit` for security scanning
- Pin versions in production

## 💰 Cost Optimization

### Free Tier Limits

- **GitHub API**: 5000 requests/hour with token
- **Streamlit Cloud**: 1 app, unlimited viewers
- **GitHub Pages**: 100GB bandwidth/month
- **Heroku**: 550-1000 dyno hours/month (free)

### Scaling Considerations

- Use caching to reduce API calls
- Implement data archiving
- Consider paid tiers for production use

## 🚀 Production Checklist

- [ ] GitHub token configured
- [ ] Error handling implemented
- [ ] Monitoring setup
- [ ] Backup strategy
- [ ] Documentation updated
- [ ] Custom domain configured (optional)
- [ ] Analytics tracking (optional)
- [ ] Security scan completed

## 🆘 Troubleshooting

### Common Issues

**"No module named 'xxx'"**:

```bash
pip install -r requirements.txt
```

**"API rate limit exceeded"**:

- Add GitHub token
- Implement caching
- Reduce request frequency

**"Streamlit app won't start"**:

- Check Python version (3.8+)
- Verify all dependencies installed
- Check for port conflicts

**"GitHub Actions failing"**:

- Verify repository secrets
- Check workflow permissions
- Review action logs

### Getting Help

- **GitHub Issues**: Report bugs and feature requests
- **Discussions**: Community support and ideas
- **Documentation**: Detailed API docs in `/docs`

---

## 🎯 Quick Deployment Summary

| Platform        | Best For               | Setup Time | Cost      |
| --------------- | ---------------------- | ---------- | --------- |
| Streamlit Cloud | Interactive dashboards | 5 minutes  | Free      |
| GitHub Pages    | Static reports         | 2 minutes  | Free      |
| Google Colab    | Experimentation        | 1 minute   | Free      |
| Heroku          | Full web apps          | 10 minutes | Free tier |
| Railway/Render  | Modern alternatives    | 5 minutes  | Free tier |

Choose the option that best fits your use case and technical requirements!

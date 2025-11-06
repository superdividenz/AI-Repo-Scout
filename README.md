# 🚀 AI Repo Scout - Zero-Cost Edition

A free, open-source tool for discovering trending GitHub repositories using AI-powered insights. Built entirely with free APIs and open-source models, with optional premium AI integration.

## ✨ Features

- **📈 Real-time Trending Analysis**: Track GitHub's hottest repositories
- **🤖 AI-Powered Insights**: Choose between free Hugging Face models or premium DeepSeek AI
- **📊 Growth Metrics**: Star velocity, contributor growth, engagement scores
- **🎯 Zero-Cost Operation**: Core features use only free APIs and open-source tools
- **📱 Interactive Dashboard**: Beautiful Streamlit web interface
- **📄 Automated Reports**: Daily/weekly markdown reports for GitHub Pages
- **⚡ Enhanced AI (Optional)**: DeepSeek integration for professional-grade analysis

## 🛠️ Tech Stack

### Core (100% Free)

- **Data Source**: GitHub REST/GraphQL API (free tier)
- **AI Models**: Hugging Face transformers (distilbert, t5-small)
- **Computation**: Python + pandas + scikit-learn
- **Dashboard**: Streamlit (free hosting available)
- **Deployment**: GitHub Pages, Streamlit Cloud

### Enhanced AI (Optional)

- **Premium AI**: DeepSeek API for superior analysis quality
- **Cost**: ~$0.001 per repository analysis (ultra-low cost)
- **Benefits**: 10x better insights, context-aware summaries, professional recommendations
- **Storage**: SQLite (local) or CSV files

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
git clone https://github.com/superdividenz/AI-Repo-Scout.git
cd AI-Repo-Scout
./setup.sh  # Automated setup script
```

### Option 2: Manual Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/superdividenz/AI-Repo-Scout.git
   cd AI-Repo-Scout
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys** (optional but recommended):

   ```bash
   # GitHub token for higher rate limits (free)
   export GITHUB_TOKEN=your_github_token_here

   # DeepSeek API for enhanced AI analysis (optional, paid)
   export DEEPSEEK_API_KEY=your_deepseek_key_here
   ```

4. **Run demos**:

   ```bash
   # Basic demo (no dependencies required)
   python3 demo.py

   # DeepSeek AI demo (shows enhanced features)
   python3 demo_deepseek.py
   ```

5. **Generate your first report**:

   ```bash
   python src/main.py --timeframe daily --languages python javascript
   ```

6. **Launch interactive dashboard**:
   ```bash
   streamlit run src/dashboard.py
   ```

## 📊 How It Works

1. **Data Collection**: Fetches trending repos from GitHub API
2. **AI Analysis**: Uses Hugging Face models to summarize repo purposes
3. **Scoring Algorithm**: Calculates momentum scores based on:
   - Star growth velocity
   - Contributor increase
   - Issue/PR activity
   - Community engagement
4. **Insight Generation**: Creates ranked lists and trend analysis
5. **Output**: Generates reports and interactive dashboards

## 💰 Revenue Potential (All Free to Start)

- **Affiliate Links**: Deploy buttons with platform affiliates
- **Sponsored Content**: Once you build an audience
- **GitHub Sponsors**: Accept donations for insights
- **Newsletter**: Substack free tier → premium subscriptions
- **B2B Services**: Custom analytics reports

## 🔧 Configuration

Create a `config.yaml` file:

```yaml
github:
  token: ${GITHUB_TOKEN} # Optional but increases rate limits
  max_repos: 500

models:
  summarizer: "t5-small"
  embeddings: "distilbert-base-uncased"

output:
  format: ["markdown", "html", "json"]
  reports_dir: "reports"
```

## 📈 Example Output

```markdown
🚀 Top Emerging Repos (Nov 6, 2025)

1. microsoft/autogen – +430% stars, AI agent framework
2. vercel/ai-sdk – Steady growth, new contributors
3. openai/consistency-models – Research breakthrough
```

## 🤝 Contributing

This is an open-source project! Contributions welcome:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - feel free to use for commercial purposes!

## 🔗 Links

- [Live Dashboard](https://ai-repo-scout.streamlit.app)
- [Daily Reports](https://superdividenz.github.io/AI-Repo-Scout)
- [API Documentation](./docs/api.md)

---

Built with ❤️ using only free and open-source tools

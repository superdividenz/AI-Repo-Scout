#!/usr/bin/env python3
"""
Quick demo script to showcase AI Repo Scout capabilities.
Runs a minimal example with sample data for demonstration.
"""

import os
import sys
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def demo_quick_analysis():
    """Run a quick demo analysis with sample data."""
    print("🚀 AI Repo Scout - Quick Demo")
    print("=" * 40)
    
    try:
        from github_client import GitHubAPIClient, calculate_momentum_score
        from ai_analyzer import AIAnalyzer
        
        print("✅ Modules imported successfully")
        
        # Sample repository data for demo
        sample_repos = [
            {
                'name': 'awesome-ai-tools',
                'full_name': 'developer/awesome-ai-tools',
                'description': 'A curated list of awesome AI tools and resources for developers',
                'html_url': 'https://github.com/developer/awesome-ai-tools',
                'language': 'Python',
                'stars': 1250,
                'forks': 180,
                'issues': 15,
                'contributors': 25,
                'recent_commits': 12,
                'created_at': '2024-01-15T10:00:00Z',
                'updated_at': '2024-11-05T15:30:00Z',
                'topics': ['ai', 'machine-learning', 'tools', 'python'],
                'license': 'MIT'
            },
            {
                'name': 'react-dashboard',
                'full_name': 'frontend/react-dashboard',
                'description': 'Modern React dashboard with beautiful UI components',
                'html_url': 'https://github.com/frontend/react-dashboard',
                'language': 'JavaScript',
                'stars': 890,
                'forks': 120,
                'issues': 8,
                'contributors': 15,
                'recent_commits': 8,
                'created_at': '2024-03-20T14:20:00Z',
                'updated_at': '2024-11-06T09:45:00Z',
                'topics': ['react', 'dashboard', 'ui', 'typescript'],
                'license': 'Apache-2.0'
            },
            {
                'name': 'rust-cli-tool',
                'full_name': 'systems/rust-cli-tool',
                'description': 'High-performance CLI tool written in Rust for data processing',
                'html_url': 'https://github.com/systems/rust-cli-tool',
                'language': 'Rust',
                'stars': 456,
                'forks': 45,
                'issues': 5,
                'contributors': 8,
                'recent_commits': 15,
                'created_at': '2024-06-10T08:15:00Z',
                'updated_at': '2024-11-06T12:00:00Z',
                'topics': ['rust', 'cli', 'performance', 'data'],
                'license': 'MIT'
            }
        ]
        
        print(f"📊 Analyzing {len(sample_repos)} sample repositories...")
        
        # Calculate momentum scores
        for repo in sample_repos:
            repo['momentum_score'] = calculate_momentum_score(repo)
        
        # Sort by momentum score
        sample_repos.sort(key=lambda x: x['momentum_score'], reverse=True)
        
        print("\n🏆 Repository Rankings:")
        print("-" * 40)
        
        for i, repo in enumerate(sample_repos, 1):
            print(f"{i}. {repo['name']} ({repo['language']})")
            print(f"   ⭐ Stars: {repo['stars']:,} | 🍴 Forks: {repo['forks']:,}")
            print(f"   🏃 Momentum Score: {repo['momentum_score']:.1f}/100")
            print(f"   📝 {repo['description'][:80]}...")
            print()
        
        # AI Analysis Demo
        print("🤖 AI Analysis Demo:")
        print("-" * 40)
        
        try:
            ai_analyzer = AIAnalyzer()
            
            # Try to generate a summary for the top repo
            top_repo = sample_repos[0]
            print(f"Generating AI summary for: {top_repo['name']}")
            
            # This will use fallback methods if AI models aren't loaded
            summary = ai_analyzer.summarize_repository(top_repo)
            print(f"AI Summary: {summary}")
            
        except Exception as e:
            print(f"AI analysis demo skipped (models not loaded): {e}")
            print("💡 Install full dependencies with: pip install -r requirements.txt")
        
        # Language Analysis
        print("\n📈 Language Trends:")
        print("-" * 40)
        
        languages = {}
        for repo in sample_repos:
            lang = repo['language']
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            print(f"  {lang}: {count} repositories")
        
        # Recommendations
        print("\n💡 Sample Recommendations:")
        print("-" * 40)
        print("• Python repositories show high momentum scores")
        print("• AI/ML tools are trending in the developer community")
        print("• Modern web frameworks continue to gain popularity")
        print("• Systems programming languages (Rust) show strong growth")
        
        print("\n✨ Demo completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install dependencies with: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False


def demo_report_preview():
    """Show what a generated report looks like."""
    print("\n📄 Sample Report Preview:")
    print("=" * 40)
    
    report_preview = """
# 🚀 AI Repo Scout Report
## Daily Trending Repositories

**Generated on:** November 6, 2024 15:30:00 UTC
**Total Repositories Analyzed:** 3
**Average Momentum Score:** 67.8

---

## 🔥 Top Trending Repository

### 1. [awesome-ai-tools](https://github.com/developer/awesome-ai-tools)

**developer/awesome-ai-tools** (Python)

A curated list of awesome AI tools and resources for developers

**Metrics:**
- ⭐ **Stars:** 1,250
- 🍴 **Forks:** 180
- 🏃 **Momentum Score:** 72.5/100
- 📈 **Star Velocity:** 4.2 stars/day
- 👥 **Contributors:** 25
- 🏷️ **Topics:** ai, machine-learning, tools, python

---

This is a preview of what full reports look like!
"""
    
    print(report_preview)


def main():
    """Run the demo."""
    print("Starting AI Repo Scout demo...\n")
    
    success = demo_quick_analysis()
    
    if success:
        demo_report_preview()
        
        print("\n🎯 Next Steps:")
        print("-" * 40)
        print("1. 🔧 Run full setup: ./setup.sh")
        print("2. 📊 Generate real report: python src/main.py --timeframe daily")
        print("3. 🌐 Launch dashboard: streamlit run src/dashboard.py")
        print("4. 📖 Read deployment guide: DEPLOYMENT.md")
        print("5. 🚀 Deploy to cloud: Follow GitHub Actions setup")
        
        print("\n📚 Learn More:")
        print("- GitHub: https://github.com/superdividenz/AI-Repo-Scout")
        print("- Documentation: README.md")
        print("- Examples: examples/usage_examples.py")
        
    else:
        print("\n🔧 Setup Required:")
        print("Run ./setup.sh to install dependencies and try again!")


if __name__ == "__main__":
    main()
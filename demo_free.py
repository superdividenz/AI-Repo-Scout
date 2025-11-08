#!/usr/bin/env python3
"""
Free-tier demo for AI Repo Scout.
Tests the system using only free APIs and lightweight processing.
"""

import os
import sys

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_free_version():
    """Test the free version of AI Repo Scout."""
    print("🚀 AI Repo Scout - Free Version Demo")
    print("=" * 50)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from github_client import GitHubAPIClient, filter_quality_repos
        from simple_ai_analyzer import EnhancedAIAnalyzer
        from data_analysis import DataAnalysisEngine
        print("✅ All imports successful!")
        
        # Test GitHub client (no token required for basic testing)
        print("\n🐙 Testing GitHub API client...")
        github_client = GitHubAPIClient()
        print("✅ GitHub client initialized")
        
        # Test AI analyzer
        print("\n🧠 Testing lightweight AI analyzer...")
        config = {'models': {'provider': 'huggingface'}}
        ai_analyzer = EnhancedAIAnalyzer(config)
        
        # Test repository summarization with sample data
        sample_repo = {
            'name': 'awesome-python',
            'description': 'A curated list of awesome Python frameworks, libraries, software and resources.',
            'language': 'Python',
            'stars': 15000,
            'topics': ['python', 'awesome', 'list', 'resources'],
            'momentum_score': 85
        }
        
        summary = ai_analyzer.summarize_repository(sample_repo)
        print(f"📝 Sample summary: {summary}")
        print("✅ AI analyzer working!")
        
        # Test data analysis engine
        print("\n📊 Testing data analysis engine...")
        data_engine = DataAnalysisEngine({})
        print("✅ Data engine initialized")
        
        # Test with sample repository data
        sample_repos = [
            sample_repo,
            {
                'name': 'react',
                'description': 'A declarative, efficient, and flexible JavaScript library for building user interfaces.',
                'language': 'JavaScript',
                'stars': 220000,
                'topics': ['javascript', 'react', 'ui', 'frontend'],
                'momentum_score': 95
            },
            {
                'name': 'tensorflow',
                'description': 'An Open Source Machine Learning Framework for Everyone',
                'language': 'Python',
                'stars': 180000,
                'topics': ['machine-learning', 'tensorflow', 'ai', 'python'],
                'momentum_score': 92
            }
        ]
        
        # Generate insights
        print("\n🔍 Generating insights...")
        insights = ai_analyzer.analyze_trends(sample_repos)
        
        print(f"📈 Analyzed {insights['total_repos']} repositories")
        print(f"🏷️  Top languages: {list(insights['language_trends'].keys())}")
        print(f"🎯 Categories found: {list(insights['category_trends'].keys())}")
        
        if insights.get('recommendations'):
            print(f"\n💡 Sample recommendations:")
            for i, rec in enumerate(insights['recommendations'][:3], 1):
                print(f"   {i}. {rec}")
        
        print("\n🎉 Free version test completed successfully!")
        print("\n" + "=" * 50)
        print("✅ Ready to use! The free version includes:")
        print("   • GitHub API integration (public repos)")
        print("   • Lightweight AI text analysis") 
        print("   • Statistical trend analysis")
        print("   • Repository categorization")
        print("   • Growth momentum scoring")
        print("   • Streamlit dashboard")
        print("\n💡 To run full analysis:")
        print("   python3 src/main.py --ai-provider huggingface")
        print("\n💡 To start dashboard:")
        print("   python3 src/main.py --dashboard")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n🔧 Setup steps:")
        print("1. Activate virtual environment: source ai-repo-scout-env/bin/activate")
        print("2. Install dependencies: pip install -r requirements-minimal.txt")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print(f"📍 Error details: {type(e).__name__}")
        return False


def check_environment():
    """Check if the environment is properly set up."""
    print("🔍 Environment Check")
    print("-" * 30)
    
    # Check Python version
    python_version = sys.version_info
    print(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if virtual environment is active
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is active")
    else:
        print("⚠️  Virtual environment not detected")
        print("💡 Activate with: source ai-repo-scout-env/bin/activate")
    
    # Check for GITHUB_TOKEN
    github_token = os.getenv('GITHUB_TOKEN')
    if github_token:
        print("✅ GITHUB_TOKEN is set")
    else:
        print("⚠️  GITHUB_TOKEN not set (optional but recommended)")
        print("💡 Set with: export GITHUB_TOKEN='your_token_here'")
    
    print()


if __name__ == "__main__":
    print("Starting Free Version Demo...\n")
    check_environment()
    success = test_free_version()
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Set GITHUB_TOKEN for higher API limits (optional)")
        print("2. Run: python3 src/main.py --ai-provider huggingface")
        print("3. Or start dashboard: python3 src/main.py --dashboard")
        sys.exit(0)
    else:
        print("\n🔧 Please fix the setup issues and try again")
        sys.exit(1)
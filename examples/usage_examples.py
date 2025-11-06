#!/usr/bin/env python3
"""
Example usage script for AI Repo Scout.
Demonstrates various ways to use the tool programmatically.
"""

import os
import sys
import asyncio
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from github_client import GitHubAPIClient, filter_quality_repos
from enhanced_ai_analyzer import EnhancedAIAnalyzer
from data_analysis import DataAnalysisEngine
from report_generator import ReportGenerator


def example_basic_usage():
    """Example 1: Basic repository discovery and analysis."""
    print("🔍 Example 1: Basic Repository Discovery")
    print("=" * 50)
    
    # Initialize client
    client = GitHubAPIClient()
    
    # Get trending Python repositories
    print("Fetching trending Python repositories...")
    repos = client.get_trending_repos(language="python", since="daily")
    
    print(f"Found {len(repos)} repositories")
    
    # Display top 5
    for i, repo in enumerate(repos[:5], 1):
        print(f"{i}. {repo['name']} ({repo['stars']} stars)")
        print(f"   {repo.get('description', 'No description')[:100]}...")
        print()


def example_ai_analysis():
    """Example 2: AI-powered repository analysis."""
    print("🤖 Example 2: AI-Powered Analysis")
    print("=" * 50)
    
    # Initialize components
    client = GitHubAPIClient()
    ai_analyzer = EnhancedAIAnalyzer()
    
    # Get repositories
    print("Fetching JavaScript repositories...")
    repos = client.get_trending_repos(language="javascript", since="weekly")
    quality_repos = filter_quality_repos(repos, min_stars=50)
    
    if not quality_repos:
        print("No quality repositories found.")
        return
    
    # Generate AI summaries
    print(f"\nGenerating AI summaries for {len(quality_repos[:3])} repositories...")
    for repo in quality_repos[:3]:
        summary = ai_analyzer.summarize_repository(repo)
        print(f"\n📦 {repo['name']}")
        print(f"AI Summary: {summary}")


def example_comprehensive_analysis():
    """Example 3: Comprehensive analysis with insights."""
    print("📊 Example 3: Comprehensive Analysis")
    print("=" * 50)
    
    # Initialize all components
    client = GitHubAPIClient()
    ai_analyzer = EnhancedAIAnalyzer()
    data_engine = DataAnalysisEngine()
    
    # Get multi-language trending repos
    languages = ["python", "javascript", "go"]
    all_repos = []
    
    print("Fetching repositories for multiple languages...")
    for lang in languages:
        repos = client.get_trending_repos(language=lang, since="daily")
        all_repos.extend(repos)
        print(f"  {lang}: {len(repos)} repositories")
    
    # Filter for quality
    quality_repos = filter_quality_repos(all_repos, min_stars=20)
    print(f"\nFiltered to {len(quality_repos)} quality repositories")
    
    # Perform comprehensive analysis
    print("Analyzing repositories...")
    df = data_engine.analyze_repositories(quality_repos)
    
    if df.empty:
        print("No data to analyze.")
        return
    
    # Generate insights
    insights = data_engine.get_trending_insights(df)
    
    # Display results
    print(f"\n📈 Analysis Results:")
    print(f"Total repositories: {insights['summary']['total_repos']}")
    print(f"Average momentum score: {insights['summary']['avg_momentum_score']:.2f}")
    
    print(f"\n🏆 Top 3 by Momentum Score:")
    top_momentum = insights['top_performers']['highest_momentum'][:3]
    for i, repo in enumerate(top_momentum, 1):
        print(f"{i}. {repo['name']} - Score: {repo['momentum_score']:.1f}")
    
    print(f"\n🚀 Language Trends:")
    for lang, stats in list(insights['language_trends'].items())[:5]:
        print(f"  {lang}: {stats['count']} repos, avg momentum: {stats['avg_momentum']:.1f}")
    
    print(f"\n💡 Recommendations:")
    for rec in insights['recommendations'][:3]:
        print(f"  • {rec}")


def example_report_generation():
    """Example 4: Generate reports in different formats."""
    print("📄 Example 4: Report Generation")
    print("=" * 50)
    
    # Initialize components
    client = GitHubAPIClient()
    data_engine = DataAnalysisEngine()
    report_generator = ReportGenerator({
        'formats': ['markdown', 'json'],
        'reports_dir': 'example_reports'
    })
    
    # Get sample data
    print("Fetching sample repositories...")
    repos = client.get_trending_repos(language="typescript", since="daily")
    quality_repos = filter_quality_repos(repos, min_stars=30)[:10]
    
    if not quality_repos:
        print("No repositories found for report generation.")
        return
    
    # Analyze
    df = data_engine.analyze_repositories(quality_repos)
    insights = data_engine.get_trending_insights(df)
    
    # Generate reports
    print("Generating reports...")
    report_files = report_generator.generate_all_reports(df, insights, "daily")
    
    print(f"Generated {len(report_files)} report files:")
    for file_path in report_files:
        print(f"  📄 {file_path}")


def example_similarity_analysis():
    """Example 5: Find similar repositories using AI."""
    print("🔗 Example 5: Repository Similarity Analysis")
    print("=" * 50)
    
    # Initialize components
    client = GitHubAPIClient()
    ai_analyzer = EnhancedAIAnalyzer()
    
    # Get a target repository (example: a popular Python ML library)
    print("Searching for machine learning repositories...")
    ml_repos = client.search_repos("machine learning python", sort="stars")
    
    if len(ml_repos) < 5:
        print("Not enough repositories for similarity analysis.")
        return
    
    target_repo = ml_repos[0]  # Use the most popular one as target
    candidate_repos = ml_repos[1:10]  # Compare against next 9
    
    print(f"\nTarget repository: {target_repo['name']}")
    print(f"Description: {target_repo.get('description', 'No description')}")
    
    # Find similar repositories
    print("\nFinding similar repositories...")
    similar_repos = ai_analyzer.find_similar_repos(target_repo, candidate_repos, top_k=3)
    
    if similar_repos:
        print(f"\nTop 3 similar repositories:")
        for i, (repo, similarity) in enumerate(similar_repos, 1):
            print(f"{i}. {repo['name']} (similarity: {similarity:.3f})")
            print(f"   {repo.get('description', 'No description')[:100]}...")
    else:
        print("No similar repositories found.")


def example_monitoring_setup():
    """Example 6: Set up continuous monitoring."""
    print("⏰ Example 6: Monitoring Setup")
    print("=" * 50)
    
    print("Setting up monitoring configuration...")
    
    config = {
        'languages': ['python', 'javascript', 'rust', 'go'],
        'timeframes': ['daily'],
        'min_stars': 50,
        'report_formats': ['markdown', 'json'],
        'update_frequency': 'daily'
    }
    
    print("Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print("\n📋 To run continuous monitoring:")
    print("python src/main.py --continuous --interval 24")
    
    print("\n📋 To schedule with cron:")
    print("0 6 * * * cd /path/to/AI-Repo-Scout && python src/main.py --timeframe daily")


def main():
    """Run all examples."""
    examples = [
        example_basic_usage,
        example_ai_analysis,
        example_comprehensive_analysis,
        example_report_generation,
        example_similarity_analysis,
        example_monitoring_setup
    ]
    
    print("🚀 AI Repo Scout - Usage Examples")
    print("=" * 60)
    print()
    
    for i, example_func in enumerate(examples, 1):
        try:
            print(f"\n{'='*60}")
            example_func()
            print(f"{'='*60}")
            
            if i < len(examples):
                input("\nPress Enter to continue to next example...")
                
        except KeyboardInterrupt:
            print("\n\nExample execution interrupted.")
            break
        except Exception as e:
            print(f"\n❌ Example failed: {e}")
            continue
    
    print("\n🎉 All examples completed!")
    print("\nNext steps:")
    print("1. Run your own analysis: python src/main.py --timeframe daily")
    print("2. Launch dashboard: streamlit run src/dashboard.py")
    print("3. Check out DEPLOYMENT.md for hosting options")


if __name__ == "__main__":
    main()
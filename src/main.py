"""
Main application for AI Repo Scout.
Orchestrates data collection, analysis, and report generation.
"""

import os
import sys
import argparse
import logging
from datetime import datetime
from typing import Dict, List
import yaml
import json

# Add current directory to Python path
sys.path.append(os.path.dirname(__file__))

from github_client import GitHubAPIClient, filter_quality_repos
from ai_analyzer import AIAnalyzer
from data_analysis import DataAnalysisEngine
from report_generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIRepoScout:
    """Main application class for AI Repo Scout."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the AI Repo Scout application.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self.load_config(config_path)
        self.github_client = GitHubAPIClient()
        self.ai_analyzer = AIAnalyzer()
        self.data_engine = DataAnalysisEngine(self.config.get('scoring', {}))
        self.report_generator = ReportGenerator(self.config.get('output', {}))
        
        logger.info("AI Repo Scout initialized successfully")
    
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            # Try relative path first, then absolute
            if not os.path.exists(config_path):
                config_path = os.path.join(os.path.dirname(__file__), '..', config_path)
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Expand environment variables
            github_token = config.get('github', {}).get('token', '')
            if github_token.startswith('${') and github_token.endswith('}'):
                env_var = github_token[2:-1]
                config['github']['token'] = os.getenv(env_var, '')
            
            logger.info(f"Configuration loaded from {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return self.default_config()
    
    def default_config(self) -> Dict:
        """Return default configuration."""
        return {
            'github': {
                'max_repos': 100,
                'token': os.getenv('GITHUB_TOKEN', '')
            },
            'data': {
                'trending_timeframes': ['daily'],
                'languages': ['python', 'javascript', 'typescript'],
                'min_stars': 10
            },
            'output': {
                'formats': ['markdown', 'json'],
                'reports_dir': 'reports'
            }
        }
    
    def collect_trending_data(self, languages: List[str] = None, timeframe: str = "daily") -> List[Dict]:
        """Collect trending repository data from GitHub.
        
        Args:
            languages: List of programming languages to fetch
            timeframe: Time period for trending ('daily', 'weekly', 'monthly')
            
        Returns:
            List of repository dictionaries
        """
        languages = languages or self.config.get('data', {}).get('languages', ['python'])
        max_repos = self.config.get('github', {}).get('max_repos', 100)
        
        logger.info(f"Collecting trending {timeframe} repositories for: {', '.join(languages)}")
        
        all_repos = []
        
        for language in languages:
            try:
                logger.info(f"Fetching {language} repositories...")
                repos = self.github_client.get_trending_repos(language=language, since=timeframe)
                all_repos.extend(repos)
                
                logger.info(f"Found {len(repos)} {language} repositories")
                
            except Exception as e:
                logger.error(f"Failed to fetch {language} repositories: {e}")
        
        # Remove duplicates based on full_name
        seen = set()
        unique_repos = []
        for repo in all_repos:
            if repo.get('full_name') not in seen:
                seen.add(repo.get('full_name'))
                unique_repos.append(repo)
        
        logger.info(f"Collected {len(unique_repos)} unique repositories")
        
        # Filter for quality
        min_stars = self.config.get('data', {}).get('min_stars', 10)
        quality_repos = filter_quality_repos(unique_repos, min_stars=min_stars)
        
        logger.info(f"Filtered to {len(quality_repos)} quality repositories")
        
        return quality_repos[:max_repos]
    
    def analyze_repositories(self, repos: List[Dict]) -> tuple:
        """Analyze repositories using AI and data analysis engines.
        
        Args:
            repos: List of repository dictionaries
            
        Returns:
            Tuple of (analyzed_dataframe, insights_dict)
        """
        if not repos:
            logger.warning("No repositories to analyze")
            return None, {}
        
        logger.info(f"Analyzing {len(repos)} repositories...")
        
        # Data analysis
        df = self.data_engine.analyze_repositories(repos)
        
        # Generate insights
        insights = self.data_engine.get_trending_insights(df)
        
        # Add AI-powered analysis
        try:
            ai_insights = self.ai_analyzer.generate_insights(repos)
            insights['ai_analysis'] = ai_insights
            
            # Add repository summaries for top repos
            top_repos = df.head(10) if not df.empty else []
            summaries = {}
            
            for _, repo in top_repos.iterrows():
                repo_dict = repo.to_dict()
                summary = self.ai_analyzer.summarize_repository(repo_dict)
                summaries[repo_dict.get('full_name', 'unknown')] = summary
            
            insights['ai_summaries'] = summaries
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            insights['ai_analysis'] = {"error": str(e)}
        
        logger.info("Repository analysis completed")
        return df, insights
    
    def generate_reports(self, df, insights: Dict, timeframe: str = "daily") -> List[str]:
        """Generate reports in various formats.
        
        Args:
            df: Analyzed repository DataFrame
            insights: Analysis insights dictionary
            timeframe: Timeframe for the report
            
        Returns:
            List of generated report file paths
        """
        logger.info("Generating reports...")
        
        report_files = self.report_generator.generate_all_reports(df, insights, timeframe)
        
        logger.info(f"Generated {len(report_files)} report files")
        return report_files
    
    def run_full_analysis(self, timeframe: str = "daily", languages: List[str] = None) -> Dict:
        """Run a complete analysis cycle.
        
        Args:
            timeframe: Time period for trending analysis
            languages: Programming languages to analyze
            
        Returns:
            Dictionary with analysis results and report paths
        """
        logger.info(f"Starting full analysis for {timeframe} trending repositories")
        
        start_time = datetime.now()
        
        try:
            # Step 1: Collect data
            repos = self.collect_trending_data(languages, timeframe)
            
            if not repos:
                logger.error("No repositories collected. Aborting analysis.")
                return {"error": "No repositories found"}
            
            # Step 2: Analyze data
            df, insights = self.analyze_repositories(repos)
            
            # Step 3: Generate reports
            report_files = self.generate_reports(df, insights, timeframe)
            
            # Step 4: Export analysis data
            data_files = []
            if df is not None and not df.empty:
                csv_path, json_path = self.data_engine.export_analysis(df, insights)
                data_files = [csv_path, json_path]
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results = {
                "success": True,
                "timestamp": end_time.isoformat(),
                "duration_seconds": duration,
                "repositories_analyzed": len(repos),
                "report_files": report_files,
                "data_files": data_files,
                "insights_summary": {
                    "total_repos": insights.get('summary', {}).get('total_repos', 0),
                    "avg_momentum": insights.get('summary', {}).get('avg_momentum_score', 0),
                    "top_languages": list(insights.get('language_trends', {}).keys())[:5],
                    "recommendations": insights.get('recommendations', [])
                }
            }
            
            logger.info(f"Full analysis completed in {duration:.2f} seconds")
            return results
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def run_continuous_monitoring(self, interval_hours: int = 24):
        """Run continuous monitoring with scheduled analysis."""
        import time
        
        logger.info(f"Starting continuous monitoring (interval: {interval_hours} hours)")
        
        while True:
            try:
                # Run analysis for different timeframes
                for timeframe in self.config.get('data', {}).get('trending_timeframes', ['daily']):
                    results = self.run_full_analysis(timeframe)
                    
                    if results.get('success'):
                        logger.info(f"Successfully completed {timeframe} analysis")
                    else:
                        logger.error(f"Failed {timeframe} analysis: {results.get('error')}")
                
                # Sleep until next interval
                sleep_seconds = interval_hours * 3600
                logger.info(f"Sleeping for {interval_hours} hours...")
                time.sleep(sleep_seconds)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(300)  # Sleep 5 minutes on error


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="AI Repo Scout - Discover trending repositories")
    
    parser.add_argument(
        '--config',
        default='config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--timeframe',
        choices=['daily', 'weekly', 'monthly'],
        default='daily',
        help='Trending timeframe'
    )
    
    parser.add_argument(
        '--languages',
        nargs='+',
        help='Programming languages to analyze'
    )
    
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run in continuous monitoring mode'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=24,
        help='Interval in hours for continuous monitoring'
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Launch Streamlit dashboard'
    )
    
    args = parser.parse_args()
    
    # Initialize application
    scout = AIRepoScout(args.config)
    
    if args.dashboard:
        # Launch Streamlit dashboard
        import subprocess
        dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard.py')
        subprocess.run(['streamlit', 'run', dashboard_path])
        
    elif args.continuous:
        # Run continuous monitoring
        scout.run_continuous_monitoring(args.interval)
        
    else:
        # Run single analysis
        results = scout.run_full_analysis(args.timeframe, args.languages)
        
        if results.get('success'):
            print("✅ Analysis completed successfully!")
            print(f"📊 Analyzed {results['repositories_analyzed']} repositories")
            print(f"⏱️  Duration: {results['duration_seconds']:.2f} seconds")
            print(f"📁 Reports generated: {len(results['report_files'])}")
            
            if results['insights_summary']['recommendations']:
                print("\n🎯 Key Recommendations:")
                for rec in results['insights_summary']['recommendations']:
                    print(f"  • {rec}")
        else:
            print(f"❌ Analysis failed: {results.get('error')}")
            sys.exit(1)


if __name__ == "__main__":
    main()
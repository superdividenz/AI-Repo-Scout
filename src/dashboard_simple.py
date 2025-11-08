"""
Simple Streamlit dashboard for AI Repo Scout - Free Version.
Displays trending repositories and insights in a clean web interface.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys
import glob

# Add src directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from github_client import GitHubAPIClient, filter_quality_repos
    from simple_ai_analyzer import EnhancedAIAnalyzer
    from data_analysis import DataAnalysisEngine
    import yaml
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="🚀 AI Repo Scout - Free Version",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .repo-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: white;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


class RepoScoutDashboard:
    """Streamlit dashboard for AI Repo Scout."""
    
    def __init__(self):
        self.github_client = None
        self.ai_analyzer = None
        self.data_engine = None
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from YAML file."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
        except Exception as e:
            st.warning(f"Could not load config: {e}")
        
        return {
            'models': {'provider': 'huggingface'},
            'data': {'languages': ['python', 'javascript', 'typescript']},
            'github': {'max_repos': 50}
        }
    
    def initialize_clients(self):
        """Initialize API clients."""
        if self.github_client is None:
            try:
                self.github_client = GitHubAPIClient()
                self.ai_analyzer = EnhancedAIAnalyzer(self.config)
                self.data_engine = DataAnalysisEngine({})
                return True
            except Exception as e:
                st.error(f"Failed to initialize clients: {e}")
                return False
        return True
    
    def load_recent_data(self):
        """Load the most recent analysis data."""
        try:
            # Look for recent data files
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            if os.path.exists(data_dir):
                csv_files = glob.glob(os.path.join(data_dir, 'analysis_*.csv'))
                json_files = glob.glob(os.path.join(data_dir, 'insights_*.json'))
                
                if csv_files and json_files:
                    # Load the most recent files
                    latest_csv = max(csv_files, key=os.path.getctime)
                    latest_json = max(json_files, key=os.path.getctime)
                    
                    df = pd.read_csv(latest_csv)
                    with open(latest_json, 'r') as f:
                        insights = json.load(f)
                    
                    return df, insights
        except Exception as e:
            st.warning(f"Could not load recent data: {e}")
        
        return None, None
    
    def run_live_analysis(self, languages, timeframe):
        """Run live analysis with current settings."""
        if not self.initialize_clients():
            return None, None
        
        try:
            with st.spinner(f"Fetching {timeframe} trending repositories for {', '.join(languages)}..."):
                # Collect data
                all_repos = []
                for language in languages:
                    repos = self.github_client.get_trending_repos(language=language, since=timeframe)
                    all_repos.extend(repos)
                
                # Remove duplicates and filter
                seen = set()
                unique_repos = []
                for repo in all_repos:
                    if repo.get('full_name') not in seen:
                        seen.add(repo.get('full_name'))
                        unique_repos.append(repo)
                
                quality_repos = filter_quality_repos(unique_repos, min_stars=10)[:20]  # Limit for demo
                
                if not quality_repos:
                    st.warning("No repositories found matching criteria")
                    return None, None
                
                # Analyze data
                df = self.data_engine.analyze_repositories(quality_repos)
                insights = self.ai_analyzer.analyze_trends(quality_repos)
                
                return df, insights
                
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            return None, None
    
    def display_metrics(self, df, insights):
        """Display key metrics."""
        if df is None or df.empty:
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Repositories", len(df))
        
        with col2:
            avg_momentum = df['momentum_score'].mean() if 'momentum_score' in df.columns else 0
            st.metric("Avg Momentum Score", f"{avg_momentum:.1f}/100")
        
        with col3:
            total_stars = df['stars'].sum() if 'stars' in df.columns else 0
            st.metric("Total Stars", f"{total_stars:,}")
        
        with col4:
            high_momentum = len(df[df['momentum_score'] > 70]) if 'momentum_score' in df.columns else 0
            st.metric("High Momentum", high_momentum)
    
    def display_top_repositories(self, df):
        """Display top repositories."""
        if df is None or df.empty:
            return
        
        st.subheader("🔥 Top Trending Repositories")
        
        # Sort by momentum score
        if 'momentum_score' in df.columns:
            top_repos = df.nlargest(10, 'momentum_score')
        else:
            top_repos = df.head(10)
        
        for idx, repo in top_repos.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="repo-card">
                    <h4>🚀 {repo.get('name', 'Unknown')} ({repo.get('language', 'N/A')})</h4>
                    <p><strong>Description:</strong> {repo.get('description', 'No description')[:200]}...</p>
                    <div style="display: flex; gap: 20px; margin-top: 10px;">
                        <span>⭐ {repo.get('stars', 0):,} stars</span>
                        <span>🍴 {repo.get('forks', 0)} forks</span>
                        <span>🏃 Momentum: {repo.get('momentum_score', 0):.1f}/100</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    def display_insights(self, insights):
        """Display AI-generated insights."""
        if not insights:
            return
        
        st.subheader("🧠 AI Insights")
        
        # Language trends
        if insights.get('language_trends'):
            st.write("**📊 Top Programming Languages:**")
            lang_data = insights['language_trends']
            for lang, count in list(lang_data.items())[:5]:
                st.write(f"- {lang}: {count} repositories")
        
        # Category trends
        if insights.get('category_trends'):
            st.write("**🏷️ Trending Categories:**")
            cat_data = insights['category_trends']
            for cat, count in list(cat_data.items())[:5]:
                st.write(f"- {cat.title()}: {count} projects")
        
        # Recommendations
        if insights.get('recommendations'):
            st.write("**💡 Key Recommendations:**")
            for rec in insights['recommendations'][:5]:
                st.write(f"- {rec}")
    
    def run(self):
        """Main dashboard application."""
        # Header
        st.markdown('<div class="main-header">🚀 AI Repo Scout Dashboard</div>', unsafe_allow_html=True)
        st.markdown("**Discover trending repositories with AI-powered insights**")
        
        # Sidebar controls
        st.sidebar.header("🎛️ Analysis Settings")
        
        # Data source options
        data_source = st.sidebar.radio(
            "Data Source",
            ["Load Recent Analysis", "Run Live Analysis"],
            help="Load recent data or fetch fresh data from GitHub"
        )
        
        df, insights = None, None
        
        if data_source == "Load Recent Analysis":
            df, insights = self.load_recent_data()
            if df is not None:
                st.sidebar.success(f"✅ Loaded {len(df)} repositories from recent analysis")
            else:
                st.sidebar.warning("⚠️ No recent data found. Try 'Run Live Analysis'")
        
        else:  # Live Analysis
            languages = st.sidebar.multiselect(
                "Programming Languages",
                ["python", "javascript", "typescript", "go", "rust", "java", "kotlin", "swift"],
                default=["python"],
                help="Select programming languages to analyze"
            )
            
            timeframe = st.sidebar.selectbox(
                "Trending Timeframe",
                ["daily", "weekly", "monthly"],
                help="Time period for trending analysis"
            )
            
            if st.sidebar.button("🚀 Run Analysis", type="primary"):
                df, insights = self.run_live_analysis(languages, timeframe)
        
        # Main content
        if df is not None and not df.empty:
            # Success message
            st.markdown(f"""
            <div class="success-box">
                <h4>✅ Analysis Complete!</h4>
                <p>Successfully analyzed <strong>{len(df)}</strong> repositories. 
                Explore the results below.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display metrics
            self.display_metrics(df, insights)
            
            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["📊 Top Repositories", "🧠 AI Insights", "📈 Data Explorer"])
            
            with tab1:
                self.display_top_repositories(df)
            
            with tab2:
                self.display_insights(insights)
            
            with tab3:
                st.subheader("📈 Raw Data")
                st.write("**Repository Analysis Data:**")
                # Display selected columns
                display_columns = [col for col in df.columns if col in 
                                 ['name', 'language', 'stars', 'forks', 'momentum_score', 'star_velocity']]
                if display_columns:
                    st.dataframe(df[display_columns], use_container_width=True)
                else:
                    st.dataframe(df, use_container_width=True)
        
        else:
            # Welcome message
            st.markdown("""
            ## 👋 Welcome to AI Repo Scout!
            
            **Free Version Features:**
            - 🔍 GitHub API integration (trending repositories)
            - 🧠 Lightweight AI analysis (repository categorization)  
            - 📊 Statistical trend analysis (momentum scoring)
            - 📈 Growth prediction and insights
            - 🎯 Actionable recommendations
            
            **Get Started:**
            1. Choose "Run Live Analysis" in the sidebar
            2. Select programming languages to analyze
            3. Pick a timeframe (daily/weekly/monthly)
            4. Click "🚀 Run Analysis" 
            
            **Tips:**
            - Add a GitHub token to increase API limits from 60 to 5000/hour
            - Recent analysis data loads faster than live analysis
            - Try different language combinations for broader insights
            """)
        
        # Footer
        st.markdown("---")
        st.markdown("**🚀 AI Repo Scout** - Discover trending repositories with AI insights | Free Version")


# Run the dashboard
if __name__ == "__main__":
    dashboard = RepoScoutDashboard()
    dashboard.run()
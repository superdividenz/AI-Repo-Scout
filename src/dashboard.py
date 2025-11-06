"""
Interactive Streamlit dashboard for AI Repo Scout.
Displays trending repositories, insights, and analytics in a beautiful web interface.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__)))

from github_client import GitHubAPIClient, filter_quality_repos
from enhanced_ai_analyzer import EnhancedAIAnalyzer
from data_analysis import DataAnalysisEngine
import yaml

# Page configuration
st.set_page_config(
    page_title="🚀 AI Repo Scout",
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
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: white;
    }
    .trending-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    .language-tag {
        background-color: #007acc;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 10px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


class RepoScoutDashboard:
    """Main dashboard class for AI Repo Scout."""
    
    def __init__(self):
        """Initialize the dashboard components."""
        self.github_client = None
        self.ai_analyzer = None
        self.data_engine = None
        self.config = self.load_config()
        
    def load_config(self) -> dict:
        """Load configuration from YAML file."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            st.error(f"Failed to load config: {e}")
            return {}
    
    @st.cache_resource
    def initialize_clients(_self):
        """Initialize API clients with caching."""
        try:
            github_client = GitHubAPIClient()
            ai_analyzer = EnhancedAIAnalyzer()
            data_engine = DataAnalysisEngine()
            return github_client, ai_analyzer, data_engine
        except Exception as e:
            st.error(f"Failed to initialize clients: {e}")
            return None, None, None
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def fetch_trending_data(_self, languages: list, timeframe: str = "daily") -> pd.DataFrame:
        """Fetch and cache trending repository data."""
        if not _self.github_client:
            return pd.DataFrame()
        
        all_repos = []
        
        # Progress bar for data fetching
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, language in enumerate(languages):
            status_text.text(f"Fetching {language} repositories...")
            
            try:
                repos = _self.github_client.get_trending_repos(language=language, since=timeframe)
                all_repos.extend(repos)
                progress_bar.progress((i + 1) / len(languages))
            except Exception as e:
                st.warning(f"Failed to fetch {language} repositories: {e}")
        
        progress_bar.empty()
        status_text.empty()
        
        if not all_repos:
            return pd.DataFrame()
        
        # Filter quality repositories
        quality_repos = filter_quality_repos(all_repos)
        
        # Convert to DataFrame and analyze
        if _self.data_engine:
            df = _self.data_engine.analyze_repositories(quality_repos)
            return df
        
        return pd.DataFrame(quality_repos)
    
    def render_header(self):
        """Render the main header."""
        st.markdown('<h1 class="main-header">🚀 AI Repo Scout</h1>', unsafe_allow_html=True)
        st.markdown("**Discover trending GitHub repositories with AI-powered insights**")
        st.markdown("---")
    
    def render_sidebar(self):
        """Render the sidebar with controls."""
        st.sidebar.header("🔧 Configuration")
        
        # Language selection
        available_languages = ["python", "javascript", "typescript", "go", "rust", "java", "cpp", "csharp", "php", "ruby"]
        selected_languages = st.sidebar.multiselect(
            "Programming Languages",
            available_languages,
            default=["python", "javascript", "typescript"]
        )
        
        # Timeframe selection
        timeframe = st.sidebar.selectbox(
            "Trending Timeframe",
            ["daily", "weekly", "monthly"],
            index=0
        )
        
        # Minimum stars filter
        min_stars = st.sidebar.slider(
            "Minimum Stars",
            min_value=1,
            max_value=1000,
            value=10,
            step=10
        )
        
        # Repository count
        max_repos = st.sidebar.slider(
            "Max Repositories to Display",
            min_value=10,
            max_value=100,
            value=50,
            step=10
        )
        
        # Refresh button
        if st.sidebar.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.experimental_rerun()
        
        return {
            'languages': selected_languages,
            'timeframe': timeframe,
            'min_stars': min_stars,
            'max_repos': max_repos
        }
    
    def render_metrics_overview(self, df: pd.DataFrame):
        """Render key metrics overview."""
        if df.empty:
            st.warning("No data available for metrics overview.")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Repositories",
                value=len(df),
                delta=f"+{len(df[df['age_days'] <= 7])}" if 'age_days' in df.columns else None
            )
        
        with col2:
            avg_momentum = df['momentum_score'].mean() if 'momentum_score' in df.columns else 0
            st.metric(
                label="Avg Momentum Score",
                value=f"{avg_momentum:.1f}",
                delta=f"+{len(df[df.get('momentum_score', 0) > avg_momentum])}"
            )
        
        with col3:
            total_stars = df['stars'].sum() if 'stars' in df.columns else 0
            st.metric(
                label="Total Stars",
                value=f"{total_stars:,}",
                delta=f"{df['star_velocity'].sum():.1f}/day" if 'star_velocity' in df.columns else None
            )
        
        with col4:
            top_languages = df['language'].value_counts().head(3).to_dict() if 'language' in df.columns else {}
            top_lang = list(top_languages.keys())[0] if top_languages else "N/A"
            st.metric(
                label="Top Language",
                value=top_lang,
                delta=f"{top_languages.get(top_lang, 0)} repos" if top_languages else None
            )
    
    def render_trending_repos(self, df: pd.DataFrame, max_repos: int):
        """Render the main trending repositories list."""
        if df.empty:
            st.warning("No trending repositories found. Try adjusting your filters.")
            return
        
        st.subheader("🔥 Trending Repositories")
        
        # Display options
        col1, col2 = st.columns([3, 1])
        with col1:
            sort_options = {
                "Momentum Score": "momentum_score",
                "Stars": "stars",
                "Star Velocity": "star_velocity",
                "Growth Potential": "growth_potential"
            }
            sort_by = st.selectbox("Sort by:", list(sort_options.keys()))
        
        with col2:
            view_mode = st.radio("View:", ["Cards", "Table"], horizontal=True)
        
        # Sort dataframe
        sort_column = sort_options[sort_by]
        if sort_column in df.columns:
            df_sorted = df.sort_values(sort_column, ascending=False).head(max_repos)
        else:
            df_sorted = df.head(max_repos)
        
        if view_mode == "Cards":
            self.render_repo_cards(df_sorted)
        else:
            self.render_repo_table(df_sorted)
    
    def render_repo_cards(self, df: pd.DataFrame):
        """Render repositories as cards."""
        for idx, repo in df.iterrows():
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Repository header
                    momentum_score = repo.get('momentum_score', 0)
                    momentum_badge = f'<span class="trending-badge">🔥 {momentum_score:.1f}</span>' if momentum_score > 70 else ''
                    
                    st.markdown(f"""
                    <div class="repo-card">
                        <h4><a href="{repo.get('html_url', '#')}" target="_blank">{repo.get('name', 'Unknown')}</a> {momentum_badge}</h4>
                        <p><strong>{repo.get('full_name', '')}</strong></p>
                        <p>{repo.get('description', 'No description available')[:200]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Metrics
                    st.metric("Stars", f"{repo.get('stars', 0):,}")
                    st.metric("Forks", f"{repo.get('forks', 0):,}")
                    if 'star_velocity' in repo:
                        st.metric("Growth", f"{repo['star_velocity']:.1f}/day")
                
                # Tags and language
                tags = []
                if repo.get('language'):
                    tags.append(f'<span class="language-tag">{repo["language"]}</span>')
                
                topics = repo.get('topics', [])
                if isinstance(topics, list) and topics:
                    for topic in topics[:3]:  # Show first 3 topics
                        tags.append(f'<span class="language-tag">{topic}</span>')
                
                if tags:
                    st.markdown(" ".join(tags), unsafe_allow_html=True)
                
                st.markdown("---")
    
    def render_repo_table(self, df: pd.DataFrame):
        """Render repositories as a table."""
        display_columns = [
            'name', 'language', 'stars', 'forks', 'momentum_score', 
            'star_velocity', 'contributors', 'html_url'
        ]
        
        # Filter columns that exist in the dataframe
        available_columns = [col for col in display_columns if col in df.columns]
        
        if available_columns:
            # Format the dataframe for display
            display_df = df[available_columns].copy()
            
            # Format numerical columns
            for col in ['stars', 'forks', 'contributors']:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:,}" if pd.notna(x) else "0")
            
            for col in ['momentum_score', 'star_velocity']:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "0.0")
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=600
            )
    
    def render_analytics(self, df: pd.DataFrame):
        """Render analytics charts and insights."""
        if df.empty:
            return
        
        st.subheader("📊 Analytics & Insights")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Language Trends", "Growth Patterns", "Repository Types", "AI Insights"])
        
        with tab1:
            self.render_language_analytics(df)
        
        with tab2:
            self.render_growth_analytics(df)
        
        with tab3:
            self.render_type_analytics(df)
        
        with tab4:
            self.render_ai_insights(df)
    
    def render_language_analytics(self, df: pd.DataFrame):
        """Render language-based analytics."""
        if 'language' not in df.columns:
            st.warning("Language data not available.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Language distribution
            lang_counts = df['language'].value_counts().head(10)
            fig = px.bar(
                x=lang_counts.values,
                y=lang_counts.index,
                orientation='h',
                title="Top Programming Languages",
                labels={'x': 'Number of Repositories', 'y': 'Language'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Average momentum by language
            if 'momentum_score' in df.columns:
                lang_momentum = df.groupby('language')['momentum_score'].mean().sort_values(ascending=False).head(10)
                fig = px.bar(
                    x=lang_momentum.index,
                    y=lang_momentum.values,
                    title="Average Momentum Score by Language",
                    labels={'x': 'Language', 'y': 'Momentum Score'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    def render_growth_analytics(self, df: pd.DataFrame):
        """Render growth pattern analytics."""
        col1, col2 = st.columns(2)
        
        with col1:
            # Stars vs. Age scatter plot
            if all(col in df.columns for col in ['age_days', 'stars']):
                fig = px.scatter(
                    df,
                    x='age_days',
                    y='stars',
                    color='language' if 'language' in df.columns else None,
                    size='momentum_score' if 'momentum_score' in df.columns else None,
                    title="Repository Growth Over Time",
                    labels={'age_days': 'Age (Days)', 'stars': 'Stars'},
                    hover_data=['name']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Momentum score distribution
            if 'momentum_score' in df.columns:
                fig = px.histogram(
                    df,
                    x='momentum_score',
                    nbins=20,
                    title="Momentum Score Distribution",
                    labels={'momentum_score': 'Momentum Score', 'count': 'Number of Repositories'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    def render_type_analytics(self, df: pd.DataFrame):
        """Render repository type analytics."""
        if 'repo_type' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Repository types pie chart
                type_counts = df['repo_type'].value_counts()
                fig = px.pie(
                    values=type_counts.values,
                    names=type_counts.index,
                    title="Repository Types Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Growth potential by type
                if 'growth_potential' in df.columns:
                    growth_by_type = df.groupby('repo_type')['growth_potential'].mean().sort_values(ascending=False)
                    fig = px.bar(
                        x=growth_by_type.index,
                        y=growth_by_type.values,
                        title="Average Growth Potential by Type",
                        labels={'x': 'Repository Type', 'y': 'Growth Potential'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    def render_ai_insights(self, df: pd.DataFrame):
        """Render AI-generated insights."""
        if not self.ai_analyzer or df.empty:
            st.warning("AI insights not available.")
            return
        
        try:
            with st.spinner("Generating AI insights..."):
                insights = self.ai_analyzer.generate_insights(df.to_dict('records'))
            
            # Display insights
            st.subheader("🤖 AI-Generated Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Top Trending Topics:**")
                if 'trending_topics' in insights:
                    topics = dict(list(insights['trending_topics'].items())[:10])
                    for topic, count in topics.items():
                        st.write(f"• {topic}: {count} repositories")
            
            with col2:
                st.write("**Category Distribution:**")
                if 'categories' in insights:
                    for category, repos in insights['categories'].items():
                        st.write(f"• {category}: {len(repos)} repositories")
            
            # Generate repository summaries for top repos
            if len(df) > 0:
                st.subheader("🎯 AI Repository Summaries")
                top_repos = df.head(5)
                
                for _, repo in top_repos.iterrows():
                    summary = self.ai_analyzer.summarize_repository(repo.to_dict())
                    st.write(f"**{repo.get('name', 'Unknown')}**: {summary}")
        
        except Exception as e:
            st.error(f"Failed to generate AI insights: {e}")
    
    def run(self):
        """Main dashboard application."""
        self.render_header()
        
        # Initialize clients
        self.github_client, self.ai_analyzer, self.data_engine = self.initialize_clients()
        
        if not self.github_client:
            st.error("Failed to initialize GitHub client. Please check your configuration.")
            return
        
        # Sidebar controls
        params = self.render_sidebar()
        
        if not params['languages']:
            st.warning("Please select at least one programming language.")
            return
        
        # Fetch data
        with st.spinner("Fetching trending repositories..."):
            df = self.fetch_trending_data(params['languages'], params['timeframe'])
        
        if df.empty:
            st.error("No repositories found. Please try different filters.")
            return
        
        # Filter by minimum stars
        if 'stars' in df.columns:
            df = df[df['stars'] >= params['min_stars']]
        
        # Render main content
        self.render_metrics_overview(df)
        st.markdown("---")
        
        self.render_trending_repos(df, params['max_repos'])
        st.markdown("---")
        
        self.render_analytics(df)


# Run the dashboard
if __name__ == "__main__":
    dashboard = RepoScoutDashboard()
    dashboard.run()
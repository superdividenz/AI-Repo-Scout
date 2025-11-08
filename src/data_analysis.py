"""
Advanced data analysis engine for repository trends and insights.
Provides scoring algorithms, trend analysis, and predictive metrics.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import logging
from dataclasses import dataclass
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TrendMetrics:
    """Container for trend analysis metrics."""
    star_velocity: float
    growth_rate: float
    momentum_score: float
    engagement_ratio: float
    contributor_velocity: float
    activity_score: float
    freshness_score: float
    quality_score: float


class DataAnalysisEngine:
    """Advanced analysis engine for repository data and trends."""
    
    def __init__(self, config: Dict = None):
        """Initialize the analysis engine.
        
        Args:
            config: Configuration dictionary for scoring weights
        """
        # If config is provided but doesn't have the expected structure, merge with defaults
        default_config = self._default_config()
        if config:
            # Merge provided config with defaults
            for key in default_config:
                if key in config:
                    if isinstance(config[key], dict) and isinstance(default_config[key], dict):
                        default_config[key].update(config[key])
                    else:
                        default_config[key] = config[key]
        self.config = default_config
        self.scaler = MinMaxScaler()
        
    def _default_config(self) -> Dict:
        """Default configuration for analysis parameters."""
        return {
            'scoring_weights': {
                'star_velocity': 0.25,
                'growth_rate': 0.20,
                'engagement': 0.15,
                'contributor_velocity': 0.15,
                'activity': 0.10,
                'freshness': 0.10,
                'quality': 0.05
            },
            'thresholds': {
                'min_stars': 10,
                'min_contributors': 2,
                'max_age_days': 365,
                'min_activity_score': 0.1
            },
            'normalization': {
                'star_velocity_cap': 50,  # Stars per day
                'growth_rate_cap': 10,    # Multiple of initial stars
                'activity_cap': 100       # Commits per week
            }
        }
    
    def analyze_repositories(self, repos: List[Dict]) -> pd.DataFrame:
        """Perform comprehensive analysis on repository data.
        
        Args:
            repos: List of repository dictionaries
            
        Returns:
            DataFrame with enriched analysis results
        """
        logger.info(f"Analyzing {len(repos)} repositories...")
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(repos)
        
        if df.empty:
            logger.warning("No repositories to analyze")
            return df
        
        # Calculate advanced metrics
        df = self._calculate_trend_metrics(df)
        df = self._calculate_momentum_scores(df)
        df = self._calculate_engagement_metrics(df)
        df = self._classify_repository_types(df)
        df = self._predict_growth_potential(df)
        
        # Sort by overall score
        df = df.sort_values('momentum_score', ascending=False)
        
        logger.info("Repository analysis completed")
        return df
    
    def _calculate_trend_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate various trend metrics for repositories."""
        
        # Convert date strings to datetime and make timezone-naive for comparison
        df['created_at'] = pd.to_datetime(df['created_at']).dt.tz_localize(None)
        df['updated_at'] = pd.to_datetime(df['updated_at']).dt.tz_localize(None)
        
        # Calculate age and time-based metrics
        now = datetime.now()
        df['age_days'] = (now - df['created_at']).dt.days
        df['days_since_update'] = (now - df['updated_at']).dt.days
        
        # Star velocity (stars per day)
        df['star_velocity'] = df['stars'] / np.maximum(df['age_days'], 1)
        
        # Growth rate (relative to repository age)
        df['growth_rate'] = np.where(
            df['age_days'] > 30,
            df['stars'] / (df['age_days'] / 30),  # Stars per month
            df['stars'] * 30 / np.maximum(df['age_days'], 1)  # Projected monthly growth
        )
        
        # Contributor velocity
        df['contributor_velocity'] = df['contributors'] / np.maximum(df['age_days'], 1) * 30  # Contributors per month
        
        # Activity score (based on recent commits)
        df['activity_score'] = np.minimum(df['recent_commits'] / 10, 1.0)  # Normalized to 0-1
        
        # Freshness score (newer is better)
        max_age = self.config['thresholds']['max_age_days']
        df['freshness_score'] = np.maximum(1 - (df['age_days'] / max_age), 0)
        
        return df
    
    def _calculate_momentum_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive momentum scores."""
        weights = self.config['scoring_weights']
        caps = self.config['normalization']
        
        # Normalize metrics to 0-1 scale
        metrics = {}
        
        # Star velocity (capped and normalized)
        metrics['star_velocity_norm'] = np.minimum(df['star_velocity'] / caps['star_velocity_cap'], 1.0)
        
        # Growth rate (capped and normalized)
        metrics['growth_rate_norm'] = np.minimum(df['growth_rate'] / caps['growth_rate_cap'], 1.0)
        
        # Engagement ratio (issues + forks relative to stars)
        total_engagement = df['issues'] + df['forks']
        metrics['engagement_norm'] = np.minimum(total_engagement / np.maximum(df['stars'], 1), 1.0)
        
        # Contributor velocity (normalized)
        metrics['contributor_velocity_norm'] = np.minimum(df['contributor_velocity'] / 5, 1.0)  # Cap at 5 contributors/month
        
        # Activity score (already normalized)
        metrics['activity_norm'] = df['activity_score']
        
        # Freshness score (already normalized)
        metrics['freshness_norm'] = df['freshness_score']
        
        # Quality score (based on description, topics, etc.)
        quality_factors = []
        quality_factors.append((df['description'].str.len() > 20).astype(float) * 0.3)  # Has good description
        quality_factors.append((df['topics'].str.len() > 0).astype(float) * 0.3)  # Has topics
        quality_factors.append((df['license'].notna()).astype(float) * 0.2)  # Has license
        quality_factors.append(np.minimum(df['contributors'] / 10, 1.0) * 0.2)  # Multiple contributors
        
        metrics['quality_norm'] = sum(quality_factors)
        
        # Calculate weighted momentum score
        momentum_components = [
            weights['star_velocity'] * metrics['star_velocity_norm'],
            weights['growth_rate'] * metrics['growth_rate_norm'],
            weights['engagement'] * metrics['engagement_norm'],
            weights['contributor_velocity'] * metrics['contributor_velocity_norm'],
            weights['activity'] * metrics['activity_norm'],
            weights['freshness'] * metrics['freshness_norm'],
            weights['quality'] * metrics['quality_norm']
        ]
        
        df['momentum_score'] = sum(momentum_components) * 100  # Scale to 0-100
        
        # Add individual normalized metrics to DataFrame
        for metric_name, values in metrics.items():
            df[metric_name] = values
        
        return df
    
    def _calculate_engagement_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate detailed engagement and community metrics."""
        
        # Fork ratio (forks relative to stars)
        df['fork_ratio'] = df['forks'] / np.maximum(df['stars'], 1)
        
        # Issue ratio (open issues relative to stars)
        df['issue_ratio'] = df['issues'] / np.maximum(df['stars'], 1)
        
        # Community engagement score
        engagement_factors = [
            np.minimum(df['fork_ratio'] * 2, 1.0),  # Normalize fork ratio
            np.minimum(df['issue_ratio'] * 5, 1.0),  # Normalize issue ratio
            np.minimum(df['contributors'] / df['stars'] * 100, 1.0),  # Contributor ratio
            df['activity_score']  # Recent activity
        ]
        
        df['engagement_score'] = np.mean(engagement_factors, axis=0) * 100
        
        # Calculate trend direction
        df['trend_direction'] = self._calculate_trend_direction(df)
        
        return df
    
    def _calculate_trend_direction(self, df: pd.DataFrame) -> np.ndarray:
        """Calculate trend direction: rising, stable, or declining."""
        directions = []
        
        for _, repo in df.iterrows():
            # Use days since last update as a proxy for activity trend
            days_inactive = repo['days_since_update']
            
            if days_inactive <= 7:
                direction = "rising"
            elif days_inactive <= 30:
                direction = "stable"
            else:
                direction = "declining"
            
            directions.append(direction)
        
        return np.array(directions)
    
    def _classify_repository_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify repositories into different types based on characteristics."""
        
        def classify_repo(repo):
            stars = repo['stars']
            age_days = repo['age_days']
            contributors = repo['contributors']
            
            # Viral: High stars, recent creation
            if stars > 1000 and age_days < 90:
                return "viral"
            
            # Established: High stars, older
            elif stars > 5000 and age_days > 365:
                return "established"
            
            # Rising: Good momentum, moderate age
            elif repo['momentum_score'] > 70 and 30 < age_days < 365:
                return "rising"
            
            # Community: Many contributors relative to stars
            elif contributors / max(stars, 1) > 0.1:
                return "community"
            
            # Experimental: Low stars, recent
            elif stars < 100 and age_days < 30:
                return "experimental"
            
            # Niche: Moderate stats
            else:
                return "niche"
        
        df['repo_type'] = df.apply(classify_repo, axis=1)
        return df
    
    def _predict_growth_potential(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict future growth potential using current metrics."""
        
        # Growth potential factors
        growth_factors = [
            df['star_velocity_norm'] * 0.3,  # Current velocity
            df['freshness_norm'] * 0.2,     # Age factor
            df['activity_norm'] * 0.2,      # Recent activity
            df['engagement_norm'] * 0.15,   # Community engagement
            df['quality_norm'] * 0.15       # Repository quality
        ]
        
        df['growth_potential'] = sum(growth_factors) * 100
        
        # Classify growth potential
        df['growth_category'] = pd.cut(
            df['growth_potential'],
            bins=[0, 30, 60, 80, 100],
            labels=['low', 'moderate', 'high', 'exceptional']
        )
        
        return df
    
    def get_trending_insights(self, df: pd.DataFrame) -> Dict:
        """Generate comprehensive insights about trending repositories."""
        
        if df.empty:
            return {"error": "No data available for analysis"}
        
        insights = {
            'summary': {
                'total_repos': len(df),
                'avg_momentum_score': df['momentum_score'].mean(),
                'top_momentum_score': df['momentum_score'].max(),
                'analysis_timestamp': datetime.now().isoformat()
            },
            'top_performers': {
                'highest_momentum': df.nlargest(5, 'momentum_score')[['name', 'full_name', 'momentum_score', 'stars']].to_dict('records'),
                'fastest_growing': df.nlargest(5, 'star_velocity')[['name', 'full_name', 'star_velocity', 'stars']].to_dict('records'),
                'most_engaging': df.nlargest(5, 'engagement_score')[['name', 'full_name', 'engagement_score', 'contributors']].to_dict('records')
            },
            'language_trends': self._analyze_language_trends(df),
            'growth_patterns': self._analyze_growth_patterns(df),
            'repository_types': df['repo_type'].value_counts().to_dict(),
            'trend_directions': df['trend_direction'].value_counts().to_dict(),
            'recommendations': self._generate_recommendations(df)
        }
        
        return insights
    
    def _analyze_language_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze trends by programming language."""
        language_stats = {}
        
        for language in df['language'].dropna().unique():
            lang_data = df[df['language'] == language]
            language_stats[language] = {
                'count': len(lang_data),
                'avg_momentum': lang_data['momentum_score'].mean(),
                'avg_stars': lang_data['stars'].mean(),
                'top_repo': lang_data.loc[lang_data['momentum_score'].idxmax(), 'name'] if len(lang_data) > 0 else None
            }
        
        # Sort by average momentum
        return dict(sorted(language_stats.items(), key=lambda x: x[1]['avg_momentum'], reverse=True))
    
    def _analyze_growth_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze different growth patterns in the data."""
        
        patterns = {
            'by_age': {
                'new (0-30 days)': df[df['age_days'] <= 30]['momentum_score'].mean(),
                'young (31-90 days)': df[(df['age_days'] > 30) & (df['age_days'] <= 90)]['momentum_score'].mean(),
                'mature (91-365 days)': df[(df['age_days'] > 90) & (df['age_days'] <= 365)]['momentum_score'].mean(),
                'established (>365 days)': df[df['age_days'] > 365]['momentum_score'].mean()
            },
            'by_size': {
                'small (0-100 stars)': df[df['stars'] <= 100]['momentum_score'].mean(),
                'medium (101-1000 stars)': df[(df['stars'] > 100) & (df['stars'] <= 1000)]['momentum_score'].mean(),
                'large (1001-10000 stars)': df[(df['stars'] > 1000) & (df['stars'] <= 10000)]['momentum_score'].mean(),
                'huge (>10000 stars)': df[df['stars'] > 10000]['momentum_score'].mean()
            },
            'growth_potential_distribution': df['growth_category'].value_counts().to_dict()
        }
        
        return patterns
    
    def _generate_recommendations(self, df: pd.DataFrame) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Top language recommendation
        lang_trends = self._analyze_language_trends(df)
        if lang_trends:
            top_lang = list(lang_trends.keys())[0]
            recommendations.append(f"🔥 {top_lang} repositories are showing the highest momentum right now")
        
        # Rising stars
        rising_repos = df[(df['age_days'] < 90) & (df['momentum_score'] > 70)]
        if len(rising_repos) > 0:
            recommendations.append(f"⭐ {len(rising_repos)} emerging repositories show exceptional growth potential")
        
        # Community engagement
        high_engagement = df[df['engagement_score'] > 80]
        if len(high_engagement) > 0:
            recommendations.append(f"👥 {len(high_engagement)} repositories have very active communities worth watching")
        
        # Undervalued gems
        undervalued = df[(df['momentum_score'] > 60) & (df['stars'] < 1000)]
        if len(undervalued) > 0:
            recommendations.append(f"💎 {len(undervalued)} undervalued repositories could be tomorrow's stars")
        
        return recommendations
    
    def cluster_repositories(self, df: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
        """Cluster repositories based on their characteristics."""
        
        if len(df) < n_clusters:
            logger.warning(f"Not enough repositories ({len(df)}) for {n_clusters} clusters")
            return df
        
        # Select features for clustering
        features = [
            'momentum_score', 'star_velocity', 'engagement_score',
            'freshness_score', 'activity_score', 'growth_potential'
        ]
        
        # Prepare feature matrix
        X = df[features].fillna(0)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df['cluster'] = kmeans.fit_predict(X)
        
        # Add cluster interpretation
        cluster_info = {}
        for cluster_id in range(n_clusters):
            cluster_data = df[df['cluster'] == cluster_id]
            cluster_info[cluster_id] = {
                'size': len(cluster_data),
                'avg_momentum': cluster_data['momentum_score'].mean(),
                'avg_stars': cluster_data['stars'].mean(),
                'top_language': cluster_data['language'].mode().iloc[0] if len(cluster_data) > 0 and not cluster_data['language'].empty else 'Unknown'
            }
        
        df.attrs['cluster_info'] = cluster_info
        return df
    
    def export_analysis(self, df: pd.DataFrame, insights: Dict, output_dir: str = "data"):
        """Export analysis results to various formats."""
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export to CSV
        csv_path = os.path.join(output_dir, f"analysis_{timestamp}.csv")
        df.to_csv(csv_path, index=False)
        logger.info(f"Analysis exported to {csv_path}")
        
        # Export insights to JSON
        json_path = os.path.join(output_dir, f"insights_{timestamp}.json")
        with open(json_path, 'w') as f:
            json.dump(insights, f, indent=2, default=str)
        logger.info(f"Insights exported to {json_path}")
        
        return csv_path, json_path
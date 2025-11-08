"""
Lightweight AI analyzer for the free tier version.
Uses simple text processing and statistical methods without heavy AI models.
"""

import logging
import os
import json
from typing import List, Dict, Tuple, Optional, Any
import numpy as np
from datetime import datetime
import re
import pickle
from collections import Counter

# Lightweight text processing
try:
    import textstat
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available. Using basic text processing.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LightweightAIAnalyzer:
    """Lightweight AI analyzer using simple text processing and statistics."""
    
    def __init__(self, config: Dict = None, cache_dir: str = "./data/models"):
        """Initialize lightweight analyzer.
        
        Args:
            config: Configuration dictionary
            cache_dir: Directory to cache analysis results
        """
        self.config = config or {}
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize simple text processing tools
        self.vectorizer = None
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words='english',
                lowercase=True,
                ngram_range=(1, 2)
            )
        
        # Technology keywords for categorization
        self.tech_keywords = {
            'web': ['web', 'frontend', 'backend', 'html', 'css', 'react', 'vue', 'angular', 'nodejs', 'express'],
            'mobile': ['mobile', 'android', 'ios', 'react-native', 'flutter', 'swift', 'kotlin'],
            'ai': ['ai', 'ml', 'machine learning', 'deep learning', 'neural', 'tensorflow', 'pytorch', 'sklearn'],
            'devops': ['docker', 'kubernetes', 'ci/cd', 'deployment', 'aws', 'cloud', 'terraform'],
            'data': ['data', 'analytics', 'visualization', 'pandas', 'numpy', 'jupyter', 'sql'],
            'game': ['game', 'gaming', 'unity', 'unreal', 'godot', '3d', 'graphics'],
            'blockchain': ['blockchain', 'crypto', 'bitcoin', 'ethereum', 'web3', 'defi', 'nft'],
            'api': ['api', 'rest', 'graphql', 'microservices', 'json', 'http']
        }
        
        logger.info("Lightweight AI analyzer initialized")
    
    def summarize_repository(self, repo: Dict) -> str:
        """Generate a simple summary of a repository using text processing.
        
        Args:
            repo: Repository dictionary
            
        Returns:
            Generated summary string
        """
        name = repo.get('name', 'Unknown')
        description = repo.get('description', '')
        language = repo.get('language', '')
        topics = repo.get('topics', [])
        stars = repo.get('stars', 0)
        
        # Build summary components
        summary_parts = []
        
        # Basic info
        if language:
            summary_parts.append(f"{name} is a {language} project")
        else:
            summary_parts.append(f"{name} is a software project")
        
        # Add description processing
        if description:
            # Clean and shorten description
            clean_desc = self._clean_text(description)
            if len(clean_desc) > 100:
                clean_desc = clean_desc[:97] + "..."
            summary_parts.append(f"that {clean_desc}")
        
        # Add category if detectable
        category = self._categorize_repo(repo)
        if category:
            summary_parts.append(f"focused on {category}")
        
        # Add popularity info
        if stars > 1000:
            summary_parts.append(f"with {stars:,} stars, showing strong community adoption")
        elif stars > 100:
            summary_parts.append(f"with {stars} stars and growing popularity")
        
        # Add topics if available
        if topics and len(topics) > 0:
            topic_str = ", ".join(topics[:3])
            summary_parts.append(f"tagged with: {topic_str}")
        
        return ". ".join(summary_parts) + "."
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        # Remove URLs, special characters, and normalize whitespace
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _categorize_repo(self, repo: Dict) -> Optional[str]:
        """Categorize repository based on description and topics."""
        text_content = ""
        
        # Combine description and topics for analysis
        if repo.get('description'):
            text_content += repo['description'].lower() + " "
        
        if repo.get('topics'):
            text_content += " ".join(repo['topics']).lower() + " "
        
        if repo.get('language'):
            text_content += repo['language'].lower() + " "
        
        # Count matches for each category
        category_scores = {}
        for category, keywords in self.tech_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_content)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores.keys(), key=lambda x: category_scores[x])
        
        return None
    
    def analyze_trends(self, repos: List[Dict]) -> Dict[str, Any]:
        """Analyze repository trends using statistical methods.
        
        Args:
            repos: List of repository dictionaries
            
        Returns:
            Dictionary containing trend analysis
        """
        insights = {
            'total_repos': len(repos),
            'language_trends': {},
            'category_trends': {},
            'popularity_metrics': {},
            'growth_analysis': {},
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
        
        if not repos:
            return insights
        
        # Language analysis
        languages = [repo.get('language') for repo in repos if repo.get('language')]
        language_counts = Counter(languages)
        insights['language_trends'] = dict(language_counts.most_common(10))
        
        # Category analysis
        categories = [self._categorize_repo(repo) for repo in repos]
        categories = [cat for cat in categories if cat]  # Remove None values
        category_counts = Counter(categories)
        insights['category_trends'] = dict(category_counts.most_common(10))
        
        # Popularity metrics
        stars = [repo.get('stars', 0) for repo in repos]
        if stars:
            insights['popularity_metrics'] = {
                'avg_stars': np.mean(stars),
                'median_stars': np.median(stars),
                'total_stars': sum(stars),
                'star_ranges': self._analyze_star_distribution(stars)
            }
        
        # Growth analysis
        growth_scores = [repo.get('momentum_score', 0) for repo in repos if repo.get('momentum_score')]
        if growth_scores:
            insights['growth_analysis'] = {
                'avg_momentum': np.mean(growth_scores),
                'high_momentum_count': len([s for s in growth_scores if s > 70]),
                'emerging_count': len([s for s in growth_scores if 50 < s < 70])
            }
        
        # Generate recommendations
        insights['recommendations'] = self._generate_simple_recommendations(repos, insights)
        
        return insights
    
    def _analyze_star_distribution(self, stars: List[int]) -> Dict[str, int]:
        """Analyze distribution of star counts."""
        ranges = {
            '0-10': 0,
            '11-100': 0,
            '101-1000': 0,
            '1001-10000': 0,
            '10000+': 0
        }
        
        for star_count in stars:
            if star_count <= 10:
                ranges['0-10'] += 1
            elif star_count <= 100:
                ranges['11-100'] += 1
            elif star_count <= 1000:
                ranges['101-1000'] += 1
            elif star_count <= 10000:
                ranges['1001-10000'] += 1
            else:
                ranges['10000+'] += 1
        
        return ranges
    
    def _generate_simple_recommendations(self, repos: List[Dict], insights: Dict) -> List[str]:
        """Generate simple recommendations based on analysis."""
        recommendations = []
        
        # Language recommendations
        top_languages = list(insights.get('language_trends', {}).keys())[:3]
        if top_languages:
            recommendations.append(f"🔥 Top trending languages: {', '.join(top_languages)}")
        
        # Category recommendations
        top_categories = list(insights.get('category_trends', {}).keys())[:2]
        if top_categories:
            recommendations.append(f"📈 Hot categories: {', '.join(top_categories)}")
        
        # Growth opportunities
        growth_stats = insights.get('growth_analysis', {})
        high_momentum = growth_stats.get('high_momentum_count', 0)
        if high_momentum > 0:
            recommendations.append(f"🚀 {high_momentum} repositories showing exceptional growth")
        
        # Community insights
        popularity = insights.get('popularity_metrics', {})
        if popularity.get('avg_stars', 0) > 1000:
            recommendations.append("⭐ Strong community engagement across trending repositories")
        
        # Technology focus areas
        emerging = growth_stats.get('emerging_count', 0)
        if emerging > 0:
            recommendations.append(f"💡 {emerging} emerging projects worth monitoring")
        
        # Add general advice
        recommendations.append("🎯 Consider contributing to repositories with active communities")
        recommendations.append("📚 Explore projects in trending categories to stay current")
        
        return recommendations[:6]  # Limit to 6 recommendations
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate simple text embeddings using TF-IDF."""
        if not texts:
            return np.array([])
        
        if self.vectorizer and SKLEARN_AVAILABLE:
            try:
                # Clean texts first
                clean_texts = [self._clean_text(text) for text in texts]
                clean_texts = [text if text else "empty" for text in clean_texts]
                
                return self.vectorizer.fit_transform(clean_texts).toarray()
            except Exception as e:
                logger.warning(f"TF-IDF embedding failed: {e}")
        
        # Fallback: simple word count features
        return self._simple_word_features(texts)
    
    def _simple_word_features(self, texts: List[str]) -> np.ndarray:
        """Create simple word-based features."""
        features = []
        
        for text in texts:
            if not text:
                features.append([0] * 10)
                continue
                
            clean_text = self._clean_text(text.lower())
            words = clean_text.split()
            
            # Simple features: length, word count, avg word length, etc.
            feature_vector = [
                len(clean_text),  # Character count
                len(words),  # Word count
                np.mean([len(word) for word in words]) if words else 0,  # Avg word length
                clean_text.count('a'),  # Vowel counts (simple)
                clean_text.count('e'),
                clean_text.count('i'),
                clean_text.count('o'),
                clean_text.count('u'),
                len([w for w in words if len(w) > 6]),  # Long words
                len(set(words)) / len(words) if words else 0  # Vocabulary diversity
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def generate_insights(self, repos: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive insights about repositories."""
        return self.analyze_trends(repos)
    
    def save_analysis_cache(self, data: Dict, cache_file: str = "lightweight_cache.pkl"):
        """Save analysis results to cache."""
        cache_path = os.path.join(self.cache_dir, cache_file)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"Analysis cache saved to {cache_path}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def load_analysis_cache(self, cache_file: str = "lightweight_cache.pkl") -> Optional[Dict]:
        """Load analysis results from cache."""
        cache_path = os.path.join(self.cache_dir, cache_file)
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                logger.info(f"Analysis cache loaded from {cache_path}")
                return data
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
        return None


# For compatibility with existing code, use the lightweight analyzer when heavy models aren't available
class EnhancedAIAnalyzer(LightweightAIAnalyzer):
    """Enhanced AI analyzer that falls back to lightweight processing."""
    
    def __init__(self, config: Dict = None, cache_dir: str = "./data/models"):
        super().__init__(config, cache_dir)
        
        # Check if we should use heavy models
        provider = self.config.get('models', {}).get('provider', 'huggingface')
        
        if provider == 'huggingface':
            logger.info("Using lightweight analyzer (no heavy AI models)")
        else:
            logger.info("Enhanced analyzer initialized in lightweight mode")


# Backward compatibility
AIAnalyzer = EnhancedAIAnalyzer
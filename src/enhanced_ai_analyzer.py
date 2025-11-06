"""
Enhanced AI-powered analysis with DeepSeek integration.
Provides repository summarization, trend analysis, and insights using both DeepSeek and Hugging Face models.
"""

import logging
import os
import json
from typing import List, Dict, Tuple, Optional, Any
import torch
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# DeepSeek API integration
try:
    from openai import OpenAI
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False
    logging.warning("OpenAI package not installed. DeepSeek features will be disabled.")

# Hugging Face models (fallback)
try:
    from transformers import (
        AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM,
        pipeline, T5Tokenizer, T5ForConditionalGeneration
    )
    from sentence_transformers import SentenceTransformer
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    logging.warning("Transformers not installed. Hugging Face features will be disabled.")

import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedAIAnalyzer:
    """Enhanced AI-powered repository analysis with DeepSeek and Hugging Face support."""
    
    def __init__(self, config: Dict = None, cache_dir: str = "./data/models"):
        """Initialize AI analyzer with configuration.
        
        Args:
            config: Configuration dictionary
            cache_dir: Directory to cache downloaded models
        """
        self.config = config or {}
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Determine which AI provider to use
        self.provider = self.config.get('models', {}).get('provider', 'huggingface')
        
        # Initialize clients
        self.deepseek_client = None
        self.huggingface_models = {}
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize AI providers based on configuration."""
        
        if self.provider == 'deepseek' and DEEPSEEK_AVAILABLE:
            self._init_deepseek()
        
        if HUGGINGFACE_AVAILABLE:
            self._init_huggingface()
    
    def _init_deepseek(self):
        """Initialize DeepSeek API client."""
        try:
            deepseek_config = self.config.get('models', {}).get('deepseek', {})
            api_key = deepseek_config.get('api_key', os.getenv('DEEPSEEK_API_KEY'))
            base_url = deepseek_config.get('base_url', 'https://api.deepseek.com')
            
            if not api_key:
                logger.warning("DeepSeek API key not found. Set DEEPSEEK_API_KEY environment variable.")
                return
            
            # Expand environment variable if needed
            if api_key.startswith('${') and api_key.endswith('}'):
                env_var = api_key[2:-1]
                api_key = os.getenv(env_var)
            
            if not api_key:
                logger.warning(f"DeepSeek API key environment variable not set: {env_var}")
                return
            
            self.deepseek_client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            self.deepseek_config = deepseek_config
            logger.info("DeepSeek API client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek client: {e}")
            self.deepseek_client = None
    
    def _init_huggingface(self):
        """Initialize Hugging Face models as fallback."""
        try:
            logger.info("Initializing Hugging Face models...")
            
            hf_config = self.config.get('models', {}).get('huggingface', {})
            
            # Load summarization model
            summarizer_model = hf_config.get('summarizer', 't5-small')
            try:
                self.huggingface_models['summarizer'] = pipeline(
                    "summarization",
                    model=summarizer_model,
                    tokenizer=summarizer_model,
                    device=-1,  # Use CPU
                    cache_dir=self.cache_dir
                )
                logger.info(f"Loaded summarizer: {summarizer_model}")
            except Exception as e:
                logger.warning(f"Failed to load summarizer {summarizer_model}: {e}")
            
            # Load similarity model
            similarity_model = hf_config.get('similarity', 'sentence-transformers/all-MiniLM-L6-v2')
            try:
                self.huggingface_models['similarity'] = SentenceTransformer(
                    similarity_model,
                    cache_folder=self.cache_dir
                )
                logger.info(f"Loaded similarity model: {similarity_model}")
            except Exception as e:
                logger.warning(f"Failed to load similarity model {similarity_model}: {e}")
            
            # Load embeddings model
            embeddings_model = hf_config.get('embeddings', 'distilbert-base-uncased')
            try:
                self.huggingface_models['embeddings_tokenizer'] = AutoTokenizer.from_pretrained(
                    embeddings_model,
                    cache_dir=self.cache_dir
                )
                self.huggingface_models['embeddings_model'] = AutoModel.from_pretrained(
                    embeddings_model,
                    cache_dir=self.cache_dir
                )
                logger.info(f"Loaded embeddings model: {embeddings_model}")
            except Exception as e:
                logger.warning(f"Failed to load embeddings model {embeddings_model}: {e}")
                
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face models: {e}")
    
    def summarize_repository(self, repo: Dict) -> str:
        """Generate an AI-powered summary of a repository.
        
        Args:
            repo: Repository dictionary with description, topics, etc.
            
        Returns:
            AI-generated summary string
        """
        if self.provider == 'deepseek' and self.deepseek_client:
            return self._summarize_with_deepseek(repo)
        elif self.huggingface_models.get('summarizer'):
            return self._summarize_with_huggingface(repo)
        else:
            return self._extract_key_info(repo)
    
    def _summarize_with_deepseek(self, repo: Dict) -> str:
        """Generate summary using DeepSeek API."""
        try:
            # Prepare context about the repository
            context = self._prepare_repo_context(repo)
            
            prompt = f"""Analyze this GitHub repository and provide a concise, insightful summary in 1-2 sentences.

Repository Information:
{context}

Focus on:
1. What the project does (main purpose/functionality)
2. Key technologies used
3. Why it's trending or noteworthy
4. Target audience/use case

Provide a professional summary that would be useful for developers and tech professionals:"""

            response = self.deepseek_client.chat.completions.create(
                model=self.deepseek_config.get('model', 'deepseek-chat'),
                messages=[
                    {"role": "system", "content": "You are an expert software developer and tech analyst who provides concise, insightful summaries of GitHub repositories. Focus on practical value and key differentiators."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.deepseek_config.get('max_tokens', 150),
                temperature=self.deepseek_config.get('temperature', 0.3)
            )
            
            summary = response.choices[0].message.content.strip()
            logger.debug(f"DeepSeek summary for {repo.get('name', 'unknown')}: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"DeepSeek summarization failed for {repo.get('name', 'unknown')}: {e}")
            # Fallback to Hugging Face or basic extraction
            if self.huggingface_models.get('summarizer'):
                return self._summarize_with_huggingface(repo)
            return self._extract_key_info(repo)
    
    def _summarize_with_huggingface(self, repo: Dict) -> str:
        """Generate summary using Hugging Face models."""
        try:
            # Prepare input text
            input_text = self._prepare_repo_context(repo, max_length=300)
            
            if len(input_text) < 50:
                return self._extract_key_info(repo)
            
            # Use T5 summarizer
            summarize_input = f"summarize: {input_text}"
            
            summary = self.huggingface_models['summarizer'](
                summarize_input,
                max_length=100,
                min_length=20,
                do_sample=False,
                truncation=True
            )
            
            return summary[0]['summary_text']
            
        except Exception as e:
            logger.error(f"Hugging Face summarization failed for {repo.get('name', 'unknown')}: {e}")
            return self._extract_key_info(repo)
    
    def _prepare_repo_context(self, repo: Dict, max_length: int = 500) -> str:
        """Prepare repository context for AI analysis."""
        context_parts = []
        
        # Basic info
        name = repo.get('name', 'Unknown')
        description = repo.get('description', '')
        language = repo.get('language', '')
        
        context_parts.append(f"Repository: {name}")
        
        if description:
            context_parts.append(f"Description: {description}")
        
        if language:
            context_parts.append(f"Primary Language: {language}")
        
        # Metrics
        stars = repo.get('stars', 0)
        forks = repo.get('forks', 0)
        contributors = repo.get('contributors', 0)
        
        if stars > 100:
            context_parts.append(f"Stars: {stars:,}")
        if forks > 10:
            context_parts.append(f"Forks: {forks:,}")
        if contributors > 1:
            context_parts.append(f"Contributors: {contributors}")
        
        # Topics/tags
        topics = repo.get('topics', [])
        if topics:
            context_parts.append(f"Topics: {', '.join(topics[:5])}")
        
        # Growth metrics
        if repo.get('momentum_score'):
            context_parts.append(f"Momentum Score: {repo['momentum_score']:.1f}/100")
        
        if repo.get('star_velocity'):
            context_parts.append(f"Star Growth: {repo['star_velocity']:.1f} stars/day")
        
        context = ". ".join(context_parts)
        
        # Truncate if too long
        if len(context) > max_length:
            context = context[:max_length] + "..."
        
        return context
    
    def _extract_key_info(self, repo: Dict) -> str:
        """Fallback method to extract key repository information."""
        name = repo.get('name', 'Unknown')
        description = repo.get('description', '')
        language = repo.get('language', '')
        stars = repo.get('stars', 0)
        
        # Create a simple summary
        summary_parts = [f"{name}"]
        
        if language:
            summary_parts.append(f"({language})")
        
        if description:
            # Truncate long descriptions
            desc = description[:100] + "..." if len(description) > 100 else description
            summary_parts.append(f"- {desc}")
        
        if stars > 100:
            summary_parts.append(f"[{stars:,} ⭐]")
        
        return " ".join(summary_parts)
    
    def analyze_trends(self, repos: List[Dict]) -> Dict[str, Any]:
        """Analyze repository trends using AI insights.
        
        Args:
            repos: List of repository dictionaries
            
        Returns:
            Dictionary containing trend analysis
        """
        if self.provider == 'deepseek' and self.deepseek_client:
            return self._analyze_trends_with_deepseek(repos)
        else:
            return self._analyze_trends_basic(repos)
    
    def _analyze_trends_with_deepseek(self, repos: List[Dict]) -> Dict[str, Any]:
        """Analyze trends using DeepSeek for advanced insights."""
        try:
            # Prepare data for analysis
            trend_data = self._prepare_trend_data(repos)
            
            prompt = f"""Analyze these trending GitHub repositories and provide insights about current development trends:

Repository Data:
{json.dumps(trend_data, indent=2)}

Please provide analysis on:
1. Emerging technology trends
2. Popular programming languages and frameworks
3. Types of projects gaining traction
4. Potential reasons for growth
5. Recommendations for developers

Format your response as structured insights that would be valuable for developers and tech professionals."""

            response = self.deepseek_client.chat.completions.create(
                model=self.deepseek_config.get('model', 'deepseek-chat'),
                messages=[
                    {"role": "system", "content": "You are a senior tech analyst specializing in software development trends and open-source ecosystem analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.deepseek_config.get('max_tokens', 800),
                temperature=self.deepseek_config.get('temperature', 0.3)
            )
            
            ai_insights = response.choices[0].message.content.strip()
            
            # Combine AI insights with basic analysis
            basic_analysis = self._analyze_trends_basic(repos)
            basic_analysis['ai_insights'] = ai_insights
            
            return basic_analysis
            
        except Exception as e:
            logger.error(f"DeepSeek trend analysis failed: {e}")
            return self._analyze_trends_basic(repos)
    
    def _prepare_trend_data(self, repos: List[Dict], max_repos: int = 20) -> List[Dict]:
        """Prepare repository data for trend analysis."""
        # Select top repositories by momentum
        top_repos = sorted(repos, key=lambda x: x.get('momentum_score', 0), reverse=True)[:max_repos]
        
        trend_data = []
        for repo in top_repos:
            trend_data.append({
                'name': repo.get('name', ''),
                'language': repo.get('language', ''),
                'description': repo.get('description', '')[:200],  # Truncate for API limits
                'stars': repo.get('stars', 0),
                'momentum_score': repo.get('momentum_score', 0),
                'topics': repo.get('topics', [])[:5],  # Limit topics
                'star_velocity': repo.get('star_velocity', 0)
            })
        
        return trend_data
    
    def _analyze_trends_basic(self, repos: List[Dict]) -> Dict[str, Any]:
        """Basic trend analysis without external AI."""
        insights = {
            'total_repos': len(repos),
            'top_languages': {},
            'trending_topics': {},
            'categories': {},
            'growth_patterns': {},
            'timestamp': datetime.now().isoformat()
        }
        
        if not repos:
            return insights
        
        # Language analysis
        languages = [repo.get('language') for repo in repos if repo.get('language')]
        for lang in languages:
            insights['top_languages'][lang] = insights['top_languages'].get(lang, 0) + 1
        
        # Topic analysis
        all_topics = []
        for repo in repos:
            all_topics.extend(repo.get('topics', []))
        
        for topic in all_topics:
            insights['trending_topics'][topic] = insights['trending_topics'].get(topic, 0) + 1
        
        # Growth patterns
        star_ranges = {'0-100': 0, '100-1000': 0, '1000-10000': 0, '10000+': 0}
        for repo in repos:
            stars = repo.get('stars', 0)
            if stars < 100:
                star_ranges['0-100'] += 1
            elif stars < 1000:
                star_ranges['100-1000'] += 1
            elif stars < 10000:
                star_ranges['1000-10000'] += 1
            else:
                star_ranges['10000+'] += 1
        
        insights['growth_patterns']['star_distribution'] = star_ranges
        
        return insights
    
    def generate_recommendations(self, repos: List[Dict], insights: Dict = None) -> List[str]:
        """Generate actionable recommendations based on analysis.
        
        Args:
            repos: List of repository dictionaries
            insights: Optional insights dictionary
            
        Returns:
            List of recommendation strings
        """
        if self.provider == 'deepseek' and self.deepseek_client:
            return self._generate_recommendations_with_deepseek(repos, insights)
        else:
            return self._generate_basic_recommendations(repos, insights)
    
    def _generate_recommendations_with_deepseek(self, repos: List[Dict], insights: Dict = None) -> List[str]:
        """Generate recommendations using DeepSeek."""
        try:
            # Prepare summary data
            summary_data = {
                'repo_count': len(repos),
                'top_languages': list(insights.get('top_languages', {}).keys())[:5] if insights else [],
                'trending_topics': list(insights.get('trending_topics', {}).keys())[:10] if insights else [],
                'top_repos': [
                    {
                        'name': repo.get('name', ''),
                        'language': repo.get('language', ''),
                        'momentum_score': repo.get('momentum_score', 0),
                        'stars': repo.get('stars', 0)
                    }
                    for repo in sorted(repos, key=lambda x: x.get('momentum_score', 0), reverse=True)[:10]
                ]
            }
            
            prompt = f"""Based on this analysis of trending GitHub repositories, provide 5-7 actionable recommendations for developers and tech professionals:

Analysis Summary:
{json.dumps(summary_data, indent=2)}

Provide specific, actionable recommendations about:
1. Technologies to learn or explore
2. Project types with growth potential
3. Skills or areas to focus on
4. Communities or ecosystems to join
5. Tools or frameworks to consider

Format each recommendation as a clear, actionable bullet point starting with an emoji."""

            response = self.deepseek_client.chat.completions.create(
                model=self.deepseek_config.get('model', 'deepseek-chat'),
                messages=[
                    {"role": "system", "content": "You are a tech career advisor and open-source expert who provides practical, actionable advice for developers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.deepseek_config.get('max_tokens', 600),
                temperature=self.deepseek_config.get('temperature', 0.4)
            )
            
            recommendations_text = response.choices[0].message.content.strip()
            
            # Parse into list
            recommendations = []
            for line in recommendations_text.split('\n'):
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-') or any(emoji in line for emoji in ['🔥', '💡', '🚀', '⭐', '📈', '🛠️', '🎯'])):
                    # Clean up the line
                    clean_line = line.lstrip('•-').strip()
                    recommendations.append(clean_line)
            
            return recommendations[:7]  # Limit to 7 recommendations
            
        except Exception as e:
            logger.error(f"DeepSeek recommendation generation failed: {e}")
            return self._generate_basic_recommendations(repos, insights)
    
    def _generate_basic_recommendations(self, repos: List[Dict], insights: Dict = None) -> List[str]:
        """Generate basic recommendations without external AI."""
        recommendations = []
        
        if not repos:
            return recommendations
        
        # Analyze top languages
        languages = {}
        for repo in repos:
            lang = repo.get('language')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        if languages:
            top_lang = max(languages.keys(), key=lambda x: languages[x])
            recommendations.append(f"🔥 {top_lang} repositories are showing the highest momentum right now")
        
        # Rising stars
        high_momentum = [repo for repo in repos if repo.get('momentum_score', 0) > 70]
        if high_momentum:
            recommendations.append(f"⭐ {len(high_momentum)} repositories show exceptional growth potential")
        
        # Community engagement
        high_engagement = [repo for repo in repos if repo.get('contributors', 0) > 10]
        if high_engagement:
            recommendations.append(f"👥 {len(high_engagement)} repositories have very active communities worth watching")
        
        # Undervalued gems
        undervalued = [repo for repo in repos if repo.get('momentum_score', 0) > 60 and repo.get('stars', 0) < 1000]
        if undervalued:
            recommendations.append(f"💎 {len(undervalued)} undervalued repositories could be tomorrow's stars")
        
        # AI/ML trend
        ai_repos = [repo for repo in repos if any(term in str(repo.get('topics', []) + [repo.get('description', '')]).lower() 
                                                 for term in ['ai', 'machine learning', 'ml', 'artificial intelligence'])]
        if ai_repos:
            recommendations.append(f"🤖 AI/ML repositories continue to dominate with {len(ai_repos)} trending projects")
        
        return recommendations
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts using available models."""
        if self.huggingface_models.get('similarity'):
            try:
                return self.huggingface_models['similarity'].encode(texts)
            except Exception as e:
                logger.error(f"Similarity model failed: {e}")
        
        # Fallback to simple text features
        return self._simple_text_features(texts)
    
    def _simple_text_features(self, texts: List[str]) -> np.ndarray:
        """Fallback method to create simple text features."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            features = vectorizer.fit_transform(texts)
            return features.toarray()
        except:
            # Ultimate fallback: random features
            return np.random.random((len(texts), 50))
    
    def save_analysis_cache(self, data: Dict, cache_file: str = "enhanced_analysis_cache.pkl"):
        """Save analysis results to cache."""
        cache_path = os.path.join(self.cache_dir, cache_file)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"Enhanced analysis cache saved to {cache_path}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def load_analysis_cache(self, cache_file: str = "enhanced_analysis_cache.pkl") -> Optional[Dict]:
        """Load analysis results from cache."""
        cache_path = os.path.join(self.cache_dir, cache_file)
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                logger.info(f"Enhanced analysis cache loaded from {cache_path}")
                return data
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
        return None


# Backward compatibility alias
AIAnalyzer = EnhancedAIAnalyzer
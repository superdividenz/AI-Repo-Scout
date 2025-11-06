"""
AI-powered analysis using free Hugging Face models.
Provides repository summarization, text embeddings, and similarity analysis.
"""

import logging
from typing import List, Dict, Tuple, Optional
import torch
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSeq2SeqLM,
    pipeline, T5Tokenizer, T5ForConditionalGeneration
)
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI-powered repository analysis using free Hugging Face models."""
    
    def __init__(self, cache_dir: str = "./data/models"):
        """Initialize AI models for analysis.
        
        Args:
            cache_dir: Directory to cache downloaded models
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize models (all free from Hugging Face)
        self.summarizer = None
        self.embeddings_model = None
        self.similarity_model = None
        
        # Model configurations
        self.models_config = {
            'summarizer': 't5-small',
            'embeddings': 'distilbert-base-uncased',
            'similarity': 'sentence-transformers/all-MiniLM-L6-v2'
        }
        
        self._load_models()
    
    def _load_models(self):
        """Load AI models with error handling and fallbacks."""
        try:
            logger.info("Loading AI models...")
            
            # Load summarization model (T5-small)
            logger.info("Loading T5 summarization model...")
            self.summarizer = pipeline(
                "summarization",
                model=self.models_config['summarizer'],
                tokenizer=self.models_config['summarizer'],
                device=-1,  # Use CPU (free)
                cache_dir=self.cache_dir
            )
            
            # Load sentence transformer for similarity
            logger.info("Loading sentence transformer model...")
            self.similarity_model = SentenceTransformer(
                self.models_config['similarity'],
                cache_folder=self.cache_dir
            )
            
            # Load embeddings model
            logger.info("Loading embeddings model...")
            self.embeddings_tokenizer = AutoTokenizer.from_pretrained(
                self.models_config['embeddings'],
                cache_dir=self.cache_dir
            )
            self.embeddings_model = AutoModel.from_pretrained(
                self.models_config['embeddings'],
                cache_dir=self.cache_dir
            )
            
            logger.info("All AI models loaded successfully!")
            
        except Exception as e:
            logger.error(f"Failed to load AI models: {e}")
            logger.info("Will use fallback text processing methods.")
    
    def summarize_repository(self, repo: Dict) -> str:
        """Generate an AI-powered summary of a repository.
        
        Args:
            repo: Repository dictionary with description, topics, etc.
            
        Returns:
            AI-generated summary string
        """
        try:
            # Prepare input text
            description = repo.get('description', '')
            topics = repo.get('topics', [])
            language = repo.get('language', '')
            
            # Create comprehensive input
            input_text = f"Repository: {repo.get('name', '')}. "
            
            if description:
                input_text += f"Description: {description}. "
            
            if language:
                input_text += f"Language: {language}. "
            
            if topics:
                input_text += f"Topics: {', '.join(topics)}. "
            
            # Add context about metrics
            stars = repo.get('stars', 0)
            if stars > 1000:
                input_text += f"Popular project with {stars} stars. "
            elif stars > 100:
                input_text += f"Growing project with {stars} stars. "
            
            # Use AI summarizer if available
            if self.summarizer and len(input_text) > 50:
                # T5 works better with "summarize:" prefix
                summarize_input = f"summarize: {input_text}"
                
                summary = self.summarizer(
                    summarize_input,
                    max_length=100,
                    min_length=20,
                    do_sample=False,
                    truncation=True
                )
                
                return summary[0]['summary_text']
            
            else:
                # Fallback: extract key information
                return self._extract_key_info(repo)
                
        except Exception as e:
            logger.error(f"Summarization failed for {repo.get('name', 'unknown')}: {e}")
            return self._extract_key_info(repo)
    
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
            summary_parts.append(f"[{stars} ⭐]")
        
        return " ".join(summary_parts)
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of embeddings
        """
        try:
            if self.similarity_model:
                # Use sentence transformer (recommended)
                embeddings = self.similarity_model.encode(texts)
                return embeddings
            
            elif self.embeddings_model:
                # Use DistilBERT embeddings
                embeddings = []
                
                for text in texts:
                    inputs = self.embeddings_tokenizer(
                        text,
                        return_tensors="pt",
                        truncation=True,
                        padding=True,
                        max_length=512
                    )
                    
                    with torch.no_grad():
                        outputs = self.embeddings_model(**inputs)
                        # Use mean pooling of last hidden states
                        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
                        embeddings.append(embedding)
                
                return np.array(embeddings)
            
            else:
                logger.warning("No embedding models available. Using simple text features.")
                return self._simple_text_features(texts)
                
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return self._simple_text_features(texts)
    
    def _simple_text_features(self, texts: List[str]) -> np.ndarray:
        """Fallback method to create simple text features."""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        try:
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            features = vectorizer.fit_transform(texts)
            return features.toarray()
        except:
            # Ultimate fallback: random features
            return np.random.random((len(texts), 50))
    
    def find_similar_repos(self, target_repo: Dict, candidate_repos: List[Dict], top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Find repositories similar to a target repository.
        
        Args:
            target_repo: The repository to find similarities for
            candidate_repos: List of repositories to compare against
            top_k: Number of similar repos to return
            
        Returns:
            List of (repo, similarity_score) tuples
        """
        try:
            # Prepare text descriptions
            target_text = self._repo_to_text(target_repo)
            candidate_texts = [self._repo_to_text(repo) for repo in candidate_repos]
            
            # Get embeddings
            all_texts = [target_text] + candidate_texts
            embeddings = self.get_embeddings(all_texts)
            
            # Calculate similarities
            target_embedding = embeddings[0:1]
            candidate_embeddings = embeddings[1:]
            
            similarities = cosine_similarity(target_embedding, candidate_embeddings)[0]
            
            # Get top-k similar repos
            similar_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in similar_indices:
                similarity_score = similarities[idx]
                similar_repo = candidate_repos[idx]
                results.append((similar_repo, float(similarity_score)))
            
            return results
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return []
    
    def _repo_to_text(self, repo: Dict) -> str:
        """Convert repository data to text for analysis."""
        text_parts = []
        
        # Add name and description
        if repo.get('name'):
            text_parts.append(repo['name'])
        
        if repo.get('description'):
            text_parts.append(repo['description'])
        
        # Add topics
        topics = repo.get('topics', [])
        if topics:
            text_parts.append(" ".join(topics))
        
        # Add language
        if repo.get('language'):
            text_parts.append(repo['language'])
        
        return " ".join(text_parts)
    
    def categorize_repositories(self, repos: List[Dict]) -> Dict[str, List[Dict]]:
        """Automatically categorize repositories using AI.
        
        Args:
            repos: List of repository dictionaries
            
        Returns:
            Dictionary with categories as keys and repo lists as values
        """
        categories = {
            'Web Development': [],
            'Machine Learning': [],
            'DevOps & Tools': [],
            'Mobile Development': [],
            'Data Science': [],
            'Gaming': [],
            'Blockchain': [],
            'Security': [],
            'Other': []
        }
        
        # Keywords for categorization
        category_keywords = {
            'Web Development': ['web', 'react', 'vue', 'angular', 'frontend', 'backend', 'api', 'server', 'http'],
            'Machine Learning': ['ml', 'ai', 'machine learning', 'neural', 'deep learning', 'tensorflow', 'pytorch'],
            'DevOps & Tools': ['devops', 'docker', 'kubernetes', 'ci', 'cd', 'deployment', 'monitoring', 'cli'],
            'Mobile Development': ['mobile', 'android', 'ios', 'react native', 'flutter', 'swift', 'kotlin'],
            'Data Science': ['data', 'analytics', 'visualization', 'pandas', 'numpy', 'jupyter', 'statistics'],
            'Gaming': ['game', 'gaming', 'unity', 'unreal', 'engine', 'graphics', '3d'],
            'Blockchain': ['blockchain', 'crypto', 'bitcoin', 'ethereum', 'smart contract', 'defi', 'web3'],
            'Security': ['security', 'cybersecurity', 'encryption', 'authentication', 'vulnerability', 'penetration']
        }
        
        for repo in repos:
            repo_text = self._repo_to_text(repo).lower()
            categorized = False
            
            # Check each category
            for category, keywords in category_keywords.items():
                if any(keyword in repo_text for keyword in keywords):
                    categories[category].append(repo)
                    categorized = True
                    break
            
            # If no category matches, put in "Other"
            if not categorized:
                categories['Other'].append(repo)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def generate_insights(self, repos: List[Dict]) -> Dict[str, any]:
        """Generate AI-powered insights about repository trends.
        
        Args:
            repos: List of repository dictionaries
            
        Returns:
            Dictionary containing various insights
        """
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
        
        # Categorization
        insights['categories'] = self.categorize_repositories(repos)
        
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
    
    def save_analysis_cache(self, data: Dict, cache_file: str = "analysis_cache.pkl"):
        """Save analysis results to cache for faster retrieval."""
        cache_path = os.path.join(self.cache_dir, cache_file)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info(f"Analysis cache saved to {cache_path}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def load_analysis_cache(self, cache_file: str = "analysis_cache.pkl") -> Optional[Dict]:
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
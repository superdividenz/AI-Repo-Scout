"""
LinkedIn Content Generator for AI Repo Scout.
Transforms repository analysis into professional LinkedIn posts.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import json
import os
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LinkedInPost:
    """Container for LinkedIn post content."""
    title: str
    content: str
    hashtags: List[str]
    post_type: str
    engagement_hooks: List[str]
    call_to_action: str


class LinkedInContentGenerator:
    """Generate professional LinkedIn content from repository analysis."""
    
    def __init__(self, config: Dict = None):
        """Initialize LinkedIn content generator."""
        self.config = config or {}
        self.post_templates = {
            'weekly_trends': self._get_weekly_trends_template(),
            'hot_repositories': self._get_hot_repos_template(),
            'technology_insights': self._get_tech_insights_template(),
            'market_analysis': self._get_market_analysis_template(),
            'developer_spotlight': self._get_developer_spotlight_template(),
            'investment_insights': self._get_investment_template()
        }
    
    def generate_weekly_trends_post(self, insights: Dict, repos_df=None) -> LinkedInPost:
        """Generate a weekly technology trends post."""
        try:
            # Extract key data
            total_repos = insights.get('total_repos', 0)
            top_languages = list(insights.get('language_trends', {}).keys())[:3]
            top_categories = list(insights.get('category_trends', {}).keys())[:3]
            recommendations = insights.get('recommendations', [])[:3]
            
            # Calculate momentum stats
            avg_momentum = insights.get('growth_analysis', {}).get('avg_momentum', 0)
            high_momentum_count = insights.get('growth_analysis', {}).get('high_momentum_count', 0)
            
            content = f"""🚀 Weekly Tech Trends Analysis - {datetime.now().strftime('%B %Y')}

I analyzed {total_repos} trending repositories this week using AI-powered insights. Here's what's driving innovation:

📈 TOP TRENDING LANGUAGES:
{chr(10).join([f"• {lang.title()}" for lang in top_languages[:3]])}

🔥 HOT CATEGORIES:
{chr(10).join([f"• {cat.title()}" for cat in top_categories[:3]])}

💡 KEY INSIGHTS:
{chr(10).join([f"• {rec}" for rec in recommendations[:3]])}

⚡ MOMENTUM METRICS:
• Average momentum score: {avg_momentum:.1f}/100
• High-growth projects: {high_momentum_count}
• Analysis confidence: High

The open-source ecosystem continues to evolve rapidly. Developers focusing on these trending areas are positioning themselves well for 2025.

What technologies are you most excited about? Share your thoughts below! 👇

#TechTrends #OpenSource #SoftwareDevelopment #Innovation #Programming"""

            hashtags = [
                "#TechTrends", "#OpenSource", "#SoftwareDevelopment", 
                "#Innovation", "#Programming", "#AI", "#GitHub"
            ]
            
            # Add language-specific hashtags
            for lang in top_languages[:2]:
                hashtags.append(f"#{lang.title()}")
            
            return LinkedInPost(
                title=f"Weekly Tech Trends - {datetime.now().strftime('%B %Y')}",
                content=content,
                hashtags=hashtags,
                post_type="weekly_trends",
                engagement_hooks=[
                    "What technologies are you most excited about?",
                    "Which trend surprised you the most?",
                    "Are you working with any of these technologies?"
                ],
                call_to_action="Share your thoughts in the comments! What's trending in your tech stack?"
            )
            
        except Exception as e:
            logger.error(f"Failed to generate weekly trends post: {e}")
            return self._get_fallback_post("weekly_trends")
    
    def generate_hot_repositories_post(self, repos_df, insights: Dict = None) -> LinkedInPost:
        """Generate a post highlighting hot repositories."""
        try:
            if repos_df is None or repos_df.empty:
                return self._get_fallback_post("hot_repositories")
            
            # Get top repositories by momentum
            top_repos = repos_df.nlargest(3, 'momentum_score') if 'momentum_score' in repos_df.columns else repos_df.head(3)
            
            repo_highlights = []
            for idx, repo in top_repos.iterrows():
                name = repo.get('name', 'Unknown')
                language = repo.get('language', 'N/A')
                stars = repo.get('stars', 0)
                momentum = repo.get('momentum_score', 0)
                description = repo.get('description', '')[:80] + "..." if len(repo.get('description', '')) > 80 else repo.get('description', '')
                
                repo_highlights.append(f"🚀 {name} ({language})\n   {description}\n   ⭐ {stars:,} stars | 📈 {momentum:.1f}/100 momentum")
            
            content = f"""🔥 Hottest GitHub Repositories This Week

I've been analyzing trending open-source projects, and these are absolutely crushing it right now:

{chr(10).join(repo_highlights)}

💡 WHY THESE MATTER:
• High momentum scores indicate rapid growth and community adoption
• Diverse technology stack representation
• Strong developer engagement and contribution activity

These projects are worth watching - they're solving real problems and gaining serious traction.

For developers: Great opportunities to contribute and learn
For businesses: Potential solutions to explore
For investors: Early indicators of emerging tech trends

Which repository caught your attention? Are you using any similar tools in your projects?

#OpenSource #GitHub #TechTrends #SoftwareDevelopment #Innovation"""

            hashtags = ["#OpenSource", "#GitHub", "#TechTrends", "#SoftwareDevelopment", "#Innovation"]
            
            # Add language hashtags from top repos
            languages = [repo.get('language') for _, repo in top_repos.iterrows() if repo.get('language')]
            for lang in set(languages):
                if lang:
                    hashtags.append(f"#{lang}")
            
            return LinkedInPost(
                title="Hottest GitHub Repositories This Week",
                content=content,
                hashtags=hashtags,
                post_type="hot_repositories",
                engagement_hooks=[
                    "Which repository caught your attention?",
                    "Have you tried any of these tools?",
                    "What's your favorite discovery method for new repos?"
                ],
                call_to_action="Drop a comment with your favorite GitHub discoveries!"
            )
            
        except Exception as e:
            logger.error(f"Failed to generate hot repositories post: {e}")
            return self._get_fallback_post("hot_repositories")
    
    def generate_technology_insights_post(self, insights: Dict) -> LinkedInPost:
        """Generate a technology insights and predictions post."""
        try:
            language_trends = insights.get('language_trends', {})
            category_trends = insights.get('category_trends', {})
            
            # Analyze trends
            top_language = max(language_trends.keys(), key=lambda x: language_trends[x]) if language_trends else "Python"
            growth_data = insights.get('growth_analysis', {})
            
            content = f"""💡 Technology Insights & Predictions for 2025

After analyzing hundreds of trending repositories, here are the patterns I'm seeing:

🎯 LANGUAGE DOMINANCE:
{top_language} continues to lead with strong ecosystem growth, particularly in AI/ML and web development spaces.

📊 EMERGING PATTERNS:
• Cross-platform development tools gaining momentum
• AI integration becoming standard, not optional  
• Developer experience (DX) tools seeing massive adoption
• Sustainability and performance optimization trending up

🔮 PREDICTIONS FOR NEXT QUARTER:
• More AI-assisted development tools
• Increased focus on edge computing solutions
• Growing emphasis on developer productivity
• Continued shift toward cloud-native architectures

⚡ DEVELOPER TAKEAWAYS:
• Invest in AI/ML skills regardless of your domain
• Focus on tools that improve team productivity
• Stay close to the open-source community
• Build with performance and sustainability in mind

The pace of innovation isn't slowing down - if anything, it's accelerating. The key is staying connected to the right signals.

What trends are you seeing in your industry? Are these insights matching your experience?

#TechTrends #SoftwareDevelopment #AI #Innovation #FutureOfTech #Programming"""

            return LinkedInPost(
                title="Technology Insights & Predictions for 2025",
                content=content,
                hashtags=["#TechTrends", "#SoftwareDevelopment", "#AI", "#Innovation", "#FutureOfTech", "#Programming"],
                post_type="technology_insights",
                engagement_hooks=[
                    "What trends are you seeing in your industry?",
                    "Do these insights match your experience?",
                    "Which prediction do you think is most likely?"
                ],
                call_to_action="Share your predictions - what tech trends are you betting on?"
            )
            
        except Exception as e:
            logger.error(f"Failed to generate technology insights post: {e}")
            return self._get_fallback_post("technology_insights")
    
    def generate_market_analysis_post(self, insights: Dict, repos_df=None) -> LinkedInPost:
        """Generate a market analysis post for business/investment audience."""
        try:
            total_repos = insights.get('total_repos', 0)
            high_momentum_count = insights.get('growth_analysis', {}).get('high_momentum_count', 0)
            category_trends = insights.get('category_trends', {})
            
            content = f"""📈 Open Source Market Analysis - Investment Perspective

Analyzed {total_repos} trending repositories this week. Here's what the data tells us about market opportunities:

🎯 HIGH-GROWTH SEGMENTS:
{chr(10).join([f"• {cat.title()} ({count} projects)" for cat, count in list(category_trends.items())[:3]])}

💰 INVESTMENT SIGNALS:
• {high_momentum_count} projects showing exceptional growth momentum
• Strong developer community engagement across all segments
• Enterprise adoption indicators in infrastructure tools
• Clear monetization paths emerging in developer tooling

🔍 MARKET OBSERVATIONS:
• Open source is becoming the default go-to-market strategy
• Companies building on popular OSS projects have faster adoption
• Developer-first products seeing higher engagement rates
• AI/ML integration is table stakes, not differentiator

⚡ BUSINESS IMPLICATIONS:
• Technical talent acquisition should focus on these trending areas
• Product roadmaps should consider open source integration strategies  
• Investment thesis should include developer ecosystem effects
• Time-to-market advantages for early movers in trending categories

The open source ecosystem is a leading indicator for commercial technology adoption. Smart money follows the developer mindshare.

For CTOs and investors: Are you tracking these signals in your decision-making?

#TechInvesting #OpenSource #MarketAnalysis #TechTrends #Innovation #BusinessStrategy"""

            return LinkedInPost(
                title="Open Source Market Analysis - Investment Perspective",
                content=content,
                hashtags=["#TechInvesting", "#OpenSource", "#MarketAnalysis", "#TechTrends", "#Innovation", "#BusinessStrategy"],
                post_type="market_analysis",
                engagement_hooks=[
                    "Are you tracking these signals in your decision-making?",
                    "What market trends are you seeing in your industry?",
                    "How do you use open source data for business insights?"
                ],
                call_to_action="What's your take on using open source trends for business strategy?"
            )
            
        except Exception as e:
            logger.error(f"Failed to generate market analysis post: {e}")
            return self._get_fallback_post("market_analysis")
    
    def _get_weekly_trends_template(self) -> str:
        return "weekly_trends"
    
    def _get_hot_repos_template(self) -> str:
        return "hot_repositories"
    
    def _get_tech_insights_template(self) -> str:
        return "technology_insights"
    
    def _get_market_analysis_template(self) -> str:
        return "market_analysis"
    
    def _get_developer_spotlight_template(self) -> str:
        return "developer_spotlight"
    
    def _get_investment_template(self) -> str:
        return "investment_insights"
    
    def _get_fallback_post(self, post_type: str) -> LinkedInPost:
        """Generate a fallback post when data is insufficient."""
        content = f"""🔍 Analyzing Open Source Trends

Currently diving deep into GitHub's trending repositories to identify the technologies and projects that are shaping the future of software development.

Stay tuned for insights on:
• Emerging programming languages and frameworks
• High-momentum projects worth watching  
• Developer tools gaining traction
• Investment opportunities in open source

The pace of innovation in the open source world continues to accelerate. Staying connected to these trends is crucial for developers, businesses, and investors alike.

What tools or projects have caught your attention lately?

#OpenSource #TechTrends #Innovation #SoftwareDevelopment"""

        return LinkedInPost(
            title=f"Tech Trends Analysis - {post_type.replace('_', ' ').title()}",
            content=content,
            hashtags=["#OpenSource", "#TechTrends", "#Innovation", "#SoftwareDevelopment"],
            post_type=post_type,
            engagement_hooks=["What tools or projects have caught your attention lately?"],
            call_to_action="Share your recent tech discoveries in the comments!"
        )
    
    def generate_all_posts(self, insights: Dict, repos_df=None) -> Dict[str, LinkedInPost]:
        """Generate all types of LinkedIn posts."""
        posts = {}
        
        try:
            posts['weekly_trends'] = self.generate_weekly_trends_post(insights, repos_df)
            posts['hot_repositories'] = self.generate_hot_repositories_post(repos_df, insights)
            posts['technology_insights'] = self.generate_technology_insights_post(insights)
            posts['market_analysis'] = self.generate_market_analysis_post(insights, repos_df)
            
            logger.info(f"Generated {len(posts)} LinkedIn posts")
            return posts
            
        except Exception as e:
            logger.error(f"Failed to generate all posts: {e}")
            return {}
    
    def export_posts_to_files(self, posts: Dict[str, LinkedInPost], output_dir: str = "linkedin_content"):
        """Export posts to individual files for easy copying."""
        os.makedirs(output_dir, exist_ok=True)
        
        for post_type, post in posts.items():
            filename = f"{post_type}_{datetime.now().strftime('%Y%m%d')}.md"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w') as f:
                f.write(f"# {post.title}\n\n")
                f.write(f"**Post Type:** {post.post_type}\n")
                f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
                f.write("## Content\n\n")
                f.write(post.content)
                f.write("\n\n## Hashtags\n\n")
                f.write(" ".join(post.hashtags))
                f.write("\n\n## Engagement Hooks\n\n")
                for hook in post.engagement_hooks:
                    f.write(f"- {hook}\n")
                f.write(f"\n## Call to Action\n\n{post.call_to_action}\n")
        
        logger.info(f"Exported {len(posts)} posts to {output_dir}/")
        return output_dir
    
    def create_posting_schedule(self, posts: Dict[str, LinkedInPost]) -> Dict:
        """Create a suggested posting schedule."""
        schedule = {
            'monday': posts.get('weekly_trends'),
            'wednesday': posts.get('hot_repositories'), 
            'friday': posts.get('technology_insights'),
            'saturday': posts.get('market_analysis')
        }
        
        return {day: post.title if post else None for day, post in schedule.items()}


# Convenience function for easy import
def generate_linkedin_content(insights: Dict, repos_df=None) -> Dict[str, LinkedInPost]:
    """Generate LinkedIn content from analysis results."""
    generator = LinkedInContentGenerator()
    return generator.generate_all_posts(insights, repos_df)
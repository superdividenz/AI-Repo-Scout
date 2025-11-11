#!/usr/bin/env python3
"""
Generate LinkedIn content from existing analysis data
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys
import os

# Add src to path
sys.path.append('src')
from linkedin_generator import LinkedInContentGenerator

def load_latest_analysis():
    """Load the most recent analysis data"""
    data_dir = Path('data')
    insight_files = list(data_dir.glob('insights_*.json'))
    
    if not insight_files:
        print("No analysis data found!")
        return None, None
    
    # Get the most recent file
    latest_file = max(insight_files, key=lambda f: f.stat().st_mtime)
    print(f"Using analysis data from: {latest_file}")
    
    with open(latest_file) as f:
        insights = json.load(f)
    
    # Convert top performers to DataFrame format
    repos_data = []
    for repo in insights['top_performers']['highest_momentum']:
        repos_data.append({
            'name': repo['name'],
            'full_name': repo['full_name'],
            'momentum_score': repo['momentum_score'],
            'stars': repo['stars'],
            'language': 'Python',  # Default for this analysis
            'description': f"High-momentum repository with {repo['stars']} stars"
        })
    
    repos_df = pd.DataFrame(repos_data)
    
    return insights, repos_df

def main():
    """Generate LinkedIn content from existing analysis data"""
    print("📊 Loading latest analysis data...")
    insights, repos_df = load_latest_analysis()
    
    if insights is None:
        print("❌ No analysis data available")
        return
    
    print(f"✅ Found analysis with {insights['summary']['total_repos']} repositories")
    print(f"📈 Average momentum score: {insights['summary']['avg_momentum_score']:.1f}")
    
    # Initialize LinkedIn generator
    config = {
        'openai_api_key': None,  # Not needed for this
        'github_token': None
    }
    
    linkedin_gen = LinkedInContentGenerator(config)
    
    print("\n📱 Generating LinkedIn content...")
    
    # Generate posts
    posts = linkedin_gen.generate_all_posts(insights, repos_df)
    
    # Export posts
    output_dir = linkedin_gen.export_posts_to_files(posts)
    
    print(f"\n✅ Generated {len(posts)} LinkedIn posts")
    print(f"📁 Saved to: {output_dir}")
    
    # Show posting schedule
    schedule = linkedin_gen.create_posting_schedule(posts)
    print(f"\n📅 Suggested posting schedule:")
    for day, post_title in schedule.items():
        print(f"  {day}: {post_title}")
    
    # Show first post preview
    if posts:
        first_post = posts[0]
        print(f"\n📄 Preview of '{first_post.title}':")
        print("=" * 50)
        print(first_post.content[:500] + "..." if len(first_post.content) > 500 else first_post.content)
        print("=" * 50)
    
    print(f"\n🎉 LinkedIn content generation completed!")
    print(f"💡 Check the {output_dir} directory for all posts")

if __name__ == "__main__":
    main()
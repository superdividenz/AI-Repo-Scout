#!/usr/bin/env python3
"""
LinkedIn Content Demo for AI Repo Scout.
Generate sample LinkedIn posts from repository analysis.
"""

import os
import sys
import json

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def demo_linkedin_content():
    """Demonstrate LinkedIn content generation."""
    print("📱 LinkedIn Content Generator Demo")
    print("=" * 50)
    
    try:
        from linkedin_generator import LinkedInContentGenerator
        import pandas as pd
        
        # Create sample data
        print("📊 Creating sample analysis data...")
        
        sample_insights = {
            'total_repos': 15,
            'language_trends': {
                'python': 6,
                'javascript': 4,
                'typescript': 3,
                'go': 2
            },
            'category_trends': {
                'ai': 5,
                'web': 4,
                'devops': 3,
                'mobile': 2,
                'blockchain': 1
            },
            'growth_analysis': {
                'avg_momentum': 78.5,
                'high_momentum_count': 8,
                'emerging_count': 5
            },
            'recommendations': [
                "🔥 Python and AI repositories dominating with 67% market share",
                "⚡ Web development tools showing 40% momentum increase",
                "🚀 DevOps automation projects gaining enterprise adoption",
                "💎 8 undervalued repositories could be tomorrow's unicorns"
            ]
        }
        
        sample_repos_data = [
            {
                'name': 'ai-code-assistant',
                'language': 'Python',
                'stars': 2500,
                'forks': 180,
                'momentum_score': 89.2,
                'description': 'AI-powered code completion and refactoring assistant for modern development workflows'
            },
            {
                'name': 'realtime-analytics',
                'language': 'JavaScript',
                'stars': 1800,
                'forks': 120,
                'momentum_score': 82.7,
                'description': 'High-performance real-time analytics dashboard with sub-second latency'
            },
            {
                'name': 'cloud-native-toolkit',
                'language': 'Go',
                'stars': 950,
                'forks': 85,
                'momentum_score': 76.4,
                'description': 'Complete toolkit for cloud-native application development and deployment'
            }
        ]
        
        sample_df = pd.DataFrame(sample_repos_data)
        
        # Generate LinkedIn content
        print("🚀 Generating professional LinkedIn posts...")
        generator = LinkedInContentGenerator()
        posts = generator.generate_all_posts(sample_insights, sample_df)
        
        print(f"✅ Generated {len(posts)} LinkedIn posts:")
        
        # Show previews
        for post_type, post in posts.items():
            print(f"\n📄 {post.title}")
            print("-" * 40)
            # Show first 200 characters of content
            preview = post.content[:200] + "..." if len(post.content) > 200 else post.content
            print(preview)
            print(f"📱 Hashtags: {' '.join(post.hashtags[:5])}")
        
        # Export to files
        print(f"\n📁 Exporting posts to files...")
        output_dir = generator.export_posts_to_files(posts, "demo_linkedin_content")
        
        # Show posting schedule
        schedule = generator.create_posting_schedule(posts)
        print(f"\n📅 Suggested Posting Schedule:")
        for day, post_title in schedule.items():
            if post_title:
                print(f"  • {day.title()}: {post_title}")
        
        print(f"\n🎯 Pro Tips:")
        print("  • Copy content from files in demo_linkedin_content/")
        print("  • Customize hashtags for your industry") 
        print("  • Add personal insights before posting")
        print("  • Engage with comments to boost reach")
        print("  • Post during peak engagement hours (9-10am, 12-1pm)")
        
        print(f"\n✨ Your LinkedIn content is ready!")
        print(f"📂 Files saved in: {output_dir}/")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're in the AI-Repo-Scout directory")
        return False
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False


if __name__ == "__main__":
    print("Starting LinkedIn Content Demo...\n")
    success = demo_linkedin_content()
    
    if success:
        print(f"\n🎉 Demo completed successfully!")
        print(f"💡 Next steps:")
        print(f"  1. Run real analysis: python3 src/main.py --linkedin")
        print(f"  2. Check the generated content files")
        print(f"  3. Customize and post to LinkedIn")
        print(f"  4. Track engagement and iterate")
    else:
        print(f"\n🔧 Please fix the issues and try again")
    
    sys.exit(0 if success else 1)
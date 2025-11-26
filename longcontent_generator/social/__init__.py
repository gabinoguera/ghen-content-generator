"""
Social Media Adapters para GHEN Content Generator.

Este módulo transforma artículos técnicos en posts optimizados para cada red social.
"""

from .adapters import (
    generate_all_social_posts,
    generate_twitter_thread,
    generate_linkedin_post,
    generate_reddit_post,
    generate_threads_post,
)

__all__ = [
    'generate_all_social_posts',
    'generate_twitter_thread',
    'generate_linkedin_post',
    'generate_reddit_post',
    'generate_threads_post',
]

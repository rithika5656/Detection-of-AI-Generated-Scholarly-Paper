"""
Chatbot Module Initialization
==============================
This module provides explainable AI chatbot functionality for the
AI-Generated Scholarly Paper Detection System.

ETHICAL NOTICE:
This chatbot ONLY explains detection results. It does NOT:
- Generate academic content
- Help bypass detection systems
- Assist in academic dishonesty

Author: AI-Generated Scholarly Paper Detection System
"""

from .explainer import (
    ExplainerChatbot,
    get_chatbot,
    chat,
    generate_explanation
)

__all__ = [
    'ExplainerChatbot',
    'get_chatbot', 
    'chat',
    'generate_explanation'
]

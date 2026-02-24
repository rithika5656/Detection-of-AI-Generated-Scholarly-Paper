"""
Explainable AI Chatbot Module
==============================
This module provides an intelligent chatbot that explains AI detection 
results to users in a clear, educational, and ethical manner.

IMPORTANT: This chatbot is designed ONLY to explain detection results.
It does NOT generate academic content or assist in academic dishonesty.

Features:
- Explains detection scores and their meaning
- Provides educational context about AI-generated text characteristics
- Answers questions about the detection methodology
- Offers guidance for improving human-written content

Author: AI-Generated Scholarly Paper Detection System
For Academic Use Only - IEEE/College-level Project
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime


class ExplainerChatbot:
    """
    An explainable AI chatbot for interpreting detection results.
    
    This chatbot provides human-readable explanations of detection
    scores and helps users understand what the analysis reveals
    about their submitted papers.
    
    ETHICAL GUIDELINES:
    - Only explains detection results
    - Does not generate academic content
    - Encourages academic integrity
    - Provides educational information about AI detection
    """
    
    def __init__(self):
        """Initialize the chatbot with response templates and knowledge base."""
        
        # Ethical disclaimer
        self.ethical_disclaimer = (
            "I'm an assistant designed to explain AI detection results. "
            "I cannot help generate academic content or assist in bypassing detection. "
            "My purpose is to support academic integrity."
        )
        
        # Intent patterns for understanding user queries
        self.intent_patterns = {
            'explain_score': [
                r'(what|explain|tell me about).*(score|result|analysis)',
                r'(why|how).*(score|detected|flagged)',
                r'(mean|meaning|interpret).*(score|result|number)',
            ],
            'explain_feature': [
                r'(what is|explain|tell me about).*(perplexity|burstiness)',
                r'(what is|explain).*(gpt|gemini|claude).*(pattern|detection)',
                r'(what|explain).*(citation|hallucination)',
                r'(what|explain).*(repetition|hedging|overflow)',
            ],
            'improve_writing': [
                r'(how|can I|should I).*(improve|fix|change|rewrite)',
                r'(make|write).*(more human|less ai|better)',
                r'(tips|advice|suggestions).*(writing|improve)',
            ],
            'methodology': [
                r'(how|what).*(detect|work|algorithm|method)',
                r'(explain|tell me about).*(system|detection|process)',
                r'(what|which).*(features|patterns|indicators)',
            ],
            'decision': [
                r'(why|explain).*(accept|reject|review)',
                r'(what|mean).*(decision|recommendation|verdict)',
                r'(should I|what should).*(do|next|action)',
            ],
            'greeting': [
                r'^(hi|hello|hey|greetings)',
                r'(how are you|what\'s up)',
            ],
            'thanks': [
                r'(thank|thanks|appreciate)',
            ],
            'help': [
                r'(help|assist|support)',
                r'(what can you|can you help)',
            ],
            'unethical_request': [
                r'(generate|write|create).*(paper|essay|content|text)',
                r'(bypass|avoid|trick|fool).*(detection|system)',
                r'(make|help).*(undetectable|pass)',
            ],
        }
        
        # Feature explanations knowledge base
        self.feature_explanations = {
            'gpt_repetition': {
                'name': 'GPT-Style Repetition',
                'description': (
                    "GPT models often use formulaic academic phrases like 'In conclusion', "
                    "'It is important to note', or 'As mentioned earlier'. High repetition "
                    "of these patterns suggests AI generation."
                ),
                'high_score_meaning': (
                    "Your text contains many formulaic phrases typical of GPT-generated content. "
                    "Human writers tend to vary their transitions and connecting phrases more."
                ),
                'low_score_meaning': (
                    "Your text shows natural variation in phrasing, which is more consistent "
                    "with human writing patterns."
                ),
            },
            'gemini_overflow': {
                'name': 'Gemini Explanatory Overflow',
                'description': (
                    "Gemini-style AI often over-explains concepts using phrases like "
                    "'Let me explain', 'In other words', or 'To elaborate further'. "
                    "This pattern indicates excessive clarification."
                ),
                'high_score_meaning': (
                    "Your text contains many over-explanation patterns. Consider being more "
                    "direct and trusting your reader to understand without repeated clarification."
                ),
                'low_score_meaning': (
                    "Your explanations are appropriately concise without unnecessary elaboration."
                ),
            },
            'claude_hedging': {
                'name': 'Claude Uncertainty Hedging',
                'description': (
                    "Claude-style AI frequently uses hedging language like 'perhaps', "
                    "'possibly', 'it seems', or 'I think'. While appropriate in moderation, "
                    "excessive hedging can indicate AI generation."
                ),
                'high_score_meaning': (
                    "Your text contains significant uncertainty hedging. Consider being more "
                    "assertive in your claims where evidence supports them."
                ),
                'low_score_meaning': (
                    "Your text shows confident assertion balanced with appropriate uncertainty."
                ),
            },
            'burstiness': {
                'name': 'Burstiness (Sentence Variation)',
                'description': (
                    "Burstiness measures variation in sentence length. Human writing typically "
                    "has high burstiness (varied sentence lengths), while AI-generated text "
                    "tends to have uniform, predictable sentence structures."
                ),
                'high_score_meaning': (
                    "Your sentences have very uniform length, which is characteristic of AI. "
                    "Human writers naturally vary between short punchy sentences and longer, "
                    "more complex ones."
                ),
                'low_score_meaning': (
                    "Your writing shows natural variation in sentence length, consistent with "
                    "human writing patterns."
                ),
            },
            'citation_hallucination': {
                'name': 'Citation Hallucination Detection',
                'description': (
                    "AI models sometimes generate fake or 'hallucinated' citations with "
                    "generic author names or implausible publication dates. This detector "
                    "identifies potentially fabricated references."
                ),
                'high_score_meaning': (
                    "Some of your citations appear suspicious. Please verify all references "
                    "against actual published works. Fabricated citations are a serious "
                    "academic integrity issue."
                ),
                'low_score_meaning': (
                    "Your citations don't show obvious signs of fabrication. However, all "
                    "citations should still be verified for accuracy."
                ),
            },
            'perplexity': {
                'name': 'Perplexity (Text Predictability)',
                'description': (
                    "Perplexity measures how predictable the text is. AI-generated text "
                    "typically has lower perplexity (more predictable word choices), while "
                    "human text is often more surprising and varied."
                ),
                'high_score_meaning': (
                    "Your text follows very predictable patterns. Human writing typically "
                    "includes more unique word choices and unexpected phrasings."
                ),
                'low_score_meaning': (
                    "Your text shows healthy unpredictability consistent with human writing."
                ),
            },
        }
        
        # Decision explanations
        self.decision_explanations = {
            'Accept': (
                "The paper shows predominantly human-written characteristics. The detection "
                "scores are below concerning thresholds. However, this is not a guarantee - "
                "final judgment should include human review."
            ),
            'Review Needed': (
                "The paper shows mixed signals that require human review. Some AI-like patterns "
                "were detected, but they could also appear in human writing. A closer examination "
                "by a human reviewer is recommended."
            ),
            'Reject': (
                "The paper shows strong indicators of AI generation across multiple metrics. "
                "The combined scores exceed acceptable thresholds. Further investigation or "
                "resubmission may be required."
            ),
        }
        
        # Conversation context
        self.context = {
            'last_analysis': None,
            'conversation_history': [],
        }
    
    def set_analysis_context(self, analysis_result: Dict[str, Any]) -> None:
        """
        Set the current analysis result for context-aware responses.
        
        Args:
            analysis_result: The full analysis result from the detection system
        """
        self.context['last_analysis'] = analysis_result
    
    def get_response(self, user_message: str, analysis_result: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate a response to the user's message.
        
        Args:
            user_message: The user's question or message
            analysis_result: Optional analysis result to provide context
            
        Returns:
            Dictionary with response text and metadata
        """
        if analysis_result:
            self.set_analysis_context(analysis_result)
        
        # Detect intent
        intent = self._detect_intent(user_message)
        
        # Generate appropriate response
        response = self._generate_response(intent, user_message)
        
        # Log conversation
        self.context['conversation_history'].append({
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'intent': intent,
            'response': response['message']
        })
        
        return response
    
    def _detect_intent(self, message: str) -> str:
        """Detect the user's intent from their message."""
        message_lower = message.lower().strip()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent
        
        return 'general_query'
    
    def _generate_response(self, intent: str, message: str) -> Dict[str, Any]:
        """Generate response based on detected intent."""
        
        if intent == 'unethical_request':
            return self._respond_to_unethical_request()
        
        if intent == 'greeting':
            return self._respond_to_greeting()
        
        if intent == 'thanks':
            return self._respond_to_thanks()
        
        if intent == 'help':
            return self._respond_to_help()
        
        if intent == 'explain_score':
            return self._explain_overall_score()
        
        if intent == 'explain_feature':
            return self._explain_specific_feature(message)
        
        if intent == 'improve_writing':
            return self._provide_writing_tips()
        
        if intent == 'methodology':
            return self._explain_methodology()
        
        if intent == 'decision':
            return self._explain_decision()
        
        return self._respond_to_general_query(message)
    
    def _respond_to_unethical_request(self) -> Dict[str, Any]:
        """Respond to requests that violate ethical guidelines."""
        return {
            'message': (
                "I cannot assist with that request. My purpose is to explain AI detection "
                "results, not to help bypass detection or generate academic content.\n\n"
                "Academic integrity is important for:\n"
                "• Developing your own critical thinking skills\n"
                "• Earning credentials that accurately reflect your abilities\n"
                "• Maintaining the value of academic qualifications\n\n"
                "If you need help with writing, please consult your institution's "
                "writing center or academic support services."
            ),
            'type': 'ethical_warning',
            'intent': 'unethical_request'
        }
    
    def _respond_to_greeting(self) -> Dict[str, Any]:
        """Respond to greetings."""
        return {
            'message': (
                "Hello! I'm your AI Detection Explainer Assistant. I can help you understand:\n\n"
                "• Your paper's detection scores and what they mean\n"
                "• Specific features like perplexity, burstiness, and pattern detection\n"
                "• Why your paper received a particular decision\n"
                "• How our detection methodology works\n\n"
                "What would you like to know about your analysis results?"
            ),
            'type': 'greeting',
            'intent': 'greeting'
        }
    
    def _respond_to_thanks(self) -> Dict[str, Any]:
        """Respond to thanks."""
        return {
            'message': (
                "You're welcome! Remember, understanding AI detection helps you become a "
                "better writer. If you have more questions about your analysis, feel free to ask!"
            ),
            'type': 'acknowledgment',
            'intent': 'thanks'
        }
    
    def _respond_to_help(self) -> Dict[str, Any]:
        """Respond to help requests."""
        return {
            'message': (
                "I can help you understand your paper's AI detection analysis. "
                "Here are some things you can ask me:\n\n"
                "📊 **About Scores:**\n"
                "• 'Explain my scores'\n"
                "• 'Why was my paper flagged?'\n\n"
                "🔍 **About Features:**\n"
                "• 'What is perplexity?'\n"
                "• 'Explain burstiness'\n"
                "• 'What is GPT-style repetition?'\n\n"
                "📝 **About Decisions:**\n"
                "• 'Why was my paper rejected?'\n"
                "• 'What does Review Needed mean?'\n\n"
                "💡 **About Improvement:**\n"
                "• 'How can I improve my writing?'\n"
                "• 'Tips for more natural writing'\n\n"
                "What would you like to know?"
            ),
            'type': 'help',
            'intent': 'help'
        }
    
    def _explain_overall_score(self) -> Dict[str, Any]:
        """Explain the overall detection score."""
        analysis = self.context.get('last_analysis')
        
        if not analysis:
            return {
                'message': (
                    "I don't have an analysis result to explain. Please upload a paper "
                    "for analysis first, or provide the analysis data in your question."
                ),
                'type': 'no_context',
                'intent': 'explain_score'
            }
        
        scores = analysis.get('scores', {})
        ai_score = scores.get('ai_score', {})
        ai_score_val = ai_score.get('score', 0) if isinstance(ai_score, dict) else ai_score
        final = scores.get('final', {})
        decision = final.get('decision', 'Unknown')
        
        # Get GenAI features if available
        genai = scores.get('genai_features', {})
        
        message = f"📊 **Analysis Summary**\n\n"
        message += f"**AI Generation Score:** {ai_score_val:.1%}\n"
        message += f"**Decision:** {decision}\n\n"
        
        if isinstance(ai_score, dict) and 'metrics' in ai_score:
            metrics = ai_score['metrics']
            message += f"**Key Metrics:**\n"
            perplexity_val = metrics.get('perplexity', 'N/A')
            burstiness_val = metrics.get('burstiness', 'N/A')
            message += f"• Perplexity: {perplexity_val}%\n" if perplexity_val != 'N/A' else f"• Perplexity: N/A\n"
            message += f"• Burstiness: {burstiness_val}%\n" if burstiness_val != 'N/A' else f"• Burstiness: N/A\n"
            message += f"• Method: {metrics.get('method', 'Unknown')}\n\n"
        
        if genai and 'features' in genai:
            message += "**GenAI Pattern Analysis:**\n"
            features = genai.get('features', {})
            for feature_name, feature_data in features.items():
                if isinstance(feature_data, dict):
                    score = feature_data.get('score', 0)
                    readable_name = feature_name.replace('_', ' ').title()
                    level = "High" if score > 0.6 else "Moderate" if score > 0.3 else "Low"
                    message += f"• {readable_name}: {level} ({score:.1%})\n"
        
        message += f"\n**What this means:**\n{self.decision_explanations.get(decision, 'No explanation available.')}"
        
        return {
            'message': message,
            'type': 'score_explanation',
            'intent': 'explain_score',
            'data': {'ai_score': ai_score_val, 'decision': decision}
        }
    
    def _explain_specific_feature(self, message: str) -> Dict[str, Any]:
        """Explain a specific detection feature."""
        message_lower = message.lower()
        
        # Find which feature is being asked about
        feature_key = None
        if 'perplexity' in message_lower:
            feature_key = 'perplexity'
        elif 'burstiness' in message_lower or 'burst' in message_lower:
            feature_key = 'burstiness'
        elif 'gpt' in message_lower or 'repetition' in message_lower:
            feature_key = 'gpt_repetition'
        elif 'gemini' in message_lower or 'overflow' in message_lower or 'over-explain' in message_lower:
            feature_key = 'gemini_overflow'
        elif 'claude' in message_lower or 'hedging' in message_lower:
            feature_key = 'claude_hedging'
        elif 'citation' in message_lower or 'hallucination' in message_lower:
            feature_key = 'citation_hallucination'
        
        if not feature_key:
            return {
                'message': (
                    "I can explain these detection features:\n\n"
                    "• **Perplexity** - Text predictability measure\n"
                    "• **Burstiness** - Sentence length variation\n"
                    "• **GPT Repetition** - Formulaic phrase patterns\n"
                    "• **Gemini Overflow** - Over-explanation patterns\n"
                    "• **Claude Hedging** - Uncertainty language\n"
                    "• **Citation Hallucination** - Fake reference detection\n\n"
                    "Which one would you like to know more about?"
                ),
                'type': 'feature_list',
                'intent': 'explain_feature'
            }
        
        feature_info = self.feature_explanations.get(feature_key, {})
        
        # Get score from context if available
        analysis = self.context.get('last_analysis')
        score_info = ""
        if analysis:
            genai = analysis.get('scores', {}).get('genai_features', {})
            if genai and 'features' in genai:
                feature_data = genai['features'].get(feature_key, {})
                if isinstance(feature_data, dict):
                    score = feature_data.get('score', 0)
                    score_info = f"\n\n**Your Score:** {score:.1%}\n"
                    if score > 0.5:
                        score_info += feature_info.get('high_score_meaning', '')
                    else:
                        score_info += feature_info.get('low_score_meaning', '')
        
        response = f"**{feature_info.get('name', feature_key)}**\n\n"
        response += feature_info.get('description', 'No description available.')
        response += score_info
        
        return {
            'message': response,
            'type': 'feature_explanation',
            'intent': 'explain_feature',
            'feature': feature_key
        }
    
    def _provide_writing_tips(self) -> Dict[str, Any]:
        """Provide tips for improving writing to appear more human-like."""
        return {
            'message': (
                "📝 **Tips for Natural Human Writing**\n\n"
                "**1. Vary Your Sentence Structure**\n"
                "Mix short sentences with longer, more complex ones. AI tends to "
                "produce uniform sentence lengths.\n\n"
                "**2. Use Unique Word Choices**\n"
                "Don't rely on common academic phrases. Find your own voice and "
                "ways to express ideas.\n\n"
                "**3. Avoid Formulaic Transitions**\n"
                "Instead of 'In conclusion' or 'It is important to note', try more "
                "specific transitions that connect your actual ideas.\n\n"
                "**4. Be Appropriately Direct**\n"
                "Balance confidence with uncertainty. Don't over-hedge with 'perhaps' "
                "and 'possibly' but also don't be overconfident without evidence.\n\n"
                "**5. Verify All Citations**\n"
                "Always cite real, verifiable sources. Never use citations you haven't "
                "actually read and verified.\n\n"
                "**6. Show Your Thinking Process**\n"
                "Include your reasoning, questions, and the evolution of your ideas. "
                "AI tends to present polished conclusions without the messy thinking.\n\n"
                "**Remember:** The goal isn't to 'beat' detection - it's to develop "
                "genuine writing skills that serve you throughout your career."
            ),
            'type': 'writing_tips',
            'intent': 'improve_writing'
        }
    
    def _explain_methodology(self) -> Dict[str, Any]:
        """Explain how the detection system works."""
        return {
            'message': (
                "🔬 **How the Detection System Works**\n\n"
                "Our system uses multiple approaches to detect AI-generated content:\n\n"
                "**1. Machine Learning Classification**\n"
                "A Random Forest model trained on known human and AI-generated academic "
                "texts analyzes linguistic patterns.\n\n"
                "**2. GenAI-Specific Features**\n"
                "We extract features characteristic of different LLMs:\n"
                "• GPT-style repetition patterns\n"
                "• Gemini explanatory overflow\n"
                "• Claude uncertainty hedging\n\n"
                "**3. Statistical Measures**\n"
                "• **Perplexity:** How predictable is the text?\n"
                "• **Burstiness:** How varied are sentence lengths?\n\n"
                "**4. Citation Analysis**\n"
                "We check for potentially hallucinated or fabricated references.\n\n"
                "**5. Score Aggregation**\n"
                "Individual scores are weighted and combined for a final decision:\n"
                "• Accept (< 30% AI probability)\n"
                "• Review Needed (30-70%)\n"
                "• Reject (> 70%)\n\n"
                "**Important:** No AI detection system is 100% accurate. Results "
                "should be used as one input to human judgment, not as definitive verdicts."
            ),
            'type': 'methodology',
            'intent': 'methodology'
        }
    
    def _explain_decision(self) -> Dict[str, Any]:
        """Explain the decision/recommendation."""
        analysis = self.context.get('last_analysis')
        
        if not analysis:
            return {
                'message': (
                    "To explain a decision, I need an analysis result. Please upload a "
                    "paper for analysis first.\n\n"
                    "In general, our decisions mean:\n\n"
                    f"**Accept:** {self.decision_explanations['Accept']}\n\n"
                    f"**Review Needed:** {self.decision_explanations['Review Needed']}\n\n"
                    f"**Reject:** {self.decision_explanations['Reject']}"
                ),
                'type': 'decision_general',
                'intent': 'decision'
            }
        
        decision = analysis.get('scores', {}).get('final', {}).get('decision', 'Unknown')
        explanation = self.decision_explanations.get(decision, 'No explanation available.')
        
        # Add specific reasons if available
        eligibility = analysis.get('eligibility', {})
        reasons = eligibility.get('reasons', [])
        
        message = f"**Your Paper's Decision: {decision}**\n\n{explanation}"
        
        if reasons:
            message += "\n\n**Specific Concerns:**\n"
            for reason in reasons:
                message += f"• {reason}\n"
        
        message += (
            "\n\n**What You Can Do:**\n"
            "• Review the specific feature scores for problem areas\n"
            "• Ask me to explain any feature you don't understand\n"
            "• Consider revising sections with high AI-like patterns\n"
            "• Ensure all citations are accurate and verifiable"
        )
        
        return {
            'message': message,
            'type': 'decision_explanation',
            'intent': 'decision',
            'decision': decision
        }
    
    def _respond_to_general_query(self, message: str) -> Dict[str, Any]:
        """Respond to queries that don't match specific intents."""
        return {
            'message': (
                "I'm not sure I understood your question. I can help you with:\n\n"
                "• **Explaining your scores** - 'What do my scores mean?'\n"
                "• **Understanding features** - 'What is perplexity?'\n"
                "• **Decision explanation** - 'Why was my paper flagged?'\n"
                "• **Writing improvement** - 'How can I improve my writing?'\n"
                "• **Methodology** - 'How does the detection work?'\n\n"
                "Could you rephrase your question or choose one of these topics?"
            ),
            'type': 'clarification',
            'intent': 'general_query'
        }
    
    def generate_automatic_explanation(self, analysis_result: Dict[str, Any]) -> str:
        """
        Generate an automatic explanation when analysis completes.
        
        This provides a proactive summary without user prompting.
        
        Args:
            analysis_result: The complete analysis result
            
        Returns:
            A formatted explanation string
        """
        self.set_analysis_context(analysis_result)
        
        scores = analysis_result.get('scores', {})
        ai_score = scores.get('ai_score', {})
        ai_score_val = ai_score.get('score', 0) if isinstance(ai_score, dict) else ai_score
        final = scores.get('final', {})
        decision = final.get('decision', 'Unknown')
        
        # Determine tone based on decision
        if decision == 'Accept':
            intro = "Great news! Your paper appears to be predominantly human-written. 📗"
        elif decision == 'Reject':
            intro = "This paper shows significant AI-generated characteristics. 📕"
        else:
            intro = "Your paper shows mixed signals and needs human review. 📙"
        
        explanation = f"{intro}\n\n"
        explanation += f"**AI Generation Probability:** {ai_score_val:.1%}\n"
        explanation += f"**Recommendation:** {decision}\n\n"
        
        # Add key insights
        genai = scores.get('genai_features', {})
        if genai and 'interpretation' in genai:
            explanation += "**Key Findings:**\n"
            for interp in genai.get('interpretation', [])[:3]:
                explanation += f"• {interp}\n"
        
        explanation += "\n💬 Ask me if you'd like to understand any score in detail!"
        
        return explanation


# Singleton instance for the API
_chatbot_instance = None

def get_chatbot() -> ExplainerChatbot:
    """Get the singleton chatbot instance."""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = ExplainerChatbot()
    return _chatbot_instance


def chat(message: str, analysis_result: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Convenience function for chatbot interaction.
    
    Args:
        message: User's message
        analysis_result: Optional analysis context
        
    Returns:
        Chatbot response dictionary
    """
    chatbot = get_chatbot()
    return chatbot.get_response(message, analysis_result)


def generate_explanation(analysis_result: Dict[str, Any]) -> str:
    """
    Generate automatic explanation for analysis result.
    
    Args:
        analysis_result: The analysis result to explain
        
    Returns:
        Formatted explanation string
    """
    chatbot = get_chatbot()
    return chatbot.generate_automatic_explanation(analysis_result)


if __name__ == "__main__":
    # Test the chatbot
    chatbot = ExplainerChatbot()
    
    # Test various intents
    test_messages = [
        "Hello!",
        "What is perplexity?",
        "Explain my scores",
        "How does the detection work?",
        "Can you help me write a paper?",  # Unethical request
        "How can I improve my writing?",
    ]
    
    print("Chatbot Testing:\n")
    for msg in test_messages:
        print(f"User: {msg}")
        response = chatbot.get_response(msg)
        print(f"Bot: {response['message'][:200]}...")
        print(f"Intent: {response['intent']}\n")
        print("-" * 50)

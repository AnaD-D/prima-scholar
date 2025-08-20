"""
Prima Scholar Mentorship Service
Provides elite-level academic mentorship using AI
"""

import openai
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
import re

class ScholarMentorshipService:
    """Provides scholar-level academic mentorship and guidance"""
    
    def __init__(self, openai_api_key: str, excellence_engine, db_manager):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.excellence_engine = excellence_engine
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Query sophistication patterns
        self.sophistication_patterns = {
            'scholar': [
                r'epistemological', r'ontological', r'paradigmatic',
                r'theoretical implications', r'methodological framework',
                r'meta-analysis', r'systematic review', r'conceptual model'
            ],
            'advanced': [
                r'analyze', r'evaluate', r'critique', r'synthesize',
                r'compare and contrast', r'theoretical perspective',
                r'research methodology', r'empirical evidence'
            ],
            'intermediate': [
                r'how does.*relate', r'what is the relationship',
                r'explain the connection', r'compare.*with',
                r'analyze the impact', r'discuss the implications'
            ],
            'basic': [
                r'what is', r'explain', r'define', r'describe',
                r'list', r'summarize', r'overview', r'introduction'
            ]
        }
        
        # Academic disciplines for context
        self.academic_contexts = {
            'STEM': ['mathematics', 'physics', 'chemistry', 'biology', 'engineering', 'computer science'],
            'Social Sciences': ['psychology', 'sociology', 'anthropology', 'political science', 'economics'],
            'Humanities': ['literature', 'philosophy', 'history', 'linguistics', 'art history'],
            'Business': ['management', 'marketing', 'finance', 'accounting', 'strategy'],
            'Medicine': ['anatomy', 'physiology', 'pathology', 'clinical', 'public health'],
            'Law': ['constitutional', 'criminal', 'civil', 'international', 'corporate']
        }
        
        self.logger.info("Scholar Mentorship Service initialized")
    
    def generate_scholar_response(self, student_id: str, query: str, 
                                context_documents: Optional[List[str]] = None) -> Dict:
        """Generate elite academic mentorship response"""
        try:
            # Get student profile and context
            student_profile = self._get_student_context(student_id)
            if not student_profile:
                return {'error': 'Student profile not found'}
            
            # Assess query sophistication
            query_sophistication = self._assess_query_sophistication(query)
            
            # Get relevant document context
            if not context_documents:
                context_documents = self._search_relevant_context(student_id, query)
            
            # Analyze excellence gap
            excellence_gap_analysis = self._analyze_excellence_gap(
                query, student_profile, query_sophistication
            )
            
            # Generate scholar-level response
            mentorship_response = self._generate_mentorship_response(
                query, student_profile, context_documents, 
                query_sophistication, excellence_gap_analysis
            )
            
            # Calculate session quality score
            session_quality = self._calculate_session_quality(
                query, mentorship_response, query_sophistication
            )
            
            # Update predictions based on engagement
            probability_updates = self._update_predictions_from_engagement(
                student_id, query, mentorship_response, session_quality
            )
            
            # Store session in database
            session_id = self._store_mentorship_session(
                student_id, query, query_sophistication, excellence_gap_analysis,
                mentorship_response, session_quality, probability_updates
            )
            
            return {
                'session_id': session_id,
                'query_sophistication': query_sophistication,
                'excellence_gap_analysis': excellence_gap_analysis,
                'scholar_response': mentorship_response['response'],
                'theoretical_frameworks': mentorship_response['frameworks'],
                'advanced_methodologies': mentorship_response['methodologies'],
                'excellence_impact': mentorship_response['excellence_impact'],
                'scholarly_actions': mentorship_response['actions'],
                'deeper_questions': mentorship_response['deeper_questions'],
                'resource_recommendations': mentorship_response['resources'],
                'thinking_elevation': mentorship_response['thinking_elevation'],
                'session_quality_score': session_quality,
                'probability_updates': probability_updates,
                'response_time': mentorship_response['response_time'],
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Mentorship response generation failed: {str(e)}")
            return {'error': str(e)}
    
    def _get_student_context(self, student_id: str) -> Optional[Dict]:
        """Get comprehensive student context for mentorship"""
        try:
            # Get basic profile
            profile = self.db.get_student_profile(student_id)
            if not profile:
                return None
            
            # Get recent mentorship sessions
            recent_sessions_query = """
            SELECT query, query_sophistication, session_quality_score, created_at
            FROM mentorship_sessions
            WHERE student_id = :student_id
            ORDER BY created_at DESC
            LIMIT 5
            """
            
            recent_sessions = self.db.execute_query(
                recent_sessions_query, {'student_id': student_id}
            )
            
            # Get document statistics
            doc_stats_query = """
            SELECT 
                COUNT(*) as total_docs,
                COUNT(CASE WHEN excellence_tier = 'elite' THEN 1 END) as elite_docs,
                AVG(complexity_score) as avg_complexity,
                GROUP_CONCAT(DISTINCT document_type) as doc_types
            FROM academic_documents
            WHERE student_id = :student_id
            """
            
            doc_stats = self.db.execute_query(doc_stats_query, {'student_id': student_id})
            
            # Combine context
            context = dict(profile)
            context.update({
                'recent_sessions': recent_sessions,
                'document_stats': doc_stats[0] if doc_stats else {},
                'academic_field': self._infer_academic_field(student_id),
                'engagement_pattern': self._analyze_engagement_pattern(recent_sessions)
            })
            
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to get student context: {str(e)}")
            return None
    
    def _assess_query_sophistication(self, query: str) -> str:
        """Assess the academic sophistication level of the query"""
        query_lower = query.lower()
        
        # Count pattern matches for each sophistication level
        sophistication_scores = {}
        for level, patterns in self.sophistication_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, query_lower))
            sophistication_scores[level] = score
        
        # Additional factors
        
        # Question complexity
        question_count = query.count('?')
        if question_count > 1:
            sophistication_scores['advanced'] = sophistication_scores.get('advanced', 0) + 1
        
        # Word count and structure
        word_count = len(query.split())
        if word_count > 30:
            sophistication_scores['advanced'] = sophistication_scores.get('advanced', 0) + 1
        elif word_count > 50:
            sophistication_scores['scholar'] = sophistication_scores.get('scholar', 0) + 1
        
        # Technical terminology
        technical_terms = [
            'methodology', 'epistemology', 'paradigm', 'framework',
            'empirical', 'theoretical', 'analysis', 'synthesis'
        ]
        technical_count = sum(1 for term in technical_terms if term in query_lower)
        
        if technical_count >= 3:
            sophistication_scores['scholar'] = sophistication_scores.get('scholar', 0) + 2
        elif technical_count >= 2:
            sophistication_scores['advanced'] = sophistication_scores.get('advanced', 0) + 1
        
        # Return highest scoring level
        if not any(sophistication_scores.values()):
            return 'basic'
        
        return max(sophistication_scores.items(), key=lambda x: x[1])[0]
    
    def _search_relevant_context(self, student_id: str, query: str, limit: int = 5) -> List[str]:
        """Search for relevant context from student's documents"""
        try:
            # Use the academic processor to search documents
            # This would typically use the existing processor instance
            # For now, we'll do a simple database search
            
            search_query = """
            SELECT content, title, excellence_tier
            FROM academic_documents
            WHERE student_id = :student_id
            AND (MATCH(content) AGAINST (:query IN NATURAL LANGUAGE MODE)
                 OR MATCH(title) AGAINST (:query IN NATURAL LANGUAGE MODE))
            ORDER BY excellence_tier DESC, complexity_score DESC
            LIMIT :limit
            """
            
            results = self.db.execute_query(search_query, {
                'student_id': student_id,
                'query': query,
                'limit': limit
            })
            
            # Extract content chunks
            context_chunks = []
            for result in results:
                # Truncate content to manageable size
                content = result['content'][:1000]
                context_chunks.append(f"[{result['title']}]: {content}")
            
            return context_chunks
            
        except Exception as e:
            self.logger.error(f"Context search failed: {str(e)}")
            return []
    
    def _analyze_excellence_gap(self, query: str, student_profile: Dict, 
                              query_sophistication: str) -> str:
        """Analyze gap between current understanding and scholar-level mastery"""
        try:
            current_score = student_profile.get('excellence_score', 60)
            target_distinction = student_profile.get('target_distinction', 'Dean_List')
            
            # Get target score from excellence engine
            target_requirements = self.excellence_engine.distinction_requirements.get(
                target_distinction, {'excellence_score_min': 80}
            )
            target_score = target_requirements['excellence_score_min']
            
            gap = max(0, target_score - current_score)
            
            # Sophistication gap analysis
            sophistication_levels = ['basic', 'intermediate', 'advanced', 'scholar']
            current_level_index = sophistication_levels.index(query_sophistication)
            target_level_index = min(len(sophistication_levels) - 1, 
                                   int(target_score / 25))  # Rough mapping
            
            sophistication_gap = max(0, target_level_index - current_level_index)
            
            gap_analysis = f"""
Excellence Gap Analysis:
- Current Excellence Score: {current_score}/100
- Target Score for {target_distinction}: {target_score}/100
- Score Gap: {gap} points
- Query Sophistication Level: {query_sophistication}
- Target Sophistication: {sophistication_levels[target_level_index]}
- Sophistication Gap: {sophistication_gap} levels

Key Areas for Elevation:
"""
            
            # Add specific areas based on gap size
            if gap > 20:
                gap_analysis += "- Significant research engagement required\n"
                gap_analysis += "- Advanced theoretical framework mastery needed\n"
            elif gap > 10:
                gap_analysis += "- Enhanced critical thinking development\n"
                gap_analysis += "- Deeper scholarly connections required\n"
            else:
                gap_analysis += "- Fine-tuning of academic excellence factors\n"
                gap_analysis += "- Consistency in high-level engagement\n"
            
            return gap_analysis
            
        except Exception as e:
            self.logger.error(f"Excellence gap analysis failed: {str(e)}")
            return "Gap analysis unavailable"
    
    def _generate_mentorship_response(self, query: str, student_profile: Dict,
                                    context_documents: List[str], 
                                    query_sophistication: str,
                                    excellence_gap_analysis: str) -> Dict:
        """Generate comprehensive scholar-level mentorship response"""
        try:
            start_time = datetime.now()
            
            # Determine academic context
            academic_field = student_profile.get('academic_field', 'interdisciplinary')
            current_score = student_profile.get('excellence_score', 60)
            target_distinction = student_profile.get('target_distinction', 'Dean_List')
            
            # Build sophisticated prompt
            mentorship_prompt = f"""
You are an elite academic mentor with expertise equivalent to Harvard, MIT, and Oxford professors. You're mentoring an ambitious student who seeks academic excellence and distinction.

STUDENT EXCELLENCE PROFILE:
- Current Excellence Score: {current_score}/100
- Target Academic Distinction: {target_distinction}
- Query Sophistication Level: {query_sophistication}
- Academic Field: {academic_field}

EXCELLENCE GAP ANALYSIS:
{excellence_gap_analysis}

ACADEMIC CONTEXT FROM STUDENT'S DOCUMENTS:
{chr(10).join(context_documents) if context_documents else "No specific context available"}

STUDENT QUERY: "{query}"

Your mission is to provide mentorship that elevates the student's thinking to scholar level while addressing their query. This is not basic tutoring - this is elite academic guidance.

RESPONSE REQUIREMENTS:
1. Address the query at the highest appropriate academic level
2. Connect to 2-3 major theoretical frameworks or scholarly traditions
3. Suggest advanced methodologies and analytical approaches
4. Identify how mastering this concept elevates their academic profile
5. Recommend specific scholarly actions and elite resources
6. Pose 2-3 deeper questions that push thinking beyond the original query
7. Explain how this response elevates their thinking beyond basic understanding

RESPONSE FORMAT (JSON):
{{
  "response": "Comprehensive scholar-level mentorship response (750-1000 words)",
  "frameworks": ["Theoretical Framework 1", "Framework 2", "Framework 3"],
  "methodologies": ["Advanced Method 1", "Method 2"],
  "excellence_impact": "Specific explanation of how this elevates academic standing",
  "actions": ["Specific Action 1", "Action 2", "Action 3"],
  "deeper_questions": ["Deep Question 1", "Question 2", "Question 3"],
  "resources": [
    {{"type": "journal", "title": "Specific Journal", "relevance": "Why this matters"}},
    {{"type": "book", "title": "Essential Book", "author": "Author", "relevance": "Academic value"}}
  ],
  "thinking_elevation": "How this response specifically elevates beyond basic level",
  "interdisciplinary_connections": ["Connection to other fields"]
}}

Maintain the tone of an inspiring, world-class academic mentor who recognizes the student's potential for greatness and refuses to accept anything less than excellence.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": mentorship_prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse response
            response_content = response.choices[0].message.content
            
            # Try to extract JSON from response
            try:
                # Look for JSON block in response
                json_start = response_content.find('{')
                json_end = response_content.rfind('}') + 1
                json_str = response_content[json_start:json_end]
                parsed_response = json.loads(json_str)
            except:
                # Fallback if JSON parsing fails
                parsed_response = self._create_fallback_response(response_content, query)
            
            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            parsed_response['response_time'] = response_time
            
            return parsed_response
            
        except Exception as e:
            self.logger.error(f"Mentorship response generation failed: {str(e)}")
            return self._create_fallback_response("", query, error=str(e))
    
    def _create_fallback_response(self, content: str, query: str, error: str = None) -> Dict:
        """Create fallback response when OpenAI fails"""
        return {
            'response': content or f"I understand you're asking about {query}. Let me provide a comprehensive academic perspective on this important topic...",
            'frameworks': ["Academic Excellence Framework", "Critical Thinking Model"],
            'methodologies': ["Systematic Analysis", "Comparative Study"],
            'excellence_impact': "This inquiry demonstrates advanced scholarly thinking",
            'actions': ["Deep dive into primary sources", "Connect with field experts", "Develop original analysis"],
            'deeper_questions': [
                f"What are the broader implications of {query}?",
                "How does this connect to emerging research trends?",
                "What interdisciplinary perspectives could enhance understanding?"
            ],
            'resources': [
                {"type": "journal", "title": "Leading Academic Journal", "relevance": "Core research in this field"},
                {"type": "book", "title": "Foundational Text", "author": "Expert Scholar", "relevance": "Essential theoretical grounding"}
            ],
            'thinking_elevation': "This response elevates thinking by connecting theoretical frameworks with practical applications",
            'interdisciplinary_connections': ["Philosophy", "Research Methods", "Contemporary Theory"],
            'response_time': 150,
            'error': error
        }
    
    def _calculate_session_quality(self, query: str, mentorship_response: Dict, 
                                 query_sophistication: str) -> float:
        """Calculate quality score for the mentorship session"""
        try:
            base_score = 3.0
            
            # Query sophistication impact
            sophistication_multipliers = {
                'basic': 1.0,
                'intermediate': 1.2,
                'advanced': 1.5,
                'scholar': 2.0
            }
            score = base_score * sophistication_multipliers.get(query_sophistication, 1.0)
            
            # Response quality factors
            response_text = mentorship_response.get('response', '')
            frameworks = mentorship_response.get('frameworks', [])
            methodologies = mentorship_response.get('methodologies', [])
            
            # Length and depth bonus
            if len(response_text) > 500:
                score += 0.3
            if len(response_text) > 800:
                score += 0.2
            
            # Frameworks and methodologies bonus
            score += min(0.4, len(frameworks) * 0.1)
            score += min(0.3, len(methodologies) * 0.1)
            
            # Response time penalty (if too slow)
            response_time = mentorship_response.get('response_time', 0)
            if response_time > 3000:  # 3 seconds
                score -= 0.2
            
            # Cap at 5.0
            return min(5.0, max(1.0, score))
            
        except Exception as e:
            self.logger.error(f"Quality calculation failed: {str(e)}")
            return 3.0
    
    def _update_predictions_from_engagement(self, student_id: str, query: str,
                                          mentorship_response: Dict, 
                                          session_quality: float) -> Dict:
        """Update academic distinction predictions based on engagement quality"""
        try:
            # Calculate engagement impact
            sophistication_impact = {
                'basic': 0.5,
                'intermediate': 1.0,
                'advanced': 2.0,
                'scholar': 3.5
            }
            
            query_sophistication = self._assess_query_sophistication(query)
            base_impact = sophistication_impact.get(query_sophistication, 1.0)
            
            # Quality multiplier
            quality_multiplier = session_quality / 4.0  # Normalize to ~1.0
            
            # Final impact calculation
            probability_increase = base_impact * quality_multiplier
            
            # Update predictions using excellence engine
            current_predictions = self.excellence_engine.predict_distinctions(student_id)
            
            updated_predictions = {}
            for distinction, current_prob in current_predictions.items():
                # Apply diminishing returns
                max_increase = min(probability_increase, (100 - current_prob) * 0.1)
                new_prob = min(100, current_prob + max_increase)
                updated_predictions[distinction] = {
                    'previous': current_prob,
                    'updated': new_prob,
                    'increase': new_prob - current_prob
                }
            
            # Store updates in database
            self._store_prediction_updates(student_id, updated_predictions)
            
            return updated_predictions
            
        except Exception as e:
            self.logger.error(f"Prediction update failed: {str(e)}")
            return {}
    
    def _store_mentorship_session(self, student_id: str, query: str, 
                                query_sophistication: str, excellence_gap_analysis: str,
                                mentorship_response: Dict, session_quality: float,
                                probability_updates: Dict) -> str:
        """Store mentorship session in database"""
        try:
            session_data = {
                'student_id': student_id,
                'query': query,
                'query_sophistication': query_sophistication,
                'excellence_gap_analysis': excellence_gap_analysis,
                'scholar_response': json.dumps(mentorship_response),
                'session_quality_score': session_quality,
                'probability_updates': json.dumps(probability_updates),
                'created_at': datetime.now()
            }
            
            insert_query = """
            INSERT INTO mentorship_sessions 
            (student_id, query, query_sophistication, excellence_gap_analysis, 
             scholar_response, session_quality_score, probability_updates, created_at)
            VALUES (:student_id, :query, :query_sophistication, :excellence_gap_analysis,
                    :scholar_response, :session_quality_score, :probability_updates, :created_at)
            """
            
            result = self.db.execute_query(insert_query, session_data)
            
            # Generate session ID (in real implementation, this would be returned by DB)
            session_id = f"session_{student_id}_{int(datetime.now().timestamp())}"
            
            self.logger.info(f"Mentorship session stored: {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Session storage failed: {str(e)}")
            return f"session_{student_id}_error"
    
    def _store_prediction_updates(self, student_id: str, predictions: Dict):
        """Store prediction updates in database"""
        try:
            for distinction, data in predictions.items():
                update_data = {
                    'student_id': student_id,
                    'distinction_type': distinction,
                    'previous_probability': data['previous'],
                    'updated_probability': data['updated'],
                    'probability_increase': data['increase'],
                    'updated_at': datetime.now()
                }
                
                upsert_query = """
                INSERT INTO prediction_updates 
                (student_id, distinction_type, previous_probability, updated_probability, 
                 probability_increase, updated_at)
                VALUES (:student_id, :distinction_type, :previous_probability, 
                        :updated_probability, :probability_increase, :updated_at)
                ON DUPLICATE KEY UPDATE
                previous_probability = updated_probability,
                updated_probability = VALUES(updated_probability),
                probability_increase = VALUES(probability_increase),
                updated_at = VALUES(updated_at)
                """
                
                self.db.execute_query(upsert_query, update_data)
                
        except Exception as e:
            self.logger.error(f"Prediction update storage failed: {str(e)}")
    
    def _infer_academic_field(self, student_id: str) -> str:
        """Infer academic field from student's documents"""
        try:
            field_query = """
            SELECT content, title
            FROM academic_documents
            WHERE student_id = :student_id
            LIMIT 10
            """
            
            docs = self.db.execute_query(field_query, {'student_id': student_id})
            
            # Simple field inference based on keywords
            field_keywords = {
                'STEM': ['algorithm', 'equation', 'analysis', 'data', 'research', 'method', 'theory'],
                'Social Sciences': ['society', 'behavior', 'culture', 'psychology', 'social'],
                'Humanities': ['literature', 'history', 'philosophy', 'art', 'culture'],
                'Business': ['business', 'management', 'strategy', 'market', 'economics'],
                'Medicine': ['medical', 'clinical', 'patient', 'health', 'disease'],
                'Law': ['legal', 'court', 'law', 'regulation', 'justice']
            }
            
            field_scores = {field: 0 for field in field_keywords}
            
            for doc in docs:
                text = (doc.get('content', '') + ' ' + doc.get('title', '')).lower()
                for field, keywords in field_keywords.items():
                    field_scores[field] += sum(1 for keyword in keywords if keyword in text)
            
            # Return field with highest score, default to STEM
            return max(field_scores.items(), key=lambda x: x[1])[0] if any(field_scores.values()) else 'STEM'
            
        except Exception as e:
            self.logger.error(f"Field inference failed: {str(e)}")
            return 'interdisciplinary'
    
    def _analyze_engagement_pattern(self, recent_sessions: List[Dict]) -> str:
        """Analyze student's engagement pattern"""
        try:
            if not recent_sessions:
                return 'new_student'
            
            avg_quality = sum(session.get('session_quality_score', 3.0) 
                            for session in recent_sessions) / len(recent_sessions)
            
            sophistication_levels = [session.get('query_sophistication', 'basic') 
                                   for session in recent_sessions]
            
            advanced_count = sum(1 for level in sophistication_levels 
                               if level in ['advanced', 'scholar'])
            
            if avg_quality > 4.0 and advanced_count >= len(recent_sessions) * 0.6:
                return 'high_achiever'
            elif avg_quality > 3.5:
                return 'consistent_learner'
            elif advanced_count > 0:
                return 'developing_scholar'
            else:
                return 'emerging_student'
                
        except Exception as e:
            self.logger.error(f"Engagement analysis failed: {str(e)}")
            return 'unknown'
    
    def get_mentorship_history(self, student_id: str, limit: int = 10) -> List[Dict]:
        """Get student's mentorship session history"""
        try:
            history_query = """
            SELECT session_id, query, query_sophistication, session_quality_score, 
                   created_at, scholar_response
            FROM mentorship_sessions
            WHERE student_id = :student_id
            ORDER BY created_at DESC
            LIMIT :limit
            """
            
            sessions = self.db.execute_query(history_query, {
                'student_id': student_id,
                'limit': limit
            })
            
            # Parse and format sessions
            formatted_sessions = []
            for session in sessions:
                try:
                    scholar_response = json.loads(session.get('scholar_response', '{}'))
                except:
                    scholar_response = {}
                
                formatted_sessions.append({
                    'session_id': session.get('session_id'),
                    'query': session.get('query'),
                    'sophistication': session.get('query_sophistication'),
                    'quality_score': session.get('session_quality_score'),
                    'created_at': session.get('created_at').isoformat() if session.get('created_at') else None,
                    'response_preview': scholar_response.get('response', '')[:200] + '...' if scholar_response.get('response') else '',
                    'frameworks_used': scholar_response.get('frameworks', [])
                })
            
            return formatted_sessions
            
        except Exception as e:
            self.logger.error(f"History retrieval failed: {str(e)}")
            return []
    
    def get_session_analytics(self, student_id: str) -> Dict:
        """Get analytics for student's mentorship sessions"""
        try:
            analytics_query = """
            SELECT 
                COUNT(*) as total_sessions,
                AVG(session_quality_score) as avg_quality,
                MAX(session_quality_score) as max_quality,
                COUNT(CASE WHEN query_sophistication = 'scholar' THEN 1 END) as scholar_queries,
                COUNT(CASE WHEN query_sophistication = 'advanced' THEN 1 END) as advanced_queries,
                COUNT(CASE WHEN session_quality_score > 4.0 THEN 1 END) as high_quality_sessions
            FROM mentorship_sessions
            WHERE student_id = :student_id
            """
            
            result = self.db.execute_query(analytics_query, {'student_id': student_id})
            
            if result:
                analytics = result[0]
                total = analytics.get('total_sessions', 0)
                
                return {
                    'total_sessions': total,
                    'average_quality': round(analytics.get('avg_quality', 0), 2),
                    'peak_quality': analytics.get('max_quality', 0),
                    'scholar_percentage': round((analytics.get('scholar_queries', 0) / max(total, 1)) * 100, 1),
                    'advanced_percentage': round((analytics.get('advanced_queries', 0) / max(total, 1)) * 100, 1),
                    'excellence_rate': round((analytics.get('high_quality_sessions', 0) / max(total, 1)) * 100, 1)
                }
            
            return {'total_sessions': 0, 'average_quality': 0, 'peak_quality': 0, 
                   'scholar_percentage': 0, 'advanced_percentage': 0, 'excellence_rate': 0}
            
        except Exception as e:
            self.logger.error(f"Analytics retrieval failed: {str(e)}")
            return {}
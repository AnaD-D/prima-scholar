"""
Prima Scholar Excellence Engine
Core algorithm for calculating excellence scores and predicting academic distinctions
"""

import numpy as np
import logging
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime, date, timedelta
from dataclasses import dataclass
import openai

@dataclass
class DistinctionRequirement:
    """Academic distinction requirements"""
    gpa_min: float
    excellence_score_min: float
    additional_requirements: List[str]
    weight_factors: Dict[str, float]

@dataclass
class ExcellenceFactors:
    """Factors contributing to academic excellence"""
    academic_performance: float  # 40%
    research_engagement: float   # 25%
    critical_thinking: float     # 20%
    leadership_service: float    # 10%
    innovation_creativity: float # 5%

class ExcellenceEngine:
    """Core engine for calculating excellence scores and predicting academic honors"""
    
    def __init__(self, db_manager, openai_api_key: str):
        self.db = db_manager
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.logger = logging.getLogger(__name__)
        
        # Excellence thresholds for different distinctions
        self.distinction_requirements = {
            'Dean_List': DistinctionRequirement(
                gpa_min=3.5,
                excellence_score_min=75,
                additional_requirements=['top_15_percent', 'full_time_enrollment'],
                weight_factors={'gpa': 0.6, 'excellence': 0.4}
            ),
            'Magna_Cum_Laude': DistinctionRequirement(
                gpa_min=3.7,
                excellence_score_min=85,
                additional_requirements=['cumulative_gpa', 'credit_hours_minimum'],
                weight_factors={'gpa': 0.5, 'excellence': 0.5}
            ),
            'Summa_Cum_Laude': DistinctionRequirement(
                gpa_min=3.9,
                excellence_score_min=95,
                additional_requirements=['thesis_defense', 'faculty_recommendation'],
                weight_factors={'gpa': 0.4, 'excellence': 0.6}
            ),
            'Phi_Beta_Kappa': DistinctionRequirement(
                gpa_min=3.8,
                excellence_score_min=90,
                additional_requirements=['liberal_arts_focus', 'character_assessment'],
                weight_factors={'gpa': 0.45, 'excellence': 0.55}
            ),
            'Rhodes_Scholar': DistinctionRequirement(
                gpa_min=3.9,
                excellence_score_min=98,
                additional_requirements=['leadership_evidence', 'athletic_achievement', 'service_commitment'],
                weight_factors={'gpa': 0.3, 'excellence': 0.7}
            ),
            'Fulbright_Scholar': DistinctionRequirement(
                gpa_min=3.8,
                excellence_score_min=92,
                additional_requirements=['research_proposal', 'language_proficiency', 'cultural_sensitivity'],
                weight_factors={'gpa': 0.35, 'excellence': 0.65}
            )
        }
        
        # Excellence calculation weights
        self.factor_weights = {
            'academic_performance': 0.40,
            'research_engagement': 0.25,
            'critical_thinking': 0.20,
            'leadership_service': 0.10,
            'innovation_creativity': 0.05
        }
        
        self.logger.info("Excellence Engine initialized")
    
    def calculate_excellence_score(self, student_id: str, student_data: Optional[Dict] = None) -> Dict:
        """Calculate comprehensive excellence score for a student"""
        try:
            if not student_data:
                student_data = self._get_comprehensive_student_data(student_id)
            
            if not student_data:
                return {'error': 'Student data not found', 'score': 0}
            
            # Calculate individual factor scores
            factors = self._calculate_excellence_factors(student_data)
            
            # Weighted total score
            total_score = (
                factors.academic_performance * self.factor_weights['academic_performance'] +
                factors.research_engagement * self.factor_weights['research_engagement'] +
                factors.critical_thinking * self.factor_weights['critical_thinking'] +
                factors.leadership_service * self.factor_weights['leadership_service'] +
                factors.innovation_creativity * self.factor_weights['innovation_creativity']
            )
            
            # Apply academic level multiplier
            level_multiplier = self._get_level_multiplier(student_data.get('academic_level', 'undergraduate'))
            final_score = min(total_score * level_multiplier, 100)
            
            # Update database
            self._update_excellence_score_in_db(student_id, final_score, factors)
            
            return {
                'excellence_score': round(final_score, 2),
                'factors': {
                    'academic_performance': round(factors.academic_performance, 2),
                    'research_engagement': round(factors.research_engagement, 2),
                    'critical_thinking': round(factors.critical_thinking, 2),
                    'leadership_service': round(factors.leadership_service, 2),
                    'innovation_creativity': round(factors.innovation_creativity, 2)
                },
                'level_multiplier': level_multiplier,
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Excellence score calculation failed for {student_id}: {str(e)}")
            return {'error': str(e), 'score': 0}
    
    def _calculate_excellence_factors(self, student_data: Dict) -> ExcellenceFactors:
        """Calculate individual excellence factors"""
        
        # Academic Performance (40%) - GPA, course difficulty, grade trends
        academic_score = self._calculate_academic_performance(student_data)
        
        # Research Engagement (25%) - Research activities, publications, presentations
        research_score = self._calculate_research_engagement(student_data)
        
        # Critical Thinking (20%) - Quality of questions, analysis depth, theoretical connections
        thinking_score = self._calculate_critical_thinking_score(student_data)
        
        # Leadership & Service (10%) - Leadership roles, community service, impact
        leadership_score = self._calculate_leadership_score(student_data)
        
        # Innovation & Creativity (5%) - Original thinking, creative solutions, novel approaches
        innovation_score = self._calculate_innovation_score(student_data)
        
        return ExcellenceFactors(
            academic_performance=academic_score,
            research_engagement=research_score,
            critical_thinking=thinking_score,
            leadership_service=leadership_score,
            innovation_creativity=innovation_score
        )
    
    def _calculate_academic_performance(self, student_data: Dict) -> float:
        """Calculate academic performance factor (0-100)"""
        gpa = student_data.get('current_gpa', 0.0)
        base_score = min((gpa / 4.0) * 100, 100)
        
        # Bonus factors
        bonus = 0
        
        # Course difficulty bonus
        if student_data.get('honors_courses', 0) > 0:
            bonus += min(student_data['honors_courses'] * 2, 10)
        
        # Grade trend bonus
        if student_data.get('gpa_trend', 'stable') == 'improving':
            bonus += 5
        elif student_data.get('gpa_trend', 'stable') == 'declining':
            bonus -= 5
        
        # Academic achievements
        achievements = student_data.get('academic_achievements', [])
        bonus += min(len(achievements) * 3, 15)
        
        return min(base_score + bonus, 100)
    
    def _calculate_research_engagement(self, student_data: Dict) -> float:
        """Calculate research engagement factor (0-100)"""
        base_score = 20  # Starting point for undergrads
        
        # Research activities
        research_projects = student_data.get('research_projects', 0)
        base_score += min(research_projects * 15, 40)
        
        # Publications and presentations
        publications = student_data.get('publications', 0)
        presentations = student_data.get('presentations', 0)
        base_score += min(publications * 20 + presentations * 10, 30)
        
        # Research mentorship sessions quality
        sessions_data = student_data.get('mentorship_sessions', [])
        if sessions_data:
            avg_quality = sum(s.get('session_quality_score', 0) for s in sessions_data) / len(sessions_data)
            base_score += min(avg_quality * 10, 10)
        
        return min(base_score, 100)
    
    def _calculate_critical_thinking_score(self, student_data: Dict) -> float:
        """Calculate critical thinking quality based on interactions"""
        base_score = 40  # Base critical thinking assumption
        
        # Analyze query sophistication from mentorship sessions
        sessions = student_data.get('mentorship_sessions', [])
        if sessions:
            sophistication_scores = {
                'basic': 10,
                'intermediate': 25,
                'advanced': 40,
                'scholar': 60
            }
            
            avg_sophistication = 0
            for session in sessions:
                sophistication_level = session.get('query_sophistication', 'basic')
                avg_sophistication += sophistication_scores.get(sophistication_level, 10)
            
            avg_sophistication /= len(sessions)
            base_score = max(base_score, avg_sophistication)
        
        # Bonus for theoretical framework usage
        frameworks_used = student_data.get('theoretical_frameworks_engaged', 0)
        base_score += min(frameworks_used * 3, 20)
        
        # Document complexity engagement
        complex_docs = student_data.get('elite_tier_documents', 0)
        base_score += min(complex_docs * 5, 15)
        
        return min(base_score, 100)
    
    def _calculate_leadership_score(self, student_data: Dict) -> float:
        """Calculate leadership and service factor"""
        base_score = 10  # Base assumption
        
        # Leadership positions
        leadership_roles = student_data.get('leadership_roles', [])
        base_score += min(len(leadership_roles) * 15, 45)
        
        # Community service hours
        service_hours = student_data.get('service_hours', 0)
        base_score += min(service_hours / 10, 25)  # 1 point per 10 hours, max 25
        
        # Impact assessment
        leadership_impact = student_data.get('leadership_impact_score', 0)
        base_score += min(leadership_impact, 20)
        
        return min(base_score, 100)
    
    def _calculate_innovation_score(self, student_data: Dict) -> float:
        """Calculate innovation and creativity factor"""
        base_score = 30  # Base creativity assumption
        
        # Original research or projects
        original_projects = student_data.get('original_projects', 0)
        base_score += min(original_projects * 10, 30)
        
        # Patents, publications, or creative works
        creative_works = student_data.get('creative_works', 0)
        base_score += min(creative_works * 15, 25)
        
        # Innovation in mentorship responses
        innovative_solutions = student_data.get('innovative_approaches_suggested', 0)
        base_score += min(innovative_solutions * 2, 15)
        
        return min(base_score, 100)
    
    def predict_distinction_probability(self, student_id: str, distinction: str) -> Dict:
        """Predict probability of achieving specific academic distinction"""
        try:
            if distinction not in self.distinction_requirements:
                return {'error': f'Unknown distinction: {distinction}'}
            
            # Get current student data
            student_data = self._get_comprehensive_student_data(student_id)
            if not student_data:
                return {'error': 'Student data not found'}
            
            requirement = self.distinction_requirements[distinction]
            
            # Calculate current excellence score
            excellence_data = self.calculate_excellence_score(student_id, student_data)
            current_excellence = excellence_data.get('excellence_score', 0)
            current_gpa = student_data.get('current_gpa', 0.0)
            
            # Calculate base probability from current metrics
            gpa_factor = min(current_gpa / requirement.gpa_min, 1.0) if requirement.gpa_min > 0 else 1.0
            excellence_factor = min(current_excellence / requirement.excellence_score_min, 1.0)
            
            # Weighted probability calculation
            base_probability = (
                gpa_factor * requirement.weight_factors['gpa'] +
                excellence_factor * requirement.weight_factors['excellence']
            ) * 100
            
            # Trajectory analysis
            trajectory_factor = self._analyze_improvement_trajectory(student_id)
            
            # Apply trajectory adjustment
            trajectory_adjusted = base_probability * (0.7 + trajectory_factor * 0.3)
            
            # Confidence calculation
            confidence = self._calculate_prediction_confidence(student_data, distinction)
            
            # Final probability (capped at 95% for realism)
            final_probability = min(trajectory_adjusted, 95)
            
            # Generate improvement factors
            improvement_factors = self._identify_improvement_factors(student_data, distinction)
            
            # Estimated timeline
            estimated_date = self._estimate_achievement_timeline(
                student_id, distinction, current_excellence, requirement.excellence_score_min
            )
            
            prediction_result = {
                'distinction': distinction,
                'probability': round(final_probability, 1),
                'confidence': round(confidence, 1),
                'current_excellence_score': current_excellence,
                'required_excellence_score': requirement.excellence_score_min,
                'current_gpa': current_gpa,
                'required_gpa': requirement.gpa_min,
                'gap': max(0, requirement.excellence_score_min - current_excellence),
                'improvement_factors': improvement_factors,
                'estimated_achievement_date': estimated_date.isoformat() if estimated_date else None,
                'trajectory_factor': round(trajectory_factor, 2),
                'key_factors': self._get_key_success_factors(distinction),
                'calculated_at': datetime.now().isoformat()
            }
            
            # Store prediction in database
            self._store_prediction_in_db(student_id, prediction_result)
            
            return prediction_result
            
        except Exception as e:
            self.logger.error(f"Prediction failed for {student_id}, {distinction}: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_improvement_trajectory(self, student_id: str) -> float:
        """Analyze student's improvement trajectory (0-1 scale)"""
        try:
            # Get historical excellence scores
            query = """
            SELECT excellence_score, trajectory_date
            FROM excellence_trajectory
            WHERE student_id = :student_id
            ORDER BY trajectory_date DESC
            LIMIT 10
            """
            
            trajectory_data = self.db.execute_query(query, {'student_id': student_id})
            
            if len(trajectory_data) < 2:
                return 0.5  # Neutral trajectory for insufficient data
            
            # Calculate trend
            scores = [float(row['excellence_score']) for row in trajectory_data]
            scores.reverse()  # Chronological order
            
            # Linear regression slope
            x = np.arange(len(scores))
            coeffs = np.polyfit(x, scores, 1)
            slope = coeffs[0]
            
            # Convert slope to 0-1 trajectory factor
            # Positive slope = improving trajectory
            trajectory_factor = max(0, min(1, 0.5 + slope / 20))
            
            return trajectory_factor
            
        except Exception as e:
            self.logger.error(f"Trajectory analysis failed: {str(e)}")
            return 0.5  # Neutral trajectory on error
    
    def _calculate_prediction_confidence(self, student_data: Dict, distinction: str) -> float:
        """Calculate confidence level for prediction (0-100)"""
        base_confidence = 70
        
        # Data completeness factor
        data_fields = [
            'current_gpa', 'mentorship_sessions', 'academic_achievements',
            'research_projects', 'leadership_roles'
        ]
        
        completeness = sum(1 for field in data_fields if student_data.get(field)) / len(data_fields)
        base_confidence += completeness * 20
        
        # Session history factor
        sessions_count = len(student_data.get('mentorship_sessions', []))
        if sessions_count >= 10:
            base_confidence += 10
        elif sessions_count >= 5:
            base_confidence += 5
        
        # Time factor (more confidence with longer tracking)
        if student_data.get('profile_age_days', 0) >= 90:
            base_confidence += 5
        
        return min(base_confidence, 95)  # Cap at 95%
    
    def _identify_improvement_factors(self, student_data: Dict, distinction: str) -> List[Dict]:
        """Identify specific factors for improvement"""
        requirement = self.
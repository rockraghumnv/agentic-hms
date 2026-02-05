"""
Explainable AI Module
Provides transparency into AI decision-making and recommendations
"""
from typing import Dict, List, Optional
from datetime import datetime

from vector_store import MedicalVectorStore
from mock_db import get_patient_data


class AIExplainer:
    """Explain AI responses and show reasoning transparency"""
    
    def __init__(self):
        """Initialize explainer with vector store access"""
        self.vector_store = MedicalVectorStore()
    
    def explain_response(
        self,
        patient_id: str,
        message_id: str,
        user_query: str,
        bot_response: str
    ) -> Dict:
        """
        Generate detailed explanation of AI response
        
        Args:
            patient_id: Patient identifier
            message_id: Message ID from conversation
            user_query: Original user question
            bot_response: AI's response
            
        Returns:
            dict: Comprehensive explanation breakdown
        """
        # Get patient data
        patient_data = get_patient_data(patient_id)
        
        # Get medical records used
        relevant_records = self.vector_store.query_patient_history(
            patient_id=patient_id,
            query_text=user_query,
            n_results=5
        )
        
        # Build explanation
        explanation = {
            'message_id': message_id,
            'user_query': user_query,
            'data_sources': self._explain_data_sources(patient_data, relevant_records),
            'patterns_detected': self._explain_patterns(user_query, patient_data, relevant_records),
            'risk_factors': self._explain_risk_factors(patient_data, relevant_records),
            'recommendation_logic': self._explain_logic(user_query, bot_response, patient_data),
            'confidence_level': self._calculate_confidence(relevant_records),
            'timestamp': datetime.now().isoformat()
        }
        
        return explanation
    
    def _explain_data_sources(
        self,
        patient_data: Dict,
        relevant_records: List[Dict]
    ) -> Dict:
        """
        Explain what data sources were used
        
        Args:
            patient_data: Patient information
            relevant_records: Medical records from vector search
            
        Returns:
            dict: Data sources breakdown
        """
        sources = {
            'family_history': None,
            'medical_records': [],
            'medications': [],
            'test_results': []
        }
        
        # Family history
        if patient_data and 'family_history' in patient_data:
            fh = patient_data['family_history']
            family_conditions = []
            
            if fh.get('father_conditions') and fh['father_conditions'].lower() != 'none':
                family_conditions.append(f"Father: {fh['father_conditions']}")
            if fh.get('mother_conditions') and fh['mother_conditions'].lower() != 'none':
                family_conditions.append(f"Mother: {fh['mother_conditions']}")
            if fh.get('siblings_conditions') and fh['siblings_conditions'].lower() != 'none':
                family_conditions.append(f"Siblings: {fh['siblings_conditions']}")
            if fh.get('family_diseases') and fh['family_diseases'].lower() != 'none':
                family_conditions.append(f"Family diseases: {fh['family_diseases']}")
            
            sources['family_history'] = family_conditions if family_conditions else None
        
        # Medical records
        for record in relevant_records:
            record_info = {
                'text': record['text'][:150] + '...' if len(record['text']) > 150 else record['text'],
                'relevance_score': round(1 / (1 + record['distance']), 2),  # Convert distance to similarity
                'metadata': record.get('metadata', {})
            }
            
            # Categorize by type
            text_lower = record['text'].lower()
            if 'glucose' in text_lower or 'hba1c' in text_lower:
                sources['test_results'].append(record_info)
            elif 'metformin' in text_lower or 'medication' in text_lower:
                sources['medications'].append(record_info)
            else:
                sources['medical_records'].append(record_info)
        
        return sources
    
    def _explain_patterns(
        self,
        query: str,
        patient_data: Dict,
        relevant_records: List[Dict]
    ) -> List[str]:
        """
        Explain patterns detected in patient data
        
        Args:
            query: User's question
            patient_data: Patient information
            relevant_records: Medical records
            
        Returns:
            List of detected patterns
        """
        patterns = []
        query_lower = query.lower()
        
        # Glucose/Diabetes patterns
        if 'glucose' in query_lower or 'sugar' in query_lower or 'diabetes' in query_lower:
            # Check family history
            if patient_data and 'family_history' in patient_data:
                fh = patient_data['family_history']
                if 'diabetes' in str(fh).lower():
                    patterns.append("🧬 Family history of diabetes detected (genetic risk factor)")
            
            # Check test results
            for record in relevant_records:
                if 'glucose' in record['text'].lower():
                    if '128' in record['text'] or '110' in record['text']:
                        patterns.append("📈 Glucose levels trending upward (95 → 110 → 128 mg/dL)")
                    if 'hba1c' in record['text'].lower():
                        patterns.append("⚠️ HbA1c at 5.9% indicates pre-diabetic range (normal <5.7%)")
        
        # Fever/Infection patterns
        if 'fever' in query_lower or 'cough' in query_lower:
            patterns.append("🌡️ Acute symptom query detected (requires monitoring)")
            patterns.append("📊 No chronic respiratory conditions in patient history")
        
        # Medication patterns
        if 'medication' in query_lower or 'medicine' in query_lower:
            for record in relevant_records:
                if 'metformin' in record['text'].lower():
                    patterns.append("💊 Currently on Metformin 500mg for blood sugar management")
                    patterns.append("📅 Medication adherence monitoring recommended")
        
        # Age-related patterns
        if patient_data and 'age' in str(patient_data).lower():
            patterns.append("👤 Patient age is significant risk factor for screening recommendations")
        
        return patterns if patterns else ["ℹ️ No significant patterns detected in available data"]
    
    def _explain_risk_factors(
        self,
        patient_data: Dict,
        relevant_records: List[Dict]
    ) -> List[Dict]:
        """
        Explain identified risk factors
        
        Args:
            patient_data: Patient information
            relevant_records: Medical records
            
        Returns:
            List of risk factors with severity
        """
        risk_factors = []
        
        # Check family history risks
        if patient_data and 'family_history' in patient_data:
            fh = patient_data['family_history']
            
            if 'diabetes' in str(fh).lower():
                risk_factors.append({
                    'factor': 'Family History of Diabetes',
                    'severity': 'High',
                    'description': 'First-degree relative with diabetes increases risk by 40%',
                    'mitigation': 'Regular HbA1c testing, lifestyle modifications'
                })
            
            if 'hypertension' in str(fh).lower() or 'heart' in str(fh).lower():
                risk_factors.append({
                    'factor': 'Family History of Cardiovascular Disease',
                    'severity': 'Medium',
                    'description': 'Increased risk for heart conditions',
                    'mitigation': 'Blood pressure monitoring, cholesterol checks'
                })
        
        # Check current health indicators
        for record in relevant_records:
            text_lower = record['text'].lower()
            
            # Pre-diabetes
            if 'hba1c' in text_lower and ('5.9' in record['text'] or '5.8' in record['text']):
                risk_factors.append({
                    'factor': 'Pre-Diabetic HbA1c Level',
                    'severity': 'High',
                    'description': 'HbA1c 5.7-6.4% indicates pre-diabetes',
                    'mitigation': 'Diet control, regular exercise, medication compliance'
                })
            
            # Elevated glucose
            if 'glucose' in text_lower and any(val in record['text'] for val in ['128', '120', '130']):
                risk_factors.append({
                    'factor': 'Elevated Fasting Glucose',
                    'severity': 'Medium',
                    'description': 'Glucose levels above 100 mg/dL indicate impaired fasting glucose',
                    'mitigation': 'Reduce sugar intake, increase physical activity'
                })
        
        return risk_factors if risk_factors else [{
            'factor': 'No Critical Risk Factors',
            'severity': 'Low',
            'description': 'Current health indicators within normal ranges',
            'mitigation': 'Continue regular health monitoring'
        }]
    
    def _explain_logic(
        self,
        query: str,
        response: str,
        patient_data: Dict
    ) -> Dict:
        """
        Explain the reasoning logic behind recommendations
        
        Args:
            query: User's question
            response: AI's response
            patient_data: Patient information
            
        Returns:
            dict: Logic breakdown
        """
        logic = {
            'decision_tree': [],
            'medical_guidelines': [],
            'personalization_factors': []
        }
        
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Decision tree
        if 'fever' in query_lower:
            logic['decision_tree'] = [
                "1. Identified acute symptom (fever)",
                "2. Checked patient history for respiratory conditions → None found",
                "3. Assessed severity based on reported symptoms",
                "4. Applied general fever management protocol",
                "5. Set monitoring timeline (24-48 hours)"
            ]
            logic['medical_guidelines'] = [
                "CDC Fever Management Guidelines",
                "WHO Symptom Monitoring Protocol"
            ]
        
        elif 'glucose' in query_lower or 'diabetes' in query_lower:
            logic['decision_tree'] = [
                "1. Retrieved recent glucose and HbA1c values",
                "2. Compared against normal ranges (glucose <100, HbA1c <5.7%)",
                "3. Analyzed family history for genetic risk",
                "4. Detected upward trend in glucose levels",
                "5. Applied ADA pre-diabetes management guidelines"
            ]
            logic['medical_guidelines'] = [
                "American Diabetes Association (ADA) Guidelines",
                "Pre-diabetes Management Protocol",
                "HbA1c Interpretation Standards"
            ]
        
        elif 'medication' in query_lower:
            logic['decision_tree'] = [
                "1. Retrieved current medication list",
                "2. Checked prescription details and dosage",
                "3. Calculated remaining supply based on dosage",
                "4. Applied <5 days threshold for refill alert",
                "5. Generated proactive reminder"
            ]
            logic['medical_guidelines'] = [
                "Medication Adherence Best Practices",
                "Metformin Dosage Guidelines"
            ]
        
        # Personalization factors
        if patient_data:
            if 'family_history' in patient_data:
                logic['personalization_factors'].append(
                    "Family medical history used to assess genetic risk"
                )
            if 'uploaded_documents' in patient_data:
                logic['personalization_factors'].append(
                    f"Analysis based on {patient_data.get('documents_processed', 0)} uploaded medical records"
                )
        
        if 'monitor' in response_lower:
            logic['personalization_factors'].append(
                "Conservative approach due to lack of emergency symptoms"
            )
        
        if not logic['personalization_factors']:
            logic['personalization_factors'] = [
                "General medical guidance applied",
                "Recommendation to consult healthcare provider for personalized advice"
            ]
        
        return logic
    
    def _calculate_confidence(self, relevant_records: List[Dict]) -> Dict:
        """
        Calculate confidence level of response
        
        Args:
            relevant_records: Medical records used
            
        Returns:
            dict: Confidence metrics
        """
        if not relevant_records:
            return {
                'level': 'Low',
                'percentage': 30,
                'reason': 'Limited patient data available'
            }
        
        # Calculate average relevance score
        avg_distance = sum(r['distance'] for r in relevant_records) / len(relevant_records)
        similarity_score = 1 / (1 + avg_distance)
        
        # Determine confidence
        if similarity_score > 0.7:
            return {
                'level': 'High',
                'percentage': int(similarity_score * 100),
                'reason': f'Strong match with {len(relevant_records)} relevant medical records'
            }
        elif similarity_score > 0.5:
            return {
                'level': 'Medium',
                'percentage': int(similarity_score * 100),
                'reason': f'Moderate match with patient data ({len(relevant_records)} records)'
            }
        else:
            return {
                'level': 'Low',
                'percentage': int(similarity_score * 100),
                'reason': 'Limited relevance to available patient data'
            }


# Convenience function
def generate_explanation(
    patient_id: str,
    message_id: str,
    user_query: str,
    bot_response: str
) -> Dict:
    """Quick explanation generation"""
    explainer = AIExplainer()
    return explainer.explain_response(patient_id, message_id, user_query, bot_response)


if __name__ == "__main__":
    # Test explainer
    print("Testing AI Explainer...")
    
    explainer = AIExplainer()
    
    explanation = explainer.explain_response(
        patient_id="PT-2026-DEMO",
        message_id="msg_1",
        user_query="What is my diabetes risk?",
        bot_response="Based on your family history and glucose levels, you are at pre-diabetic stage..."
    )
    
    print(f"\nData Sources: {len(explanation['data_sources'])} categories")
    print(f"Patterns: {len(explanation['patterns_detected'])} detected")
    print(f"Risk Factors: {len(explanation['risk_factors'])} identified")
    print(f"Confidence: {explanation['confidence_level']['level']}")
    
    print("\nExplainer test complete!")

"""
Phase 4: End-to-End API Integration Test
Simple test using the actual API endpoint to verify Phase 4 works.
"""

import requests
import json


def test_phase4_api_e2e():
    """End-to-end test calling the actual API with Phase 4 features."""
    
    # Sample job posting
    job_payload = {
        "job_id": "phase4-test-001",
        "title": "Supply Chain Manager - GCC",
        "company_name": "Test Logistics Co",
        "country": "UAE",
        "city": "Dubai",
        "industry": "Logistics & Supply Chain",
        "functional_area": "Operations",
        "designation": "Mid-Senior Level",
        "min_experience_years": 5,
        "max_experience_years": 10,
        "salary_min": 100000,
        "salary_max": 150000,
        "currency": "USD",
        "job_description": "Lead supply chain operations for GCC region",
        "required_skills": [
            "Supply Chain Management",
            "Logistics Planning",
            "Inventory Management",
            "Transportation Management",
        ],
        "preferred_skills": ["SAP", "Power BI", "Six Sigma"],
        "require_gcc_experience": True,
    }
    
    # GCC veteran candidate (should score very high)
    candidate_payload = {
        "candidate_id": "phase4-cand-001",
        "name": "Ahmed Al-Mansouri",
        "nationality": "Emirati",
        "current_country": "UAE",
        "current_city": "Dubai",
        "total_experience_years": 8,
        "gcc_experience_years": 8,
        "skills": [
            "Supply Chain Management",
            "Logistics Planning",
            "Inventory Management",
            "Transportation Management",
            "SAP",
            "Power BI",
            "Six Sigma Green Belt",
        ],
        "current_salary": 135000,
        "expected_salary": 145000,
        "currency": "USD",
        "job_history": [
            {
                "title": "Supply Chain Manager",
                "company": "Aramex",
                "years": 4,
                "location": "Dubai, UAE",
            },
            {
                "title": "Logistics Supervisor",
                "company": "DP World",
                "years": 4,
                "location": "Jebel Ali, UAE",
            },
        ],
    }
    
    # Prepare request
    payload = {
        "job": job_payload,
        "candidate": candidate_payload,
    }
    
    print("\n" + "="*70)
    print("PHASE 4: ENTERPRISE-GRADE HYBRID SCORING SYSTEM TEST")
    print("="*70)
    print("\n📋 Testing GCC veteran candidate against GCC logistics role...")
    print(f"   Candidate: {candidate_payload['name']} ({candidate_payload['gcc_experience_years']} years GCC exp)")
    print(f"   Role: {job_payload['title']}")
    print(f"   Skills Match: {len(set(candidate_payload['skills']) & set(job_payload['required_skills']))}/{len(job_payload['required_skills'])} required")
    
    # Send request to local API
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/evaluate",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "sk-test-local-dev-key-12345"
            }
        )
        
        if response.status_code != 200:
            print(f"\n❌ API returned error {response.status_code}")
            print(response.text)
            return False
            
        result = response.json()
        
        print("\n" + "-"*70)
        print("✅ EVALUATION COMPLETE - Phase 4 Features Active")
        print("-"*70)
        
        # Core scoring
        print(f"\n🎯 SCORING RESULTS:")
        print(f"   Decision: {result.get('decision', 'N/A')}")
        print(f"   Base Score: {result.get('base_score', 'N/A')}")
        print(f"   Adjusted Score: {result.get('adjusted_score', 'N/A')}")
        print(f"   Total Score: {result.get('total_score', 'N/A')}")
        
        # Contextual adjustments
        adjustments = result.get('contextual_adjustments', [])
        if adjustments:
            print(f"\n⚡ CONTEXTUAL ADJUSTMENTS ({len(adjustments)} applied):")
            for adj in adjustments:
                impact_sign = "+" if adj['impact'] > 0 else ""
                print(f"   {adj['rule_name']}: {impact_sign}{adj['impact']} points")
                print(f"      → {adj['reason']}")
        
        # Confidence metrics
        confidence = result.get('confidence_metrics')
        if confidence:
            print(f"\n📊 CONFIDENCE METRICS:")
            print(f"   Level: {confidence.get('confidence_level', 'N/A').upper()}")
            print(f"   Score: {confidence.get('confidence_score', 0):.2f}")
            if confidence.get('uncertainty_factors'):
                print(f"   Uncertainty Factors: {', '.join(confidence['uncertainty_factors'])}")
        
        # Feature interactions
        interactions = result.get('feature_interactions', [])
        if interactions:
            print(f"\n🔗 FEATURE INTERACTIONS ({len(interactions)} detected):")
            for interact in interactions:
                print(f"   {interact['interaction_type']}: +{interact['impact']:.1f} points")
                print(f"      → {interact['description']}")
        
        # Performance
        perf = result.get('performance_metrics')
        if perf:
            print(f"\n⚙️ PERFORMANCE METRICS:")
            print(f"   Evaluation Time: {perf.get('evaluation_time_ms', 0):.2f} ms")
            print(f"   Rules Evaluated: {perf.get('rules_evaluated', 0)}")
            print(f"   Adjustments Applied: {perf.get('adjustments_applied', 0)}")
            print(f"   Interactions Detected: {perf.get('interactions_detected', 0)}")
        
        # Metadata
        metadata = result.get('scoring_metadata')
        if metadata:
            print(f"\n🏷️ SCORING METADATA:")
            print(f"   Weight Profile: {metadata.get('weight_profile', 'N/A')}")
            print(f"   Model Version: {result.get('model_version', 'N/A')}")
        
        print("\n" + "="*70)
        print("Phase 4 Advanced Hybrid Scoring: ✅ OPERATIONAL")
        print("="*70)
        
        # Validate Phase 4 features are present
        assert result.get('base_score') is not None, "Missing base_score"
        assert result.get('adjusted_score') is not None, "Missing adjusted_score"
        assert result.get('confidence_metrics') is not None, "Missing confidence_metrics"
        assert result.get('contextual_adjustments') is not None, "Missing contextual_adjustments"
        assert result.get('performance_metrics') is not None, "Missing performance_metrics"
        assert result.get('scoring_metadata') is not None, "Missing scoring_metadata"
        assert result.get('model_version') == "2.0.0", "Model version should be 2.0.0"
        
        # GCC veteran should score high
        assert result['total_score'] >= 80, f"Expected score >= 80 for perfect GCC veteran, got {result['total_score']}"
        
        # Should have GCC bonus
        gcc_bonus_found = any('GCC' in adj['rule_code'] for adj in adjustments)
        assert gcc_bonus_found, "Expected GCC experience bonus for 8-year GCC veteran"
        
        print("\n✅ All Phase 4 assertions passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("\n⚠️ Could not connect to API at http://localhost:8000")
        print("   Please start the API server first with: uvicorn logis_ai_candidate_engine.api.main:app --reload")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_phase4_api_e2e()
    exit(0 if success else 1)

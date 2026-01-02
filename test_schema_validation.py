"""
Schema validation test for updated Job and Candidate schemas.
Tests that the new schemas can parse the updated sample data.
"""

import json
from logis_ai_candidate_engine.core.schemas.job import Job
from logis_ai_candidate_engine.core.schemas.candidate import Candidate


def test_job_schema():
    """Test Job schema with updated sample data"""
    print("=" * 80)
    print("Testing Job Schema")
    print("=" * 80)
    
    with open("logis_ai_candidate_engine/data/sample_job.json", "r") as f:
        job_data = json.load(f)
        job_data.pop("_comment", None)  # Remove comment field
    
    try:
        job = Job(**job_data)
        print("✅ Job schema validation: PASSED")
        print(f"   Job ID: {job.job_id}")
        print(f"   Title: {job.title}")
        print(f"   Company: {job.company_name}")
        print(f"   Required Skills: {job.required_skills}")
        print(f"   Require GCC Exp: {job.require_gcc_experience}")
        print(f"   Visa Requirement: {job.visa_requirement}")
        print(f"   Custom Questions: {len(job.custom_questions)} questions")
        return True
    except Exception as e:
        print(f"❌ Job schema validation: FAILED")
        print(f"   Error: {str(e)}")
        return False


def test_candidate_schema():
    """Test Candidate schema with updated sample data"""
    print("\n" + "=" * 80)
    print("Testing Candidate Schema")
    print("=" * 80)
    
    with open("logis_ai_candidate_engine/data/sample_candidate.json", "r") as f:
        candidate_data = json.load(f)
        candidate_data.pop("_comment", None)  # Remove comment field
    
    try:
        candidate = Candidate(**candidate_data)
        print("✅ Candidate schema validation: PASSED")
        print(f"   Candidate ID: {candidate.candidate_id}")
        print(f"   Name: {candidate.full_name}")
        print(f"   Nationality: {candidate.nationality}")
        print(f"   Visa Status: {candidate.visa_status}")
        print(f"   Total Experience: {candidate.total_experience_years} years")
        print(f"   GCC Experience: {candidate.gcc_experience_years} years")
        print(f"   Skills: {candidate.skills}")
        print(f"   Employment History: {len(candidate.employment_history)} entries")
        print(f"   Education Details: {len(candidate.education_details)} entries")
        print(f"   Languages: {candidate.languages_known}")
        return True
    except Exception as e:
        print(f"❌ Candidate schema validation: FAILED")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n🔍 SCHEMA VALIDATION TEST SUITE")
    print("Testing updated schemas against sample data\n")
    
    job_passed = test_job_schema()
    candidate_passed = test_candidate_schema()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if job_passed and candidate_passed:
        print("✅ All schema validations PASSED")
        print("\nPhase 0 (Schema Alignment) completed successfully!")
        print("\nKey improvements:")
        print("  • Job schema: Added 15+ new fields (company, visa, education, etc.)")
        print("  • Candidate schema: Added 25+ new fields (nationality, visa, GCC exp, etc.)")
        print("  • Structured models: EmploymentHistory, EducationDetails")
        print("  • Enhanced response: SectionScore, ImprovementTip for detailed feedback")
        return 0
    else:
        print("❌ Some schema validations FAILED")
        print("Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())

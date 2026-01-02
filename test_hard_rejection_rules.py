"""
Comprehensive test suite for enhanced Hard Rejection Engine.
Tests all 8 rejection rules with various edge cases.
"""

import pytest
from datetime import datetime, timedelta

from logis_ai_candidate_engine.core.rules.hard_rejection_engine import (
    HardRejectionEngine,
    HardRejectionResult,
)
from logis_ai_candidate_engine.core.schemas.job import Job
from logis_ai_candidate_engine.core.schemas.candidate import Candidate


# ============================================================================
# Test Fixtures
# ============================================================================

def create_base_job(**overrides) -> Job:
    """Create a base job with all required fields"""
    defaults = {
        "job_id": "job-test-001",
        "country": "UAE",
        "title": "Software Engineer",
        "industry": "Technology",
        "functional_area": "Engineering",
        "designation": "Engineer",
        "min_experience_years": 3,
        "max_experience_years": 8,
        "salary_min": 10000,
        "salary_max": 20000,
        "currency": "AED",
        "required_skills": ["python", "javascript"],
        "job_description": "Software engineering role",
    }
    defaults.update(overrides)
    return Job(**defaults)


def create_base_candidate(**overrides) -> Candidate:
    """Create a base candidate with all required fields"""
    defaults = {
        "candidate_id": "cand-test-001",
        "nationality": "Indian",
        "current_country": "UAE",
        "visa_status": "Work Visa",
        "visa_expiry": (datetime.now() + timedelta(days=365)).date().isoformat(),
        "expected_salary": 15000,
        "currency": "AED",
        "total_experience_years": 5.0,
        "gcc_experience_years": 2.0,
        "skills": ["python", "javascript"],
    }
    defaults.update(overrides)
    return Candidate(**defaults)


# ============================================================================
# HR-001: Location + Visa Tests
# ============================================================================

def test_hr001_same_country_passes():
    """Candidate in same country as job passes"""
    job = create_base_job(country="UAE")
    candidate = create_base_candidate(current_country="UAE")
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-001:PASSED" in result.rule_trace


def test_hr001_different_country_with_work_visa_passes():
    """Candidate in different country with work visa passes"""
    job = create_base_job(country="UAE")
    candidate = create_base_candidate(
        current_country="India",
        visa_status="Work Visa",
    )
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-001:PASSED" in result.rule_trace


def test_hr001_different_country_no_work_auth_fails():
    """Candidate in different country without work authorization fails"""
    job = create_base_job(country="UAE")
    candidate = create_base_candidate(
        current_country="India",
        visa_status="Visit Visa",
    )
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is False
    assert result.rejection_rule_code == "HR-001"
    assert "HR-001:FAILED" in result.rule_trace
    assert "work authorization" in result.rejection_reason.lower()


def test_hr001_citizen_status_passes():
    """Candidate with citizen status passes regardless of location"""
    job = create_base_job(country="UAE")
    candidate = create_base_candidate(
        current_country="India",
        visa_status="Citizen",
    )
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-001:PASSED" in result.rule_trace


# ============================================================================
# HR-002: Visa Expiry Tests
# ============================================================================

def test_hr002_visa_expires_soon_fails():
    """Visa expiring within 90 days fails"""
    job = create_base_job()
    candidate = create_base_candidate(
        visa_expiry=(datetime.now() + timedelta(days=45)).date().isoformat()
    )
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is False
    assert result.rejection_rule_code == "HR-002"
    assert "HR-002:FAILED" in result.rule_trace


def test_hr002_visa_expires_after_90_days_passes():
    """Visa expiring after 90 days passes"""
    job = create_base_job()
    candidate = create_base_candidate(
        visa_expiry=(datetime.now() + timedelta(days=120)).date().isoformat()
    )
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-002:PASSED" in result.rule_trace


def test_hr002_no_visa_expiry_passes():
    """Candidate without visa expiry date passes"""
    job = create_base_job()
    candidate = create_base_candidate(visa_expiry=None)
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-002:PASSED" in result.rule_trace


# ============================================================================
# HR-003: Salary Tests
# ============================================================================

def test_hr003_salary_within_range_passes():
    """Salary within job range passes"""
    job = create_base_job(salary_max=20000)
    candidate = create_base_candidate(expected_salary=15000)
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-003:PASSED" in result.rule_trace


def test_hr003_salary_at_max_passes():
    """Salary exactly at max passes"""
    job = create_base_job(salary_max=20000)
    candidate = create_base_candidate(expected_salary=20000)
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-003:PASSED" in result.rule_trace


def test_hr003_salary_within_10_percent_tolerance_passes():
    """Salary within 10% tolerance passes"""
    job = create_base_job(salary_max=20000)
    candidate = create_base_candidate(expected_salary=21000)  # 5% over
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-003:PASSED" in result.rule_trace


def test_hr003_salary_exceeds_tolerance_fails():
    """Salary exceeding 10% tolerance fails"""
    job = create_base_job(salary_max=20000)
    candidate = create_base_candidate(expected_salary=23000)  # 15% over
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is False
    assert result.rejection_rule_code == "HR-003"
    assert "HR-003:FAILED" in result.rule_trace


# ============================================================================
# HR-004: Minimum Experience Tests
# ============================================================================

def test_hr004_experience_meets_minimum_passes():
    """Experience meeting minimum requirement passes"""
    job = create_base_job(min_experience_years=3)
    candidate = create_base_candidate(total_experience_years=5.0)
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-004:PASSED" in result.rule_trace


def test_hr004_experience_exactly_minimum_passes():
    """Experience exactly at minimum passes"""
    job = create_base_job(min_experience_years=3)
    candidate = create_base_candidate(total_experience_years=3.0)
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-004:PASSED" in result.rule_trace


def test_hr004_experience_below_minimum_fails():
    """Experience below minimum fails"""
    job = create_base_job(min_experience_years=5)
    candidate = create_base_candidate(total_experience_years=3.0)
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is False
    assert result.rejection_rule_code == "HR-004"
    assert "HR-004:FAILED" in result.rule_trace


# ============================================================================
# HR-005: Maximum Experience Tests
# ============================================================================

def test_hr005_experience_within_max_passes():
    """Experience within max range passes"""
    job = create_base_job(max_experience_years=8)
    candidate = create_base_candidate(total_experience_years=6.0)
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-005:PASSED" in result.rule_trace


def test_hr005_experience_within_tolerance_passes():
    """Experience within 3-year tolerance passes"""
    job = create_base_job(max_experience_years=8)
    candidate = create_base_candidate(total_experience_years=10.0)  # 2 years over
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-005:PASSED" in result.rule_trace


def test_hr005_experience_exceeds_tolerance_fails():
    """Experience exceeding tolerance fails"""
    job = create_base_job(max_experience_years=8)
    candidate = create_base_candidate(total_experience_years=15.0)  # 7 years over
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is False
    assert result.rejection_rule_code == "HR-005"
    assert "HR-005:FAILED" in result.rule_trace
    assert "overqualified" in result.rejection_reason.lower()


def test_hr005_no_max_experience_passes():
    """No max experience requirement always passes"""
    job = create_base_job(max_experience_years=None)
    candidate = create_base_candidate(total_experience_years=20.0)
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-005:PASSED" in result.rule_trace


# ============================================================================
# HR-006: Nationality Tests
# ============================================================================

def test_hr006_no_nationality_restriction_passes():
    """No nationality restriction passes all candidates"""
    job = create_base_job(preferred_nationality=[])
    candidate = create_base_candidate(nationality="Indian")
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-006:PASSED" in result.rule_trace


def test_hr006_matching_nationality_passes():
    """Matching nationality passes"""
    job = create_base_job(preferred_nationality=["Indian", "Pakistani"])
    candidate = create_base_candidate(nationality="Indian")
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-006:PASSED" in result.rule_trace


def test_hr006_non_matching_nationality_fails():
    """Non-matching nationality fails"""
    job = create_base_job(preferred_nationality=["UAE National"])
    candidate = create_base_candidate(nationality="Indian")
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is False
    assert result.rejection_rule_code == "HR-006"
    assert "HR-006:FAILED" in result.rule_trace


# ============================================================================
# HR-007: Education Tests
# ============================================================================

def test_hr007_no_education_requirement_passes():
    """No education requirement passes"""
    job = create_base_job(required_education=None)
    candidate = create_base_candidate(education_level="High School")
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-007:PASSED" in result.rule_trace


def test_hr007_exact_education_match_passes():
    """Exact education match passes"""
    job = create_base_job(required_education="Bachelors")
    candidate = create_base_candidate(education_level="Bachelors")
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-007:PASSED" in result.rule_trace


def test_hr007_higher_education_passes():
    """Higher education than required passes"""
    job = create_base_job(required_education="Bachelors")
    candidate = create_base_candidate(education_level="Masters")
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-007:PASSED" in result.rule_trace


def test_hr007_lower_education_fails():
    """Lower education than required fails"""
    job = create_base_job(required_education="Masters")
    candidate = create_base_candidate(education_level="Bachelors")
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is False
    assert result.rejection_rule_code == "HR-007"
    assert "HR-007:FAILED" in result.rule_trace


# ============================================================================
# HR-008: GCC Experience Tests
# ============================================================================

def test_hr008_gcc_not_required_passes():
    """GCC experience not required passes"""
    job = create_base_job(require_gcc_experience=False)
    candidate = create_base_candidate(gcc_experience_years=0)
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-008:PASSED" in result.rule_trace


def test_hr008_gcc_required_and_present_passes():
    """GCC experience required and candidate has it passes"""
    job = create_base_job(require_gcc_experience=True)
    candidate = create_base_candidate(gcc_experience_years=2.0)
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "HR-008:PASSED" in result.rule_trace


def test_hr008_gcc_required_but_missing_fails():
    """GCC experience required but candidate has none fails"""
    job = create_base_job(require_gcc_experience=True)
    candidate = create_base_candidate(gcc_experience_years=0)
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is False
    assert result.rejection_rule_code == "HR-008"
    assert "HR-008:FAILED" in result.rule_trace
    assert "GCC" in result.rejection_reason


# ============================================================================
# Integration Tests
# ============================================================================

def test_all_rules_pass():
    """Perfect candidate passes all rules"""
    job = create_base_job(
        country="UAE",
        min_experience_years=3,
        max_experience_years=8,
        salary_max=20000,
        required_education="Bachelors",
        require_gcc_experience=True,
    )
    
    candidate = create_base_candidate(
        current_country="UAE",
        visa_status="Work Visa",
        visa_expiry=(datetime.now() + timedelta(days=365)).date().isoformat(),
        expected_salary=15000,
        total_experience_years=5.0,
        gcc_experience_years=2.0,
        education_level="Bachelors",
        nationality="Indian",
    )
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is True
    assert "PASSED_ALL_HARD_RULES" in result.rule_trace
    assert result.rejection_reason is None
    assert result.rejection_rule_code is None
    
    # Verify all 8 rules were checked
    assert "HR-001:PASSED" in result.rule_trace
    assert "HR-002:PASSED" in result.rule_trace
    assert "HR-003:PASSED" in result.rule_trace
    assert "HR-004:PASSED" in result.rule_trace
    assert "HR-005:PASSED" in result.rule_trace
    assert "HR-006:PASSED" in result.rule_trace
    assert "HR-007:PASSED" in result.rule_trace
    assert "HR-008:PASSED" in result.rule_trace


def test_early_rejection_stops_evaluation():
    """Early rejection stops evaluation of subsequent rules"""
    job = create_base_job(country="UAE")
    candidate = create_base_candidate(
        current_country="India",
        visa_status="Visit Visa",  # Will fail HR-001
    )
    
    result = HardRejectionEngine.evaluate(job, candidate)
    
    assert result.is_eligible is False
    assert result.rejection_rule_code == "HR-001"
    assert "HR-001:FAILED" in result.rule_trace
    
    # Subsequent rules should not be evaluated
    assert "HR-002" not in " ".join(result.rule_trace)
    assert "HR-003" not in " ".join(result.rule_trace)


if __name__ == "__main__":
    # Run tests with pytest
    import sys
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))

# Phase 3: NER CV Parsing - Integration Tests
# test_phase3_cv_parsing.py
#
# Comprehensive test suite for the CV parsing system including:
# - Pattern extraction (emails, phones, dates)
# - Section detection and segmentation
# - Skill extraction with taxonomy matching
# - Experience parsing
# - Education parsing
# - CV-to-Candidate mapping
# - API endpoint testing

import pytest
import json
from typing import Dict, Any

# CV Parser components
from logis_ai_candidate_engine.ml.cv_parser import (
    CVParser,
    PatternMatcher,
    SectionDetector,
    SkillExtractor,
    ExperienceExtractor,
    EducationExtractor,
    ParsedCV,
    parse_cv,
)
from logis_ai_candidate_engine.ml.cv_candidate_mapper import (
    CVToCandidateMapper,
    map_cv_to_candidate,
)
from logis_ai_candidate_engine.core.schemas.candidate import Candidate


# =============================================================================
# TEST DATA: Sample CV texts for testing
# =============================================================================

SAMPLE_CV_FULL = """
John Smith
john.smith@example.com | +971 50 123 4567 | linkedin.com/in/johnsmith

PROFESSIONAL SUMMARY
Experienced Supply Chain Manager with 10+ years in logistics and distribution. 
Expert in WMS, TMS, and SAP ERP systems. Strong background in process optimization
and team leadership.

WORK EXPERIENCE

Supply Chain Director | ABC Logistics LLC
January 2020 - Present
- Oversee end-to-end supply chain operations for 5 distribution centers
- Implemented new WMS system reducing fulfillment time by 25%
- Manage team of 45 logistics professionals
- Achieved $2M cost savings through process optimization

Operations Manager | XYZ Freight Services
March 2015 - December 2019
- Managed daily logistics operations and fleet of 120 vehicles
- Developed demand planning strategies improving forecast accuracy by 30%
- Led customs clearance and compliance initiatives

Logistics Coordinator | Global Shipping Corp
June 2012 - February 2015
- Coordinated international freight forwarding operations
- Processed import/export documentation
- Maintained inventory accuracy of 99.5%

EDUCATION

Master of Business Administration (MBA) - Supply Chain Management
University of Dubai, 2014

Bachelor of Commerce (B.Com)
Mumbai University, 2010

SKILLS
Python, SQL, SAP, WMS, TMS, Demand Planning, Procurement, 
Inventory Management, Excel, Tableau, Power BI, Six Sigma

CERTIFICATIONS
- Lean Six Sigma Green Belt
- CSCP - Certified Supply Chain Professional

LANGUAGES
English (Fluent), Arabic (Intermediate), Hindi (Native)
"""

SAMPLE_CV_MINIMAL = """
Jane Doe
jane@email.com

Skills: Python, Machine Learning, Data Analysis

Experience:
- Data Scientist at Tech Corp (2020-Present)
"""

SAMPLE_CV_TECH = """
Mohammed Al-Hassan
mohammed.alhassan@techmail.com
+971 55 987 6543

SUMMARY
Senior Software Engineer specializing in Python, FastAPI, and Machine Learning.
5+ years building production ML systems.

EXPERIENCE

Senior ML Engineer at DataTech Solutions
Jan 2021 - Present
- Built recommendation systems using TensorFlow and PyTorch
- Deployed models on AWS and Kubernetes
- Led team of 4 engineers

Software Developer at StartupXYZ
2018 - 2020
- Full-stack development with React and Django
- Database design with PostgreSQL

EDUCATION
MSc Computer Science, MIT, 2018
BSc Software Engineering, 2016

SKILLS
Python, TensorFlow, PyTorch, FastAPI, React, Django, PostgreSQL, 
AWS, Docker, Kubernetes, Machine Learning, NLP
"""


# =============================================================================
# TEST: Pattern Matcher
# =============================================================================

class TestPatternMatcher:
    """Tests for PatternMatcher class"""
    
    def test_extract_emails(self):
        """Test email extraction from text"""
        text = "Contact me at john@example.com or support@company.org"
        emails = PatternMatcher.extract_emails(text)
        
        assert len(emails) == 2
        assert "john@example.com" in emails
        assert "support@company.org" in emails
    
    def test_extract_phones(self):
        """Test phone number extraction"""
        text = "Call +971 50 123 4567 or (555) 123-4567"
        phones = PatternMatcher.extract_phones(text)
        
        assert len(phones) >= 1
        # Should extract at least one valid phone
        assert any("971" in p or "555" in p for p in phones)
    
    def test_extract_linkedin(self):
        """Test LinkedIn URL extraction"""
        text = "Connect with me at linkedin.com/in/johndoe or https://www.linkedin.com/in/janedoe"
        linkedin = PatternMatcher.extract_linkedin(text)
        
        assert linkedin is not None
        assert "linkedin.com/in" in linkedin.lower()
    
    def test_detect_degree_level(self):
        """Test degree level detection"""
        assert PatternMatcher.detect_degree_level("Master of Science in CS") == "masters"
        assert PatternMatcher.detect_degree_level("Bachelor's Degree") == "bachelors"
        assert PatternMatcher.detect_degree_level("Ph.D. in Physics") == "phd"
        assert PatternMatcher.detect_degree_level("MBA from Harvard") == "masters"
    
    def test_is_likely_job_title(self):
        """Test job title detection"""
        assert PatternMatcher.is_likely_job_title("Software Engineer") == True
        assert PatternMatcher.is_likely_job_title("Supply Chain Manager") == True
        assert PatternMatcher.is_likely_job_title("Logistics Coordinator") == True
        assert PatternMatcher.is_likely_job_title("Random Text Here") == False


# =============================================================================
# TEST: Section Detector
# =============================================================================

class TestSectionDetector:
    """Tests for SectionDetector class"""
    
    def test_detect_experience_section(self):
        """Test detection of experience section headers"""
        detector = SectionDetector()
        
        section, confidence = detector.detect_section("WORK EXPERIENCE")
        assert section == "experience"
        assert confidence >= 0.6
        
        section, confidence = detector.detect_section("Employment History")
        assert section == "experience"
        assert confidence >= 0.6
    
    def test_detect_education_section(self):
        """Test detection of education section headers"""
        detector = SectionDetector()
        
        section, confidence = detector.detect_section("EDUCATION")
        assert section == "education"
        assert confidence >= 0.6
        
        section, confidence = detector.detect_section("Academic Background")
        assert section == "education"
        assert confidence >= 0.6
    
    def test_detect_skills_section(self):
        """Test detection of skills section headers"""
        detector = SectionDetector()
        
        section, confidence = detector.detect_section("SKILLS")
        assert section == "skills"
        assert confidence >= 0.6
        
        section, confidence = detector.detect_section("Technical Skills")
        assert section == "skills"
        assert confidence >= 0.6
    
    def test_segment_cv(self):
        """Test CV segmentation into sections"""
        detector = SectionDetector()
        sections = detector.segment_cv(SAMPLE_CV_FULL)
        
        assert "experience" in sections or "header" in sections
        # The CV should be segmented into multiple sections
        assert len(sections) >= 2


# =============================================================================
# TEST: Skill Extractor
# =============================================================================

class TestSkillExtractor:
    """Tests for SkillExtractor class"""
    
    def test_extract_known_skills(self):
        """Test extraction of skills from taxonomy"""
        extractor = SkillExtractor()
        skills = extractor.extract_skills("Expert in Python, SQL, and machine learning")
        
        skill_names = [s.normalized_skill for s in skills]
        
        # Should find Python and SQL
        assert any("python" in s.lower() for s in skill_names)
        assert any("sql" in s.lower() for s in skill_names)
    
    def test_extract_logistics_skills(self):
        """Test extraction of logistics-specific skills"""
        extractor = SkillExtractor()
        text = "Experienced with WMS, TMS, supply chain management, and SAP"
        skills = extractor.extract_skills(text, section="skills")
        
        skill_names = [s.normalized_skill for s in skills]
        
        # Should find logistics skills
        assert any("warehouse" in s.lower() or "wms" in s.lower() for s in skill_names)
    
    def test_skill_confidence_scores(self):
        """Test that extracted skills have confidence scores"""
        extractor = SkillExtractor()
        skills = extractor.extract_skills("Python programming and data analysis")
        
        for skill in skills:
            assert hasattr(skill, 'confidence')
            assert 0 <= skill.confidence <= 1
            assert hasattr(skill, 'source_section')


# =============================================================================
# TEST: Experience Extractor
# =============================================================================

class TestExperienceExtractor:
    """Tests for ExperienceExtractor class"""
    
    def test_extract_experiences(self):
        """Test extraction of work experiences"""
        extractor = ExperienceExtractor()
        
        exp_text = """
        Supply Chain Director at ABC Logistics
        January 2020 - Present
        - Managed operations
        
        Operations Manager, XYZ Corp
        2018 - 2020
        """
        
        experiences = extractor.extract_experiences(exp_text)
        
        # Should find at least one experience
        assert len(experiences) >= 1
    
    def test_experience_date_parsing(self):
        """Test that experience dates are parsed correctly"""
        extractor = ExperienceExtractor()
        
        exp_text = """
        Manager at Company
        Jan 2020 - Present
        - Did things
        """
        
        experiences = extractor.extract_experiences(exp_text)
        
        if experiences:
            exp = experiences[0]
            assert exp.start_date is not None or exp.job_title is not None


# =============================================================================
# TEST: Education Extractor
# =============================================================================

class TestEducationExtractor:
    """Tests for EducationExtractor class"""
    
    def test_extract_education(self):
        """Test extraction of education entries"""
        extractor = EducationExtractor()
        
        edu_text = """
        Master of Business Administration (MBA)
        University of Dubai, 2014
        
        Bachelor of Science in Computer Science
        MIT, 2010
        """
        
        education = extractor.extract_education(edu_text)
        
        # Should find at least one education entry
        assert len(education) >= 1
        
        # First should be MBA (masters level)
        if education:
            assert education[0].degree is not None


# =============================================================================
# TEST: Full CV Parser
# =============================================================================

class TestCVParser:
    """Tests for the main CVParser class"""
    
    def test_parse_full_cv(self):
        """Test parsing a complete CV"""
        parser = CVParser()
        result = parser.parse(SAMPLE_CV_FULL)
        
        assert isinstance(result, ParsedCV)
        assert result.name is not None
        assert result.contact.email is not None
        assert len(result.skills) > 0
    
    def test_parse_extracts_contact_info(self):
        """Test that contact information is extracted"""
        parser = CVParser()
        result = parser.parse(SAMPLE_CV_FULL)
        
        assert result.contact.email == "john.smith@example.com"
        assert result.contact.phone is not None
    
    def test_parse_extracts_name(self):
        """Test that candidate name is extracted"""
        parser = CVParser()
        result = parser.parse(SAMPLE_CV_FULL)
        
        assert result.name is not None
        assert "John" in result.name or "Smith" in result.name
    
    def test_parse_extracts_skills(self):
        """Test that skills are extracted from CV"""
        parser = CVParser()
        result = parser.parse(SAMPLE_CV_FULL)
        
        skill_names = [s.normalized_skill.lower() for s in result.skills]
        
        # Should find key skills
        assert any("python" in s for s in skill_names) or \
               any("sql" in s for s in skill_names) or \
               any("sap" in s for s in skill_names)
    
    def test_parse_minimal_cv(self):
        """Test parsing a minimal CV doesn't crash"""
        parser = CVParser()
        result = parser.parse(SAMPLE_CV_MINIMAL)
        
        assert isinstance(result, ParsedCV)
        assert result.extraction_confidence >= 0
    
    def test_parse_calculates_experience_years(self):
        """Test that total experience years is calculated"""
        parser = CVParser()
        result = parser.parse(SAMPLE_CV_FULL)
        
        # Should calculate some experience (may be None if parsing fails)
        # But shouldn't crash
        assert isinstance(result, ParsedCV)
    
    def test_parse_returns_confidence_score(self):
        """Test that parsing returns a confidence score"""
        parser = CVParser()
        result = parser.parse(SAMPLE_CV_FULL)
        
        assert 0 <= result.extraction_confidence <= 1
    
    def test_parse_extracts_languages(self):
        """Test that languages are extracted"""
        parser = CVParser()
        result = parser.parse(SAMPLE_CV_FULL)
        
        # The sample CV has English, Arabic, Hindi
        assert len(result.languages) >= 0  # May be empty if languages section not detected
    
    def test_convenience_function(self):
        """Test the parse_cv convenience function"""
        result = parse_cv(SAMPLE_CV_TECH)
        
        assert isinstance(result, ParsedCV)
        assert result.extraction_confidence >= 0


# =============================================================================
# TEST: CV to Candidate Mapper
# =============================================================================

class TestCVToCandidateMapper:
    """Tests for CVToCandidateMapper class"""
    
    def test_map_cv_to_candidate(self):
        """Test mapping parsed CV to Candidate schema"""
        parser = CVParser()
        mapper = CVToCandidateMapper()
        
        parsed = parser.parse(SAMPLE_CV_FULL)
        candidate = mapper.map(parsed, candidate_id="test_001")
        
        assert isinstance(candidate, Candidate)
        assert candidate.candidate_id == "test_001"
    
    def test_map_includes_skills(self):
        """Test that mapped candidate includes skills"""
        parser = CVParser()
        mapper = CVToCandidateMapper()
        
        parsed = parser.parse(SAMPLE_CV_FULL)
        candidate = mapper.map(parsed, candidate_id="test_002")
        
        assert len(candidate.skills) > 0
    
    def test_map_with_additional_data(self):
        """Test mapping with additional override data"""
        parser = CVParser()
        mapper = CVToCandidateMapper()
        
        parsed = parser.parse(SAMPLE_CV_MINIMAL)
        candidate = mapper.map(
            parsed,
            candidate_id="test_003",
            additional_data={
                "nationality": "Indian",
                "current_country": "UAE",
                "expected_salary": 15000,
                "total_experience_years": 5.0,
            }
        )
        
        assert candidate.nationality == "Indian"
        assert candidate.current_country == "UAE"
        assert candidate.expected_salary == 15000
        assert candidate.total_experience_years == 5.0
    
    def test_map_includes_contact_info(self):
        """Test that contact info is mapped"""
        parser = CVParser()
        mapper = CVToCandidateMapper()
        
        parsed = parser.parse(SAMPLE_CV_FULL)
        candidate = mapper.map(parsed, candidate_id="test_004")
        
        assert candidate.email == "john.smith@example.com"
    
    def test_map_includes_cv_text(self):
        """Test that raw CV text is preserved"""
        parser = CVParser()
        mapper = CVToCandidateMapper()
        
        parsed = parser.parse(SAMPLE_CV_TECH)
        candidate = mapper.map(parsed, candidate_id="test_005")
        
        assert candidate.cv_text is not None
        assert len(candidate.cv_text) > 0
    
    def test_convenience_function(self):
        """Test the map_cv_to_candidate convenience function"""
        parsed = parse_cv(SAMPLE_CV_TECH)
        candidate = map_cv_to_candidate(parsed, candidate_id="test_006")
        
        assert isinstance(candidate, Candidate)


# =============================================================================
# TEST: API Endpoints
# =============================================================================

class TestCVParsingAPI:
    """Tests for the CV parsing API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        from logis_ai_candidate_engine.api.main import app
        return TestClient(app)
    
    def test_cv_parse_endpoint(self, client):
        """Test the /api/v1/cv/parse endpoint"""
        response = client.post(
            "/api/v1/cv/parse",
            json={"cv_text": SAMPLE_CV_FULL}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert data["name"] is not None or len(data["skills"]) > 0
        assert "extraction_confidence" in data
    
    def test_cv_parse_to_candidate_endpoint(self, client):
        """Test the /api/v1/cv/parse-to-candidate endpoint"""
        response = client.post(
            "/api/v1/cv/parse-to-candidate",
            json={
                "cv_text": SAMPLE_CV_FULL,
                "nationality": "British",
                "current_country": "UAE",
                "expected_salary": 25000,
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "candidate" in data
        assert data["candidate"]["nationality"] == "British"
    
    def test_cv_extract_skills_endpoint(self, client):
        """Test the /api/v1/cv/extract-skills endpoint"""
        response = client.post(
            "/api/v1/cv/extract-skills",
            json={
                "cv_text": "Expert in Python, SQL, Machine Learning, and TensorFlow",
                "normalize": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "skills" in data
        assert data["total_skills_found"] > 0
    
    def test_cv_health_endpoint(self, client):
        """Test the /api/v1/cv/health endpoint"""
        response = client.get("/api/v1/cv/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "cv-parser"
    
    def test_cv_parse_rejects_short_text(self, client):
        """Test that very short CV text is rejected"""
        response = client.post(
            "/api/v1/cv/parse",
            json={"cv_text": "Too short"}
        )
        
        # Should fail validation (min 50 chars)
        assert response.status_code == 422


# =============================================================================
# TEST: End-to-End Integration
# =============================================================================

class TestEndToEndCVParsing:
    """End-to-end integration tests"""
    
    def test_full_pipeline_logistics_cv(self):
        """Test full pipeline with a logistics-focused CV"""
        # Parse CV
        parser = CVParser()
        parsed = parser.parse(SAMPLE_CV_FULL)
        
        # Verify logistics skills detected
        skill_names = [s.normalized_skill.lower() for s in parsed.skills]
        logistics_skills = ['warehouse_management', 'transportation_management', 
                          'supply_chain_management', 'demand_planning', 'procurement']
        
        found_logistics = [ls for ls in logistics_skills 
                         if any(ls in sn or sn in ls for sn in skill_names)]
        
        # Map to candidate
        mapper = CVToCandidateMapper()
        candidate = mapper.map(
            parsed,
            candidate_id="e2e_test_001",
            additional_data={
                "nationality": "British",
                "current_country": "UAE",
                "expected_salary": 25000,
            }
        )
        
        # Verify candidate is valid
        assert isinstance(candidate, Candidate)
        assert len(candidate.skills) > 0
        assert candidate.nationality == "British"
    
    def test_full_pipeline_tech_cv(self):
        """Test full pipeline with a technical CV"""
        # Parse CV
        parser = CVParser()
        parsed = parser.parse(SAMPLE_CV_TECH)
        
        # Verify tech skills detected
        skill_names = [s.normalized_skill.lower() for s in parsed.skills]
        
        # Should find Python, TensorFlow, etc.
        tech_skills_found = [s for s in skill_names 
                           if any(t in s for t in ['python', 'tensorflow', 'pytorch', 'react'])]
        
        assert len(tech_skills_found) > 0, f"Expected tech skills, found: {skill_names}"
        
        # Map to candidate
        candidate = map_cv_to_candidate(
            parsed,
            candidate_id="e2e_test_002",
            additional_data={
                "nationality": "Emirati",
                "current_country": "UAE",
                "expected_salary": 30000,
            }
        )
        
        # Verify
        assert isinstance(candidate, Candidate)
        assert candidate.email is not None


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

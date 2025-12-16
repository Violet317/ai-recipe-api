#!/usr/bin/env python3
"""
Property-based tests for configuration validation completeness.

**Feature: frontend-backend-connection, Property 6: Configuration validation completeness**
**Validates: Requirements 2.5, 4.4**
"""

import os
import unittest
from unittest.mock import patch
from hypothesis import given, strategies as st, settings
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env_manager import EnvironmentManager, ConfigStatus, ConfigReport
from validate_config import main as validate_main
import sys
import io
import json


class TestConfigurationValidationProperties(unittest.TestCase):
    """Property-based tests for configuration validation completeness"""
    
    def setUp(self):
        """Set up test environment"""
        self.manager = EnvironmentManager()
        # Save original environment
        self.original_env = dict(os.environ)
    
    def tearDown(self):
        """Restore original environment"""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    @given(
        required_vars=st.dictionaries(
            keys=st.sampled_from(["SECRET_KEY", "CORS_ORIGINS"]),
            values=st.one_of(
                st.none(),  # Missing
                st.text(min_size=32, max_size=64, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),  # Valid SECRET_KEY
                st.just("http://localhost:3000,https://example.com"),  # Valid CORS
                st.just("invalid"),  # Invalid value
                st.just("")  # Empty value
            ),
            min_size=0,
            max_size=2
        ),
        optional_vars=st.dictionaries(
            keys=st.sampled_from(["DATABASE_URL", "RAILWAY_STATIC_URL"]),
            values=st.one_of(
                st.none(),  # Missing
                st.just("sqlite:///./test.db"),  # Valid DATABASE_URL
                st.just("https://test.railway.app"),  # Valid RAILWAY_STATIC_URL
                st.just("invalid-url"),  # Invalid value
                st.just("")  # Empty value
            ),
            min_size=0,
            max_size=2
        )
    )
    @settings(max_examples=100)
    def test_configuration_validation_completeness_property(self, required_vars, optional_vars):
        """
        **Feature: frontend-backend-connection, Property 6: Configuration validation completeness**
        
        For any configuration check execution, the validation system should correctly check
        all required environment variables and configuration items, and report accurate status.
        
        **Validates: Requirements 2.5, 4.4**
        """
        # Clear environment to start fresh
        for key in list(os.environ.keys()):
            if key in ["SECRET_KEY", "CORS_ORIGINS", "DATABASE_URL", "RAILWAY_STATIC_URL"]:
                del os.environ[key]
        
        # Set up test environment variables
        all_vars = {**required_vars, **optional_vars}
        for key, value in all_vars.items():
            if value is not None:
                os.environ[key] = value
        
        # Execute configuration validation
        report = self.manager.validate_environment_variables()
        
        # Property 1: All defined required variables should be checked
        required_var_names = set(self.manager.REQUIRED_VARS.keys())
        reported_required_names = {item.name for item in report.items if item.required}
        
        self.assertEqual(required_var_names, reported_required_names,
                        "All required variables should be included in validation report")
        
        # Property 2: All defined optional variables should be checked
        optional_var_names = set(self.manager.OPTIONAL_VARS.keys())
        reported_optional_names = {item.name for item in report.items if not item.required}
        
        self.assertEqual(optional_var_names, reported_optional_names,
                        "All optional variables should be included in validation report")
        
        # Property 3: Status accuracy for each variable
        for item in report.items:
            actual_value = os.getenv(item.name)
            
            if item.name in self.manager.REQUIRED_VARS:
                config = self.manager.REQUIRED_VARS[item.name]
                if actual_value is None:
                    self.assertEqual(item.status, ConfigStatus.MISSING,
                                   f"Missing required variable {item.name} should have MISSING status")
                elif not config["validator"](actual_value):
                    self.assertEqual(item.status, ConfigStatus.INVALID,
                                   f"Invalid required variable {item.name} should have INVALID status")
                else:
                    self.assertEqual(item.status, ConfigStatus.VALID,
                                   f"Valid required variable {item.name} should have VALID status")
            
            elif item.name in self.manager.OPTIONAL_VARS:
                config = self.manager.OPTIONAL_VARS[item.name]
                if actual_value is None:
                    self.assertEqual(item.status, ConfigStatus.WARNING,
                                   f"Missing optional variable {item.name} should have WARNING status")
                elif not config["validator"](actual_value):
                    self.assertEqual(item.status, ConfigStatus.INVALID,
                                   f"Invalid optional variable {item.name} should have INVALID status")
                else:
                    self.assertEqual(item.status, ConfigStatus.VALID,
                                   f"Valid optional variable {item.name} should have VALID status")
        
        # Property 4: Overall status accuracy
        has_missing_required = any(
            item.status == ConfigStatus.MISSING and item.required 
            for item in report.items
        )
        has_invalid_required = any(
            item.status == ConfigStatus.INVALID and item.required 
            for item in report.items
        )
        has_warnings_or_invalid_optional = any(
            item.status in [ConfigStatus.WARNING, ConfigStatus.INVALID] and not item.required
            for item in report.items
        )
        
        if has_missing_required or has_invalid_required:
            self.assertEqual(report.overall_status, ConfigStatus.INVALID,
                           "Overall status should be INVALID when required variables are missing or invalid")
        elif has_warnings_or_invalid_optional:
            self.assertEqual(report.overall_status, ConfigStatus.WARNING,
                           "Overall status should be WARNING when optional variables have issues")
        else:
            self.assertEqual(report.overall_status, ConfigStatus.VALID,
                           "Overall status should be VALID when all variables are valid")
        
        # Property 5: Report completeness - all items should have required fields
        for item in report.items:
            self.assertIsNotNone(item.name, "Each item should have a name")
            self.assertIsNotNone(item.status, "Each item should have a status")
            self.assertIsNotNone(item.message, "Each item should have a message")
            self.assertIsInstance(item.required, bool, "Each item should have a required flag")
    
    @given(
        environment_sets=st.lists(
            st.dictionaries(
                keys=st.sampled_from(["SECRET_KEY", "CORS_ORIGINS", "DATABASE_URL", "RAILWAY_STATIC_URL"]),
                values=st.one_of(
                    st.text(min_size=32, max_size=64, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
                    st.just("http://localhost:3000"),
                    st.just("sqlite:///./test.db"),
                    st.just("https://test.railway.app")
                ),
                min_size=0,
                max_size=4
            ),
            min_size=1,
            max_size=3
        )
    )
    @settings(max_examples=50)
    def test_validation_consistency_across_multiple_checks(self, environment_sets):
        """
        **Feature: frontend-backend-connection, Property 6: Configuration validation completeness**
        
        For any sequence of configuration checks with the same environment,
        the validation results should be consistent across multiple executions.
        
        **Validates: Requirements 2.5, 4.4**
        """
        for env_set in environment_sets:
            # Clear and set environment
            for key in ["SECRET_KEY", "CORS_ORIGINS", "DATABASE_URL", "RAILWAY_STATIC_URL"]:
                if key in os.environ:
                    del os.environ[key]
            
            for key, value in env_set.items():
                os.environ[key] = value
            
            # Perform multiple validation checks
            report1 = self.manager.validate_environment_variables()
            report2 = self.manager.validate_environment_variables()
            report3 = self.manager.validate_environment_variables()
            
            # Property: Consistency across multiple checks
            self.assertEqual(report1.overall_status, report2.overall_status,
                           "Multiple validation checks should have consistent overall status")
            self.assertEqual(report2.overall_status, report3.overall_status,
                           "Multiple validation checks should have consistent overall status")
            
            # Property: Same variables should be reported each time
            names1 = {item.name for item in report1.items}
            names2 = {item.name for item in report2.items}
            names3 = {item.name for item in report3.items}
            
            self.assertEqual(names1, names2,
                           "Same variables should be reported in each validation check")
            self.assertEqual(names2, names3,
                           "Same variables should be reported in each validation check")
            
            # Property: Status should be consistent for each variable
            for item1 in report1.items:
                item2 = next(item for item in report2.items if item.name == item1.name)
                item3 = next(item for item in report3.items if item.name == item1.name)
                
                self.assertEqual(item1.status, item2.status,
                               f"Status for {item1.name} should be consistent across checks")
                self.assertEqual(item2.status, item3.status,
                               f"Status for {item1.name} should be consistent across checks")
    
    @given(
        config_scenarios=st.lists(
            st.one_of(
                st.just({"SECRET_KEY": "valid_secret_key_that_is_long_enough_32chars", "CORS_ORIGINS": "http://localhost:3000"}),  # All valid
                st.just({"SECRET_KEY": "short", "CORS_ORIGINS": "http://localhost:3000"}),  # Invalid SECRET_KEY
                st.just({"SECRET_KEY": "valid_secret_key_that_is_long_enough_32chars", "CORS_ORIGINS": "invalid"}),  # Invalid CORS
                st.just({"CORS_ORIGINS": "http://localhost:3000"}),  # Missing SECRET_KEY
                st.just({"SECRET_KEY": "valid_secret_key_that_is_long_enough_32chars"}),  # Missing CORS_ORIGINS
                st.just({})  # All missing
            ),
            min_size=1,
            max_size=6
        )
    )
    @settings(max_examples=50)
    def test_validation_report_json_serialization_property(self, config_scenarios):
        """
        **Feature: frontend-backend-connection, Property 6: Configuration validation completeness**
        
        For any configuration state, the validation report should be serializable to JSON
        and contain all required information for external tools and scripts.
        
        **Validates: Requirements 2.5, 4.4**
        """
        for scenario in config_scenarios:
            # Clear and set environment
            for key in ["SECRET_KEY", "CORS_ORIGINS", "DATABASE_URL", "RAILWAY_STATIC_URL"]:
                if key in os.environ:
                    del os.environ[key]
            
            for key, value in scenario.items():
                os.environ[key] = value
            
            # Generate JSON report
            json_report = self.manager.generate_config_report_json()
            
            # Property: JSON should be valid and parseable
            try:
                parsed_report = json.loads(json_report)
            except json.JSONDecodeError:
                self.fail("Configuration report should generate valid JSON")
            
            # Property: JSON report should contain all required fields
            self.assertIn("items", parsed_report, "JSON report should contain 'items' field")
            self.assertIn("overall_status", parsed_report, "JSON report should contain 'overall_status' field")
            self.assertIn("summary", parsed_report, "JSON report should contain 'summary' field")
            
            # Property: Each item should have complete information
            for item in parsed_report["items"]:
                self.assertIn("name", item, "Each item should have 'name' field")
                self.assertIn("status", item, "Each item should have 'status' field")
                self.assertIn("message", item, "Each item should have 'message' field")
                self.assertIn("required", item, "Each item should have 'required' field")
                self.assertIn("value", item, "Each item should have 'value' field")
            
            # Property: Status values should be valid enum values
            valid_statuses = {"valid", "invalid", "missing", "warning"}
            self.assertIn(parsed_report["overall_status"], valid_statuses,
                         "Overall status should be a valid enum value")
            
            for item in parsed_report["items"]:
                self.assertIn(item["status"], valid_statuses,
                             f"Item status for {item['name']} should be a valid enum value")


if __name__ == "__main__":
    unittest.main()
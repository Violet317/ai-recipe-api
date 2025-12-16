#!/usr/bin/env python3
"""
Property-based tests for environment variable management consistency.

**Feature: frontend-backend-connection, Property 3: Environment variable management consistency**
**Validates: Requirements 1.5, 2.1, 2.3, 2.4**
"""

import os
import unittest
from unittest.mock import patch
from hypothesis import given, strategies as st, settings
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from env_manager import EnvironmentManager, ConfigStatus, ConfigReport


class TestEnvironmentManagerProperties(unittest.TestCase):
    """Property-based tests for environment variable management"""
    
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
        secret_key=st.text(min_size=32, max_size=64, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),
        cors_origins=st.lists(
            st.one_of(
                st.just("*"),
                st.builds(
                    lambda protocol, domain, port: f"{protocol}://{domain}" + (f":{port}" if port else ""),
                    protocol=st.sampled_from(["http", "https"]),
                    domain=st.one_of(
                        st.just("localhost"),
                        st.builds(
                            lambda name: f"{name}.com",
                            name=st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz")
                        )
                    ),
                    port=st.one_of(st.none(), st.integers(min_value=1000, max_value=9999))
                )
            ),
            min_size=1,
            max_size=5
        ),
        railway_url=st.one_of(
            st.none(),
            st.builds(
                lambda domain: f"https://{domain}.railway.app",
                domain=st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz")
            )
        )
    )
    @settings(max_examples=100)
    def test_environment_variable_consistency_property(self, secret_key, cors_origins, railway_url):
        """
        **Feature: frontend-backend-connection, Property 3: Environment variable management consistency**
        
        For any environment variable update, the system should correctly apply new configuration
        and all services should use consistent configuration values.
        
        **Validates: Requirements 1.5, 2.1, 2.3, 2.4**
        """
        # Clear environment to start fresh
        for key in list(os.environ.keys()):
            if key in ["SECRET_KEY", "CORS_ORIGINS", "RAILWAY_STATIC_URL", "DATABASE_URL"]:
                del os.environ[key]
        
        # Set up valid environment variables
        os.environ["SECRET_KEY"] = secret_key
        os.environ["CORS_ORIGINS"] = ",".join(cors_origins)
        if railway_url:
            os.environ["RAILWAY_STATIC_URL"] = railway_url
        
        # Create two manager instances to simulate different services
        manager1 = EnvironmentManager()
        manager2 = EnvironmentManager()
        
        # Both managers should validate the same environment consistently
        report1 = manager1.validate_environment_variables()
        report2 = manager2.validate_environment_variables()
        
        # Property 1: Validation consistency across manager instances
        self.assertEqual(report1.overall_status, report2.overall_status,
                        "Different manager instances should have consistent validation results")
        
        # Property 2: Configuration retrieval consistency
        api_url1 = manager1.get_api_base_url()
        api_url2 = manager2.get_api_base_url()
        self.assertEqual(api_url1, api_url2,
                        "API base URL should be consistent across manager instances")
        
        cors_origins1 = manager1.get_cors_origins()
        cors_origins2 = manager2.get_cors_origins()
        self.assertEqual(cors_origins1, cors_origins2,
                        "CORS origins should be consistent across manager instances")
        
        # Property 3: Valid configuration should result in VALID status
        if report1.overall_status == ConfigStatus.VALID:
            # All required variables should be present and valid
            required_items = [item for item in report1.items if item.required]
            for item in required_items:
                self.assertIn(item.status, [ConfigStatus.VALID],
                            f"Required variable {item.name} should be VALID when overall status is VALID")
        
        # Property 4: Configuration update consistency
        # Simulate environment variable update
        new_secret = secret_key + "updated"
        os.environ["SECRET_KEY"] = new_secret
        
        # Both managers should see the updated configuration
        updated_report1 = manager1.validate_environment_variables()
        updated_report2 = manager2.validate_environment_variables()
        
        self.assertEqual(updated_report1.overall_status, updated_report2.overall_status,
                        "Updated configuration should be consistent across manager instances")
    
    @given(
        invalid_cors=st.one_of(
            st.just(""),
            st.just("invalid-url"),
            st.just("ftp://invalid.com"),
            st.text(min_size=1, max_size=10, alphabet="!@#$%^&*()")
        ),
        short_secret=st.text(min_size=0, max_size=31, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    )
    @settings(max_examples=100)
    def test_invalid_configuration_consistency_property(self, invalid_cors, short_secret):
        """
        **Feature: frontend-backend-connection, Property 3: Environment variable management consistency**
        
        For any invalid environment variable configuration, the system should consistently
        report validation errors across all manager instances.
        
        **Validates: Requirements 2.4, 2.5**
        """
        # Clear environment
        for key in list(os.environ.keys()):
            if key in ["SECRET_KEY", "CORS_ORIGINS", "RAILWAY_STATIC_URL", "DATABASE_URL"]:
                del os.environ[key]
        
        # Set invalid configuration
        os.environ["SECRET_KEY"] = short_secret
        os.environ["CORS_ORIGINS"] = invalid_cors
        
        # Create multiple manager instances
        manager1 = EnvironmentManager()
        manager2 = EnvironmentManager()
        
        # Both should report invalid configuration consistently
        report1 = manager1.validate_environment_variables()
        report2 = manager2.validate_environment_variables()
        
        # Property: Invalid configuration should be consistently detected
        self.assertEqual(report1.overall_status, ConfigStatus.INVALID,
                        "Invalid configuration should result in INVALID status")
        self.assertEqual(report2.overall_status, ConfigStatus.INVALID,
                        "Invalid configuration should result in INVALID status")
        self.assertEqual(report1.overall_status, report2.overall_status,
                        "Invalid configuration detection should be consistent")
        
        # Property: Error messages should be consistent
        invalid_items1 = [item for item in report1.items if item.status == ConfigStatus.INVALID]
        invalid_items2 = [item for item in report2.items if item.status == ConfigStatus.INVALID]
        
        self.assertEqual(len(invalid_items1), len(invalid_items2),
                        "Number of invalid items should be consistent")
        
        # Check that the same variables are marked as invalid
        invalid_names1 = {item.name for item in invalid_items1}
        invalid_names2 = {item.name for item in invalid_items2}
        self.assertEqual(invalid_names1, invalid_names2,
                        "Same variables should be marked as invalid consistently")
    
    @given(
        config_updates=st.lists(
            st.dictionaries(
                keys=st.sampled_from(["SECRET_KEY", "CORS_ORIGINS", "RAILWAY_STATIC_URL"]),
                values=st.one_of(
                    st.text(min_size=32, max_size=64, alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"),  # Valid secret keys
                    st.just("http://localhost:3000,https://example.com"),  # Valid CORS
                    st.just("https://test.railway.app")  # Valid Railway URL
                ),
                min_size=1,
                max_size=3
            ),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=50)
    def test_configuration_update_sequence_consistency(self, config_updates):
        """
        **Feature: frontend-backend-connection, Property 3: Environment variable management consistency**
        
        For any sequence of environment variable updates, the system should maintain
        consistency and each update should be properly reflected.
        
        **Validates: Requirements 1.5, 2.1, 2.3**
        """
        manager = EnvironmentManager()
        
        # Set initial valid configuration
        os.environ["SECRET_KEY"] = "initial_secret_key_that_is_long_enough_32chars"
        os.environ["CORS_ORIGINS"] = "http://localhost:3000"
        
        initial_report = manager.validate_environment_variables()
        
        # Apply sequence of updates
        for update in config_updates:
            # Apply the update
            for key, value in update.items():
                os.environ[key] = value
            
            # Validate that the update is reflected
            current_report = manager.validate_environment_variables()
            
            # Property: Each update should be properly validated
            self.assertIsInstance(current_report, ConfigReport,
                                "Validation should always return a ConfigReport")
            
            # Property: Updated values should be reflected in configuration
            for key, expected_value in update.items():
                actual_value = os.getenv(key)
                self.assertEqual(actual_value, expected_value,
                               f"Environment variable {key} should reflect the update")
            
            # Property: Manager should consistently retrieve updated values
            if "RAILWAY_STATIC_URL" in update:
                api_url = manager.get_api_base_url()
                if update["RAILWAY_STATIC_URL"]:
                    self.assertEqual(api_url, update["RAILWAY_STATIC_URL"],
                                   "API base URL should reflect Railway URL update")
            
            if "CORS_ORIGINS" in update:
                cors_origins = manager.get_cors_origins()
                expected_origins = [o.strip() for o in update["CORS_ORIGINS"].split(",")]
                self.assertEqual(cors_origins, expected_origins,
                               "CORS origins should reflect the update")


if __name__ == "__main__":
    unittest.main()
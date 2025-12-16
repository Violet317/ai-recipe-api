#!/usr/bin/env python3
"""
Business functionality validation tests
Tests core API endpoints and business logic without requiring a running server
"""

import sys
import os
import json
from typing import Dict, Any, List

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import SessionLocal, Recipe, User
from recipe_service import recommend_recipes
from auth import verify_password, get_password_hash, create_access_token
from main import RecipeRequest, UserCreate, UserLogin


def test_database_connection():
    """Test database connectivity"""
    print("🔍 Testing database connection...")
    try:
        db = SessionLocal()
        # Try to query recipes
        recipe_count = db.query(Recipe).count()
        print(f"✅ Database connected successfully. Found {recipe_count} recipes.")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_recipe_recommendation_logic():
    """Test recipe recommendation business logic"""
    print("\n🍳 Testing recipe recommendation logic...")
    try:
        # Test with common ingredients
        test_ingredients = ["番茄", "鸡蛋"]
        recipes = recommend_recipes(test_ingredients)
        
        if recipes:
            print(f"✅ Recipe recommendation works. Found {len(recipes)} recipes for {test_ingredients}")
            # Show first recipe as example
            first_recipe = recipes[0]
            print(f"   Example: {first_recipe.get('name', 'Unknown')} (Match: {first_recipe.get('match_rate', 0)}%)")
            return True
        else:
            print(f"⚠️  No recipes found for ingredients: {test_ingredients}")
            return False
    except Exception as e:
        print(f"❌ Recipe recommendation failed: {e}")
        return False


def test_user_authentication_logic():
    """Test user authentication business logic"""
    print("\n🔐 Testing user authentication logic...")
    try:
        # Test password hashing
        test_password = "test_password_123"
        hashed = get_password_hash(test_password)
        print(f"✅ Password hashing works")
        
        # Test password verification
        if verify_password(test_password, hashed):
            print(f"✅ Password verification works")
        else:
            print(f"❌ Password verification failed")
            return False
        
        # Test token creation
        token = create_access_token(data={"sub": "test_user"})
        if token:
            print(f"✅ Token creation works")
            return True
        else:
            print(f"❌ Token creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Authentication logic failed: {e}")
        return False


def test_user_registration_logic():
    """Test user registration business logic"""
    print("\n👤 Testing user registration logic...")
    try:
        db = SessionLocal()
        
        # Use unique identifiers to avoid conflicts
        import time
        unique_id = str(int(time.time()))
        test_username = f"test_business_user_{unique_id}"
        test_email = f"test_{unique_id}@example.com"
        
        # Check if test user already exists and clean up
        existing_user = db.query(User).filter(User.username == test_username).first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
        
        existing_email_user = db.query(User).filter(User.email == test_email).first()
        if existing_email_user:
            db.delete(existing_email_user)
            db.commit()
        
        # Create test user
        test_user_data = UserCreate(
            username=test_username,
            email=test_email,
            password="test_password_123"
        )
        
        # Simulate registration logic
        hashed_password = get_password_hash(test_user_data.password)
        db_user = User(
            username=test_user_data.username,
            email=test_user_data.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        print(f"✅ User registration logic works. Created user ID: {db_user.id}")
        
        # Clean up
        db.delete(db_user)
        db.commit()
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ User registration logic failed: {e}")
        if 'db' in locals():
            db.close()
        return False


def test_user_login_logic():
    """Test user login logic"""
    print("\n🔑 Testing user login logic...")
    try:
        db = SessionLocal()
        
        # Create a test user for login testing with unique identifiers
        import time
        unique_id = str(int(time.time()))
        test_username = f"test_login_user_{unique_id}"
        test_email = f"login_test_{unique_id}@example.com"
        test_password = "login_test_123"
        
        # Clean up any existing test user
        existing_user = db.query(User).filter(User.username == test_username).first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
        
        existing_email_user = db.query(User).filter(User.email == test_email).first()
        if existing_email_user:
            db.delete(existing_email_user)
            db.commit()
        
        # Create test user
        hashed_password = get_password_hash(test_password)
        db_user = User(
            username=test_username,
            email=test_email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Test login logic
        login_data = UserLogin(username=test_username, password=test_password)
        
        # Simulate login verification
        user = db.query(User).filter(User.username == login_data.username).first()
        if user and verify_password(login_data.password, user.hashed_password):
            token = create_access_token(data={"sub": user.username})
            print(f"✅ User login logic works. Generated token for user: {user.username}")
            success = True
        else:
            print(f"❌ User login verification failed")
            success = False
        
        # Clean up
        db.delete(db_user)
        db.commit()
        db.close()
        return success
        
    except Exception as e:
        print(f"❌ User login logic failed: {e}")
        if 'db' in locals():
            db.close()
        return False


def test_recipe_data_integrity():
    """Test recipe data integrity and format"""
    print("\n📊 Testing recipe data integrity...")
    try:
        db = SessionLocal()
        recipes = db.query(Recipe).limit(5).all()
        
        if not recipes:
            print("⚠️  No recipes found in database")
            db.close()
            return False
        
        print(f"✅ Found {len(recipes)} recipes to validate")
        
        for recipe in recipes:
            # Check required fields
            if not recipe.name:
                print(f"❌ Recipe {recipe.id} missing name")
                return False
            
            # Check JSON fields can be parsed
            try:
                ingredients = json.loads(recipe.ingredients)
                steps = json.loads(recipe.steps)
                tags = json.loads(recipe.tags)
                
                if not isinstance(ingredients, list):
                    print(f"❌ Recipe {recipe.id} ingredients not a list")
                    return False
                    
                if not isinstance(steps, list):
                    print(f"❌ Recipe {recipe.id} steps not a list")
                    return False
                    
                if not isinstance(tags, list):
                    print(f"❌ Recipe {recipe.id} tags not a list")
                    return False
                    
            except json.JSONDecodeError as e:
                print(f"❌ Recipe {recipe.id} has invalid JSON: {e}")
                return False
        
        print(f"✅ All recipe data is properly formatted")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Recipe data integrity test failed: {e}")
        if 'db' in locals():
            db.close()
        return False


def run_all_business_tests():
    """Run all business functionality tests"""
    print("🚀 Starting Business Functionality Validation Tests")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Recipe Recommendation Logic", test_recipe_recommendation_logic),
        ("User Authentication Logic", test_user_authentication_logic),
        ("User Registration Logic", test_user_registration_logic),
        ("User Login Logic", test_user_login_logic),
        ("Recipe Data Integrity", test_recipe_data_integrity),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 60)
    print("📋 Business Functionality Test Results:")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All business functionality tests passed!")
        return True
    else:
        print("⚠️  Some business functionality tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    success = run_all_business_tests()
    sys.exit(0 if success else 1)
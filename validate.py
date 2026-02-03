"""
Validation Script - Verify A/B Testing System
Tests all components to ensure production readiness
"""

import sys
import traceback


def test_data_simulation():
    """Test data simulation module."""
    print("=" * 60)
    print("TEST 1: Data Simulation Module")
    print("=" * 60)
    
    try:
        from data_simulation import ExperimentDataSimulator
        
        # Create simulator
        simulator = ExperimentDataSimulator(n_users=10000)
        data = simulator.generate_experiment_data()
        
        # Validate
        assert len(data) == 10000, "Incorrect number of users"
        assert len(data['variant'].unique()) == 2, "Should have 2 variants"
        assert 'engagement' in data.columns, "Missing engagement column"
        assert 'retained_7d' in data.columns, "Missing retention column"
        assert data['engagement'].min() >= 0, "Engagement should be non-negative"
        
        # Check split
        control_pct = (data['variant'] == 'control').sum() / len(data)
        assert 0.48 <= control_pct <= 0.52, "Split should be approximately 50/50"
        
        print("✅ Data simulation working correctly")
        print(f"   - Generated {len(data):,} users")
        print(f"   - Control: {(data['variant'] == 'control').sum():,} users")
        print(f"   - Treatment: {(data['variant'] == 'treatment').sum():,} users")
        print(f"   - Avg engagement: {data['engagement'].mean():.2f}")
        print(f"   - Retention rate: {data['retained_7d'].mean():.2%}")
        return True
        
    except Exception as e:
        print(f"❌ Data simulation failed: {str(e)}")
        traceback.print_exc()
        return False


def test_analysis():
    """Test statistical analysis module."""
    print("\n" + "=" * 60)
    print("TEST 2: Statistical Analysis Module")
    print("=" * 60)
    
    try:
        from data_simulation import generate_data
        from analysis import ABTestAnalyzer
        
        # Generate test data
        data = generate_data()
        
        # Run analysis
        analyzer = ABTestAnalyzer(alpha=0.05)
        results = analyzer.run_full_analysis(data)
        
        # Validate structure
        assert 'engagement' in results, "Missing engagement results"
        assert 'retention' in results, "Missing retention results"
        assert 'decision' in results, "Missing decision results"
        
        # Validate engagement results
        eng = results['engagement']
        assert 'p_value' in eng, "Missing p-value"
        assert 'is_significant' in eng, "Missing significance flag"
        assert 'ci_lower' in eng and 'ci_upper' in eng, "Missing CI"
        
        # Validate retention results
        ret = results['retention']
        assert 'p_value' in ret, "Missing p-value"
        assert 'is_significant' in ret, "Missing significance flag"
        
        # Validate decision
        decision = results['decision']
        assert 'decision' in decision, "Missing decision"
        assert decision['decision'] in ['SHIP', 'DO NOT SHIP', 'SHIP WITH CAUTION'], "Invalid decision"
        
        print("✅ Statistical analysis working correctly")
        print(f"   - Engagement uplift: {eng['relative_diff_pct']:.2f}%")
        print(f"   - Engagement p-value: {eng['p_value']:.6f}")
        print(f"   - Retention uplift: {ret['relative_diff_pct']:.2f}%")
        print(f"   - Retention p-value: {ret['p_value']:.6f}")
        print(f"   - Decision: {decision['decision']}")
        print(f"   - Confidence: {decision['confidence']}")
        return True
        
    except Exception as e:
        print(f"❌ Statistical analysis failed: {str(e)}")
        traceback.print_exc()
        return False


def test_imports():
    """Test all required imports."""
    print("\n" + "=" * 60)
    print("TEST 3: Dependencies and Imports")
    print("=" * 60)
    
    required_packages = [
        'pandas', 'numpy', 'scipy', 'streamlit', 'plotly'
    ]
    
    all_imported = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} imported successfully")
        except ImportError:
            print(f"❌ {package} import failed")
            all_imported = False
    
    return all_imported


def test_file_structure():
    """Test project file structure."""
    print("\n" + "=" * 60)
    print("TEST 4: Project File Structure")
    print("=" * 60)
    
    import os
    
    required_files = [
        'app.py',
        'data_simulation.py',
        'analysis.py',
        'requirements.txt',
        'README.md'
    ]
    
    all_exist = True
    for filename in required_files:
        if os.path.exists(f'/app/{filename}'):
            size = os.path.getsize(f'/app/{filename}')
            print(f"✅ {filename} exists ({size:,} bytes)")
        else:
            print(f"❌ {filename} missing")
            all_exist = False
    
    return all_exist


def main():
    """Run all validation tests."""
    print("\n" + "🔍 " + "=" * 58)
    print("🔍 A/B TESTING SYSTEM - VALIDATION SUITE")
    print("🔍 " + "=" * 58 + "\n")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Dependencies", test_imports),
        ("Data Simulation", test_data_simulation),
        ("Statistical Analysis", test_analysis),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 60)
    print(f"OVERALL: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! System is production-ready.")
        print("\n📊 To launch the dashboard, run:")
        print("   streamlit run app.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

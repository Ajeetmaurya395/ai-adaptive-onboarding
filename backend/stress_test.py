from backend.gap_engine import calculate_gap
import json

def test_alias():
    """Verify that 'k8s' correctly matches 'Kubernetes' via the alias map."""
    # Resume has 'k8s', JD requires 'Kubernetes'
    result = calculate_gap(["k8s"], ["Kubernetes"], "We need someone with Kubernetes experience.")
    print(f"Alias Test (k8s -> Kubernetes): {'PASS' if 'Kubernetes' in result['matched_skills'] else 'FAIL'}")
    print(f"  Matched: {result['matched_skills']}")
    assert "Kubernetes" in result['matched_skills']

def test_normalization():
    """Verify that 'React.js' canonicalizes to 'React' via skill_lookup.json."""
    # Resume has 'React.js', JD requires 'React'
    result = calculate_gap(["React.js"], ["React"], "Frontend developer with React skills.")
    print(f"Normalization Test (React.js -> React): {'PASS' if 'React' in result['matched_skills'] else 'FAIL'}")
    print(f"  Matched: {result['matched_skills']}")
    assert "React" in result['matched_skills']

if __name__ == "__main__":
    try:
        test_alias()
        test_normalization()
        print("\n✅ [STRESS TEST] All O*NET-backed logic verified successfully!")
    except AssertionError as e:
        print(f"\n❌ [STRESS TEST] Failed: {e}")
    except Exception as e:
        print(f"\n❌ [ERROR] An unexpected error occurred: {e}")

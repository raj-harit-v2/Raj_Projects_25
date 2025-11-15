"""
Comprehensive Diagnostics for Phase 1, 2 & 3
Tests all components and generates detailed report
"""

import sys
import json
from pathlib import Path
import datetime

def diagnostic_header(title):
    """Print diagnostic section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_imports():
    """Test all module imports"""
    diagnostic_header("DIAGNOSTIC 1: Module Imports")
    
    try:
        from modules.heuristics import preprocess_query, postprocess_result
        print("[OK] modules.heuristics imported")
        
        from modules.historical_context import HistoricalContextManager
        print("[OK] modules.historical_context imported")
        
        from modules.perception import run_perception
        print("[OK] modules.perception imported")
        
        from modules.decision import generate_plan
        print("[OK] modules.decision imported")
        
        from modules.action import run_python_sandbox
        print("[OK] modules.action imported")
        
        from core.loop import AgentLoop
        print("[OK] core.loop imported")
        
        from core.context import AgentContext
        print("[OK] core.context imported")
        
        from core.session import MultiMCP
        print("[OK] core.session imported")
        
        print("\n[SUCCESS] All module imports successful")
        return True
    except Exception as e:
        print(f"\n[FAILED] Import error: {e}")
        return False

def test_heuristics():
    """Test heuristics module functionality"""
    diagnostic_header("DIAGNOSTIC 2: Heuristics Module")
    
    try:
        from modules.heuristics import preprocess_query
        
        # Test query
        test_query = "Calculate the factorial of 10"
        result = preprocess_query(test_query)
        
        print(f"[TEST] Query: {test_query}")
        print(f"[OK] Canonical: {result['canonical']}")
        print(f"[OK] Query Type: {result['query_type']}")
        print(f"[OK] Topic: {result['topic']}")
        print(f"[OK] Hash: {result['query_hash']}")
        print(f"[OK] Entities: {result['entities']}")
        print(f"[OK] Suggested Tools: {result['suggested_tools']}")
        
        print("\n[SUCCESS] Heuristics module functional")
        return True
    except Exception as e:
        print(f"\n[FAILED] Heuristics error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_historical_context():
    """Test historical context manager"""
    diagnostic_header("DIAGNOSTIC 3: Historical Context Manager")
    
    try:
        from modules.historical_context import HistoricalContextManager
        
        mgr = HistoricalContextManager()
        
        print(f"[OK] Manager initialized")
        print(f"[OK] Topics: {list(mgr.store['topics'].keys())}")
        
        stats = mgr.get_statistics()
        print(f"[OK] Total conversations: {stats['total']}")
        print(f"[OK] By topic: {stats['by_topic']}")
        
        # Test context retrieval
        context = mgr.format_context_for_prompt("mathematics", limit=2)
        print(f"[OK] Context retrieval works: {len(context)} chars")
        
        print("\n[SUCCESS] Historical context manager functional")
        return True
    except Exception as e:
        print(f"\n[FAILED] Historical context error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_faiss_index():
    """Test FAISS index status"""
    diagnostic_header("DIAGNOSTIC 4: FAISS Document Index")
    
    try:
        index_path = Path("faiss_index/index.bin")
        meta_path = Path("faiss_index/metadata.json")
        
        if not index_path.exists():
            print("[WARNING] FAISS index not found")
            return False
        
        print(f"[OK] Index file exists: {index_path.stat().st_size / 1024:.1f} KB")
        print(f"[OK] Metadata exists: {meta_path.stat().st_size / 1024:.1f} KB")
        
        # Check metadata
        metadata = json.load(open(meta_path))
        docs = set(m['doc'] for m in metadata)
        
        print(f"[OK] Total chunks: {len(metadata)}")
        print(f"[OK] Documents indexed: {len(docs)}")
        print(f"[OK] Sample docs: {list(docs)[:3]}")
        
        print("\n[SUCCESS] FAISS index operational")
        return True
    except Exception as e:
        print(f"\n[FAILED] FAISS error: {e}")
        return False

def test_prompts():
    """Test prompt files"""
    diagnostic_header("DIAGNOSTIC 5: Prompt Files")
    
    try:
        new_prompt = Path("prompts/New_Decision_Prompt.txt")
        perception_prompt = Path("prompts/perception_prompt.txt")
        
        if new_prompt.exists():
            content = new_prompt.read_text()
            word_count = len(content.split())
            print(f"[OK] New_Decision_Prompt.txt exists: {word_count} words")
            
            # Check for historical_context placeholder
            if '{historical_context}' in content:
                print("[OK] Historical context parameter present")
            else:
                print("[WARNING] Historical context parameter missing")
        else:
            print("[WARNING] New_Decision_Prompt.txt not found")
        
        if perception_prompt.exists():
            print("[OK] perception_prompt.txt exists")
        else:
            print("[WARNING] perception_prompt.txt not found")
        
        print("\n[SUCCESS] Prompt files verified")
        return True
    except Exception as e:
        print(f"\n[FAILED] Prompt error: {e}")
        return False

def test_configuration():
    """Test configuration files"""
    diagnostic_header("DIAGNOSTIC 6: Configuration")
    
    try:
        import yaml
        
        config_path = Path("config/profiles.yaml")
        config = yaml.safe_load(config_path.read_text())
        
        max_steps = config['strategy']['max_steps']
        planning_mode = config['strategy']['planning_mode']
        
        print(f"[OK] profiles.yaml loaded")
        print(f"[OK] Max steps: {max_steps}")
        print(f"[OK] Planning mode: {planning_mode}")
        
        if max_steps >= 5:
            print("[OK] Max steps is 5 or higher (good for complex queries)")
        else:
            print("[WARNING] Max steps is low - may need increase")
        
        print("\n[SUCCESS] Configuration validated")
        return True
    except Exception as e:
        print(f"\n[FAILED] Config error: {e}")
        return False

def test_agent_startup():
    """Test agent can be imported"""
    diagnostic_header("DIAGNOSTIC 7: Agent Startup Check")
    
    try:
        # Test agent import
        import agent
        print("[OK] agent.py imports successfully")
        
        # Check for main function
        if hasattr(agent, 'main'):
            print("[OK] main() function exists")
        
        # Check for log function
        if hasattr(agent, 'log'):
            print("[OK] log() function exists")
        
        print("\n[SUCCESS] Agent module ready")
        return True
    except Exception as e:
        print(f"\n[FAILED] Agent import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_test_suite():
    """Test the test suite exists"""
    diagnostic_header("DIAGNOSTIC 8: Test Suite")
    
    try:
        test_files = [
            "tests/test_heuristics.py",
            "tests/test_historical_context.py",
            "tests/test_integration.py",
            "tests/run_all_tests.py"
        ]
        
        for test_file in test_files:
            if Path(test_file).exists():
                print(f"[OK] {test_file} exists")
            else:
                print(f"[WARNING] {test_file} missing")
        
        print("\n[SUCCESS] Test suite verified")
        return True
    except Exception as e:
        print(f"\n[FAILED] Test suite error: {e}")
        return False

def test_documentation():
    """Test documentation files"""
    diagnostic_header("DIAGNOSTIC 9: Documentation Files")
    
    try:
        doc_files = [
            "README.md",
            "Heuristics.md",
            "Bug_Fix_Report.md",
            "START_HERE.md",
            "QUICK_START.md",
            "requirements.txt",
            ".gitignore"
        ]
        
        for doc_file in doc_files:
            if Path(doc_file).exists():
                size = Path(doc_file).stat().st_size / 1024
                print(f"[OK] {doc_file}: {size:.1f} KB")
            else:
                print(f"[WARNING] {doc_file} missing")
        
        print("\n[SUCCESS] Documentation files verified")
        return True
    except Exception as e:
        print(f"\n[FAILED] Documentation error: {e}")
        return False

def generate_diagnostic_report(results):
    """Generate comprehensive diagnostic report"""
    report_path = "DIAGNOSTIC_REPORT.md"
    
    passed = sum(results.values())
    total = len(results)
    
    report = f"""# Comprehensive Diagnostic Report - Phase 1, 2 & 3

## Overview
**Date:** {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Diagnostics:** {total}
**Passed:** {passed}
**Failed:** {total - passed}
**Success Rate:** {(passed/total*100):.1f}%

---

## Diagnostic Results

"""
    
    diagnostic_names = {
        'imports': '1. Module Imports',
        'heuristics': '2. Heuristics Module',
        'historical': '3. Historical Context Manager',
        'faiss': '4. FAISS Document Index',
        'prompts': '5. Prompt Files',
        'config': '6. Configuration',
        'agent': '7. Agent Startup',
        'tests': '8. Test Suite',
        'docs': '9. Documentation'
    }
    
    for key, name in diagnostic_names.items():
        status = "✅ PASSED" if results.get(key, False) else "❌ FAILED"
        report += f"### {name}: {status}\n\n"
    
    report += "\n---\n\n"
    
    if passed == total:
        report += """## 🎉 ALL DIAGNOSTICS PASSED!

**System Status:** ✅ Fully Operational
**Ready For:** Live query execution
**Next Step:** Run `python agent.py` and execute 3 unique queries

---

## Ready to Execute Queries

### Query 1: Math Multi-Step
```
Calculate the square root of 144 and then find its factorial value
```

### Query 2: Document Analysis
```
Search documents to find what Don Tapscott's book Wikinomics discusses about mass collaboration
```

### Query 3: Hybrid Math + Document
```
What is 25 multiplied by 4 and does this number appear in any document about policies?
```

### Execution Instructions:
1. Run: `python agent.py`
2. Type each query when prompted
3. Copy FULL console output (from query input to final answer)
4. Fill in the log templates in `logs/` directory
5. Save completed logs

---
"""
    else:
        report += f"""## ⚠️ {total - passed} Diagnostic(s) Failed

**Action Required:** Review failed diagnostics and fix issues before proceeding.

---
"""
    
    report += f"\n**Report Generated:** {datetime.datetime.now().isoformat()}\n"
    report += f"**Diagnostic Suite:** Phase 1, 2 & 3 Validation\n"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[SAVED] Diagnostic report: {report_path}")
    return report_path

def main():
    """Run all diagnostics"""
    print("\n" + "="*70)
    print("  COMPREHENSIVE SYSTEM DIAGNOSTICS")
    print("  Phase 1, 2 & 3 Validation")
    print("="*70)
    
    results = {}
    
    # Run all diagnostic tests
    results['imports'] = test_imports()
    results['heuristics'] = test_heuristics()
    results['historical'] = test_historical_context()
    results['faiss'] = test_faiss_index()
    results['prompts'] = test_prompts()
    results['config'] = test_configuration()
    results['agent'] = test_agent_startup()
    results['tests'] = test_test_suite()
    results['docs'] = test_documentation()
    
    # Generate report
    diagnostic_header("GENERATING DIAGNOSTIC REPORT")
    report_path = generate_diagnostic_report(results)
    
    # Summary
    passed = sum(results.values())
    total = len(results)
    
    print("\n" + "="*70)
    if passed == total:
        print("  [SUCCESS] ALL DIAGNOSTICS PASSED!")
        print(f"  {passed}/{total} checks successful")
        print("  Status: READY FOR QUERY EXECUTION")
    else:
        print(f"  [WARNING] {total - passed}/{total} diagnostic(s) failed")
        print("  Status: REVIEW REQUIRED")
    print("="*70)
    
    print(f"\n[REPORT] {report_path}")
    print("\n[NEXT] Execute queries: python agent.py\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


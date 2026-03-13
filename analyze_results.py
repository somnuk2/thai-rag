#!/usr/bin/env python
"""Analyze comprehensive test results"""

import json
import statistics

# Load results
with open('test_results/dual_mode_test_20260312_202855.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("\n" + "="*70)
print("📊 COMPREHENSIVE TEST ANALYSIS (100 Questions)")
print("="*70)

for mode in ['supabase', 'local']:
    results = data[mode]
    tests = results['tests']
    scores = [t['similarity_score'] for t in tests]
    
    print(f"\n🔍 {mode.upper()} Mode:")
    print(f"   Tests: {len(tests)}/100")
    print(f"   \u2713 Passed: {len([t for t in tests if 'error' not in t])}/100")
    
    print(f"\n   📈 Similarity Scores:")
    print(f"      Average:  {statistics.mean(scores):.4f}")
    print(f"      Median:   {statistics.median(scores):.4f}")
    print(f"      Std Dev:  {statistics.stdev(scores):.4f}")
    print(f"      Min:      {min(scores):.4f}")
    print(f"      Max:      {max(scores):.4f}")
    
    # Score distribution
    ranges = {
        'Excellent (0.85-1.00)': len([s for s in scores if s >= 0.85]),
        'Good (0.70-0.85)': len([s for s in scores if 0.70 <= s < 0.85]),
        'Fair (0.50-0.70)': len([s for s in scores if 0.50 <= s < 0.70]),
        'Poor (<0.50)': len([s for s in scores if s < 0.50]),
    }
    
    print(f"\n   📊 Score Distribution:")
    for range_name, count in ranges.items():
        pct = (count / len(scores)) * 100
        print(f"      {range_name}: {count:3d} ({pct:5.1f}%)")

print(f"\n{'='*70}")
print("📋 Comparison:")
print(f"   Supabase: {data['supabase']['average_similarity']:.4f}")
print(f"   Local:    {data['local']['average_similarity']:.4f}")
print(f"   Diff:     {abs(data['supabase']['average_similarity'] - data['local']['average_similarity']):.4f}")
print(f"{'='*70}\n")

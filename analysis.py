"""
Statistical Analysis Module for A/B Testing
Performs hypothesis testing, confidence intervals, and ship/no-ship decision logic
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Tuple


class ABTestAnalyzer:
    """
    Performs rigorous statistical analysis for A/B test experiments.
    
    Implements Microsoft's standard approach to experimentation:
    - Clear hypothesis formulation
    - Appropriate statistical tests (t-test for continuous, z-test for proportions)
    - Confidence intervals for effect size
    - Evidence-based decision recommendations
    """
    
    def __init__(self, alpha: float = 0.05):
        """
        Initialize analyzer with significance level.
        
        Args:
            alpha: Significance level (typically 0.05 for 95% confidence)
        """
        self.alpha = alpha
        self.confidence_level = 1 - alpha
    
    def analyze_engagement_metric(
        self, 
        control_data: np.ndarray, 
        treatment_data: np.ndarray
    ) -> Dict:
        """
        Analyze continuous engagement metric using independent t-test.
        
        Why t-test?
        - Engagement (actions per user) is a continuous metric
        - We're comparing means of two independent groups
        - With large samples (n > 30), t-test is robust to normality violations
        
        Args:
            control_data: Engagement values for control group
            treatment_data: Engagement values for treatment group
            
        Returns:
            Dictionary with test results and metrics
        """
        # Sample statistics
        control_mean = np.mean(control_data)
        treatment_mean = np.mean(treatment_data)
        control_std = np.std(control_data, ddof=1)
        treatment_std = np.std(treatment_data, ddof=1)
        control_n = len(control_data)
        treatment_n = len(treatment_data)
        
        # Perform independent t-test (two-tailed)
        t_stat, p_value = stats.ttest_ind(treatment_data, control_data)
        
        # Calculate absolute and relative uplift
        absolute_diff = treatment_mean - control_mean
        relative_diff_pct = (absolute_diff / control_mean) * 100
        
        # Confidence interval for difference in means
        # Using pooled standard error
        pooled_se = np.sqrt(
            (control_std**2 / control_n) + (treatment_std**2 / treatment_n)
        )
        degrees_of_freedom = control_n + treatment_n - 2
        t_critical = stats.t.ppf(1 - self.alpha/2, degrees_of_freedom)
        
        ci_lower = absolute_diff - t_critical * pooled_se
        ci_upper = absolute_diff + t_critical * pooled_se
        
        # Statistical significance
        is_significant = p_value < self.alpha
        
        return {
            'metric_name': 'Engagement (Actions per User)',
            'control_mean': control_mean,
            'treatment_mean': treatment_mean,
            'control_std': control_std,
            'treatment_std': treatment_std,
            'control_n': control_n,
            'treatment_n': treatment_n,
            'absolute_diff': absolute_diff,
            'relative_diff_pct': relative_diff_pct,
            't_statistic': t_stat,
            'p_value': p_value,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'confidence_level': self.confidence_level,
            'is_significant': is_significant,
            'test_type': 'Independent t-test'
        }
    
    def analyze_retention_metric(
        self, 
        control_data: np.ndarray, 
        treatment_data: np.ndarray
    ) -> Dict:
        """
        Analyze binary retention metric using z-test for proportions.
        
        Why z-test for proportions?
        - Retention is a binary outcome (retained=1, churned=0)
        - We're comparing proportions (rates) between two groups
        - With large samples, normal approximation is valid
        
        Args:
            control_data: Binary retention flags for control group
            treatment_data: Binary retention flags for treatment group
            
        Returns:
            Dictionary with test results and metrics
        """
        # Sample statistics
        control_n = len(control_data)
        treatment_n = len(treatment_data)
        control_retained = np.sum(control_data)
        treatment_retained = np.sum(treatment_data)
        control_rate = control_retained / control_n
        treatment_rate = treatment_retained / treatment_n
        
        # Pooled proportion for z-test
        pooled_proportion = (control_retained + treatment_retained) / (control_n + treatment_n)
        pooled_se = np.sqrt(
            pooled_proportion * (1 - pooled_proportion) * (1/control_n + 1/treatment_n)
        )
        
        # Z-test statistic
        z_stat = (treatment_rate - control_rate) / pooled_se
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))  # Two-tailed
        
        # Absolute and relative uplift
        absolute_diff = treatment_rate - control_rate
        relative_diff_pct = (absolute_diff / control_rate) * 100
        
        # Confidence interval using normal approximation
        se_diff = np.sqrt(
            (control_rate * (1 - control_rate) / control_n) + 
            (treatment_rate * (1 - treatment_rate) / treatment_n)
        )
        z_critical = stats.norm.ppf(1 - self.alpha/2)
        
        ci_lower = absolute_diff - z_critical * se_diff
        ci_upper = absolute_diff + z_critical * se_diff
        
        # Statistical significance
        is_significant = p_value < self.alpha
        
        return {
            'metric_name': '7-Day Retention Rate',
            'control_rate': control_rate,
            'treatment_rate': treatment_rate,
            'control_n': control_n,
            'treatment_n': treatment_n,
            'control_retained': int(control_retained),
            'treatment_retained': int(treatment_retained),
            'absolute_diff': absolute_diff,
            'relative_diff_pct': relative_diff_pct,
            'z_statistic': z_stat,
            'p_value': p_value,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'confidence_level': self.confidence_level,
            'is_significant': is_significant,
            'test_type': 'Two-proportion z-test'
        }
    
    def make_ship_decision(
        self, 
        engagement_results: Dict, 
        retention_results: Dict,
        min_engagement_uplift: float = 3.0,
        min_retention_uplift: float = 2.0
    ) -> Dict:
        """
        Make ship/no-ship decision based on statistical evidence and business thresholds.
        
        Decision criteria (Microsoft standard practice):
        1. Statistical significance (p < 0.05)
        2. Practical significance (meets minimum uplift thresholds)
        3. Consistent positive results across key metrics
        4. Confidence interval doesn't include negative effects
        
        Args:
            engagement_results: Results from engagement analysis
            retention_results: Results from retention analysis
            min_engagement_uplift: Minimum acceptable engagement uplift (%)
            min_retention_uplift: Minimum acceptable retention uplift (%)
            
        Returns:
            Dictionary with decision and reasoning
        """
        # Check each metric
        engagement_pass = (
            engagement_results['is_significant'] and 
            engagement_results['relative_diff_pct'] >= min_engagement_uplift and
            engagement_results['ci_lower'] > 0
        )
        
        retention_pass = (
            retention_results['is_significant'] and 
            retention_results['relative_diff_pct'] >= min_retention_uplift and
            retention_results['ci_lower'] > 0
        )
        
        # Decision logic
        if engagement_pass and retention_pass:
            decision = "SHIP"
            confidence = "High"
            reasoning = (
                f"Strong evidence to ship the feature:\n"
                f"• Engagement: +{engagement_results['relative_diff_pct']:.2f}% "
                f"(p={engagement_results['p_value']:.4f})\n"
                f"• Retention: +{retention_results['relative_diff_pct']:.2f}% "
                f"(p={retention_results['p_value']:.4f})\n"
                f"Both metrics show statistically significant improvements "
                f"above minimum thresholds with positive confidence intervals."
            )
        elif engagement_pass or retention_pass:
            decision = "SHIP WITH CAUTION"
            confidence = "Medium"
            passing_metric = "Engagement" if engagement_pass else "Retention"
            failing_metric = "Retention" if engagement_pass else "Engagement"
            reasoning = (
                f"Mixed evidence:\n"
                f"• {passing_metric} shows significant positive impact\n"
                f"• {failing_metric} does not meet ship criteria\n"
                f"Consider shipping with close monitoring or further testing."
            )
        else:
            decision = "DO NOT SHIP"
            confidence = "High"
            reasons = []
            
            if not engagement_results['is_significant']:
                reasons.append(f"Engagement uplift not statistically significant (p={engagement_results['p_value']:.4f})")
            elif engagement_results['relative_diff_pct'] < min_engagement_uplift:
                reasons.append(f"Engagement uplift below minimum threshold ({engagement_results['relative_diff_pct']:.2f}% < {min_engagement_uplift}%)")
            
            if not retention_results['is_significant']:
                reasons.append(f"Retention uplift not statistically significant (p={retention_results['p_value']:.4f})")
            elif retention_results['relative_diff_pct'] < min_retention_uplift:
                reasons.append(f"Retention uplift below minimum threshold ({retention_results['relative_diff_pct']:.2f}% < {min_retention_uplift}%)")
            
            reasoning = "Insufficient evidence to ship:\n" + "\n".join(f"• {r}" for r in reasons)
        
        return {
            'decision': decision,
            'confidence': confidence,
            'reasoning': reasoning,
            'engagement_pass': engagement_pass,
            'retention_pass': retention_pass,
            'min_engagement_threshold': min_engagement_uplift,
            'min_retention_threshold': min_retention_uplift
        }
    
    def run_full_analysis(self, df: pd.DataFrame) -> Dict:
        """
        Run complete A/B test analysis pipeline.
        
        Args:
            df: Experiment DataFrame with columns: user_id, variant, engagement, retained_7d
            
        Returns:
            Dictionary with complete analysis results
        """
        # Split data by variant
        control = df[df['variant'] == 'control']
        treatment = df[df['variant'] == 'treatment']
        
        # Analyze metrics
        engagement_results = self.analyze_engagement_metric(
            control['engagement'].values,
            treatment['engagement'].values
        )
        
        retention_results = self.analyze_retention_metric(
            control['retained_7d'].values,
            treatment['retained_7d'].values
        )
        
        # Make decision
        decision = self.make_ship_decision(engagement_results, retention_results)
        
        return {
            'engagement': engagement_results,
            'retention': retention_results,
            'decision': decision
        }


if __name__ == "__main__":
    # Test the analyzer with sample data
    from data_simulation import generate_data
    
    print("Running A/B Test Analysis...")
    data = generate_data()
    
    analyzer = ABTestAnalyzer(alpha=0.05)
    results = analyzer.run_full_analysis(data)
    
    print("\n=== ENGAGEMENT RESULTS ===")
    eng = results['engagement']
    print(f"Control: {eng['control_mean']:.2f} ± {eng['control_std']:.2f}")
    print(f"Treatment: {eng['treatment_mean']:.2f} ± {eng['treatment_std']:.2f}")
    print(f"Uplift: {eng['relative_diff_pct']:.2f}%")
    print(f"P-value: {eng['p_value']:.4f}")
    print(f"Significant: {eng['is_significant']}")
    
    print("\n=== RETENTION RESULTS ===")
    ret = results['retention']
    print(f"Control: {ret['control_rate']:.2%}")
    print(f"Treatment: {ret['treatment_rate']:.2%}")
    print(f"Uplift: {ret['relative_diff_pct']:.2f}%")
    print(f"P-value: {ret['p_value']:.4f}")
    print(f"Significant: {ret['is_significant']}")
    
    print("\n=== DECISION ===")
    print(f"Decision: {results['decision']['decision']}")
    print(f"Confidence: {results['decision']['confidence']}")
    print(f"\n{results['decision']['reasoning']}")

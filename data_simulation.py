"""
Data Simulation Module for A/B Testing Experiment
Generates realistic user-level data for "Smart Reminder" feature testing
"""

import numpy as np
import pandas as pd
from typing import Tuple


class ExperimentDataSimulator:
    """
    Simulates user-level experimentation data with realistic variance and measurable uplift.
    
    Mimics production A/B testing scenarios at Microsoft where:
    - Users are randomly assigned to control or treatment groups
    - Treatment group shows measurable but noisy improvement
    - Natural variance exists across user behavior
    """
    
    def __init__(self, n_users: int = 50000, random_seed: int = 42):
        """
        Initialize the data simulator.
        
        Args:
            n_users: Total number of users in the experiment
            random_seed: Seed for reproducibility
        """
        self.n_users = n_users
        self.random_seed = random_seed
        np.random.seed(random_seed)
    
    def generate_experiment_data(
        self, 
        control_engagement_mean: float = 12.5,
        control_engagement_std: float = 4.2,
        treatment_uplift_pct: float = 10.0,
        control_retention_rate: float = 0.35,
        treatment_retention_uplift_pct: float = 8.0
    ) -> pd.DataFrame:
        """
        Generate realistic user-level experiment data.
        
        Args:
            control_engagement_mean: Average daily actions for control group
            control_engagement_std: Standard deviation of engagement
            treatment_uplift_pct: Expected percentage uplift in treatment engagement
            control_retention_rate: 7-day retention rate for control group
            treatment_retention_uplift_pct: Retention rate uplift percentage
            
        Returns:
            DataFrame with user-level experiment data
        """
        # Ensure 50/50 split for proper A/B testing
        n_control = self.n_users // 2
        n_treatment = self.n_users - n_control
        
        # Generate user IDs
        user_ids = [f"user_{i:06d}" for i in range(self.n_users)]
        
        # Random assignment to variants (50/50 split)
        variants = ['control'] * n_control + ['treatment'] * n_treatment
        np.random.shuffle(variants)
        
        # Generate engagement metric (daily actions/clicks)
        # Control group: baseline behavior
        control_engagement = np.random.normal(
            control_engagement_mean, 
            control_engagement_std, 
            n_control
        )
        control_engagement = np.maximum(control_engagement, 0)  # No negative actions
        
        # Treatment group: higher mean due to feature impact
        treatment_mean = control_engagement_mean * (1 + treatment_uplift_pct / 100)
        treatment_engagement = np.random.normal(
            treatment_mean,
            control_engagement_std * 1.05,  # Slightly higher variance
            n_treatment
        )
        treatment_engagement = np.maximum(treatment_engagement, 0)
        
        # Combine and shuffle to match variant order
        engagement_dict = {
            'control': control_engagement,
            'treatment': treatment_engagement
        }
        engagement = [
            engagement_dict['control'][sum(1 for v in variants[:i] if v == 'control')] 
            if variants[i] == 'control' 
            else engagement_dict['treatment'][sum(1 for v in variants[:i] if v == 'treatment')]
            for i in range(self.n_users)
        ]
        
        # Generate retention flags (7-day retention)
        # Using logistic-like probability model
        treatment_retention_rate = control_retention_rate * (1 + treatment_retention_uplift_pct / 100)
        
        retention = []
        for i, variant in enumerate(variants):
            if variant == 'control':
                # Add some correlation with engagement
                base_prob = control_retention_rate
                engagement_boost = min(0.1, (engagement[i] - control_engagement_mean) / 100)
                prob = np.clip(base_prob + engagement_boost, 0, 1)
            else:
                base_prob = treatment_retention_rate
                engagement_boost = min(0.1, (engagement[i] - treatment_mean) / 100)
                prob = np.clip(base_prob + engagement_boost, 0, 1)
            
            retention.append(1 if np.random.random() < prob else 0)
        
        # Create DataFrame
        df = pd.DataFrame({
            'user_id': user_ids,
            'variant': variants,
            'engagement': np.round(engagement, 2),
            'retained_7d': retention
        })
        
        return df
    
    def get_experiment_summary(self, df: pd.DataFrame) -> dict:
        """
        Generate summary statistics for the experiment.
        
        Args:
            df: Experiment data DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_users': len(df),
            'control_users': len(df[df['variant'] == 'control']),
            'treatment_users': len(df[df['variant'] == 'treatment']),
            'control_avg_engagement': df[df['variant'] == 'control']['engagement'].mean(),
            'treatment_avg_engagement': df[df['variant'] == 'treatment']['engagement'].mean(),
            'control_retention_rate': df[df['variant'] == 'control']['retained_7d'].mean(),
            'treatment_retention_rate': df[df['variant'] == 'treatment']['retained_7d'].mean(),
        }
        
        return summary


def generate_data() -> pd.DataFrame:
    """
    Convenience function to generate experiment data with default parameters.
    
    Returns:
        DataFrame with simulated experiment data
    """
    simulator = ExperimentDataSimulator(n_users=50000)
    return simulator.generate_experiment_data()


if __name__ == "__main__":
    # Test the simulator
    simulator = ExperimentDataSimulator(n_users=50000)
    data = simulator.generate_experiment_data()
    
    print("Experiment Data Sample:")
    print(data.head(10))
    print("\nData Shape:", data.shape)
    print("\nData Types:")
    print(data.dtypes)
    print("\nSummary Statistics:")
    summary = simulator.get_experiment_summary(data)
    for key, value in summary.items():
        print(f"{key}: {value}")

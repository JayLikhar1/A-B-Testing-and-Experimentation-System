"""
Streamlit Dashboard for A/B Testing & Experimentation System
Production-quality dashboard for Microsoft-style experiment analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from data_simulation import ExperimentDataSimulator
from analysis import ABTestAnalyzer


# Page configuration
st.set_page_config(
    page_title="A/B Testing & Experimentation System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0078D4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #505050;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F3F2F1;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #0078D4;
    }
    .ship-decision {
        font-size: 1.5rem;
        font-weight: 700;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        margin: 2rem 0;
    }
    .ship-yes {
        background-color: #DFF6DD;
        color: #107C10;
        border: 2px solid #107C10;
    }
    .ship-no {
        background-color: #FDE7E9;
        color: #A80000;
        border: 2px solid #A80000;
    }
    .ship-caution {
        background-color: #FFF4CE;
        color: #8A6D3B;
        border: 2px solid #F9A825;
    }
    </style>
    """, unsafe_allow_html=True)


def create_distribution_plot(control_data, treatment_data, metric_name):
    """Create overlapping distribution plots for control vs treatment."""
    fig = go.Figure()
    
    # Control distribution
    fig.add_trace(go.Histogram(
        x=control_data,
        name='Control',
        opacity=0.7,
        marker_color='#605E5C',
        nbinsx=50,
        histnorm='probability density'
    ))
    
    # Treatment distribution
    fig.add_trace(go.Histogram(
        x=treatment_data,
        name='Treatment',
        opacity=0.7,
        marker_color='#0078D4',
        nbinsx=50,
        histnorm='probability density'
    ))
    
    fig.update_layout(
        title=f'{metric_name} Distribution: Control vs Treatment',
        xaxis_title=metric_name,
        yaxis_title='Density',
        barmode='overlay',
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(x=0.7, y=0.95)
    )
    
    return fig


def create_comparison_bar_chart(control_value, treatment_value, metric_name, is_percentage=False):
    """Create bar chart comparing control vs treatment."""
    fig = go.Figure()
    
    format_str = '.2%' if is_percentage else '.2f'
    
    fig.add_trace(go.Bar(
        x=['Control', 'Treatment'],
        y=[control_value, treatment_value],
        marker_color=['#605E5C', '#0078D4'],
        text=[f'{control_value:{format_str}}', f'{treatment_value:{format_str}}'],
        textposition='outside',
    ))
    
    fig.update_layout(
        title=f'{metric_name}: Control vs Treatment',
        yaxis_title=metric_name,
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig


def create_confidence_interval_plot(results, metric_name):
    """Create confidence interval visualization."""
    fig = go.Figure()
    
    ci_lower = results['ci_lower']
    ci_upper = results['ci_upper']
    point_estimate = results['absolute_diff']
    
    # Add confidence interval as error bar
    fig.add_trace(go.Scatter(
        x=[point_estimate],
        y=[metric_name],
        error_x=dict(
            type='data',
            symmetric=False,
            array=[ci_upper - point_estimate],
            arrayminus=[point_estimate - ci_lower],
            color='#0078D4',
            thickness=3,
            width=10
        ),
        mode='markers',
        marker=dict(size=12, color='#0078D4'),
        name='Point Estimate'
    ))
    
    # Add vertical line at zero
    fig.add_vline(x=0, line_dash="dash", line_color="red", opacity=0.5)
    
    fig.update_layout(
        title=f'{metric_name} - {results["confidence_level"]*100:.0f}% Confidence Interval',
        xaxis_title='Effect Size',
        template='plotly_white',
        height=250,
        showlegend=False,
        yaxis=dict(showticklabels=False)
    )
    
    return fig


def main():
    # Header
    st.markdown('<div class="main-header">📊 A/B Testing & Experimentation System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Production-Quality Experiment Analysis for "Smart Reminder" Feature</div>', unsafe_allow_html=True)
    
    # Sidebar for experiment configuration
    st.sidebar.title("⚙️ Experiment Configuration")
    
    # Simulation parameters
    st.sidebar.subheader("Data Simulation")
    n_users = st.sidebar.slider("Number of Users", 10000, 100000, 50000, 5000)
    treatment_uplift = st.sidebar.slider("Expected Engagement Uplift (%)", 0.0, 20.0, 10.0, 0.5)
    retention_uplift = st.sidebar.slider("Expected Retention Uplift (%)", 0.0, 15.0, 8.0, 0.5)
    
    # Analysis parameters
    st.sidebar.subheader("Analysis Parameters")
    alpha = st.sidebar.select_slider("Significance Level (α)", options=[0.01, 0.05, 0.10], value=0.05)
    min_eng_threshold = st.sidebar.slider("Min Engagement Uplift for Ship (%)", 0.0, 10.0, 3.0, 0.5)
    min_ret_threshold = st.sidebar.slider("Min Retention Uplift for Ship (%)", 0.0, 10.0, 2.0, 0.5)
    
    # Generate data button
    if st.sidebar.button("🔄 Generate New Experiment", type="primary"):
        st.session_state.clear()
    
    # Generate or load data
    if 'experiment_data' not in st.session_state:
        with st.spinner("Generating experiment data..."):
            simulator = ExperimentDataSimulator(n_users=n_users)
            st.session_state.experiment_data = simulator.generate_experiment_data(
                treatment_uplift_pct=treatment_uplift,
                treatment_retention_uplift_pct=retention_uplift
            )
            st.session_state.summary = simulator.get_experiment_summary(st.session_state.experiment_data)
    
    data = st.session_state.experiment_data
    summary = st.session_state.summary
    
    # Run analysis
    if 'analysis_results' not in st.session_state:
        with st.spinner("Running statistical analysis..."):
            analyzer = ABTestAnalyzer(alpha=alpha)
            st.session_state.analysis_results = analyzer.run_full_analysis(data)
    
    results = st.session_state.analysis_results
    
    # Recompute decision with new thresholds
    analyzer = ABTestAnalyzer(alpha=alpha)
    decision = analyzer.make_ship_decision(
        results['engagement'],
        results['retention'],
        min_engagement_uplift=min_eng_threshold,
        min_retention_uplift=min_ret_threshold
    )
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Problem Statement",
        "🔬 Experiment Setup",
        "📊 Results & Metrics",
        "📈 Statistical Analysis",
        "✅ Decision & Recommendation"
    ])
    
    # TAB 1: Problem Statement
    with tab1:
        st.header("Problem Statement")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### Business Context
            We are testing a new feature called **"Smart Reminder"** in our productivity application. 
            This feature proactively reminds users about pending tasks and upcoming deadlines using 
            intelligent timing and personalized notifications.
            
            ### Research Question
            **Does the Smart Reminder feature significantly improve user engagement and retention?**
            
            ### Hypothesis
            
            **Business Hypothesis:**
            - The Smart Reminder feature will increase daily user engagement and improve 7-day retention 
              by helping users stay on top of their tasks more effectively.
            
            **Statistical Hypotheses:**
            
            **For Engagement (Actions per User):**
            - **H₀ (Null):** μ_treatment = μ_control (No difference in average engagement)
            - **H₁ (Alternative):** μ_treatment > μ_control (Treatment has higher engagement)
            
            **For Retention (7-Day Rate):**
            - **H₀ (Null):** p_treatment = p_control (No difference in retention rates)
            - **H₁ (Alternative):** p_treatment > p_control (Treatment has higher retention)
            
            ### Success Metrics
            
            1. **Primary Metric:** Average daily engagement (actions/clicks per user)
            2. **Secondary Metric:** 7-day retention rate
            3. **Statistical Threshold:** p < 0.05 (95% confidence)
            4. **Business Threshold:** Minimum uplift requirements set in configuration
            """)
        
        with col2:
            st.info("""
            **Why These Metrics?**
            
            📊 **Engagement** measures immediate feature impact on user behavior.
            
            🔄 **Retention** captures long-term value and habit formation.
            
            Together, they provide a comprehensive view of feature success.
            """)
            
            st.success("""
            **Experiment Design**
            
            ✅ Randomized assignment
            
            ✅ 50/50 split
            
            ✅ Large sample size
            
            ✅ Appropriate statistical tests
            """)
    
    # TAB 2: Experiment Setup
    with tab2:
        st.header("Experiment Setup & Data")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Users", f"{summary['total_users']:,}")
        col2.metric("Control Users", f"{summary['control_users']:,}")
        col3.metric("Treatment Users", f"{summary['treatment_users']:,}")
        col4.metric("Significance Level", f"{alpha}")
        
        st.subheader("Sample Data")
        st.dataframe(data.head(20), use_container_width=True)
        
        st.subheader("Data Summary Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Control Group**")
            control_stats = data[data['variant'] == 'control']['engagement'].describe()
            st.dataframe(control_stats, use_container_width=True)
        
        with col2:
            st.markdown("**Treatment Group**")
            treatment_stats = data[data['variant'] == 'treatment']['engagement'].describe()
            st.dataframe(treatment_stats, use_container_width=True)
        
        # Download data
        csv = data.to_csv(index=False)
        st.download_button(
            label="📥 Download Experiment Data (CSV)",
            data=csv,
            file_name="ab_test_experiment_data.csv",
            mime="text/csv"
        )
    
    # TAB 3: Results & Metrics
    with tab3:
        st.header("Results & Metric Comparison")
        
        # Engagement metrics
        st.subheader("📊 Engagement Metric")
        
        col1, col2, col3 = st.columns(3)
        eng = results['engagement']
        col1.metric(
            "Control Avg",
            f"{eng['control_mean']:.2f}",
            help="Average daily actions per user in control group"
        )
        col2.metric(
            "Treatment Avg",
            f"{eng['treatment_mean']:.2f}",
            delta=f"{eng['relative_diff_pct']:.2f}%",
            help="Average daily actions per user in treatment group"
        )
        col3.metric(
            "Absolute Uplift",
            f"+{eng['absolute_diff']:.2f}",
            help="Absolute difference in actions per user"
        )
        
        # Engagement visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = create_distribution_plot(
                data[data['variant'] == 'control']['engagement'],
                data[data['variant'] == 'treatment']['engagement'],
                'Engagement (Actions per User)'
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = create_comparison_bar_chart(
                eng['control_mean'],
                eng['treatment_mean'],
                'Average Engagement'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        st.divider()
        
        # Retention metrics
        st.subheader("🔄 Retention Metric")
        
        col1, col2, col3 = st.columns(3)
        ret = results['retention']
        col1.metric(
            "Control Rate",
            f"{ret['control_rate']:.2%}",
            help="7-day retention rate in control group"
        )
        col2.metric(
            "Treatment Rate",
            f"{ret['treatment_rate']:.2%}",
            delta=f"{ret['relative_diff_pct']:.2f}%",
            help="7-day retention rate in treatment group"
        )
        col3.metric(
            "Absolute Uplift",
            f"+{ret['absolute_diff']:.2%}",
            help="Absolute difference in retention rate"
        )
        
        # Retention visualization
        fig3 = create_comparison_bar_chart(
            ret['control_rate'],
            ret['treatment_rate'],
            '7-Day Retention Rate',
            is_percentage=True
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    # TAB 4: Statistical Analysis
    with tab4:
        st.header("Statistical Analysis")
        
        # Engagement analysis
        st.subheader("📊 Engagement Statistical Test")
        
        eng = results['engagement']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            **Test Used:** {eng['test_type']}
            
            **Why Independent t-test?**
            - Engagement is a continuous metric (actions per user)
            - We're comparing means of two independent groups
            - With large sample sizes (n > 30), the t-test is robust to violations of normality
            - Appropriate for detecting differences in central tendency
            
            **Results:**
            - **t-statistic:** {eng['t_statistic']:.4f}
            - **p-value:** {eng['p_value']:.6f}
            - **Degrees of freedom:** {eng['control_n'] + eng['treatment_n'] - 2}
            - **Statistical significance:** {'✅ Yes' if eng['is_significant'] else '❌ No'} (α = {alpha})
            """)
        
        with col2:
            if eng['is_significant']:
                st.success(f"""
                **Statistically Significant**
                
                p-value ({eng['p_value']:.6f}) < α ({alpha})
                
                We reject H₀ and conclude there is significant evidence that treatment 
                has different engagement than control.
                """)
            else:
                st.warning(f"""
                **Not Statistically Significant**
                
                p-value ({eng['p_value']:.6f}) ≥ α ({alpha})
                
                We fail to reject H₀. Insufficient evidence of a difference.
                """)
        
        # Confidence interval
        fig_ci_eng = create_confidence_interval_plot(eng, 'Engagement Difference')
        st.plotly_chart(fig_ci_eng, use_container_width=True)
        
        st.markdown(f"""
        **{eng['confidence_level']*100:.0f}% Confidence Interval:** [{eng['ci_lower']:.3f}, {eng['ci_upper']:.3f}]
        
        We are {eng['confidence_level']*100:.0f}% confident that the true difference in engagement between 
        treatment and control falls within this interval.
        """)
        
        st.divider()
        
        # Retention analysis
        st.subheader("🔄 Retention Statistical Test")
        
        ret = results['retention']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            **Test Used:** {ret['test_type']}
            
            **Why z-test for proportions?**
            - Retention is a binary outcome (retained=1, churned=0)
            - We're comparing proportions (rates) between two independent groups
            - With large samples, the normal approximation to the binomial is valid
            - Standard approach for A/B tests with conversion-type metrics
            
            **Results:**
            - **z-statistic:** {ret['z_statistic']:.4f}
            - **p-value:** {ret['p_value']:.6f}
            - **Statistical significance:** {'✅ Yes' if ret['is_significant'] else '❌ No'} (α = {alpha})
            """)
        
        with col2:
            if ret['is_significant']:
                st.success(f"""
                **Statistically Significant**
                
                p-value ({ret['p_value']:.6f}) < α ({alpha})
                
                We reject H₀ and conclude there is significant evidence that treatment 
                has different retention than control.
                """)
            else:
                st.warning(f"""
                **Not Statistically Significant**
                
                p-value ({ret['p_value']:.6f}) ≥ α ({alpha})
                
                We fail to reject H₀. Insufficient evidence of a difference.
                """)
        
        # Confidence interval
        fig_ci_ret = create_confidence_interval_plot(ret, 'Retention Difference')
        st.plotly_chart(fig_ci_ret, use_container_width=True)
        
        st.markdown(f"""
        **{ret['confidence_level']*100:.0f}% Confidence Interval:** [{ret['ci_lower']:.4f}, {ret['ci_upper']:.4f}]
        
        We are {ret['confidence_level']*100:.0f}% confident that the true difference in retention rate between 
        treatment and control falls within this interval.
        """)
    
    # TAB 5: Decision & Recommendation
    with tab5:
        st.header("Ship Decision & Recommendation")
        
        # Decision display
        if decision['decision'] == "SHIP":
            decision_class = "ship-yes"
            emoji = "✅"
        elif decision['decision'] == "DO NOT SHIP":
            decision_class = "ship-no"
            emoji = "❌"
        else:
            decision_class = "ship-caution"
            emoji = "⚠️"
        
        st.markdown(
            f'<div class="ship-decision {decision_class}">{emoji} {decision["decision"]}</div>',
            unsafe_allow_html=True
        )
        
        st.markdown(f"**Confidence Level:** {decision['confidence']}")
        
        st.subheader("Decision Reasoning")
        st.info(decision['reasoning'])
        
        # Decision criteria breakdown
        st.subheader("Decision Criteria Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Engagement Metric**")
            criteria_eng = {
                "Statistical Significance": "✅ Pass" if eng['is_significant'] else "❌ Fail",
                f"Meets Min Uplift ({min_eng_threshold}%)": "✅ Pass" if eng['relative_diff_pct'] >= min_eng_threshold else "❌ Fail",
                "Positive Confidence Interval": "✅ Pass" if eng['ci_lower'] > 0 else "❌ Fail",
                "Overall": "✅ Pass" if decision['engagement_pass'] else "❌ Fail"
            }
            for criterion, status in criteria_eng.items():
                st.markdown(f"- {criterion}: **{status}**")
        
        with col2:
            st.markdown("**Retention Metric**")
            criteria_ret = {
                "Statistical Significance": "✅ Pass" if ret['is_significant'] else "❌ Fail",
                f"Meets Min Uplift ({min_ret_threshold}%)": "✅ Pass" if ret['relative_diff_pct'] >= min_ret_threshold else "❌ Fail",
                "Positive Confidence Interval": "✅ Pass" if ret['ci_lower'] > 0 else "❌ Fail",
                "Overall": "✅ Pass" if decision['retention_pass'] else "❌ Fail"
            }
            for criterion, status in criteria_ret.items():
                st.markdown(f"- {criterion}: **{status}**")
        
        st.divider()
        
        # Recommendations and next steps
        st.subheader("Next Steps & Recommendations")
        
        if decision['decision'] == "SHIP":
            st.success("""
            **Recommended Actions:**
            1. ✅ Proceed with full rollout of Smart Reminder feature
            2. 📊 Set up monitoring dashboards for post-launch metrics
            3. 🎯 Define success metrics for 30-day, 60-day, 90-day checkpoints
            4. 📝 Document learnings for future experiments
            5. 🔄 Plan follow-up experiments for feature optimization
            """)
        elif decision['decision'] == "DO NOT SHIP":
            st.error("""
            **Recommended Actions:**
            1. ❌ Do not ship the feature in its current form
            2. 🔍 Conduct user research to understand why the feature didn't perform
            3. 🛠️ Iterate on the feature design based on findings
            4. 🧪 Run additional experiments with refined version
            5. 📊 Consider alternative features or approaches
            """)
        else:
            st.warning("""
            **Recommended Actions:**
            1. ⚠️ Consider partial rollout (e.g., 10-20% of users) with close monitoring
            2. 📊 Set up real-time dashboards to catch any issues early
            3. 🔍 Conduct qualitative research to understand mixed signals
            4. 🧪 Plan follow-up experiments to confirm results
            5. 📝 Establish clear rollback criteria
            """)
        
        st.divider()
        
        # Limitations and considerations
        st.subheader("Limitations & Considerations")
        st.markdown("""
        **Study Limitations:**
        - Experiment duration may not capture long-term behavior changes
        - External factors (seasonality, marketing campaigns) not controlled for
        - Single experiment; replication would strengthen conclusions
        - Assumes stable user population (no composition changes)
        
        **Future Work:**
        - Run experiments in different user segments (power users, new users, etc.)
        - Test different variations of the Smart Reminder feature
        - Measure additional metrics (revenue impact, user satisfaction, support tickets)
        - Conduct qualitative research to understand the "why" behind the numbers
        - Implement continuous A/B testing framework for ongoing optimization
        """)


if __name__ == "__main__":
    main()

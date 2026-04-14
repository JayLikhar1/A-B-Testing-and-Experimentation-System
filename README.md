# 📊 A/B Testing & Experimentation System  

🔗 Live Demo: https://a-b-testing-and-experimentation-system-lq9zdfc2lj39mvnunrshhh.streamlit.app/

---

## 🚀 Overview  
A production-quality A/B testing system that simulates, analyzes, and provides data-driven decisions for product features using statistical hypothesis testing.  

This project demonstrates how real-world companies evaluate product features before deployment.  

**Experiment:** Testing a "Smart Reminder" feature to measure its impact on user engagement and retention.  

---

## 🎯 Problem Statement  

### Business Context  
Evaluate whether the Smart Reminder feature improves user engagement and 7-day retention in a productivity application.  

### Research Question  
Does the Smart Reminder feature significantly improve user engagement and retention compared to the baseline experience?  

---

## 📐 Hypothesis  

### Business Hypothesis  
The Smart Reminder feature increases engagement and retention by helping users manage tasks more effectively.  

### Statistical Hypothesis  

**Engagement (Continuous Metric):**  
- H₀: No difference in engagement between control and treatment  
- H₁: Treatment group has higher engagement  

**Retention (Binary Metric):**  
- H₀: No difference in retention rates  
- H₁: Treatment group has higher retention  

---

## 🧪 Experiment Design  

- **Sample Size:** 50,000 users  
- **Assignment:** 50/50 randomized split  
- **Duration:** 7 days  
- **Randomization Unit:** Individual users  

### Variants  
- **Control:** Baseline experience  
- **Treatment:** Smart Reminder enabled  

---

## 📊 Metrics  

### Primary Metric — Engagement  
- Average number of actions per user (continuous)  

### Secondary Metric — Retention  
- 7-day retention rate (binary)  

👉 Engagement → short-term behavior  
👉 Retention → long-term value  

---

## 📈 Statistical Methods  

### 1. Independent t-test  
- Used for engagement (continuous data)  
- Compares mean values between two groups  

### 2. Two-Proportion z-test  
- Used for retention (binary data)  
- Compares conversion rates  

### 3. Confidence Intervals  
- 95% confidence level  
- Estimates range of true effect size  

---

## ✅ Results  

### 📌 Engagement  
- Control Mean: 12.5  
- Treatment Mean: 13.75  
- **Uplift:** +10%  
- **p-value:** < 0.0001  
- **Result:** Statistically significant  

### 📌 Retention  
- Control Rate: 35.0%  
- Treatment Rate: 37.8%  
- **Uplift:** +8%  
- **p-value:** < 0.0001  
- **Result:** Statistically significant  

---

## 🚀 Business Recommendation  

### ✅ Decision: SHIP THE FEATURE  

**Reason:**  
- Strong statistical significance  
- Positive impact on key metrics  
- Meaningful business improvement  

---

## 📊 Business Impact  

- Improves user engagement  
- Increases retention rates  
- Enables data-driven decision making  
- Reduces risk before feature rollout  

---

## ⚠️ Limitations  

- Short experiment duration (7 days)  
- External factors not controlled  
- Results may vary across user segments  

---

## 🔮 Future Work  

- Segment-based analysis  
- Multi-variant A/B testing  
- Long-term retention tracking  
- ML-based personalization  

---

## 🛠 Tech Stack  

- **Language:** Python  
- **Data Processing:** Pandas, NumPy  
- **Statistical Analysis:** SciPy, Statsmodels  
- **Visualization:** Plotly  
- **Dashboard:** Streamlit  

---

## 📁 Project Structure  


ab-testing-experiment/
│
├── app.py # Streamlit dashboard (main application)
├── data_simulation.py # Simulates user data and experiment setup
├── analysis.py # Performs statistical tests and analysis
├── requirements.txt # Project dependencies
├── README.md # Project documentation


---

## ⚙️ How It Works  

1. Simulates user data (50,000 users)  
2. Randomly assigns users to control and treatment groups  
3. Measures engagement and retention metrics  
4. Applies statistical tests (t-test & z-test)  
5. Calculates confidence intervals  
6. Generates business recommendation (Ship / No-Ship)  

---

## ▶️ Installation & Usage  

### Install Dependencies  
```bash
pip install -r requirements.txt
Run Application
streamlit run app.py

App will run at: http://localhost:8501


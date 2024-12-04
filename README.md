# **Tesla Supply Chain Demand Forecasting - Project Documentation**

## **Project Overview**
In this project, I have developed a demand forecasting system for Tesla’s supply chain that uses real-time news articles. The articles are analyzed through sentiment analysis to predict if there will be high demand or low demand for automotive parts. By leveraging machine learning, this system can identify market trends, predict demand fluctuations, and optimize inventory management.

## **Problem Statement**
The goal is to predict demand for automotive parts based on external market signals (i.e., news articles). If there are signs of disruptions in the supply chain (e.g., shortage of critical components), the model should forecast a high demand, otherwise, it should predict low demand.

## **Project Use Case at Tesla**
### **Automated Demand Forecasting:**
Tesla can use this solution to predict demand for parts and materials based on the latest news articles. This can drive automated inventory management, procurement decisions, and supply chain planning.

### **Supply Chain Optimization:**
By understanding real-time supply chain disruptions (e.g., shortage of semiconductors), Tesla can adjust production schedules, pricing, and distribution logistics.

### **Market Sentiment Analysis:**
Tesla can monitor public sentiment on key components (like lithium or microchips) and forecast how those fluctuations could impact their production lines.

## **Tech Stack Used**
### **Programming Languages and Libraries:**
- **Python:** The primary programming language used to implement the entire solution.
- **pandas:** Data manipulation and analysis for handling the data throughout the pipeline.
- **scikit-learn:** Machine learning algorithms (Random Forest Classifier), data preprocessing, and evaluation.
- **textblob:** For sentiment analysis on the descriptions of the articles to predict demand.
- **matplotlib, seaborn:** For creating visualizations of the data and the model’s performance.
- **mysql-connector-python:** Python library to connect to MySQL and interact with the database.
- **kafka-python:** For integrating and interacting with Apache Kafka, enabling the streaming of real-time news articles.
- **imblearn:** To handle class imbalance using SMOTE (Synthetic Minority Over-sampling Technique), improving model accuracy on imbalanced data.

### **Database:**
- **MySQL:** A relational database used for storing and retrieving news data, including the title, description, published_at, and URL for each article.

### **API and Real-time Data:**
- **NewsAPI:** A RESTful API used to fetch real-time news articles about the supply chain, logistics, and procurement topics.
- **Apache Kafka:** A distributed event streaming platform used to stream news data in real-time from the producer (fetching data from NewsAPI) to the consumer (storing it in MySQL).

### **Containerization:**
- **Docker:** Used to containerize the entire application, ensuring that the environment, libraries, and dependencies are isolated and reproducible. This makes it easier to deploy and scale the application. Docker ensures consistency across different environments (e.g., local development, staging, production).

## **1. Setup and Initialization**
### **CLI Setup:**
To run this project locally or on any server, ensure you have Python 3.x installed and all dependencies are met. The recommended way to set up the environment is through virtual environments.

```bash
# Step 1: Clone the repository
git clone https://github.com/yourusername/tesla-supply-chain.git

# Step 2: Navigate to the project folder
cd tesla-supply-chain

# Step 3: Create a virtual environment (optional but recommended)
python3 -m venv .venv

# Step 4: Activate the virtual environment
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Step 5: Install all dependencies
pip install -r requirements.txt
```

### **Environment Configuration:**
Sensitive data, like API keys and database credentials, are stored in a .env file for security and ease of access:

Create a .env file:
Store sensitive details like MySQL credentials and NewsAPI key.

## **2. Data Collection and Integration**
### **MySQL Database Connection:**
Using MySQL as the backend database, I stored the articles fetched from NewsAPI in a structured format. The database is set up to hold essential fields like title, description, URL, and published date of articles related to supply chain and logistics.

```python
# Connect to MySQL Database
db_connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password=db_password,  # Use password from environment variable
    database="supply_chain"
)
cursor = db_connection.cursor()

# Query to select the articles data
cursor.execute("SELECT title, description, published_at FROM articles")

# Fetch all rows from the database
rows = cursor.fetchall()

# Convert rows to a pandas DataFrame
df = pd.DataFrame(rows, columns=["title", "description", "publishedAt"])
```

### **Producer (Kafka):**
In the producer script, I connected to the NewsAPI, fetch real-time news articles related to supply chain and logistics, and stream the data through Apache Kafka. The Kafka consumer will then process this data and store it in MySQL.

NewsAPI provides a JSON response that contains articles, which I parsed and then pushed to a Kafka topic. This ensures real-time streaming of news data for prediction.

```python
# Fetching data from NewsAPI and streaming to Kafka
def fetch_news():
    to_date = datetime.datetime.utcnow()
    from_date = to_date - datetime.timedelta(days=30)  # Last 30 days

    params = {
        'q': 'supply chain OR logistics OR procurement OR shipping',
        'from': from_date.isoformat(),
        'to': to_date.isoformat(),
        'sortBy': 'publishedAt',
        'language': 'en',
        'apiKey': api_key  # API key from the environment
    }
    # Fetch and push articles to Kafka topic
    producer.send('supply_chain_news', value=article)
```

## **3. Data Preprocessing and Feature Engineering**
Once the articles are collected, the data preprocessing involves cleaning the raw text, transforming it into numerical representations using TF-IDF (Term Frequency-Inverse Document Frequency), and preparing it for machine learning.

### **Text Cleaning:**
- Remove URLs and special characters from the article descriptions.
- Convert text to lowercase to ensure consistency.
- Remove unnecessary white spaces.

```python
def clean_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    text = text.strip()  # Remove leading/trailing spaces
    return text
```

### **TF-IDF Vectorization:**
After cleaning the text, I used TF-IDF to convert the text into numeric vectors. This helps capture the importance of words across all documents.

```python
from sklearn.feature_extraction.text import TfidfVectorizer

# Convert text to TF-IDF features
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
X_tfidf = vectorizer.fit_transform(df['cleaned_description'])
```

### **Sentiment Analysis:**
Using TextBlob, I extracted the sentiment polarity of each article's description. The sentiment score is then used to predict demand: positive sentiment indicates high demand and negative sentiment indicates low demand.

```python
def get_sentiment(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity  # Range from -1 (negative) to +1 (positive)
```

## **4. Model Building**
### **Random Forest Classifier:**
I chose the Random Forest Classifier for demand prediction because it handles large datasets well and prevents overfitting through ensemble learning.

- Cross-validation was used to evaluate the model’s generalizability.
- Hyperparameter tuning was done using GridSearchCV to find the best parameters for the classifier.

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

# Hyperparameter tuning using GridSearchCV
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

grid_search = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=5)
grid_search.fit(X_train, y_train)
```

After hyperparameter tuning, the model was trained on the dataset, and I evaluated its performance using classification metrics.

## **5. Handling Class Imbalance with SMOTE**
The dataset exhibited class imbalance, where most articles predicted low demand. To address this, I applied SMOTE (Synthetic Minority Over-sampling Technique) to balance the class distribution.

```python
from imblearn.over_sampling import SMOTE

# Apply SMOTE to balance the classes
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
```

This allowed us to make the model more robust and less biased towards the majority class.

## **6. Model Evaluation**
### **Classification Report:**
After training, the model's accuracy, precision, recall, and f1-score were assessed to ensure it performs well in real-world scenarios. The evaluation results indicated that the model was able to classify high demand and low demand articles accurately.

```python
from sklearn.metrics import classification_report

# Classification report
y_pred = best_model.predict(X_test)
print(classification_report(y_test, y_pred))
```

### **Cross-validation:**
I further evaluated the model by performing cross-validation to ensure it is generalizable to unseen data.

```python
from sklearn.model_selection import cross_val_score
cv_scores = cross_val_score(clf, X_train, y_train, cv=5)
```

## **7. Visualization and Insights**
### **Sentiment Distribution:**
I visualized the sentiment score distribution to understand the sentiment distribution across articles.

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Sentiment Score Distribution Plot
plt.figure(figsize=(8, 6))
sns.histplot(df['sentiment'], bins=30, kde=True)
plt.title("Sentiment Score Distribution")
plt.xlabel("Sentiment Score")
plt.ylabel("Density")
plt.show()
```

### **Predicted Demand Distribution:**
I also visualized how well the model predicted high and low demand based on news articles.

```python
# Predicted Demand Distribution Plot
plt.figure(figsize=(8, 6))
sns.countplot(data=df, x='predicted_demand')
plt.title("Predicted Demand Distribution")
plt.xlabel("Predicted Demand")
plt.ylabel("Frequency")
plt.show()
```

## **8. Final Model and Use Case**
After optimizing the model and validating it using cross-validation, the Random Forest model was able to predict demand for new articles with high accuracy. For example:

```python
new_description = "The global shortage of lithium is causing delays in production for electric vehicles."
cleaned_desc = clean_text(new_description)
tfidf_new = vectorizer.transform([cleaned_desc])
demand_prediction = best_model.predict(tfidf_new)

print(f"Predicted Demand: {'High Demand' if demand_prediction[0] == 1 else 'Low Demand'}")
```

This model can be deployed in Tesla’s real-time supply chain system to predict parts demand automatically based on global news articles.

## **Conclusion**
This project successfully demonstrated how real-time news analysis can be used to predict demand in the supply chain. The solution is scalable, allowing for real-time integration with Tesla’s systems, providing them with an automated decision-making tool that optimizes supply chain operations based on market dynamics.



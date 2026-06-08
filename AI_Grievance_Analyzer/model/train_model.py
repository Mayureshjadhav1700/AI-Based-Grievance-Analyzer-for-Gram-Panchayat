import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report
import joblib

# =============================
# 1. Load and Prepare Dataset
# =============================
data = pd.read_csv("dataset/grievances1.csv")

# Strip any leading/trailing spaces from column names
data.columns = data.columns.str.strip()

# Ensure necessary columns exist
if 'Complaint_Text' not in data.columns or 'Category' not in data.columns:
    raise KeyError("❌ Dataset must contain 'Complaint_Text' and 'Category' columns")

print("✅ Columns in dataset:", data.columns.tolist())
print("🧾 Total entries:", len(data))

# =============================
# 2. Text Cleaning Function
# =============================
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)              # remove URLs
    text = re.sub(r'[^a-z\s]', '', text)             # remove punctuation & numbers
    text = re.sub(r'\s+', ' ', text).strip()         # remove extra spaces
    words = [word for word in text.split() if word not in stop_words]
    return ' '.join(words)

# Apply cleaning
data['Cleaned_Complaint'] = data['Complaint_Text'].apply(clean_text)

# =============================
# 3. Feature & Label Separation
# =============================
X = data['Cleaned_Complaint']
y = data['Category']

# =============================
# 4. Train-Test Split
# =============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# =============================
# 5. TF-IDF Vectorization
# =============================
vectorizer = TfidfVectorizer(
    sublinear_tf=True,
    stop_words='english',
    ngram_range=(1, 3),   # unigrams + bigrams + trigrams
    min_df=2,
    max_df=0.8
)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# =============================
# 6. Model Training (Logistic Regression)
# =============================
# Use GridSearchCV for better hyperparameters
params = {
    'C': [0.5, 1, 2, 3],
    'solver': ['liblinear', 'saga']
}
grid = GridSearchCV(LogisticRegression(max_iter=500, class_weight='balanced'),
                    params, cv=5, n_jobs=-1, verbose=1)
grid.fit(X_train_vec, y_train)

model = grid.best_estimator_
print("🏆 Best Parameters:", grid.best_params_)

# =============================
# 7. Model Evaluation
# =============================
y_pred = model.predict(X_test_vec)
print("\n📊 Classification Report:\n", classification_report(y_test, y_pred))

# =============================
# 8. Save Model and Vectorizer
# =============================
joblib.dump(vectorizer, "vectorizer.pkl")
joblib.dump(model, "grievance_model.pkl")
print("\n✅ Model and vectorizer saved successfully!")

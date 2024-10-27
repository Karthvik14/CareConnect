## 🏥 CareConnect  : Your AI Health Companion, Always Here to Care

#### An AI-powered healthcare consultation platform that provides medical image analysis and text-based health consultations using Google's Gemini Pro model.

#### 🌟 Features:

- Medical Image Analysis: Upload and analyze medical images for preliminary insights
- Text-based Health Consultation: Interactive chat interface for health-related queries
- Responsive Design: Fully responsive interface that works across devices
- Real-time Analysis: Quick and detailed AI-powered responses
- Professional Format: Structured responses following medical consultation patterns

#### 🛠️ Technology Stack

- Backend: Flask (Python)
- Frontend: HTML5, CSS3
- AI Model: Google Gemini Pro 1.5 (gemini-1.5-pro-002)
- Evaluation: Custom model evaluation framework

#### 🚀 Installation

#### 1. Clone the repository:
```
git clone https://github.com/yourusername/careconnect.git
cd careconnect
```
#### 2. Install required packages:
```
pip install -r requirements.txt
```
#### 3. Create an ```api_key.py``` file in the root directory:
```
api_key = "your-google-ai-api-key-here"
```
#### 4. Start the application:
```
python app.py
```
#### 💻 Usage

#### Image Analysis

1. Click on the "Image Analysis" tab
2. Upload a medical image using the upload button
3. Click "Analyze Image" to receive AI-powered insights
4. Review the detailed analysis provided

#### Text Consultation

1. Navigate to the "Text Consultation" tab
2. Type your health-related query in the chat input
3. Receive structured responses

#### 📊 Model Evaluation
The project includes a comprehensive evaluation framework ```evaluate_model.py``` that assesses:

- Response Quality Metrics
- Section Coverage
- Medical Relevance
- Response Coherence
- Practical Advice
- Response Time

#### 🎨 Project Structure
```
CareConnect/
│
├── static/
│   ├── uploads/                 # Image upload directory
│   └── main.css                 # Main stylesheet
│
├── templates/
│   └── index.html               # Main application template
│
├── app.py                       # Flask application
├── utils
│   └──evaluate_model.py         # Model evaluation framework
│
├── api_key.py                   # API key configuration
└── README.md                    # Project documentation
```



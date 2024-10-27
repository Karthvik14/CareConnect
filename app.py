from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from werkzeug.utils import secure_filename
from datetime import datetime
import base64

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure Google Gemini AI
from api_key import api_key
genai.configure(api_key=api_key)

# AI Model Configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-002",
    generation_config=generation_config,
)

# Text consultation prompt
text_prompt = """
You are a compassionate and knowledgeable doctor who provides detailed guidance. For ANY health concern, respond with empathy and thoroughness using this format:

"Hello! I understand your situation about [specific concern, with brief context and acknowledgment of how it might be affecting their daily life]. I'll help you manage this while considering your current constraints and circumstances.

GREETING FORMAT:
For general greetings (hi/hello):
"Hello! How are you feeling today? I'm here to listen and help. Please feel free to share what's concerning you."

Immediate Relief Steps:
• [First immediate solution with explanation of why and how it helps]
• [Second immediate solution with practical implementation tips]
• [Third immediate solution with expected benefits]
• [Fourth immediate solution with any necessary precautions]

Management Tips:
• [First management tip with detailed guidance on implementation]
• [Second management tip with explanation of its importance]
• [Third management tip with variations for different situations]
• [Fourth management tip with long-term benefits]

Prevention Tips:
• [First prevention tip with lifestyle modification suggestions]
• [Second prevention tip with explanation of underlying factors]
• [Third prevention tip with adaptive strategies]
• [Fourth prevention tip with maintenance recommendations]

Warning Signs to Watch For:
• [First warning sign with explanation of its significance]
• [Second warning sign with context of when to be concerned]
• [Third warning sign with associated symptoms to monitor]
• [Fourth warning sign with urgency level indication]

While these suggestions can help you manage your current situation, please consult a healthcare provider if your symptoms persist or worsen. Every person's health situation is unique, and these recommendations should be adapted to your specific circumstances."

For example, for back pain while working:
"Hello! I understand you're experiencing back pain while needing to continue your work. This can be particularly challenging as it affects both your comfort and productivity. I'll help you manage this while considering your work constraints and daily routine.

Immediate Relief Steps:
• Adjust your sitting posture - keep your back straight and supported against your chair. This helps align your spine and reduces pressure on your lower back muscles. Try to maintain a 90-degree angle at your hips and knees.
• Do gentle seated stretches every hour - simple movements like shoulder rolls and gentle back twists can help release muscle tension and promote blood flow. Aim for 2-3 minutes of stretching.
• Use a small cushion or rolled towel for lower back support - place it in the curve of your lower back to maintain natural spine curvature. Adjust the thickness until you find what feels most comfortable.
• Apply pressure to painful areas with your hands - using circular motions, gently massage the affected areas for 30-60 seconds. This can help increase blood flow and provide temporary relief.

Management Tips:
• Take micro-breaks to shift position slightly every 20-30 minutes - even small movements can prevent muscle stiffness and reduce pressure points
• Do gentle seated twists in your chair - rotate your upper body while keeping your hips stable, holding each side for 10-15 seconds
• Perform ankle and leg movements while seated - simple exercises like ankle circles and leg stretches help maintain circulation
• Keep your feet flat on the floor or use a footrest - proper foot positioning helps maintain good posture throughout your spine

Prevention Tips:
• Set up an ergonomic workspace - ensure your screen is at eye level, keyboard allows relaxed shoulders, and chair provides proper support
• Schedule regular movement breaks - set reminders to stand and walk for 2-3 minutes every hour
• Strengthen core muscles during free time - focus on gentle exercises like pelvic tilts and bridges that support proper posture
• Maintain good posture habits throughout the day - be mindful of your positioning during all activities, not just while working

Warning Signs to Watch For:
• Severe or shooting pain - especially if it comes on suddenly or is significantly worse than your usual discomfort
• Numbness or tingling in legs or feet - this could indicate nerve compression requiring medical attention
• Loss of bladder/bowel control - this is a medical emergency requiring immediate care
• Pain spreading down legs with associated weakness - could indicate nerve involvement needing professional evaluation

While these suggestions can help you manage your current situation, please consult a healthcare provider if your symptoms persist or worsen. Remember that back pain can be complex, and what works best may vary from person to person."

Always follow this format for ANY health concern, adapting the specific advice to the situation while maintaining the structure. Provide detailed explanations and context for each point to help users better understand and implement the recommendations.
"""
# Image analysis prompt
image_prompt = """
You are an empathetic doctor reviewing patient images. 

Start your response with:
1. A warm greeting
2. Acknowledgment of the image shared
3. Show that you're here to help

For example:
"Hello! Thank you for sharing this image with me. I'll be happy to take a look and provide some insights about what I observe."

Then provide your analysis:
1. Describe what you see in simple terms
2. Explain possible conditions in clear paragraphs
3. Share practical advice and recommendations
4. Use friendly, conversational language

Keep your tone warm and supportive throughout, like a caring doctor speaking to their patient.

Remember to end with: "While I can provide general information based on the image, please consult a healthcare provider for proper diagnosis and treatment."
"""

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload a PNG or JPEG image.'}), 400

        # Read the image file
        image_data = file.read()
        
        # Create the image part for the model
        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": image_data
            }
        ]
        
        # Create the prompt parts
        prompt_parts = [
            image_parts[0],
            image_prompt,
        ]
        
        try:
            # Generate content
            response = model.generate_content(prompt_parts)
            
            # Check if response is valid
            if response and hasattr(response, 'text'):
                return jsonify({'result': response.text})
            else:
                return jsonify({'error': 'Invalid response from AI model'}), 500
                
        except Exception as e:
            print(f"AI Model Error: {str(e)}")
            return jsonify({'error': 'Error processing image with AI model'}), 500
        
    except Exception as e:
        print(f"General Error: {str(e)}")
        return jsonify({'error': 'Error processing request'}), 500

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400
            
        user_message = data['message']
        
        try:
            # Generate AI response
            response = model.generate_content(f"{text_prompt}\n\nUser Question: {user_message}")
            
            if response and hasattr(response, 'text'):
                return jsonify({'response': response.text})
            else:
                return jsonify({'error': 'Invalid response from AI model'}), 500
                
        except Exception as e:
            print(f"AI Model Error: {str(e)}")
            return jsonify({'error': 'Error generating response'}), 500
        
    except Exception as e:
        print(f"General Error: {str(e)}")
        return jsonify({'error': 'Error processing request'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File is too large. Maximum size is 16MB'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
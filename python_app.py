from flask import Flask, render_template_string, request, redirect, url_for, flash, send_file
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'xlsx', 'xls'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
RESPONSES_FILE = 'responses.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Evaluation Form (Part 1)</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        
        .description {
            color: #666;
            margin-bottom: 30px;
            padding: 15px;
            background: #f9f9f9;
            border-left: 4px solid #4285f4;
            border-radius: 4px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        
        .required {
            color: #d93025;
        }
        
        input[type="text"],
        input[type="number"],
        textarea,
        select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.3s;
        }
        
        input:focus,
        textarea:focus,
        select:focus {
            outline: none;
            border-color: #4285f4;
        }
        
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        
        .file-upload-section {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 4px;
            margin: 30px 0;
        }
        
        .file-upload-section h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 20px;
        }
        
        .file-category {
            margin-bottom: 20px;
            padding: 15px;
            background: white;
            border-radius: 4px;
            border: 1px solid #e0e0e0;
        }
        
        .file-category h3 {
            color: #555;
            margin-bottom: 10px;
            font-size: 16px;
        }
        
        input[type="file"] {
            padding: 10px;
            border: 2px dashed #ddd;
            border-radius: 4px;
            width: 100%;
            cursor: pointer;
        }
        
        input[type="file"]:hover {
            border-color: #4285f4;
        }
        
        button {
            background: #4285f4;
            color: white;
            padding: 14px 30px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        button:hover {
            background: #357ae8;
        }
        
        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .helper-text {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        
        .section-divider {
            height: 1px;
            background: #e0e0e0;
            margin: 30px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Product Evaluation (Part 1)</h1>
        
        <div class="description">
            <strong>Form Description:</strong><br>
            Describe your role in evaluating this solution. Include: (1) Your expertise and professional title, 
            (2) The organization you represent, (3) Your evaluation purpose (acquisition, investment, partnership, etc.), 
            (4) Your key evaluation criteria (problem-solution fit, viability, risks, commercialization potential, etc.), 
            and (5) What would make this opportunity attractive or concerning to you.
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST" enctype="multipart/form-data">
            
            <div class="form-group">
                <label>Describe your role in evaluating this solution <span class="required">*</span></label>
                <textarea name="evaluator_role" required></textarea>
                <div class="helper-text">Include your expertise, organization, evaluation purpose, criteria, and what makes this attractive/concerning</div>
            </div>
            
            <div class="section-divider"></div>
            
            <div class="form-group">
                <label>What is the name of your solution/product? <span class="required">*</span></label>
                <input type="text" name="solution_name" required>
            </div>
            
            <div class="form-group">
                <label>What specific problem does your solution solve? <span class="required">*</span></label>
                <textarea name="problem_solved" required></textarea>
            </div>
            
            <div class="form-group">
                <label>Who specifically experiences this problem? (Describe your target customer) <span class="required">*</span></label>
                <textarea name="target_customer" required></textarea>
            </div>
            
            <div class="form-group">
                <label>How do these customers currently solve this problem today? <span class="required">*</span></label>
                <textarea name="current_solution" required></textarea>
            </div>
            
            <div class="form-group">
                <label>How does your solution solve this problem differently or better? <span class="required">*</span></label>
                <textarea name="solution_advantage" required></textarea>
            </div>
            
            <div class="form-group">
                <label>What is your primary market sector? <span class="required">*</span></label>
                <select name="market_sector" required>
                    <option value="">Select...</option>
                    <option value="Healthcare">Healthcare</option>
                    <option value="Technology">Technology</option>
                    <option value="Finance">Finance</option>
                    <option value="Manufacturing">Manufacturing</option>
                    <option value="Retail">Retail</option>
                    <option value="Energy">Energy</option>
                    <option value="Education">Education</option>
                    <option value="Agriculture">Agriculture</option>
                    <option value="Other">Other</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>What geographic region(s) are you targeting? <span class="required">*</span></label>
                <input type="text" name="geographic_region" required placeholder="e.g., North America, Europe, Global">
            </div>
            
            <div class="form-group">
                <label>Who are your known competitors? <span class="required">*</span></label>
                <textarea name="competitors" required></textarea>
            </div>
            
            <div class="form-group">
                <label>What is your primary business model? <span class="required">*</span></label>
                <select name="business_model" required>
                    <option value="">Select...</option>
                    <option value="SaaS/Subscription">SaaS/Subscription</option>
                    <option value="Direct Sales">Direct Sales</option>
                    <option value="Licensing">Licensing</option>
                    <option value="Marketplace">Marketplace</option>
                    <option value="Freemium">Freemium</option>
                    <option value="Hardware Sales">Hardware Sales</option>
                    <option value="Consulting/Services">Consulting/Services</option>
                    <option value="Other">Other</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Do you have a secondary business model you're considering?</label>
                <input type="text" name="secondary_business_model" placeholder="Optional">
            </div>
            
            <div class="form-group">
                <label>What is your projected revenue over the next 12 months? <span class="required">*</span></label>
                <input type="text" name="projected_revenue" required placeholder="e.g., $500K, $2M">
            </div>
            
            <div class="form-group">
                <label>What stage is your solution at? <span class="required">*</span></label>
                <select name="solution_stage" required>
                    <option value="">Select...</option>
                    <option value="Idea/Concept">Idea/Concept</option>
                    <option value="Prototype">Prototype</option>
                    <option value="MVP">MVP</option>
                    <option value="Beta">Beta</option>
                    <option value="Live/Production">Live/Production</option>
                    <option value="Scaling">Scaling</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>How many paying customers do you currently have? <span class="required">*</span></label>
                <input type="number" name="paying_customers" required min="0">
            </div>
            
            <div class="form-group">
                <label>How many pilot programs or proof-of-concept projects have you completed? <span class="required">*</span></label>
                <input type="number" name="pilot_programs" required min="0">
            </div>
            
            <div class="form-group">
                <label>How much total funding have you raised to date? <span class="required">*</span></label>
                <input type="text" name="total_funding" required placeholder="e.g., $0, $250K, $5M">
            </div>
            
            <div class="form-group">
                <label>What is your current monthly burn rate (spending)? <span class="required">*</span></label>
                <input type="text" name="burn_rate" required placeholder="e.g., $10K/month">
            </div>
            
            <div class="form-group">
                <label>If not currently active, what was your previous monthly burn rate?</label>
                <input type="text" name="previous_burn_rate" placeholder="Optional">
            </div>
            
            <div class="form-group">
                <label>How many team members would transition with this solution (if acquired)? <span class="required">*</span></label>
                <input type="number" name="team_members" required min="0">
            </div>
            
            <div class="form-group">
                <label>What type of solution is this? <span class="required">*</span></label>
                <select name="solution_type" required>
                    <option value="">Select...</option>
                    <option value="Materials">Materials</option>
                    <option value="Hardware">Hardware</option>
                    <option value="Software">Software</option>
                    <option value="Service">Service</option>
                    <option value="IP/Patent">IP/Patent</option>
                    <option value="Hybrid">Hybrid</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>What are your known supply chain requirements? <span class="required">*</span></label>
                <textarea name="supply_chain" required></textarea>
            </div>
            
            <div class="form-group">
                <label>What is your intellectual property status? <span class="required">*</span></label>
                <textarea name="ip_status" required placeholder="Patents filed, pending, granted, trade secrets, etc."></textarea>
            </div>
            
            <div class="form-group">
                <label>What is your role/persona in relation to this solution? <span class="required">*</span></label>
                <select name="role_persona" required>
                    <option value="">Select...</option>
                    <option value="Founder/Co-founder">Founder/Co-founder</option>
                    <option value="CEO">CEO</option>
                    <option value="CTO">CTO</option>
                    <option value="Product Manager">Product Manager</option>
                    <option value="Investor">Investor</option>
                    <option value="Advisor">Advisor</option>
                    <option value="Other">Other</option>
                </select>
            </div>
            
            <div class="section-divider"></div>
            
            <div class="file-upload-section">
                <h2>Document Uploads</h2>
                <p class="helper-text">Please upload relevant documents (PDF, DOC, DOCX, PPT, PPTX, TXT, XLS, XLSX - Max 16MB per file)</p>
                
                <div class="file-category">
                    <h3>1. Abstracts</h3>
                    <input type="file" name="abstracts" accept=".pdf,.doc,.docx,.txt" multiple>
                </div>
                
                <div class="file-category">
                    <h3>2. External Decks</h3>
                    <input type="file" name="external_decks" accept=".pdf,.ppt,.pptx" multiple>
                </div>
                
                <div class="file-category">
                    <h3>3. Internal Decks (without regulatory violation issues)</h3>
                    <input type="file" name="internal_decks" accept=".pdf,.ppt,.pptx" multiple>
                </div>
                
                <div class="file-category">
                    <h3>4. Internal descriptions and analysis (without regulatory violation issues)</h3>
                    <input type="file" name="internal_analysis" accept=".pdf,.doc,.docx,.txt" multiple>
                </div>
                
                <div class="file-category">
                    <h3>5. Market-related documents</h3>
                    <input type="file" name="market_docs" accept=".pdf,.doc,.docx,.xls,.xlsx" multiple>
                </div>
            </div>
            
            <button type="submit">Submit Evaluation</button>
        </form>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Collect form data
            form_data = {
                'submission_date': datetime.now().isoformat(),
                'evaluator_role': request.form.get('evaluator_role'),
                'solution_name': request.form.get('solution_name'),
                'problem_solved': request.form.get('problem_solved'),
                'target_customer': request.form.get('target_customer'),
                'current_solution': request.form.get('current_solution'),
                'solution_advantage': request.form.get('solution_advantage'),
                'market_sector': request.form.get('market_sector'),
                'geographic_region': request.form.get('geographic_region'),
                'competitors': request.form.get('competitors'),
                'business_model': request.form.get('business_model'),
                'secondary_business_model': request.form.get('secondary_business_model'),
                'projected_revenue': request.form.get('projected_revenue'),
                'solution_stage': request.form.get('solution_stage'),
                'paying_customers': request.form.get('paying_customers'),
                'pilot_programs': request.form.get('pilot_programs'),
                'total_funding': request.form.get('total_funding'),
                'burn_rate': request.form.get('burn_rate'),
                'previous_burn_rate': request.form.get('previous_burn_rate'),
                'team_members': request.form.get('team_members'),
                'solution_type': request.form.get('solution_type'),
                'supply_chain': request.form.get('supply_chain'),
                'ip_status': request.form.get('ip_status'),
                'role_persona': request.form.get('role_persona'),
                'uploaded_files': []
            }
            
            # Handle file uploads
            file_categories = ['abstracts', 'external_decks', 'internal_decks', 'internal_analysis', 'market_docs']
            
            for category in file_categories:
                files = request.files.getlist(category)
                for file in files:
                    if file and file.filename and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        unique_filename = f"{timestamp}_{category}_{filename}"
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                        file.save(filepath)
                        form_data['uploaded_files'].append({
                            'category': category,
                            'original_filename': filename,
                            'saved_filename': unique_filename
                        })
            
            # Save response to JSON file
            responses = []
            if os.path.exists(RESPONSES_FILE):
                with open(RESPONSES_FILE, 'r') as f:
                    responses = json.load(f)
            
            responses.append(form_data)
            
            with open(RESPONSES_FILE, 'w') as f:
                json.dump(responses, f, indent=2)
            
            flash('Form submitted successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Error submitting form: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("Starting Product Evaluation Form Server...")
    print("Access the form at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
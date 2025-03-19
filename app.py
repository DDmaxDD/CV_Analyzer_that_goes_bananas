import streamlit as st
import PyPDF2
import docx
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Set page config and custom CSS
st.set_page_config(
    page_title="A CV Analyzer that goes bananas 🍌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fun monkey quotes
MONKEY_QUOTES = [
    "Yo dawg, lemme check that CV for ya! 🐒",
    "Bananas for days, skills for life! 🍌",
    "Swingin' through resumes like Tarzan! 🦍",
    "Monkey see, monkey analyze! 🐵",
    "Gonna peel back the layers of that CV! 🍌",
    "Time to go bananas over these skills! 🐒",
    "Let's get this monkey business started! 🐵",
    "CV analysis? That's my jam! 🍌",
    "Gonna climb through this CV like a pro! 🐒",
    "Monkey magic, coming right up! ✨",
    "OOGA BOOGA! Time to go resume crazy! 🙈",
    "Bananalyzing your CV with monkey power! 🍌💪",
    "Jungle skills detector: ACTIVATED! 🌴🔍",
    "Hold onto your bananas, CV inspection incoming! 🍌🚀",
    "This monkey's about to go BANANAS on your resume! 🐒✨",
    "Monkey see CV, monkey do analysis! WOOHOO! 🐵📊",
    "Swinging from skill to skill like a CV ninja! 🐒⚔️",
    "EEEK EEEK! Found some juicy skills! 🙈💎",
    "Monkey business degree in full effect! 🎓🐒",
    "Warning: Extremely bananas analysis ahead! ⚠️🍌",
    "Unleashing the monkey madness on your CV! 💫🐒",
    "Banana-powered skill scanner: ENGAGED! 🍌⚡",
    "Monkey see potential, monkey go WOW! 🐵✨",
    "Time to get absolutely coconuts! 🥥🐒",
    "Your CV is about to get MONKEYFIED! 🙈🔮"
]

# Custom CSS for monkey and banana theme
st.markdown("""
    <style>
    .stApp {
        background-color: #FFF9E6;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="50" x="50" font-size="30">🍌</text></svg>');
        background-repeat: repeat;
        background-size: 50px;
        background-opacity: 0.1;
    }
    .stButton>button {
        background-color: #FFB800;
        color: #4A3B24;
        border: 2px solid #4A3B24;
        padding: 10px 20px;
        border-radius: 25px;
        transition: all 0.3s ease;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FFD700;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(74, 59, 36, 0.2);
    }
    .stMarkdown {
        background-color: #FFF9E6;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(74, 59, 36, 0.1);
        margin: 10px 0;
        border: 2px solid #FFB800;
    }
    .stFileUploader {
        background-color: #FFF9E6;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(74, 59, 36, 0.1);
        border: 2px solid #FFB800;
    }
    h1 {
        color: #4A3B24;
        text-align: center;
        padding: 20px;
        background: linear-gradient(45deg, #FFB800, #FFD700);
        border-radius: 15px;
        margin-bottom: 30px;
        border: 3px solid #4A3B24;
        font-family: "Comic Sans MS", cursive;
    }
    h2 {
        color: #4A3B24;
        text-align: center;
        margin-bottom: 20px;
        font-family: "Comic Sans MS", cursive;
    }
    .stColumns {
        gap: 20px;
    }
    .stColumn {
        background-color: #FFF9E6;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(74, 59, 36, 0.1);
        border: 2px solid #FFB800;
    }
    .stMarkdown h3 {
        color: #4A3B24;
        font-family: "Comic Sans MS", cursive;
    }
    .stMarkdown li {
        color: #4A3B24;
    }
    .fun-quote {
        font-family: "Comic Sans MS", cursive;
        font-size: 1.2em;
        color: #4A3B24;
        text-align: center;
        padding: 10px;
        margin: 10px 0;
        background: #FFD700;
        border-radius: 10px;
        border: 2px dashed #4A3B24;
    }
    .analysis-box {
        background-color: #FFF9E6;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(74, 59, 36, 0.1);
        margin: 10px 0;
        border: 2px solid #FFB800;
    }
    </style>
    """, unsafe_allow_html=True)

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(docx_file):
    doc = docx.Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Tokenize
    tokens = word_tokenize(text)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    return " ".join(tokens)

def analyze_cv_with_openai(text):
    try:
        response = client.chat.completions.create(
            model="o3-mini-2025-01-31",
            messages=[
                {"role": "system", "content": """You are a helpful CV analyzer specializing in marketing automation roles. 
                Analyze the CV and provide detailed feedback in a fun, monkey-themed way. Focus on:
                1. Technical skills relevant to marketing automation
                2. Marketing experience and expertise
                3. Automation tools and platforms
                4. Areas for improvement
                5. Overall fit for marketing automation roles
                Keep the tone playful and include monkey/banana emojis! 🐒🍌"""},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Oops! Something went bananas with the AI analysis! 🍌 Error: {str(e)}"

def analyze_cv(text):
    # Define comprehensive skills list for marketing automation
    skills = {
        'technical': [
            # Programming & Scripting
            'python', 'javascript', 'sql', 'html', 'css', 'php', 'ruby', 
            'node.js', 'typescript', 'jquery', 'react', 'vue.js',
            'api development', 'rest api', 'soap api', 'graphql',
            'shell scripting', 'powershell', 'bash',
            
            # Data & Analytics
            'data analysis', 'data visualization', 'data mining',
            'statistical analysis', 'predictive analytics',
            'a/b testing implementation', 'multivariate testing',
            'google analytics', 'google tag manager',
            'adobe analytics', 'mixpanel', 'heap analytics',
            'tableau', 'power bi', 'looker', 'data studio',
            'sql queries', 'database management', 'etl processes',
            'big data tools', 'data warehousing',
            
            # Marketing Technology
            'tag management', 'pixel implementation',
            'utm parameter management', 'conversion tracking',
            'event tracking', 'custom dimensions',
            'marketing attribution modeling',
            'customer data platforms (cdp)',
            'dmp implementation', 'remarketing pixels',
            
            # Integration & Automation
            'api integration', 'webhook configuration',
            'zapier development', 'make.com scripting',
            'automation workflows', 'middleware development',
            'custom integration development',
            'etl pipeline creation', 'data synchronization',
            'real-time data processing',
            
            # Web Technologies
            'web development', 'cms systems',
            'wordpress development', 'shopify development',
            'landing page optimization', 'spa development',
            'progressive web apps', 'amp implementation',
            'website performance optimization',
            'mobile optimization', 'responsive design',
            
            # Cloud & Infrastructure
            'aws', 'azure', 'google cloud platform',
            'cloud computing', 'serverless functions',
            'lambda functions', 'cloud automation',
            'docker', 'kubernetes', 'microservices',
            'ci/cd pipelines', 'version control', 'git',
            
            # Security & Compliance
            'data privacy implementation', 'gdpr compliance',
            'ccpa compliance', 'security best practices',
            'oauth implementation', 'api authentication',
            'ssl/tls configuration', 'data encryption',
            
            # Testing & Monitoring
            'automated testing', 'ab testing tools',
            'performance monitoring', 'error tracking',
            'log analysis', 'debugging tools',
            'cross-browser testing', 'load testing',
            
            # Email Technical Skills
            'email html coding', 'esp technical setup',
            'dkim/spf configuration', 'email authentication',
            'email deliverability', 'email rendering testing',
            'amp for email', 'dynamic email content',
            
            # CRM & Database
            'crm customization', 'database design',
            'sql optimization', 'data modeling',
            'salesforce development', 'hubspot development',
            'dynamics 365 customization',
            
            # Tracking & Analytics Implementation
            'google analytics implementation',
            'facebook pixel setup', 'linkedin insight tag',
            'custom tracking scripts', 'data layer implementation',
            'cross-domain tracking', 'enhanced ecommerce',
            'conversion tracking setup'
        ],
        'marketing': [
            # Digital Marketing Fundamentals
            'seo', 'sem', 'ppc advertising', 'display advertising',
            'social media marketing', 'content marketing', 'email marketing',
            'affiliate marketing', 'influencer marketing', 'viral marketing',
            'inbound marketing', 'outbound marketing', 'growth hacking',
            
            # Analytics & Data
            'marketing analytics', 'web analytics', 'social media analytics',
            'conversion rate optimization', 'a/b testing', 'multivariate testing',
            'funnel analysis', 'cohort analysis', 'attribution modeling',
            'customer segmentation', 'predictive analytics', 'marketing metrics',
            'roi analysis', 'kpi tracking', 'performance marketing',
            
            # Content & Strategy
            'content strategy', 'content planning', 'editorial calendar',
            'copywriting', 'storytelling', 'brand messaging',
            'content distribution', 'content optimization',
            'marketing communications', 'brand voice', 'tone of voice',
            'content personalization', 'dynamic content',
            
            # Social Media
            'social media strategy', 'community management',
            'social listening', 'social media advertising',
            'social media analytics', 'social media optimization',
            'instagram marketing', 'facebook marketing', 'linkedin marketing',
            'twitter marketing', 'tiktok marketing', 'youtube marketing',
            
            # Email Marketing
            'email strategy', 'email campaign management',
            'email segmentation', 'email personalization',
            'drip campaigns', 'newsletter management',
            'email deliverability', 'email compliance',
            'subscriber management', 'email list building',
            
            # Campaign Management
            'campaign planning', 'campaign execution',
            'campaign optimization', 'cross-channel campaigns',
            'integrated marketing campaigns', 'seasonal campaigns',
            'product launches', 'event marketing', 'promotional campaigns',
            
            # Lead Generation & CRM
            'lead generation', 'lead nurturing', 'lead scoring',
            'customer journey mapping', 'customer lifecycle marketing',
            'crm strategy', 'customer segmentation',
            'account-based marketing', 'pipeline management',
            
            # Market Research
            'market analysis', 'competitor analysis',
            'customer research', 'audience insights',
            'trend analysis', 'market segmentation',
            'buyer persona development', 'customer feedback analysis',
            
            # Brand Management
            'brand strategy', 'brand development',
            'brand guidelines', 'brand positioning',
            'brand awareness', 'brand loyalty',
            'reputation management', 'crisis communication',
            
            # Marketing Operations
            'marketing resource management', 'budget management',
            'vendor management', 'marketing compliance',
            'marketing project management', 'marketing team leadership',
            'marketing process optimization', 'marketing documentation'
        ],
        'automation': [
            # Marketing Automation Platforms
            'hubspot', 'marketo', 'pardot', 'salesforce marketing cloud',
            'oracle eloqua', 'act-on', 'active campaign', 'mailchimp',
            'constant contact', 'klaviyo', 'braze', 'iterable',
            'customer.io', 'autopilot', 'drip', 'sendinblue',
            
            # Integration Platforms
            'zapier', 'make.com', 'workato', 'tray.io',
            'n8n', 'power automate', 'automate.io', 'integromat',
            'mulesoft', 'boomi', 'celigo', 'jitterbit',
            'snaplogic', 'azure logic apps', 'aws step functions',
            
            # CRM Automation
            'salesforce automation', 'hubspot workflows',
            'dynamics 365 automation', 'zoho automation',
            'pipedrive automation', 'freshsales automation',
            'zendesk automation', 'insightly automation',
            
            # Email Automation
            'email workflow automation', 'drip campaigns',
            'triggered emails', 'behavioral emails',
            'transactional emails', 'automated newsletters',
            'email sequence automation', 'email personalization',
            
            # Social Media Automation
            'buffer', 'hootsuite', 'sprout social',
            'later', 'agorapulse', 'sendible',
            'social media scheduling', 'social listening automation',
            'social media response automation',
            
            # Lead Management Automation
            'lead routing automation', 'lead scoring automation',
            'lead nurturing workflows', 'lead qualification automation',
            'account assignment automation', 'territory management automation',
            
            # Process Automation
            'rpa (robotic process automation)', 'business process automation',
            'workflow automation', 'task automation',
            'document automation', 'approval automation',
            'data entry automation', 'reporting automation',
            
            # Customer Service Automation
            'chatbots', 'automated ticketing',
            'automated response systems', 'customer support automation',
            'knowledge base automation', 'faq automation',
            
            # Analytics & Reporting Automation
            'automated reporting', 'dashboard automation',
            'data aggregation automation', 'analytics automation',
            'kpi tracking automation', 'performance monitoring automation',
            
            # Campaign Automation
            'campaign workflow automation', 'multi-channel automation',
            'trigger-based automation', 'event-based automation',
            'personalization automation', 'content automation',
            'a/b testing automation', 'optimization automation'
        ]
    }
    
    # Initialize results
    results = {
        'technical_skills': [],
        'marketing_skills': [],
        'automation_skills': [],
        'ai_analysis': None
    }
    
    # Get AI analysis for skill mapping
    try:
        skill_analysis_prompt = f"""Analyze this CV and identify the most relevant skills from the following categories. 
        For each category, provide a JSON response with:
        1. Found skills (skills explicitly mentioned or strongly implied)
        2. Potential skills (skills that could be developed based on experience)
        3. Missing critical skills (important skills not present)
        
        Categories and their skills:
        {skills}
        
        CV Text:
        {text}
        
        Provide the response in this exact JSON format:
        {{
            "technical_skills": {{
                "found": [],
                "potential": [],
                "missing": []
            }},
            "marketing_skills": {{
                "found": [],
                "potential": [],
                "missing": []
            }},
            "automation_skills": {{
                "found": [],
                "potential": [],
                "missing": []
            }}
        }}"""

        response = client.chat.completions.create(
            model="o3-mini-2025-01-31",
            messages=[
                {"role": "system", "content": "You are a CV analyzer specializing in marketing automation roles. Analyze the CV and map skills to the provided categories."},
                {"role": "user", "content": skill_analysis_prompt}
            ]
        )
        
        skill_analysis = response.choices[0].message.content
        
        # Get general CV analysis
        general_analysis = analyze_cv_with_openai(text)
        
        # Parse the skill analysis and update results
        import json
        try:
            skill_data = json.loads(skill_analysis)
            
            # Format the skill analysis in a readable way
            formatted_analysis = []
            
            for category in ['technical', 'marketing', 'automation']:
                category_analysis = f"\n#### {category.title()} Skills\n"
                
                found = skill_data[f'{category}_skills']['found']
                potential = skill_data[f'{category}_skills']['potential']
                missing = skill_data[f'{category}_skills']['missing']
                
                if found:
                    category_analysis += "\n**Found Skills:**\n"
                    category_analysis += "\n".join(f"• {skill}" for skill in found) + "\n"
                
                if potential:
                    category_analysis += "\n**Potential Skills:**\n"
                    category_analysis += "\n".join(f"• {skill}" for skill in potential) + "\n"
                
                if missing:
                    category_analysis += "\n**Missing Critical Skills:**\n"
                    category_analysis += "\n".join(f"• {skill}" for skill in missing) + "\n"
                
                formatted_analysis.append(category_analysis)
            
            # Combine the analyses
            results['ai_analysis'] = f"""### Skill Analysis 🎯\n{''.join(formatted_analysis)}\n### General Analysis 📝\n{general_analysis}"""
            
            # Update the found skills for the UI
            for category in ['technical', 'marketing', 'automation']:
                results[f'{category}_skills'] = skill_data[f'{category}_skills']['found']
                
        except json.JSONDecodeError:
            st.error("Oops! Something went bananas with the skill analysis! 🍌")
            
    except Exception as e:
        st.error(f"Oops! Something went bananas with the AI analysis! 🍌 Error: {str(e)}")
    
    return results

def main():
    st.title("A CV analyzer that goes bananas 🍌")
    
    # Display random monkey quote
    st.markdown(f"""
        <div class="fun-quote">
            {random.choice(MONKEY_QUOTES)}
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style='text-align: center; color: #4A3B24; font-size: 1.2em; margin-bottom: 30px; font-family: "Comic Sans MS", cursive;'>
            Yo! Drop that CV here and let's see what skills you got! 🐒
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Choose a CV file", type=['pdf', 'docx'])

    if uploaded_file is not None:
        try:
            with st.spinner("Monkey's analyzing your CV... 🐒"):
                # Extract text based on file type
                if uploaded_file.type == "application/pdf":
                    text = extract_text_from_pdf(uploaded_file)
                else:
                    text = extract_text_from_docx(uploaded_file)

                # Analyze the CV
                results = analyze_cv(text)

                # Display results with enhanced styling
                st.markdown("""
                    <h2 style='text-align: center; color: #4A3B24; margin: 30px 0; font-family: "Comic Sans MS", cursive;'>
                        Yo dawg, here's what I found! 🍌
                    </h2>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### Technical Skills 🛠️")
                    st.markdown("#### Found in your CV:")
                    if results['technical_skills']:
                        for skill in results['technical_skills']:
                            st.markdown(f"• {skill}")
                    else:
                        st.markdown("No technical skills found yet! 🐒")
                
                with col2:
                    st.markdown("### Marketing Skills 📢")
                    st.markdown("#### Found in your CV:")
                    if results['marketing_skills']:
                        for skill in results['marketing_skills']:
                            st.markdown(f"• {skill}")
                    else:
                        st.markdown("No marketing skills found yet! 🍌")
                
                with col3:
                    st.markdown("### Automation Skills ⚙️")
                    st.markdown("#### Found in your CV:")
                    if results['automation_skills']:
                        for skill in results['automation_skills']:
                            st.markdown(f"• {skill}")
                    else:
                        st.markdown("No automation skills found yet! 🐒")

                # Display AI Analysis
                st.markdown("""
                    <h2 style='text-align: center; color: #4A3B24; margin: 30px 0; font-family: "Comic Sans MS", cursive;'>
                        Monkey's Deep Analysis 🐒
                    </h2>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="analysis-box">
                        {results['ai_analysis']}
                    </div>
                """, unsafe_allow_html=True)

                # Add another random quote at the bottom
                st.markdown(f"""
                    <div class="fun-quote">
                        {random.choice(MONKEY_QUOTES)}
                    </div>
                """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Oops! Something went bananas! 🍌 Error: {str(e)}")

if __name__ == "__main__":
    main() 
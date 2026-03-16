"""
Skill Categories Configuration
Defines categorized skill keywords for deep resume analysis
"""

SKILL_CATEGORIES = {
    "Technical": [
        # Programming Languages
        "Python", "Java", "C++", "JavaScript", "C#", "PHP", "SQL", "Ruby", "Go", 
        "HTML5", "CSS", "Swift",
        
        # Cloud Platforms
        "AWS", "Microsoft Azure", "Google Cloud Platform", "Azure", "GCP",
        
        # Data Analysis & BI
        "Data Analysis", "Data Mining", "Statistical Modeling", "Tableau", 
        "Power BI", "SAS", "Model Building", "Algorithm Design",
        
        # AI/ML
        "Neural Networks", "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning",
        
        # Security
        "Ethical Hacking", "Risk Assessment", "Cryptography", "Firewalls", 
        "Incident Response", "Cybersecurity",
        
        # DevOps & Version Control
        "Git", "Version Control", "Docker", "Kubernetes", "CI/CD", "Jenkins",
        
        # Web Development
        "React", "Node.js", "API Development", "REST API", "GraphQL",
        
        # Databases
        "MySQL", "PostgreSQL", "MongoDB", "Oracle", "Database Design",
        
        # Engineering & Technical
        "AutoCAD", "SolidWorks", "MATLAB", "PLC Programming",
        
        # Operating Systems
        "Linux", "macOS", "Windows", "Unix",
        
        # Other Technical
        "Technical Writing", "Microsoft Office 365", "Google Workspace"
    ],
    
    "Software & Tools": [
        # CRM & Marketing
        "Salesforce", "HubSpot", "Marketo", "Mailchimp",
        
        # Office Suites
        "Microsoft Excel", "Microsoft Office 365", "Google Workspace",
        
        # Design Tools
        "Adobe Photoshop", "Illustrator", "InDesign", "Figma", "Sketch", 
        "UI/UX Design", "Canva",
        
        # Financial Software
        "QuickBooks", "SAP", "Xero", "Financial Modeling", "Advanced Excel",
        
        # Project Management
        "Jira", "Trello", "Asana", "Monday.com", "Microsoft Project",
        
        # Communication
        "Zendesk", "Slack", "Microsoft Teams",
        
        # Web Platforms
        "WordPress", "Shopify",
        
        # Analytics
        "Google Analytics 4", "SEO", "SEM", "A/B Testing",
        
        # Healthcare
        "EHR", "EMR", "Medical Coding", "Telehealth Platforms"
    ],
    
    "Leadership & Management": [
        # Core Leadership
        "Strategic Planning", "Team Leadership", "Project Management", 
        "Budgeting", "Resource Allocation", "Conflict Resolution", 
        "Mentoring", "Performance Tracking", "Cross-functional Collaboration",
        
        # Methodologies
        "Agile Methodology", "Scrum", "Lean Manufacturing", "Six Sigma", 
        "Change Management", "Kanban",
        
        # Management Skills
        "Operations Management", "Decision Making", "Delegation", 
        "Stakeholder Management", "Risk Assessment", "Business Development", 
        "Process Improvement", "Quality Assurance",
        
        # Strategic
        "Strategic Thinking", "Business Strategy", "Organizational Development"
    ],
    
    "Communication & Interpersonal": [
        # Communication Skills
        "Public Speaking", "Technical Writing", "Presentations", 
        "Active Listening", "Verbal Communication", "Written Correspondence",
        
        # Interpersonal
        "Empathy", "Diplomacy", "Adaptability", "Negotiation", "Persuasion", 
        "Conflict Resolution", "Emotional Intelligence", "Rapport Building",
        
        # Client-Facing
        "Client Relations", "Account Management", "Customer Service",
        
        # Collaboration
        "Teamwork", "Collaboration", "Facilitation", "Intercultural Communication",
        "Cross-Cultural Competency", "Non-verbal Communication"
    ],
    
    "Industry Knowledge": [
        # Regulatory & Compliance
        "Regulatory Compliance", "HIPAA", "GDPR", "OSHA", "GAAP", "IFRS",
        "Data Privacy", "Auditing",
        
        # Business & Market
        "Market Research", "Competitive Analysis", "Product Lifecycle Management", 
        "Supply Chain Management", "Business Acumen", "Financial Forecasting",
        
        # Quality & Risk
        "Quality Assurance", "Risk Management",
        
        # Customer & Product
        "Customer Journey Mapping", "Digital Transformation", 
        
        # Sustainability
        "Sustainable Practices", "ESG Reporting",
        
        # Strategy & Development
        "Change Management", "Strategic Storytelling", "Global Trade Policies",
        "Business Development"
    ],
    "Core Competencies": [
        "Analytical Skills", "Critical Thinking", "Problem Solving", "Strategic Planning",
        "Business Analysis", "Relationship Management", "Decision Making"
    ],
    "Professional Skills": [
        "Project Management", "Agile Methodology", "Scrum", "Business Strategy",
        "Operational Excellence", "Stakeholder Management", "Conflict Resolution"
    ],
    "Tools & Technologies": [
        "Jira", "Trello", "Asana", "Slack", "Microsoft Teams", "Zoom", "Docker",
        "Kubernetes", "Git", "GitHub", "VS Code", "Postman"
    ],
    "Languages": [
        "English", "Spanish", "French", "German", "Chinese", "Japanese", "Hindi"
    ],
    "Analytics": [
        "SQL", "Python", "Predictive Modeling", "A/B Testing", "Data Visualization",
        "Statistical Analysis", "Tableau", "Power BI"
    ],
    "Visual Design": [
        "Adobe Photoshop", "Illustrator", "Figma", "Sketch", "UI Design", "UX Design",
        "Graphic Design", "Typography"
    ],
    "Project Management Skills": [
        "Agile", "Scrum", "Risk Management", "Budget Control", "PMP", "PRINCE2",
        "Sprint Planning", "Resource Management"
    ],
    "Digital Marketing": [
        "SEO", "SEM", "Content Strategy", "Google Analytics", "Social Media Marketing",
        "Email Marketing", "PPC", "Marketing Automation"
    ]
}

# Hierarchical Skill Structure for more nuanced matching
SKILL_HIERARCHY = {
    "Technical": {
        "Software Engineering": {
            "Programming": ["Python", "Java", "C++", "JavaScript", "C#", "PHP", "Ruby", "Go", "Swift", "Kotlin", "Rust", "TypeScript"],
            "Web Development": {
                "Frontend": ["HTML5", "CSS3", "React", "Vue.js", "Angular", "Svelte", "Next.js", "Tailwind CSS"],
                "Backend": ["Node.js", "Django", "Flask", "FastAPI", "Spring Boot", "Laravel", "ASP.NET Core"],
                "API": ["REST API", "GraphQL", "gRPC", "WebSockets"]
            },
            "Mobile Development": ["Android", "iOS", "React Native", "Flutter", "Xamarin"],
            "Testing": ["Unit Testing", "Integration Testing", "Cypress", "Selenium", "Jest", "Pytest"]
        },
        "Data & AI": {
            "Data Science": ["Data Analysis", "Statistics", "Pandas", "NumPy", "R"],
            "Machine Learning": ["Neural Networks", "TensorFlow", "PyTorch", "Scikit-Learn", "Deep Learning", "NLP", "Computer Vision"],
            "Data Engineering": ["Spark", "Hadoop", "Airflow", "Kafka", "ETL Pipelines"],
            "BI & Visualization": ["Tableau", "Power BI", "Looker", "Data Visualization"]
        },
        "Cloud & DevOps": {
            "Cloud Platforms": ["AWS", "Azure", "GCP", "Heroku", "DigitalOcean"],
            "Containerization": ["Docker", "Kubernetes", "Container Orchestration"],
            "CI/CD": ["Jenkins", "GitHub Actions", "GitLab CI", "CircleCI"],
            "Infrastructure as Code": ["Terraform", "Ansible", "CloudFormation"]
        },
        "Databases": {
            "SQL": ["PostgreSQL", "MySQL", "SQL Server", "Oracle", "SQLite"],
            "NoSQL": ["MongoDB", "Redis", "Cassandra", "DynamoDB", "Elasticsearch"]
        },
        "Cybersecurity": ["Ethical Hacking", "Cryptography", "Network Security", "Penetration Testing", "Security Auditing"]
    },
    "Business & Management": {
        "Project Management": ["Agile", "Scrum", "Kanban", "PMP", "Prince2", "Jira", "Asana"],
        "Leadership": ["Team Leadership", "Strategic Planning", "Mentoring", "Stakeholder Management"],
        "Business Operations": ["Operations Management", "Supply Chain", "Budgeting", "Resource Allocation"],
        "Sales & Marketing": ["CRM", "Salesforce", "SEO", "Content Strategy", "Digital Marketing"]
    }
}

# Transferable skills identification (Inference Map)
# If a candidate has these roles/experiences, they likely have these skills
TRANSFERABLE_SKILLS = {
    "Customer Support": ["Communication", "Problem Solving", "Empathy", "Conflict Resolution", "Patience"],
    "Leadership": ["Management", "Strategic Planning", "Mentoring", "Decision Making"],
    "Project Management": ["Organization", "Time Management", "Leadership", "Stakeholder Management"],
    "Technical Writing": ["Communication", "Attention to Detail", "Documentation"],
    "Teaching": ["Communication", "Public Speaking", "Mentoring", "Patience"],
    "Research": ["Analytical Skills", "Critical Thinking", "Problem Solving", "Writing"]
}

# Create a flattened version of hierarchy for backward compatibility
def flatten_hierarchy(hierarchy, prefix=""):
    flat = {}
    for key, value in hierarchy.items():
        if isinstance(value, dict):
            child_flat = flatten_hierarchy(value)
            # Add all skills from children to this parent category too
            all_child_skills = []
            for sub_skills in child_flat.values():
                all_child_skills.extend(sub_skills)
            flat[key] = list(set(all_child_skills))
            # Merge child categories
            for k, v in child_flat.items():
                flat[k] = v
        else:
            flat[key] = value
    return flat

# Update SKILL_CATEGORIES from hierarchy
NEW_FLAT_CATEGORIES = flatten_hierarchy(SKILL_HIERARCHY)
for cat, skills in NEW_FLAT_CATEGORIES.items():
    if cat not in SKILL_CATEGORIES:
        SKILL_CATEGORIES[cat] = []
    for skill in skills:
        if skill not in SKILL_CATEGORIES[cat]:
            SKILL_CATEGORIES[cat].append(skill)

# Create a flattened lookup for quick category identification
SKILL_TO_CATEGORY = {}
for category, skills in SKILL_CATEGORIES.items():
    for skill in skills:
        SKILL_TO_CATEGORY[skill.lower()] = category

# Skill synonyms for better matching and normalization
SKILL_SYNONYMS = {
    # Programming Languages
    "python3": "Python",
    "python 3": "Python",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "ts": "TypeScript",
    "golang": "Go",
    "cpp": "C++",
    "c plus plus": "C++",
    "c#": "C#",
    "c sharp": "C#",
    
    # Web Frameworks
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "vue": "Vue.js",
    "vuejs": "Vue.js",
    "vue.js": "Vue.js",
    "angular": "Angular",
    "angularjs": "Angular",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "express": "Express",
    "expressjs": "Express",
    
    # AI/ML
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "neural nets": "Neural Networks",
    "nlp": "Natural Language Processing",
    
    # Cloud
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    
    # DevOps
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    
    # Others
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "git": "Git",
    "github": "GitHub",
    "docker": "Docker",
}

# Extend SKILL_TO_CATEGORY with synonyms
for synonym, canonical in SKILL_SYNONYMS.items():
    synonym_lower = synonym.lower()
    if canonical.lower() in SKILL_TO_CATEGORY:
        SKILL_TO_CATEGORY[synonym_lower] = SKILL_TO_CATEGORY[canonical.lower()]

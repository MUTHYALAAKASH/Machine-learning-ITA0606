import os
import random
import pandas as pd
import numpy as np

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

def generate_job_dataset(num_samples=5000, scam_ratio=0.18):
    """
    Generates a realistic, diverse dataset modeled after the EMSCAD 
    (Employment Scam Aegean Dataset) for fake job posting detection.
    """
    
    # Legitimate Job Templates & Data Pools
    legit_titles = [
        "Senior Software Engineer", "Full Stack Developer", "Data Scientist", "DevOps Engineer",
        "Frontend React Developer", "Cloud Solutions Architect", "Machine Learning Engineer",
        "Financial Analyst", "Staff Accountant", "Investment Banking Associate", "Risk Manager",
        "Registered Nurse (RN)", "Clinical Research Coordinator", "Medical Assistant",
        "Digital Marketing Manager", "Content Strategist", "Product Marketing Specialist",
        "Human Resources Generalist", "Talent Acquisition Specialist", "HR Business Partner",
        "Customer Success Manager", "Technical Support Specialist", "Client Relationship Officer",
        "Operations Manager", "Supply Chain Analyst", "Logistics Coordinator", "Project Manager",
        "Cybersecurity Analyst", "Database Administrator", "QA Automation Engineer"
    ]
    
    legit_companies = [
        "Apex Cloud Technologies", "Meridian Health Solutions", "Vanguard Financial Partners",
        "Nexus Data Systems", "OmniGlobal Logistics", "Beacon Creative Media",
        "Elevate Biotech Labs", "Pinnacle Enterprise Software", "Horizon Energy Systems",
        "Quantum Security Group", "BlueSky Retail Innovations", "Crestview Capital Advisory"
    ]
    
    legit_profiles = [
        "We are an established industry leader with over 15 years of delivering cutting-edge software solutions to Fortune 500 enterprises globally.",
        "Founded in 2012, our organization is dedicated to providing high-quality healthcare and medical diagnostics with state-of-the-art facilities.",
        "A premier financial advisory and investment firm managing diversified portfolios with a strong emphasis on regulatory compliance and transparency.",
        "A fast-growing venture-backed technology startup revolutionizing cloud orchestration and scalable distributed systems.",
        "A multinational logistics and supply chain enterprise operating across 40 countries, committed to operational excellence and sustainability.",
        "A creative digital agency partnering with global brands to design compelling user experiences, digital marketing campaigns, and brand identities."
    ]
    
    legit_descriptions = [
        "We are seeking an experienced professional to join our core team. In this role, you will collaborate with cross-functional teams, participate in architectural design reviews, and build robust, high-performance systems. The ideal candidate exhibits strong analytical problem-solving abilities and a track record of successful project execution.",
        "Join our dynamic department as we expand our market presence. You will be responsible for managing day-to-day operations, conducting deep-dive data analysis, preparing executive reports, and driving process automation. You will work closely with department heads and external stakeholders.",
        "An exciting opportunity to lead impactful initiatives in a collaborative environment. Key responsibilities include designing scalable workflows, monitoring performance metrics, mentoring junior staff members, and adhering to strict industry standards and governance protocols.",
        "We are looking for a dedicated specialist to support our growing customer base. You will analyze complex technical requirements, troubleshoot escalation issues, document standard operating procedures, and continuously improve service delivery standards."
    ]
    
    legit_requirements = [
        "Bachelor's or Master's degree in Computer Science, Engineering, Business, or related discipline. Minimum 3-5 years of hands-on professional experience. Proficiency with modern tooling, version control, and agile methodologies. Excellent written and verbal communication skills.",
        "Demonstrated expertise with analytical frameworks, statistical modeling, and relational databases (SQL, PostgreSQL). Strong organizational skills with ability to prioritize competing deadlines in a fast-paced environment.",
        "Valid state licensure or professional certification where applicable. At least 2+ years of relevant clinical or corporate experience. Proven interpersonal skills with a commitment to high ethics and customer privacy.",
        "Strong leadership and collaboration skills. Experience working with cloud platforms (AWS, GCP, or Azure), CI/CD pipelines, and enterprise software architectures. Detail-oriented approach to code quality and testing."
    ]
    
    legit_benefits = [
        "Comprehensive health, dental, and vision insurance. 401(k) matching program up to 5%. Generous paid time off (PTO) and parental leave. Annual professional development stipend.",
        "Competitive base salary plus performance bonuses. Flexible hybrid work schedule. Wellness programs, gym membership reimbursement, and life insurance.",
        "Equity options, top-tier medical benefits with low deductibles, paid volunteer days, modern tech stipend, and catered office lunches.",
        "Medical/Dental coverage, tuition reimbursement, employee assistance program, retirement pension options, and company-matched charitable donations."
    ]
    
    legit_industries = [
        "Information Technology", "Financial Services", "Hospital & Health Care",
        "Marketing & Advertising", "Logistics & Supply Chain", "Management Consulting",
        "Higher Education", "Telecommunications", "Biotechnology"
    ]
    
    legit_functions = [
        "Engineering", "Information Technology", "Finance", "Healthcare",
        "Marketing", "Human Resources", "Sales", "Customer Service", "Operations"
    ]
    
    # Scam Job Templates & Data Pools
    scam_titles = [
        "URGENT: Work From Home Data Entry Clerk ($45/hr)",
        "Home Based Customer Service Representative - Immediate Start",
        "Mystery Shopper / Quality Assurance Inspector - Earn Weekly Cash",
        "Virtual Assistant / Personal Assistant to Senior Executive",
        "Remote Payment Processing Agent - No Experience Needed",
        "Immediate Opening: Package Reshipment Specialist (High Pay)",
        "Crypto Account Manager / Bitcoin Transaction Assistant",
        "Data Entry / Typing Specialist - Flexible Hours Daily Payout",
        "Online Order Processor - Work 2 Hours a Day Make $3000/Month",
        "Administrative Office Assistant - Work from Anywhere Immediately",
        "Online Survey Evaluator & Product Reviewer (Easy Cash)",
        "Remote Financial Transaction Clerk - Instant Hiring"
    ]
    
    scam_profiles = [
        "",  # Scammers often omit company profiles
        "Global international company recruiting independent contractors worldwide for quick remote projects.",
        "We are a newly established overseas consulting firm expanding into the United States and Canada with lucrative opportunities.",
        "Private VIP executive seeking reliable personal assistant to handle confidential correspondence and errands remotely.",
        "Premier international payment clearing syndicate facilitating peer-to-peer foreign currency exchanges."
    ]
    
    scam_descriptions = [
        "URGENTLY HIRING! We are looking for self-motivated individuals to work from the comfort of their home. No previous experience required! Guaranteed weekly paycheck between $1200 - $2500 depending on hours. You will receive assignments daily via email or messaging app. Must be able to follow simple instructions and start immediately. To apply, contact our hiring manager Dr. Robert Smith directly on Telegram: @HireManager2026 or WhatsApp with your full name and resume.",
        "Earn easy money working just 2-3 hours per day! We will provide you with a company check or advance funds to purchase necessary office equipment (laptop, printer, software license) from our certified vendor. Your duty is to cash the check, deposit into your personal account, deduct your weekly commission of $600, and forward the balance via Western Union, MoneyGram, or Zelle.",
        "SECRET SHOPPER OPPORTUNITY: Evaluate major retail outlets and financial wire transfer services in your neighborhood. You will be sent an official cashier check ranging from $2000 to $4500. Cash the check at your local bank, keep $400 as your mystery evaluation fee, and test the customer service speed by wiring the remaining funds via Bitcoin ATM or gift cards.",
        "Work from home data entry typing job. Earn $35 to $60 per hour. Flexible timings, students and stay-at-home parents welcome. No interview required! Immediate selection. You must have a smartphone or computer with internet connection. Reach out to HR department on Telegram @OnlineRecruitmentHR immediately to confirm your position today.",
        "Financial transaction assistant needed immediately. Your primary duty will be receiving company payments, converting to cryptocurrency (USDT / Bitcoin), and transferring to company vendor wallets. High commissions of 10% per transaction. Daily payouts guaranteed without delay."
    ]
    
    scam_requirements = [
        "No experience required! Must have an active bank account (minimum 6 months old) capable of receiving wire transfers and mobile check deposits. Must have a smartphone and access to Telegram or WhatsApp for daily communications.",
        "Any degree or high school diploma accepted. Must be 18 years or older, honest, trustworthy, and able to execute banking transactions promptly within 24 hours of receiving instructions.",
        "Basic computer literacy, typing skills, willingness to work unsupervised. Immediate availability is mandatory. Must have a valid checking account to process vendor payments.",
        "No resume needed. Just contact hiring manager on WhatsApp / Telegram for quick online orientation and background registration."
    ]
    
    scam_benefits = [
        "Daily or weekly payouts via CashApp, PayPal, Zelle, or Western Union. Free company laptop after 30 days of probationary period. High bonuses for fast check clearing.",
        "Make your own schedule! Earn up to $5000 per month without leaving your bedroom. Free training provided via text messaging. No boss looking over your shoulder.",
        "Huge performance incentives, quick cash bonuses, complete freedom to work from anywhere in the world.",
        "Immediate payment advance, travel allowance, zero commute, guaranteed income."
    ]
    
    scam_industries = [
        "Telecommunications", "Financial Services", "Retail",
        "Consumer Services", "Administrative Support", ""
    ]
    
    scam_functions = [
        "Customer Service", "Administrative", "Finance", "General Business", ""
    ]
    
    rows = []
    num_scams = int(num_samples * scam_ratio)
    num_legit = num_samples - num_scams
    
    # Generate Legitimate Postings
    for i in range(num_legit):
        title = random.choice(legit_titles)
        company = random.choice(legit_companies)
        profile = random.choice(legit_profiles)
        desc = random.choice(legit_descriptions)
        reqs = random.choice(legit_requirements)
        bens = random.choice(legit_benefits)
        industry = random.choice(legit_industries)
        function = random.choice(legit_functions)
        
        # Real companies usually have logos (85%) and screening questions (75%)
        has_logo = 1 if random.random() < 0.85 else 0
        has_questions = 1 if random.random() < 0.75 else 0
        telecommuting = 1 if random.random() < 0.35 else 0
        
        rows.append({
            "job_id": i + 1,
            "title": title,
            "company_profile": profile,
            "description": desc,
            "requirements": reqs,
            "benefits": bens,
            "telecommuting": telecommuting,
            "has_company_logo": has_logo,
            "has_questions": has_questions,
            "employment_type": random.choice(["Full-time", "Part-time", "Contract", "Permanent"]),
            "required_experience": random.choice(["Mid-Senior level", "Associate", "Entry level", "Director"]),
            "required_education": random.choice(["Bachelor's Degree", "Master's Degree", "High School or equivalent", "Unspecified"]),
            "industry": industry,
            "function": function,
            "fraudulent": 0
        })
        
    # Generate Scam Postings
    for j in range(num_scams):
        title = random.choice(scam_titles)
        profile = random.choice(scam_profiles)
        desc = random.choice(scam_descriptions)
        reqs = random.choice(scam_requirements)
        bens = random.choice(scam_benefits)
        industry = random.choice(scam_industries)
        function = random.choice(scam_functions)
        
        # Fake jobs rarely have logos (only ~15%) and rarely have actual structured questions (~20%)
        has_logo = 1 if random.random() < 0.15 else 0
        has_questions = 1 if random.random() < 0.20 else 0
        telecommuting = 1 if random.random() < 0.85 else 0 # Mostly "work from home"
        
        rows.append({
            "job_id": num_legit + j + 1,
            "title": title,
            "company_profile": profile,
            "description": desc,
            "requirements": reqs,
            "benefits": bens,
            "telecommuting": telecommuting,
            "has_company_logo": has_logo,
            "has_questions": has_questions,
            "employment_type": random.choice(["Full-time", "Part-time", "Contract", "Temporary", ""]),
            "required_experience": random.choice(["Entry level", "Not Applicable", ""]),
            "required_education": random.choice(["High School or equivalent", "Unspecified", ""]),
            "industry": industry,
            "function": function,
            "fraudulent": 1
        })
        
    # Shuffle dataset thoroughly
    random.shuffle(rows)
    df = pd.DataFrame(rows)
    
    return df

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = generate_job_dataset(num_samples=5000, scam_ratio=0.18)
    output_path = os.path.join("data", "fake_job_postings.csv")
    df.to_csv(output_path, index=False)
    print(f"Successfully generated dataset with {len(df)} rows ({df['fraudulent'].sum()} fraudulent, {len(df) - df['fraudulent'].sum()} legitimate).")
    print(f"Saved to: {output_path}")

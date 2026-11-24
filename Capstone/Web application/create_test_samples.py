import os
from PIL import Image, ImageDraw, ImageFont

def generate_sample_images():
    output_dir = "sample_images"
    os.makedirs(output_dir, exist_ok=True)

    # -------------------------------------------------------------
    # 1. FAKE JOB 1: TELEGRAM / WHATSAPP WORK FROM HOME DATA ENTRY
    # -------------------------------------------------------------
    img1 = Image.new("RGB", (650, 480), color="#fff1f2")
    d1 = ImageDraw.Draw(img1)
    
    # Outer red caution border
    d1.rectangle([(10, 10), (640, 470)], outline="#f43f5e", width=3)
    
    # Red header banner
    d1.rectangle([(10, 10), (640, 75)], fill="#e11d48")
    d1.text((25, 25), "URGENT HIRING: REMOTE DATA ENTRY CLERK", fill="#ffffff")
    d1.text((25, 48), "IMMEDIATE START - NO INTERVIEW REQUIRED", fill="#fecdd3")
    
    # Content body
    body_fake1 = [
        "Earn $48.00 / Hour working from home! Flexible 2-3 hours/day.",
        "Guaranteed weekly payouts between $1,200 - $2,500 via Zelle / CashApp.",
        "",
        "Job Duties:",
        "- Simple copy-paste typing and file forwarding.",
        "- We provide advance company check to purchase equipment",
        "  (laptop, printer) from our certified vendor.",
        "- Deposit the check, keep your weekly commission, wire balance.",
        "",
        "Requirements:",
        "- Must have an active personal checking account to deposit checks.",
        "- Must have smartphone with Telegram or WhatsApp.",
        "",
        "TO APPLY NOW:",
        "Contact Hiring Manager Dr. Robert on Telegram: @Robert_Hire2026",
        "Or text WhatsApp: +1 (555) 019-2834 with your full name."
    ]
    
    y = 95
    for line in body_fake1:
        if line.startswith("TO APPLY") or line.startswith("URGENT"):
            color = "#be123c"
        elif line.startswith("Requirements:") or line.startswith("Job Duties:"):
            color = "#0f172a"
        else:
            color = "#334155"
        d1.text((30, y), line, fill=color)
        y += 22
        
    p1 = os.path.join(output_dir, "fake_job_telegram_data_entry.png")
    img1.save(p1)
    print(f"Created: {p1}")

    # -------------------------------------------------------------
    # 2. FAKE JOB 2: CASHIER CHECK MYSTERY SHOPPER SCAM
    # -------------------------------------------------------------
    img2 = Image.new("RGB", (650, 460), color="#fff7ed")
    d2 = ImageDraw.Draw(img2)
    
    # Amber/orange border
    d2.rectangle([(10, 10), (640, 450)], outline="#f97316", width=3)
    d2.rectangle([(10, 10), (640, 75)], fill="#ea580c")
    d2.text((25, 25), "SECRET SHOPPER & EVALUATOR WANTED", fill="#ffffff")
    d2.text((25, 48), "EARN $500 PER SURVEY - WEEKLY CASH COMMISSIONS", fill="#ffedd5")
    
    body_fake2 = [
        "Earn quick cash evaluating local banking and wire transfer outlets!",
        "",
        "How It Works:",
        "1. We mail you an official Cashier's Check for $3,850.",
        "2. Deposit check into your personal bank account.",
        "3. Keep $500 as your mystery evaluation fee.",
        "4. Test customer service speed by wiring the remaining $3,350",
        "   via Western Union, MoneyGram, or Bitcoin ATM.",
        "",
        "Qualifications:",
        "- Must have checking account open for at least 6 months.",
        "- Honest, reliable, must execute transfers within 24 hours.",
        "- No previous experience or resume required.",
        "",
        "Contact us on WhatsApp: +1 (555) 018-9922 to confirm your check mailing."
    ]
    
    y = 95
    for line in body_fake2:
        if "Western Union" in line or "Cashier's Check" in line or "WhatsApp" in line:
            color = "#c2410c"
        else:
            color = "#334155"
        d2.text((30, y), line, fill=color)
        y += 23
        
    p2 = os.path.join(output_dir, "fake_job_check_mystery_shopper.png")
    img2.save(p2)
    print(f"Created: {p2}")

    # -------------------------------------------------------------
    # 3. VALID JOB 1: SENIOR SOFTWARE ENGINEER (TECH COMPANY)
    # -------------------------------------------------------------
    img3 = Image.new("RGB", (650, 500), color="#f8fafc")
    d3 = ImageDraw.Draw(img3)
    
    # Clean professional blue header
    d3.rectangle([(10, 10), (640, 490)], outline="#cbd5e1", width=2)
    d3.rectangle([(10, 10), (640, 80)], fill="#1e293b")
    
    # Logo representation
    d3.rectangle([(25, 22), (65, 65)], fill="#3b82f6")
    d3.text((35, 30), "N", fill="#ffffff")
    
    d3.text((80, 25), "Apex Cloud Technologies Inc. | Official Career Portal", fill="#94a3b8")
    d3.text((80, 48), "Senior Backend Software Engineer (Python / Distributed Systems)", fill="#ffffff")
    
    body_valid1 = [
        "Job ID: ACT-2026-8942 | Location: San Francisco, CA (Hybrid Remote)",
        "Department: Core Infrastructure Engineering | Employment: Full-time",
        "",
        "About the Role:",
        "We are seeking an experienced Senior Software Engineer to design, scale,",
        "and maintain our real-time streaming data processing pipeline.",
        "",
        "Key Qualifications & Requirements:",
        "- Bachelor's or Master's degree in Computer Science or related field.",
        "- 5+ years production experience with Python, Go, or Java.",
        "- Strong proficiency in PostgreSQL, Redis, Apache Kafka, and Docker.",
        "- Solid understanding of microservice architectures and CI/CD pipelines.",
        "",
        "Benefits & Perks:",
        "- Competitive base salary ($155,000 - $185,000) + equity options.",
        "- Comprehensive health, dental, and vision insurance with low deductible.",
        "- 401(k) matching up to 5%, generous PTO, and annual learning stipend.",
        "",
        "Apply online via our official career portal: https://careers.apexcloud.io"
    ]
    
    y = 98
    for line in body_valid1:
        if line.startswith("Key Qualifications") or line.startswith("Benefits"):
            color = "#0f172a"
        elif "careers.apexcloud.io" in line:
            color = "#1d68eb"
        else:
            color = "#475569"
        d3.text((30, y), line, fill=color)
        y += 21
        
    p3 = os.path.join(output_dir, "valid_job_software_engineer.png")
    img3.save(p3)
    print(f"Created: {p3}")

    # -------------------------------------------------------------
    # 4. VALID JOB 2: CLINICAL RESEARCH COORDINATOR (HEALTHCARE)
    # -------------------------------------------------------------
    img4 = Image.new("RGB", (650, 490), color="#f8fafc")
    d4 = ImageDraw.Draw(img4)
    
    d4.rectangle([(10, 10), (640, 480)], outline="#cbd5e1", width=2)
    d4.rectangle([(10, 10), (640, 80)], fill="#0f766e")
    
    # Hospital cross logo
    d4.rectangle([(25, 22), (65, 65)], fill="#ffffff")
    d4.text((40, 32), "+", fill="#0f766e")
    
    d4.text((80, 25), "Meridian Health Solutions | Academic Medical Center", fill="#ccfbf1")
    d4.text((80, 48), "Clinical Research Operations Coordinator (RN / BSN)", fill="#ffffff")
    
    body_valid2 = [
        "Req ID: MHS-9021 | Location: Boston, MA | Department: Oncology Research",
        "",
        "Position Summary:",
        "Coordinate clinical trial execution for novel oncology therapeutics.",
        "Ensure strict adherence to FDA regulations, IRB protocols, and HIPAA.",
        "",
        "Minimum Requirements:",
        "- Bachelor's Degree in Nursing (BSN) or Life Sciences.",
        "- Active State Registered Nurse (RN) license or ACRP/SOCRA certification.",
        "- 2+ years experience in clinical trial coordination or patient management.",
        "- Excellent written documentation and patient communication skills.",
        "",
        "Compensation & Benefits:",
        "- Competitive pay ($85,000 - $105,000), state pension retirement plan.",
        "- Full medical, dental, and vision coverage, 25 days paid vacation.",
        "- Tuition assistance and continuing medical education (CME) budget.",
        "",
        "Apply directly at: https://meridianhealth.org/careers/requisition/9021"
    ]
    
    y = 98
    for line in body_valid2:
        if line.startswith("Minimum Requirements") or line.startswith("Compensation"):
            color = "#0f172a"
        elif "meridianhealth.org" in line:
            color = "#0f766e"
        else:
            color = "#475569"
        d4.text((30, y), line, fill=color)
        y += 21
        
    p4 = os.path.join(output_dir, "valid_job_clinical_coordinator.png")
    img4.save(p4)
    print(f"Created: {p4}")

if __name__ == "__main__":
    generate_sample_images()

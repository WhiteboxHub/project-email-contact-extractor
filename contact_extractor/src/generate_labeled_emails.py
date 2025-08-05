import pandas as pd
import random
import os

recruiter_names = [
    "John Doe", "Jane Smith", "Alex Johnson", "Priya Patel", "Michael Lee", "Sara Kim", "David Brown", "Emily Clark",
    "Chris Evans", "Olivia White", "Liam Miller", "Sophia Turner", "Noah Wilson", "Ava Harris", "Mason Lewis", "Isabella Young",
    "Ethan Carter", "Charlotte Brooks", "Lucas Scott", "Megan Reed", "Benjamin Hall", "Ella Turner", "Henry Adams", "Grace Lee"
]

companies = [
    "Acme Corp", "Globex Inc", "Initech", "Umbrella Corp", "Wayne Enterprises", "Stark Industries", "Wonka Industries",
    "Cyberdyne Systems", "Hooli", "Massive Dynamic", "Pied Piper", "Vandelay Industries", "Dunder Mifflin", "Prestige Worldwide",
    "Monsters Inc", "Oscorp", "Tyrell Corporation", "Soylent Corp", "Virtucon", "Gringotts Bank", "Gekko & Co", "Duff Beer",
    "Oceanic Airlines", "Good Burger", "OpenAI", "DeepMind", "NVIDIA", "Google AI", "Meta AI", "Anthropic", "Cohere",
    "Hugging Face", "Databricks", "UiPath", "DataRobot", "C3.ai"
]

roles = [
    "Software Engineer", "Data Scientist", "Product Manager", "DevOps Engineer", "Business Analyst", "QA Tester", "UX Designer",
    "Cloud Architect", "Backend Developer", "Frontend Developer", "AI Researcher", "Mobile Developer", "Full Stack Developer",
    "IT Consultant", "System Administrator", "Network Engineer", "Technical Lead", "Support Engineer", "Business Development Manager",
    "Sales Engineer", "Machine Learning Engineer", "AI Engineer", "Deep Learning Engineer", "NLP Engineer",
    "Computer Vision Engineer", "MLOps Engineer", "Data Engineer", "Applied Scientist", "Research Scientist (AI/ML)",
    "AI Product Manager", "UI Developer", "UI Engineer", "React Developer", "Angular Developer", "Frontend UI Developer",
    "Fullstack UI Developer"
]

recruiter_emails = [
    "recruiter@acme.com", "hr@globex.com", "talent@initech.com", "careers@umbrella.com", "jobs@wayne.com", "opportunities@stark.com",
    "recruitment@hooli.com", "jobs@massivedynamic.com", "talent@piedpiper.com", "careers@vandelay.com", "hr@dundermifflin.com",
    "recruiter@tyrell.com", "hr@soylent.com", "talent@virtucon.com", "careers@gringotts.com", "jobs@gekko.com",
    "ai-jobs@openai.com", "ml-recruiter@deepmind.com", "careers@nvidia.com", "talent@huggingface.co", "jobs@uipath.com",
    "recruit@datarobot.com", "ai-recruiter@meta.com", "ml-jobs@google.com", "ui-jobs@cohere.com"
]

phones = [
    "+1-555-123-4567", "+1-555-987-6543", "+1-555-222-3333", "+1-555-444-5555", "+1-555-666-7777", "+1-555-888-9999",
    "+44-20-7946-0958", "+91-22-4000-1234"
]

recruiter_templates = [
    "Hi {name}, I am {recruiter} from {company}. We have an exciting opportunity for you as a {role}. Please contact me at {email} or {phone}.",
    "Dear {name}, I found your profile interesting for a {role} at {company}. Let's connect! Regards, {recruiter}, {email}, {phone}",
    "Hello {name}, We are hiring for a {role} at {company}. If interested, reply to {email} or call {phone}.",
    "Hi {name}, I came across your resume and wanted to discuss a {role} position at {company}. Contact me at {email}.",
    "Dear {name}, Are you open to new opportunities? We have a {role} opening at {company}. Regards, {recruiter}, {email}",
    "Hi {name}, I am reaching out from {company} regarding a {role} role. Let me know if you are interested. You can reach me at {email}.",
    "Hi {name}, We are seeking a {role} for our AI/ML platform at {company}. If interested, please send your resume to {email}.",
    "Hello {name}, Your expertise in UI and Fullstack development is in high demand at {company}. Let's discuss this {role} opportunity. Contact: {recruiter}, {email}, {phone}"
]

recruiter_subjects = [
    "Opportunity for {role} at {company}",
    "Exciting {role} Position at {company}",
    "Invitation to Interview at {company}",
    "Let's Connect: {role} Opening at {company}",
    "Career Opportunity: {role} at {company}",
    "Join Our Team as a {role} at {company}",
    "AI/ML Engineer Needed at {company}",
    "Fullstack UI Developer Opportunity at {company}"
]

spam_blacklist_emails = [
    "newsletter@randomsite.com", "noreply@offers.com", "support@fakebank.com", "alerts@shopping.com",
    "info@spammy.com", "promo@deals.com", "no-reply@updates.com", "recruiter@jobboard.com"
]

spam_blacklist_subjects = [
    "Your Weekly Newsletter", "Congratulations! You've Won", "Don't Miss Out!", "Special Offer Just for You",
    "Update Your Account", "Last Chance!", "Security Alert", "Black Friday Deals"
]

spam_blacklist_bodies = [
    "Click here to claim your prize now!", "This is your last chance to save big on our products.",
    "Dear user, your account needs to be updated. Please login to continue.",
    "Exclusive offer: Get 50% off on all items. Limited time only!",
    "Reset your password by clicking the link below.",
    "Security alert: Suspicious login detected. Please confirm your identity.",
    "Don't miss our exclusive Black Friday deals!"
]

gray_subjects = [
    "Job Alert: New Openings in Your Area", "Networking Opportunity", "Professional Network Invitation"
]

gray_bodies = [
    "We found new job openings that match your profile. Click here to view more.",
    "Join our platform to expand your professional network.",
    "You have been invited to join our professional network."
]

gray_emails = [
    "jobs@jobboard.com", "networking@platform.com", "invite@business.com"
]

data = []

for _ in range(3000):
    name = random.choice(recruiter_names)
    recruiter = random.choice(recruiter_names)
    company = random.choice(companies)
    role = random.choice(roles)
    email = random.choice(recruiter_emails)
    phone = random.choice(phones)
    subject = random.choice(recruiter_subjects).format(role=role, company=company)
    body = random.choice(recruiter_templates).format(name=name, recruiter=recruiter, company=company, role=role, email=email, phone=phone)
    data.append({
        "subject": subject,
        "body": body,
        "from_email": email,
        "label": 1
    })

for _ in range(3000):
    r = random.random()
    if r < 0.7:
        subject = random.choice(spam_blacklist_subjects)
        body = random.choice(spam_blacklist_bodies)
        from_email = random.choice(spam_blacklist_emails)
    elif r < 0.9:
        subject = random.choice(gray_subjects)
        body = random.choice(gray_bodies)
        from_email = random.choice(gray_emails)
    else:
        subject = "Notification from System"
        body = "This is an automated message. Please do not reply."
        from_email = "system@company.com"
    data.append({
        "subject": subject,
        "body": body,
        "from_email": from_email,
        "label": 0
    })

random.shuffle(data)
df = pd.DataFrame(data)

# Ensure the output directory exists
output_path = os.path.join("..", "data")
os.makedirs(output_path, exist_ok=True)

df.to_csv(os.path.join(output_path, "labeled_emails.csv"), index=False)
print("✅ Generated labeled_emails.csv with", len(df), "rows.")


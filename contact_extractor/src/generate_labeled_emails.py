import pandas as pd
import random 

# Expanded pools for recruiter/vendor (positive) and spam/junk (negative) examples
recruiter_names = [
    "John Doe", "Jane Smith", "Alex Johnson", "Priya Patel", "Michael Lee", "Sara Kim", "David Brown", "Emily Clark",
    "Chris Evans", "Olivia White", "Liam Miller", "Sophia Turner", "Noah Wilson", "Ava Harris", "Mason Lewis", "Isabella Young",
    "Ethan Carter", "Charlotte Brooks", "Lucas Scott", "Megan Reed", "Benjamin Hall", "Ella Turner", "Henry Adams", "Grace Lee"
]
companies = [
    "Acme Corp", "Globex Inc", "Initech", "Umbrella Corp", "Wayne Enterprises", "Stark Industries", "Wonka Industries", "Cyberdyne Systems",
    "Hooli", "Massive Dynamic", "Pied Piper", "Vandelay Industries", "Dunder Mifflin", "Prestige Worldwide", "Monsters Inc", "Oscorp",
    "Tyrell Corporation", "Soylent Corp", "Virtucon", "Gringotts Bank", "Gekko & Co", "Duff Beer", "Oceanic Airlines", "Good Burger",
    # Add more AI/ML and UI/Fullstack relevant companies
    "OpenAI", "DeepMind", "NVIDIA", "Google AI", "Meta AI", "Anthropic", "Cohere", "Hugging Face", "Databricks", "UiPath", "DataRobot", "C3.ai"
]
roles = [
    "Software Engineer", "Data Scientist", "Product Manager", "DevOps Engineer", "Business Analyst", "QA Tester", "UX Designer", "Cloud Architect",
    "Backend Developer", "Frontend Developer", "AI Researcher", "Mobile Developer", "Full Stack Developer", "IT Consultant", "System Administrator",
    "Network Engineer", "Technical Lead", "Support Engineer", "Business Development Manager", "Sales Engineer",
    # Add more AI/ML and UI/Fullstack roles
    "Machine Learning Engineer", "AI Engineer", "Deep Learning Engineer", "NLP Engineer", "Computer Vision Engineer",
    "MLOps Engineer", "Data Engineer", "Applied Scientist", "Research Scientist (AI/ML)", "AI Product Manager",
    "UI Developer", "UI Engineer", "React Developer", "Angular Developer", "Frontend UI Developer", "Fullstack UI Developer"
]
recruiter_emails = [
    "recruiter@acme.com", "hr@globex.com", "talent@initech.com", "careers@umbrella.com", "jobs@wayne.com", "opportunities@stark.com",
    "recruitment@hooli.com", "jobs@massivedynamic.com", "talent@piedpiper.com", "careers@vandelay.com", "hr@dundermifflin.com",
    "recruiter@tyrell.com", "hr@soylent.com", "talent@virtucon.com", "careers@gringotts.com", "jobs@gekko.com",
    # Add more AI/ML and UI/Fullstack recruiter emails
    "ai-jobs@openai.com", "ml-recruiter@deepmind.com", "careers@nvidia.com", "talent@huggingface.co", "jobs@uipath.com",
    "recruit@datarobot.com", "ai-recruiter@meta.com", "ml-jobs@google.com", "ui-jobs@cohere.com"
]
phones = [
    "+1-555-123-4567", "+1-555-987-6543", "+1-555-222-3333", "+1-555-444-5555", "+1-555-666-7777", "+1-555-888-9999",
    "+44-20-7946-0958", "+91-22-4000-1234"
]

# Recruiter/vendor templates (positive)
recruiter_templates = [
    "Hi {name}, I am {recruiter} from {company}. We have an exciting opportunity for you as a {role}. Please contact me at {email} or {phone}.",
    "Dear {name}, I found your profile interesting for a {role} at {company}. Let's connect! Regards, {recruiter}, {email}, {phone}",
    "Hello {name}, We are hiring for a {role} at {company}. If interested, reply to {email} or call {phone}.",
    "Hi {name}, I came across your resume and wanted to discuss a {role} position at {company}. Contact me at {email}.",
    "Dear {name}, Are you open to new opportunities? We have a {role} opening at {company}. Regards, {recruiter}, {email}",
    "Hi {name}, I am reaching out from {company} regarding a {role} role. Let me know if you are interested. You can reach me at {email}.",
    "Hello {name}, Your experience seems like a great fit for our {role} position at {company}. Please let me know if you are interested.",
    "Dear {name}, We are expanding our team at {company} and would like to consider you for a {role} position. Contact: {recruiter}, {email}, {phone}",
    "Hi {name}, I noticed your background in {role}. We have a similar opening at {company}. Let's connect!",
    "Hello {name}, I am {recruiter} from {company}. We are looking for a {role}. If you are interested, please reply to this email.",
    "Dear {name}, I would like to invite you to interview for a {role} at {company}. Please let me know your availability.",
    "Hi {name}, We have reviewed your profile and would like to discuss a {role} opportunity at {company}. Regards, {recruiter}, {email}, {phone}",
    "Hello {name}, Are you interested in a new {role} role? {company} is hiring! Contact me at {email}.",
    "Dear {name}, I am {recruiter} from {company}. We are impressed by your experience and would like to discuss a {role} position.",
    "Hi {name}, This is {recruiter} from {company}. We are a staffing agency with a {role} opening. Please reply if interested.",
    "Dear {name}, Our client {company} is looking for a {role}. If you are interested, please send your resume to {email}.",
    "Hello {name}, I am a vendor partner with {company}. We have a contract {role} position available. Contact me at {email}.",
    # AI/ML and Fullstack UI specific recruiter templates
    "Hi {name}, We are looking for talented individuals for an AI/ML project at {company}. Your background in {role} is a great fit. Please reach out at {email}.",
    "Dear {name}, {company} is expanding its AI/ML team and we think your experience as a {role} would be valuable. Let's connect at {email} or {phone}.",
    "Hello {name}, We have an urgent requirement for a Fullstack UI Developer at {company}. If you are interested, please contact me at {email}.",
    "Hi {name}, Our AI research group at {company} is hiring for {role}. Would you be open to a quick call? Regards, {recruiter}, {email}",
    "Dear {name}, We are building next-gen ML products at {company} and would love to have you as a {role}. Please reply to {email}.",
    "Hello {name}, Your expertise in UI and Fullstack development is in high demand at {company}. Let's discuss this {role} opportunity. Contact: {recruiter}, {email}, {phone}",
    "Hi {name}, We are seeking a {role} for our AI/ML platform at {company}. If interested, please send your resume to {email}.",
    "Dear {name}, {company} is hiring for multiple AI/ML and Fullstack UI roles. Your profile stood out to us. Let's connect at {email}."
]

recruiter_subjects = [
    "Opportunity for {role} at {company}",
    "Exciting {role} Position at {company}",
    "Invitation to Interview at {company}",
    "Let's Connect: {role} Opening at {company}",
    "Your Profile Matches Our {role} Role",
    "Career Opportunity: {role} at {company}",
    "Interested in a {role} Role at {company}?",
    "We Want You for {role} at {company}",
    "Immediate Opening: {role} at {company}",
    "Join Our Team as a {role} at {company}",
    "Contract {role} Opportunity at {company}",
    "Staffing Opportunity: {role} at {company}",
    "AI/ML Engineer Needed at {company}",
    "Join Our AI Research Team as a {role} at {company}",
    "Fullstack UI Developer Opportunity at {company}",
    "Machine Learning Role at {company}",
    "Exciting AI/ML and UI Roles at {company}",
    "Invitation: Interview for {role} (AI/ML) at {company}",
    "Immediate Opening: Fullstack UI at {company}"
]

spam_blacklist_emails = [
    "newsletter@randomsite.com", "noreply@offers.com", "support@fakebank.com", "alerts@shopping.com",
    "info@spammy.com", "promo@deals.com", "no-reply@updates.com", "service@subscriptions.com",
    "billing@onlineshop.com", "security@webmail.com", "offers@superdeals.com", "contact@randompromo.com",
    "jobs-listings@linkedin.com", "newsletters-noreply@linkedin.com", "inmail-hit-reply@linkedin.com",
    "hit-reply@linkedin.com", "indeedapply@indeed.com", "messages-noreply@linkedin.com",
    "jobalerts-noreply@linkedin.com", "editors-noreply@linkedin.com", "groups-noreply@linkedin.com",
    "no-reply@innova-path.com", "do-not-reply@trashmail.com", "notifications@mailinator.com",
    "jobs@jobboard.com", "info@newsletter.com", "noreply@newsletter.com", "newsletter@newsletter.com",
    "alerts@company.com", "update@company.com", "donotreply@company.com", "support@company.com",
    "admin@company.com", "system@company.com", "bounce@company.com", "postmaster@company.com",
    "auto@company.com", "digest@company.com", "bulk@company.com", "mail@company.com", "email@company.com",
    "recruiter@jobboard.com"
]

spam_blacklist_subjects = [
    "Your Weekly Newsletter", "Congratulations! You've Won", "Don't Miss Out!", "Special Offer Just for You",
    "Update Your Account", "Important Notification", "Last Chance!", "Your Subscription Renewal",
    "Act Now: Limited Time Offer", "Exclusive Deal Inside", "Win a Free iPhone", "Your Invoice is Ready",
    "Security Alert", "Password Reset Request", "Welcome to Our Service", "Thank You for Your Purchase",
    "Reset Your Password", "Account Suspended", "Verify Your Account", "Limited Time Offer",
    "Black Friday Deals", "Cyber Monday Sale", "Refer a Friend", "Suspicious Login Detected",
    "Your Account Has Been Locked", "Action Required: Update Info", "Subscription Expiring Soon"
]

spam_blacklist_bodies = [
    "Click here to claim your prize now!", "This is your last chance to save big on our products.",
    "Dear user, your account needs to be updated. Please login to continue.",
    "Thank you for subscribing to our newsletter. Stay tuned for more updates.",
    "Exclusive offer: Get 50% off on all items. Limited time only!",
    "Your subscription will expire soon. Renew now to continue enjoying our services.",
    "We noticed unusual activity in your account. Please verify your information.",
    "Congratulations! You have been selected for a special reward.",
    "Your invoice for the recent purchase is attached. Please review and contact support if you have questions.",
    "Reset your password by clicking the link below.",
    "Welcome to our service! We're glad to have you.",
    "Thank you for your payment. Your order will be processed soon.",
    "Security alert: Suspicious login detected. Please confirm your identity.",
    "Don't miss our exclusive Black Friday deals!",
    "Refer a friend and get a discount on your next purchase.",
    "Your account has been temporarily suspended. Contact support for more information.",
    "Your account has been locked due to suspicious activity.",
    "Please update your billing information to avoid service interruption.",
    "You have been invited to join our professional network.",
    "We would like to discuss a potential collaboration.",
    "Join our platform to expand your professional network.",
    "Your resume was recently viewed by several employers.",
    "We found new job openings that match your profile. Click here to view more.",
    "Your account has been temporarily suspended. Contact support for more information.",
    "This is an automated message. Please do not reply."
]

gray_subjects = [
    "Job Alert: New Openings in Your Area", "Networking Opportunity", "Invitation to Join Our Platform",
    "Business Proposal", "Let's Connect on LinkedIn", "Your Resume Has Been Viewed",
    "Potential Collaboration", "Professional Network Invitation"
]
gray_bodies = [
    "We found new job openings that match your profile. Click here to view more.",
    "Let's connect and explore potential business opportunities.",
    "You have been invited to join our professional network.",
    "Your resume was recently viewed by several employers.",
    "We would like to discuss a potential collaboration.",
    "Join our platform to expand your professional network.",
    "This is an automated message. Please do not reply.",
    "We are expanding our network and would like to connect with you."
]
gray_emails = [
    "jobs@jobboard.com", "networking@platform.com", "invite@business.com", "alerts@jobsearch.com",
    "noreply@linkedin.com", "info@careers.com", "newsletter@newsletter.com", "noreply@newsletter.com"
]

data = []

for _ in range(3000):
    name = random.choice(recruiter_names)
    recruiter = random.choice(recruiter_names)
    company = random.choice(companies)
    role = random.choice(roles)
    email = random.choice(recruiter_emails)
    phone = random.choice(phones)
    template = random.choice(recruiter_templates)
    subject_template = random.choice(recruiter_subjects)
    subject = subject_template.format(role=role, company=company)
    body = template.format(name=name, recruiter=recruiter, company=company, role=role, email=email, phone=phone)
    from_email = email
    data.append({"subject": subject, "body": body, "from_email": from_email, "label": 1})

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
    data.append({"subject": subject, "body": body, "from_email": from_email, "label": 0})

random.shuffle(data)

df = pd.DataFrame(data)
df.to_csv("../data/labeled_emails.csv", index=False)
print("Generated labeled_emails.csv with", len(df), "rows.")

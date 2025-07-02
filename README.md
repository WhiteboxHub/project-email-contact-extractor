## Getting Started with Contacts Extractor By NER Models

1. **Clone this repository:**
   ```
   git clone https://github.com/WhiteboxHub/email_contact_extractor.git
   ```

2. **Navigate to the project directory:**
   ```
   cd email_contact_extractor/contact_extractor
   ```

3. **Add required configuration files:**
   - Place your `config/accounts.yaml` and `config/rules.yaml` files in the `contact_extractor/config/` directory.

4. **Create a virtual environment:**
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```
6. **Generate labeled training data:**
   ```
   python src/generate_labeled_emails.py
   ```
   This will create `labeled_emails.csv` in the `data/` folder.

7. **Train the recruiter/junk classifier:**
   ```
   python src/train_classifier.py
   ```
   This uses the generated `labeled_emails.csv` to train a logistic regression model for recruiter/vendor email detection.

8. **Run the extractor and monitor progress in the console:**
   ```
   python src/main.py
   ```
   The output with extracted contacts will be saved in `data/output.csv`.



### Contributors

- whitebox-learning!

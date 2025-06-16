# TFG - Application for the Study of Password Cracking Attacks based on Information Extracted from Social Networks
Author: Blanca Ruiz González

Final Degree Project - Universidad Carlos III de Madrid

- PURPOSE:
 
This application simulates how an attacker could exploit personal data from public Instagram profiles to generate customized dictionaries and evaluate the security of user passwords. The tool combines data extraction, AI-based wordlist expansion/reduction, and password cracking using John the Ripper.

- ⚠️ :
 
This project is intended SOLELY for educational and ethical research purposes. The author does NOT endorse or take responsibility for any malicious or illegal use of this tool. Using this tool to access accounts without explicit consent is strictly prohibited by law.

- PROJECT STRUCTURE:
  
  dictionaries/ -> Stores one dictionary '.txt' file per Instagram profile.
  
  statistics/ -> Where John the Ripper execution logs and ZIPs are stored.
  
  words_generated/ -> Temporarily stores the password combinations generated in intermediate/advanced modes.
  
  .env -> Environment file where the private keys such as the Gemini API key and Instagram credentials have to be stored.
  
  main.py	-> The main application script. Launches the GUI and allows interaction with all modules (data extraction, Gemini, password cracking).
  
  crawler_module.py	-> Contains the InstagramCrawler class that automates Instagram login and data scraping using Playwright. Extracts profile information, captions, and processes posts.
  
  gemini.py	-> Implements the GeminiProcessor class to interact with the Gemini API. Used for expanding or reducing dictionaries with AI-generated suggestions.
  
  john_reaper.py	-> Module responsible for executing password cracking using John the Ripper. Handles different attack modes and manages results.
  
  styles.py	-> Contains centralized styling for the PyQt6 GUI components (buttons, labels, layouts). Helps maintain consistency and reduce redundancy.
  
  permission_window.py	-> Defines a modal dialog that requests user consent before extracting data from an Instagram profile.
  
  worker.py	-> Includes worker classes for running Gemini and John the Ripper tasks in background threads to keep the UI responsive.
  
  open_window.py	-> Class responsible for rendering a text viewer window that displays the contents of a selected dictionary file.
  
  john-local.conf -> Custom rule file used by John the Ripper in advanced mode, includes both Jumbo and personalized rules based on Instagram password patterns.


- INSTRUCTIONS TO RUN THE PROGRAM - Follow the steps below to set up and run the application locally:
  
1. Make sure you have the following installed:
   
   Python 3.10 or later, Node.js and npm (for Playwright installation), John the Ripper, Google Gemini API access
   
2. Install requirements.txt
   
   pip install -r requirements.txt
   
3. Define your credentials in the .env file

4. Make sure the following folders exist:
   
   dictionaries/
   
   passwords/
   
   statistics/
   
   words_generated/
   

5. Configure John the Ripper: Ensure that john-local.conf is in the correct directory (next to john.exe or in the working directory) and contains your custom INSTAPOWER rule set.

6. Prepare a sample password file in passwords/ folder.
   Example format: username:5f4dcc3b5aa765d61d8327deb882cf99
   
7. Run the Program:
    
   python main.py
  

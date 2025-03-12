ContentAutomation

Overview

ContentAutomation is a fully automated pipeline that transforms Reddit stories into engaging videos. By leveraging text-to-speech, video editing automation, and AI-based tools, this project streamlines content creation for platforms like YouTube and TikTok.

Features

Automated Reddit Story Extraction: Fetches and processes top posts from relevant subreddits.

Text-to-Speech (TTS) Integration: Uses Azure TTS API to generate realistic voiceovers.

Background Video Selection: Matches visuals with the story for a compelling experience.

Subtitle Automation: Uses PyAutoGUI to integrate captions with CapCut Desktop.

Final Video Processing: MoviePy merges video, audio, and subtitles into a polished final product.

YouTube Upload Automation: Uses YouTube Data API to post content effortlessly.

Installation & Setup

Prerequisites

Python 3.11 (Virtual Environment Recommended)

Conda (For managing dependencies)

Azure TTS API Key

YouTube Data API Credentials

CapCut Desktop (For subtitle automation)

Steps

Clone the repository:

git clone https://github.com/yourusername/ContentAutomation.git
cd ContentAutomation

Set up a virtual environment with Conda:

conda create --name content_auto python=3.11
conda activate content_auto

Install dependencies:

pip install -r requirements.txt

Set up API keys securely:

Store credentials in a .env file (use python-dotenv)

Use environment variables to keep sensitive data safe

Usage

Run the script:

python main.py

The script will:

Fetch and process a Reddit story

Convert text to speech

Automate subtitle generation in CapCut

Merge assets into a final video

Upload to YouTube (if enabled)

Best Practices

Modular Code Structure: Each function is independent, making it reusable and easy to debug.

Error Handling & Logging: Implements try-except blocks to prevent crashes and logs key events.

Security: Avoids hardcoding API keys, using .env files instead.

Scalability: Designed with future improvements in mind (e.g., support for multiple platforms).

Efficiency: Uses automation to reduce manual effort and increase productivity.

Contributing

If you’d like to improve ContentAutomation, feel free to submit a pull request or suggest features in the issues tab.

Future Improvements

Enhanced Video Editing Features

Multiple Voice Styles for TTS

Support for Different Platforms Beyond YouTube

⚡ Automate Smarter, Create Faster, Innovate Continuously! ⚡

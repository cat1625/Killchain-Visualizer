Kill Chain Visualizer

Kill Chain Visualizer is a cybersecurity analytics dashboard that maps security logs and alerts to the Cyber Kill Chain framework. It helps visualize attack progression from reconnaissance to actions on objectives, enabling better threat tracking and faster incident response.

Overview

The system ingests log data and classifies events into different attack phases. It transforms raw security events into a structured visual timeline, allowing analysts to understand how an intrusion evolves across multiple stages.

Features

Attack phase mapping based on the Cyber Kill Chain model

Interactive dashboard for visualizing attack flow

Log parsing and event classification

Timeline view of intrusion progression

Sample attack simulation support

Clean and modular project structure

Tech Stack

Python

Flask or Streamlit (depending on your implementation)

HTML, CSS, JavaScript

JSON for log data handling

Project Structure

killchain-visualizer
│
├── app.py
├── static/
├── templates/
├── sample_data/
├── requirements.txt
└── README.md

Installation

Clone the repository:

git clone https://github.com/cat1625/Killchain-Visualizer.git

Navigate to the project folder:

cd Killchain-Visualizer

Create virtual environment:

python -m venv venv

Activate environment:

Windows:
venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run the application:

python app.py
or
streamlit run app.py

Use Case

This project simulates a mini Security Operations Center environment where analysts can observe how cyber attacks move through different stages. It is useful for academic projects, cybersecurity demonstrations, and threat analysis practice.

Future Enhancements

Real-time log streaming

MITRE ATT&CK mapping integration

Automated alerting system

Threat scoring and risk assessment

Deployment with Docker

Author

Kharshavarthan

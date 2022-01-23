
# I/OAI 
Link to Devpost: [here](https://devpost.com/submit-to/14609-mchacks-9/manage/submissions/300524-tony-stark-simulator/project_details/edit)

## About
Instead of a mouse, Input/Output Artificial Intelligence, or I/OAI, uses a user's webcam to move their cursor to where their face OR hand is pointing towards through machine learning. 

Additionally, I/OAI allows users to map their preferred hand movements for commands such as "click", "minimize", "open applications", "navigate websites", and more! 

I/OAI also allows users to input data using their voice, so they don't need to use a keyboard and mouse. This increases accessbility for those who don't readily have access to these peripherals. 

## Getting started
1. Clone the repository
2. Follow the steps [here](https://cloud.google.com/speech-to-text/docs/before-you-begin) to get a ```requirements.json``` file and set it as a global variable
3. Run  ```pip install -r requirements.txt``` in the terminal
4. Run ```python app.py``` in the terminal
5. Done!

## Instructions
1. Using the learn tab, toggle to a selection for which you want to automate
2. follow the instructions on the screen, depending on which selection you chose, this can be one of two types:
	- Type 1 - mouse command : enter a sign and a movement, that sign and movement is now mapped to a mouse command, such as click, or scroll. 
	- Type 2 - open application : enter a sign and movement,  then say what application/website you'd like to open, that command is now mapped to opening the application/website


# TonyStarkSimulator
Link to Devpost: [here](https://devpost.com/submit-to/14609-mchacks-9/manage/submissions/300524-tony-stark-simulator/project_details/edit)
## About
Instead of a mouse, Tony Stark Simulator, or TSS, uses a user's webcam to move their cursor to where their face is pointing towards. Additionally, TSS allows users to map their preferred hand movements for commands such as "click", "minimize", "disable TSS face recognition", and more!
TSS also allows users to input data using their voice, so they don't need to use a keyboard.
## Getting started
1. clone the repository
2. follow the steps [here](https://cloud.google.com/speech-to-text/docs/before-you-begin) to get a requirements .json file and set it as a global variable
5. ```cd ``` to the root of the folder
6. run  ```pip install -r requirements.txt``` in the terminal
7. run ```app.py``` in the terminal
8. Done !
## Instructions
1. using the learn tab, toggle to a selection for which you want to automate
2. follow the instructions on the screen, depending on which selection you chose, this can be one of two types:
	Type 1 - mouse command : enter a sign and a movement, that sign and movement is now mapped to a mouse command, such as click, or scroll. 
	Type 2 - open application : enter a sign and movement,  then say what application/website you'd like to open, that command is now mapped to opening the application/website

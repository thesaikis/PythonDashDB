# Matching Your Academic Interests With Universities

## Purpose
This application is designed to help students find universities and faculty members based on their research (or general) interests. It targets students who are applying to university, whether they are looking for a Bachelor's, Master's, or beyond. The application aims to provide a platform where students can explore information about univerisites and faculty members to make informed decisions about where they apply for schools. The objective is to simplify the process of discovering relevant academic institutions and connecting with potential mentors.

## Installation
To install the application, follow these steps:
1. Clone the repository.
2. Ensure Python 3.10.12 is present.
3. Install dependencies with `pip3 install -r requirements.txt`.
4. Set up and load the Academic World database into MySQL, Neo4j, and MongoDB.
5. Change the user and password in each of the *_utils.py files if necessary.

## Usage
Ensure all of the databases are running and are able to be connected to. Then, run `python3 app.py`. By default, the application will be available at `http://localhost:8050/`.

## Design
Each widget is self-contained in its own "box", with one exception. At the top of the webpage is where the user will input their interests. Optionally, the user can select a range of years using the slider right below it.

The widgets, in left-right/top-down order are as follows:
1. Top Universities:
    - This widget shows the univerisites with the most publications in the user's selected keywords. The user may select a university by clicking on its bar on the graph to see more information.
2. Top Faculty:
    - This widget shows the faculty members with the most publications in the user's selected keywords. The user may select a faculty member by clicking on their bar on the graph to see more information.
3. Highest Impact:
    - This widget shows a pie chart of the faculty members with the highest impact in the user's chosen keywords. The faculty members are ranked by the keyword relevant citations (KRC). This widget only shows the top 10 faculty members with the highest impact.
4. University Information:
    - This widget allows the user to search for specific universities. This is mainly used so that the user can view the image associated with the university. It also lists the number of published faculty members.
5. Faculty Information:
    - This widget allows the user to search for specific faculty members. It displays the faculty member's photo, position, interests, email, phone number, and the university they are associated with.
6. Faculty Review:
    - This widget is in the same "box" as the faculty information widget. Clicking on the button will open a popup which shows reviews made by other users for the selected faculty member. The current user, if they choose to do so, may also add their own review for the faculty member.
7. Add or Update Universities:
    - This widget allows the user to update the image of existing universities, or create a new university providing a name and image. The main purpose is to update outdated images on the universities, but also enables the user to add universities that do not exist in the database.
8. Total Research:
    - This widget shows a scatter plot based on the university's total faculty members, their total publications, and the total amount of keywords they have published in. The user may view their own selected universities only, or leave the input empty to examine all universities.
9. Most Cited Publications:
    - This widget shows a table of the selected faculty member's most cited publications. It's intended use is that the user can view the publications of the faculty member to have a more informed decisision and directly view which publications of the faculty member are the most popular.

## Implementation
This application is implemented in Python3 using various powerful libraries and databases:
- Dash: For building the web-based dashboard.
- Dash Bootstrap Components: For more complex features used in the dashboard.
- Plotly: For creating the graphs and figures.
- MySQL: One of the databases used in the backend. Additionally used to query the lists used in the dropdown options.
    - Used in widgets 1, 2, 9.
- MongoDB: One of the databases used in the backend.
    - Used in widgets 5, 6, 8.
- Neo4j: One of the databases used in the backend.
    - Used in widgets 3, 4, 7.

## Database Techniques
Three different database techniques are used in this application.
1. Indexing
    - This is used on the publication year in MySQL to improve query speed when the user specifies a year range. This applies to widgets 1 and 2.
2. Constraint
    - This is used in Neo4j to ensure the data being added in widget 7 does not already exist. It also ensures that the fields exist when updating or creating a new university.
3. Prepared Statements
    - Prepared statements are used in MySQL. When the application begins on the server side, it prepares a statement that is used in widget 9.

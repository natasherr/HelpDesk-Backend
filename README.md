# HelpDesk System

### Group Members:
- Ashley Natasha
- Brian Joseph
- Victor Kichwen
#### Date: 2025/02/17 - 2025/03/05 

## Live Link
[Vercel](https://helpdesk-psi.vercel.app/)

## Introduction

The *HelpDesk System* is a web-based platform that simplifies technical problem-solving for students. Users can raise issues, find solutions, vote on helpful answers, and track responses. It supports tags for easy filtering by language, learning stage, or technical challenge. With API-driven functionality, it fosters seamless integration and a collaborative learning community.

## Problem Statement

Students often encounter recurring challenges and struggle to find quick, relevant solutions. Repeating efforts can be frustrating and inefficient, and navigating solutions can be difficult.

## Solution

The *HelpDesk System* addresses these challenges by providing a user-friendly platform where students can:
- Raise issues they encounter.
- Post solutions to problems.
- Vote on solutions based on their usefulness.
- Tag problems and solutions to make them easily searchable.
- Keep track of solutions and answers in an organized, efficient manner.
- Receive notifications about new responses, votes, and answers.

The system will help reduce redundancy, encourage collaboration, and enhance the learning experience for all users.

## User Stories

- A user can:
  - Raise technical issues or problems they encounter.
  - Post solutions to other students’ problems.
  - Vote on the most helpful solutions provided by others.
  - Mark and follow questions of interest to track responses.
  - Receive notifications when there are new answers, votes, or responses.

## Features

### Authentication
- *Login/Signup*: Users can create an account, log in, and manage their profiles securely.
- *Password Reset*: Secure password recovery functionality.
  
### Problem Management
- *Raise Problem*: Users can submit a new problem, specifying details such as the issue type, category, and description.
- *Tagging Problems*: Each problem can be tagged with relevant categories, such as "language", "stage", or "technical issue".
- *Link Similar Problems*: Related issues can be linked to guide students toward similar problems with possible solutions.

### Solution Management
- *Post Solutions*: Users can reply to problems by posting solutions, whether they are answers to questions or suggestions.
- *Vote on Solutions*: Users can vote on solutions to indicate their usefulness. The most helpful solutions will rise to the top.

### Notifications
- *Response Notifications*: Users receive notifications when a response is added to a question they raised or followed.
- *Vote Notifications*: Users are notified when their solution gets a vote.
  
### FAQ System
- *Frequently Asked Questions*: Common issues and solutions will be compiled into an FAQ section for easy access.

## Technologies Used
- *Backend*: Flask (Python)
- *Database*: PostgreSQL
- *Frontend*: React.js (with Context API for state management)
- *API*: RESTful APIs to handle problem raising, solution posting, and voting
- *Authentication*: JWT (JSON Web Tokens) for secure authentication and OAuth for social authentication

## ERD Diagram

An Entity-Relationship Diagram (ERD) illustrating the structure of the database:

![Alt text](/frontend/public/drawsql.png "DrawSQL Diagram")

## User Interface

### Home Page
The homepage provides easy navigation, displaying the latest problems, popular solutions, and access to various categories:

![Alt text](/frontend/public/home.png "Home Page")

## Getting Started

### Prerequisites

- Javascript
- React(Vite)
- NPM
- Tailwind CSS
- Toastify

## API Endpoints

### Response Format
Fetching problems:
```jsx
   {
    "problems": [
        {
            "id": 1,
            "description": "How to center a div in CSS?",
            "tag": {
                "id": 2,
                "name": "CSS"
            },
            "user": {
                "id": 5,
                "username": "john_doe"
            },
            "solutions": [
                {
                    "id": 10,
                    "description": "You can use flexbox: display: flex; justify-content: center; align-items: center;",
                    "user": {
                        "id": 7,
                        "username": "jane_smith"
                    },
                    "tag": {
                        "id": 2,
                        "name": "CSS"
                    }
                },
                {
                    "id": 12,
                    "description": "Another way is to use text-align: center for inline elements.",
                    "user": {
                        "id": 8,
                        "username": "mark_taylor"
                    },
                    "tag": {
                        "id": 2,
                        "name": "CSS"
                    }
                }
            ]
        },
        {
            "id": 2,
            "description": "What is the difference between let and var in JavaScript?",
            "tag": {
                "id": 3,
                "name": "JavaScript"
            },
            "user": {
                "id": 6,
                "username": "alice_wonder"
            },
            "solutions": []
        }
    ],
    "total_pages": 5,
    "current_page": 1,
    "total_problems": 45
}
```

Fetching solutions:
```jsx
{
    "solutions": [
        {
            "id": 10,
            "user_id": 7,
            "problem_id": 1,
            "description": "You can use flexbox: display: flex; justify-content: center; align-items: center;",
            "tag_id": 2,
            "user": {
                "id": 7,
                "username": "jane_smith"
            },
            "tag": {
                "id": 2,
                "name": "CSS"
            }
        },
        {
            "id": 12,
            "user_id": 8,
            "problem_id": 1,
            "description": "Another way is to use text-align: center for inline elements.",
            "tag_id": 2,
            "user": {
                "id": 8,
                "username": "mark_taylor"
            },
            "tag": {
                "id": 2,
                "name": "CSS"
            }
        }
    ],
    "total_pages": 3,
    "current_page": 1,
    "total_solutions": 25
}
```

### Installation

1. Clone the repositories:
   
   ```bash
   git clone https://github.com/natasherr/HelpDesk-Frontend

   git clone https://github.com/natasherr/HelpDesk-Backend

2. Install backend dependencies:
   ```
   pipenv install
   ```
   
3. Set up the database:
   ```
   pipenv shell
   flask db upgrade
   ```

4. Install frontend dependencies:
   ```
   npm install 
   ```
   
5. Start the backend server:
   ```
   pipenv shell
   gunicorn app:app
   ```
   
6. Start the frontend development server:
   ```
   npm run dev
   ```
   

## Contact Information
- Brian Joseph - brianjoseph8132@gmail.com
- Ashley Natasha - ashleyotsiula@gmail.com
- Victor Kichwen - vkipchirchir@gmail.com


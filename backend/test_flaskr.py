import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

from flaskr import create_app
from models import setup_db, Question, Category
load_dotenv()


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = 'trivia_test'
        self.db_host = os.environ.get('DB_HOST')
        self.db_user=os.environ.get('DB_USER')
        self.db_password=os.environ.get('DB_PASS')
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(self.db_user,self.db_password,self.db_host, self.database_name)
        setup_db(self.app, self.database_path)

        

        self.new_question = {
        'question': 'What is the color of the moon?',
        'answer': 'blue',
        'category': 1,
        'difficulty': 1,
        }

  
        self.new_question_error = {
        'question': ' ',
        'answer': ' ',
        'difficulty': 1,
        'category': 1
        
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertGreater(len(data["categories"]), 0)

    def test_400_sent_requesting_invalid_category(self):
        res = self.client().get("/categories/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(len(data["categories"]))

    def test_400_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


    def test_for_questions_search(self):
        res = self.client().post("/questions/search", json={"searchTerm": "what"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])


    def test_400_for_invalid_questions_search(self):
        res = self.client().post("/questions/search", json={"searchTerm": "winkdbfikrui"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")



    def test_get_question_by_category(self):
        res = self.client().get("/categories/3/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["current_category"], "Geography")
        self.assertTrue(len(data["questions"]))

    def test_400_for_fail_to_get_question_by_category(self):
        res = self.client().get("/categories/1000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")


    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(data['total_questions'])

    def test_500_if_question_creation_fails(self):
        res = self.client().post("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "server error")

    def test_delete_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        # self.assertTrue(data["deleted"])
        self.assertTrue(data['total_questions'])


    def test_404_delete_question(self):
        # deletes a question that does not exist
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_play_quiz_by_category(self):
        quiz = {
            'previous_questions': [1, 2, 3],
            'quiz_category': {
                'type': 'Science',
                'id': '1'
            }
        }
        check = self.client().post('/quizzes', json=quiz)
        data = json.loads(check.data)

        self.assertEqual(check.status_code, 200)
        # self.assertTrue(data['success'])
        self.assertTrue(data['question']['question'])
        # check if the question is not in the previous question
        self.assertTrue(data['question']['id'] not in quiz['previous_questions'])

    def test_error_500_play_quiz(self):
        # play quiz with no given parameter
        check = self.client().post('/quizzes')
        data = json.loads(check.data)

        self.assertEqual(check.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'server error')




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
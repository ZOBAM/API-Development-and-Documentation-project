from http import client
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgresql://{}:{}@{}/{}".format("student", "student", 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {"question": "Which country has the largest black population in Africa?", "answer": "Nigeria","difficulty": "3", "category": 3}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    #test /questions end point
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])

    def test_get_questions_failure(self):
        res = self.client().get('/questions?page=1000')

        self.assertEqual(res.status_code, 404)
    #test get /categories end point
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
    def test_get_categories_failure(self):
        res = self.client().post('/categories')

        self.assertEqual(res.status_code, 405)
    #test /questions (POST) end point
    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_create_new_question_failure(self):
        res = self.client().post('/questions')

        self.assertEqual(res.status_code, 422)
    #test /questions (DELETE) end point
    def test_delete_question(self):
        res = self.client().delete('/questions/47')

        self.assertEqual(res.status_code, 200)
    def test_delete_question_failure(self):
        res =self.client().delete('/questions/1000')

        self.assertTrue(res.status_code, 422)
    # test /search endpoint
    def test_search_ok(self):
        res = self.client().post('/search', json = {'searchTerm': 'world'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])

    def test_search_failure(self):
        res = self.client().get('/search')

        self.assertEqual(res.status_code, 405)
    # test /quiz end point
    def test_quiz(self):
        res = self.client().post('/quizzes', json = {'quiz_category': '1', 'previous_questions': []})

        self.assertEqual(res.status_code, 200)
    def test_quiz_failure(self):
        res = self.client().get('/quizzes', json = {'quiz_category': '1', 'previous_questions': []})

        self.assertEqual(res.status_code, 405)
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
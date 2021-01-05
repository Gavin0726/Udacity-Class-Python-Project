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
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://gavin@localhost:5432/trivia_test'
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question':'this is a test question',
            'answer':'this is a test answer',
            'difficulty':2,
            'category':4
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    
    """
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'],1)
        self.assertEqual(data['total_questions'],18)
        

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_question_search_with_results(self):
        res = self.client().post('/questions',json={'searchTerm':'Africa'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']),1)

    def test_get_question_search_without_results(self):
        res = self.client().post('/questions',json={'searchTerm':'USA'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']),0)

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
  

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        
  
    def test_405_if_book_creation_not_allowed(self):
        res = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code,405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')
    
    def test_delete_question(self):
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 5).one_or_none()


        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deletedid'],5)
        self.assertEqual(question, None)

    def test_400_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


    def test_given_behavior(self):
        """Test _____________ """
        res = self.client().get('/')

        self.assertEqual(res.status_code, 200)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
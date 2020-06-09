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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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
    def test_get_paginated_question(self):
        response=self.client().get('/questions')
        data=json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])

    def test_404_error_beyond_valid_pages(self):
        response=self.client().get('/questions?page=100')
        data=json.loads(response.data)

        self.assertEqual(data['error'],404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

    def test_get_categories(self):
        response=self.client().get('/categories')
        data=json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_categories'])

    def test_404_error_no_categories(self):
        response=self.client().get('/categories/100')
        data=json.loads(response.data)

        self.assertEqual(data['error'],404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

    def test_delete_a_question(self):
        question_to_delete=Question('new Question?','new answer?','Sports',1)
        question_to_delete.insert()
        question_id=question_to_delete.id
        response=self.client().delete(f'/questions/{question_id}')
        data=json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],question_id)
    
    def test_404_error_non_existing_question(self):
        response=self.client().delete('/questions/a')
        data=json.loads(response.data)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

    def test_add_question(self):
        question_to_add={
            'question':'new question?',
            'answer':'new answer',
            'category':'Sports',
            'difficulty':3

        }
        total_questions_before=len(Question.query.all())
        response=self.client().post('/questions', json=question_to_add)
        data=json.loads(response.data)
        total_questions_after=len(Question.query.all())
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(total_questions_after, total_questions_before + 1)

    def test_422_error_add_question(self):
        question_to_add={
            'question':'new question?',
            'answer':'new answer',
            'category':'Sports',

        }
        total_questions_before=len(Question.query.all())
        response=self.client().post('/questions', json=question_to_add)
        data=json.loads(response.data)
        self.assertEqual(data['error'],422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'unprocessable')

    def test_search_question(self):
        response=self.client().post('/questions',json={'searchTerm':'new'} )
        data=json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['questions']),2)

    def test_404_if_search_fails(self):
        response=self.client().post('/questions',json={'searchTerm':'hi'})
        data=json.loads(response.data)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

    def test_get_question_by_category(self):
        response=self.client().get('/categories/1/questions')
        data=json.loads(response.data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])  

    def test_404_error_get_question_by_category(self):
        response=self.client().get('/categories/a/questions')
        data=json.loads(response.data)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')   

    def test_play_quiz(self):
        new_quiz_round= {'previous_questions': [],'quiz_category': {'type': 'Sports', 'id': '1'}}
        response = self.client().post('/quizzes',json= new_quiz_round)
        data=json.loads(response.data)
        self.assertEqual(respone.status_code,200)
        self.assertEqual(data['success'],True)  

    def test_404_error_play_quiz(self):
        new_quiz_round = {'previous_questions': []}
        response=self.client().post('/quizzes',json=new_quiz_round )
        data=json.loads(response.data)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')  



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
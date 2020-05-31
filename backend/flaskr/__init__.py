import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def pagination_questions(request, selection):
  page=request.args.get('page', 1,type= int)
  start= (page-1)* QUESTIONS_PER_PAGE
  end= start + QUESTIONS_PER_PAGE
  questions = [question.format() for question in selection]
  current_questions= questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app, resources={'/': {'origins': '*'}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

    

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories= Category.query.all()
    categories_dict={}
    for category in  categories:
      categories_dict[category.id]= category.type
    if len(categories_dict)==0:
      abort(404)

    return jsonify({
      'success':True,
      'categories':categories_dict,
      'total_categories': len(categories_dict)

    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    selection = Question.query.all()
    total_questions=len(selection)
    current_questions=pagination_questions(request, selection)

    categories= Category.query.all()
    categories_dict={}
    for category in  categories:
      categories_dict[category.id]= category.type
    
    if len(current_questions)==0:
      abort(404)
    
    return jsonify({
      'success':True,
      'questions': current_questions,
      'total_questions':total_questions,
      'categories':categories_dict
    })


  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question= Question.query.filter_by(id=question_id).one_or_none()
      if question is None:
        abort(404)
      question.delete()
      return jsonify({
        'success':True,
        'deleted':question_id,
        'total_questions':len(Question.query.all())
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def post_questions():
    body=request.get_json()
    #In case of searching for a term 

    if (body.get('searchTerm')):
      search_term=body.get('searchTerm')

      selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      if (len(selection)==0):
        abort(404)
      paginated = pagination_questions(request, selection)

      # return results
      return jsonify({
        'success': True,
        'questions': paginated,
        'total_questions': len(selection)
      })

    else:
      #load data from body
      new_question=body.get('question')
      new_answer=body.get('answer')
      new_difficulty=body.get('difficulty')
      new_category=body.get('category')

      #ensure all fields are valid
      if (new_question is None) or (new_answer is None) or (new_difficulty is None) or (new_category is None):
        abort(422)

      try:
        question= Question(new_question,new_answer,new_category,new_difficulty)
        #insert the question to the database
        question.insert()
        selection= Question.query.order_by(Question.id).all()
        current_questions=pagination_questions(request,selection)

        return jsonify({
          'success':True,
          'created':question.id,
          'created_question':question.question,
          'questions':current_questions,
          'total_questions':len(current_questions)
        })


      except:
        abort(422)


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_question_by_category(id):
    try:
      category=Category.query.filter_by(id=id).one_or_none()
      if (category is None):
        abort(404)
      questions=Question.query.filter_by(category=category.type).all()
      paginate=pagination_questions(request,questions)
      return jsonify({
        'success':True,
        'questions':paginate,
        'total_questions':len(questions),
        'current_category':category.type
        
      })

    except:
      abort(422)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def get_random_quiz_questions():
    body=request.get_json()
    previous_question=request.get_json('previous_questions')
    quiz_category=request.get_json('quiz_category')

    if (quiz_category is None) or (previous_question is None):
      abort (400)

    #for ALL categories
    if (quiz_category['id']==0):
      questions=Question.query.all()
    else:
      questions=Question.query.filter_by(category=category['id']).all()
    total=len(questions)
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success':False,
      'error':400,
      'message':'bad request'
    })

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success':False,
      'error':404,
      'message':'resource not found'
    })
  @app.errorhandler(422)
  def  unprocessable(error):
    return jsonify({
      'success':False,
      'error':422,
      'message':'unprocessable'
    })
  
  return app

    
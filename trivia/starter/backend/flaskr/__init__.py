import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import json

from sqlalchemy.sql.sqltypes import JSON 

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'


    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods','GET, POST, PATCH, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials','true')
        return response
    
    ''' 
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/')
    # @cross_origin()
    def hello_world():
            return jsonify({'message':'Hello, World!'})

    QUESTIONS_PER_PAGE = 10

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page-1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        
        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions
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
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        
        if len(current_questions) == 0:
            abort(404)

        categoryselection = Category.query.order_by(Category.id).all()
    
        
        if len(categoryselection) == 0:
            abort(404)
        
        categories = [category.format() for category in categoryselection]
        cate={}
        for cateitem in categories:
            cate.update({cateitem["id"]:cateitem["type"]})
        return jsonify({
            'success':True,
            'questions':current_questions,
            'categories':cate,
            'current_category':1,
            'total_questions':len(Question.query.all())
        })

    '''
    
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>', methods =['DELETE'])
    def delete_questions(question_id):

        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)
                        
            
            question.delete()

            # selection = Question.query.order_by(Question.id).all()
            # current_questions = paginate_questions(request, selection)

            return jsonify({
                'success':True,
                'deletedid':question.id,
               
            })
        except:
            abort(400)
    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods = ['POST'])
    @cross_origin()
    def create_search_question():
        
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)
        search = body.get('searchTerm',None)

        
        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search))) 
                current_questions = paginate_questions(request, selection)
                print(len(current_questions))
                return jsonify({
                    'success':True,
                    'questions': current_questions,
                    'totalquestions':len(current_questions),
                    'currentCategory':1
                })

            else:
                question = Question(question=new_question, answer=new_answer,difficulty=new_difficulty,category=new_category)
                question.insert()

            
                return jsonify({
                    'success':True,
                    'createdquesitonid':question.id,
                })

        except:
            abort(422)

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_bycategory(category_id):
       
        try:
            selection = Question.query.filter(Question.category == category_id).all()
            # selection = Question.query.order_by(Question.id).all()

            if selection is None:
                abort(404)
                        
        
           
            # selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success':True,
                'questions':current_questions,
                'totalQuestions':len(Question.query.all()),
                'currentCategory':category_id
            })
        except:
            abort(400)


    @app.route('/categories')
    def retrieve_categories():
        selection = Category.query.order_by(Category.id).all()
    
        
        if len(selection) == 0:
            abort(404)
        
        categories = [category.format() for category in selection]
        cate={}
        for cateitem in categories:
            cate.update({cateitem["id"]:cateitem["type"]})
        

        
        return jsonify({
            'success':True,
            'categories':cate,
            
        })
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
    @app.route('/quizzes' , methods = ['POST'])
    @cross_origin()
    def retrieve_quiz():

        body = request.get_json()

        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)
        
        try:
            if quiz_category["id"] == 0:
                selection = Question.query.all()
            else:
                selection = Question.query.filter(Question.category == quiz_category["id"]).all()
            
            if selection is None:
                abort(404)
            
            questionids=[]
        
                        
            questions = [question.format() for question in selection]
            
            for questionitem in questions:
                if not questionitem["id"] in previous_questions:
                    questionids.append(questionitem["id"])
            
            if not questionids:
                quiz = False
            else:
                questionid = random.sample(questionids, 1)
                
                # selection = Question.query.order_by(Question.id).all()
                question = Question.query.filter(Question.id == questionid[0]).all()
                
                quiz = question[0].format()

            
            return jsonify({
                'success':True,
                'question':quiz,
            })
        except:
            abort(400)
    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success":False,
            "error":404,
            "message":"resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success":False,
            "error":422,
            "message":"unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success":False,
            "error":400,
            "message":"bad request"
        }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success":False,
            "error":405,
            "message":"method not allowed"
        }), 405

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success":False,
            "error":500,
            "message":"server error"
        }), 500

    return app


    
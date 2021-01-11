import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import json

from sqlalchemy.sql.sqltypes import JSON

from models import setup_db, Question, Category

SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("Please provide the SECRET_KEY=gavinguo ")
elif not SECRET_KEY == 'gavinguo':
    raise ValueError("Please provide the right SECRET_KEY")

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, \
                                Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, \
                                 PATCH, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    @app.route('/')
    # @cross_origin()
    def hello_world():
        return jsonify({'message': 'Hello, World!'})

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page-1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    def paginate(request):
        page = request.args.get('page', 1, type=int)
        start = (page-1) * QUESTIONS_PER_PAGE

        return start

    @app.route('/questions')
    def retrieve_questions():
        start = paginate(request)
        selection = Question.query.order_by(Question.id) \
            .limit(QUESTIONS_PER_PAGE).offset(start)
        # current_questions = paginate_questions(request, selection)
        current_questions = [question.format() for question in selection]

        if len(current_questions) == 0:
            abort(404)

        categoryselection = Category.query.order_by(Category.id).all()

        if len(categoryselection) == 0:
            abort(404)

        categories = [category.format() for category in categoryselection]
        cate = {}
        for cateitem in categories:
            cate.update({cateitem["id"]: cateitem["type"]})
        return jsonify({
            'success': True,
            'questions': current_questions,
            'categories': cate,
            'current_category': 1,
            'total_questions': len(Question.query.all())
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):

        try:
            question = Question.query.filter(Question.id == question_id) \
                    .one_or_none()

            if question is None:
                abort(404)

            question.delete()

            # selection = Question.query.order_by(Question.id).all()
            # current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deletedid': question.id
            })

        except BaseException:
            abort(400)

    @app.route('/questions', methods=['POST'])
    @cross_origin()
    def create_search_question():

        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_difficulty = body.get('difficulty', None)
        new_category = body.get('category', None)
        search = body.get('searchTerm', None)

        try:
            if search:
                selection = Question.query.order_by(Question.id) \
                        .filter(Question.question.ilike('%{}%'.format(search)))
                current_questions = paginate_questions(request, selection)
                print(len(current_questions))
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'totalquestions': len(current_questions),
                    'currentCategory': 1
                })

            else:
                question = Question(
                                    question=new_question,
                                    answer=new_answer,
                                    difficulty=new_difficulty,
                                    category=new_category
                                    )
                question.insert()

                return jsonify({
                    'success': True,
                    'createdquesitonid': question.id,
                })

        except BaseException:
            abort(422)

    @app.route('/categories/<int:category_id>/questions')
    def retrieve_questions_bycategory(category_id):
        start = paginate(request)
        try:
            selection = Question.query \
                        .filter(Question.category == category_id) \
                        .limit(QUESTIONS_PER_PAGE).offset(start)
            # selection = Question.query.order_by(Question.id).all()

            if selection is None:
                abort(404)

            # selection = Question.query.order_by(Question.id).all()
            current_questions = [question.format() for question in selection]

            return jsonify({
                'success': True,
                'questions': current_questions,
                'totalQuestions': len(Question.query.all()),
                'currentCategory': category_id
            })
        except BaseException:
            abort(400)

    @app.route('/categories')
    def retrieve_categories():
        selection = Category.query.order_by(Category.id).all()

        if len(selection) == 0:
            abort(404)

        categories = [category.format() for category in selection]
        cate = {}
        for cateitem in categories:
            cate.update({cateitem["id"]: cateitem["type"]})

        return jsonify({
            'success': True,
            'categories': cate,
        })

    @app.route('/quizzes', methods=['POST'])
    @cross_origin()
    def retrieve_quiz():

        body = request.get_json()

        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)

        try:
            if quiz_category["id"] == 0:
                selection = Question.query.all()
            else:
                selection = Question.query \
                            .filter(Question.category == quiz_category["id"]) \
                            .all()

            if selection is None:
                abort(404)

            questionids = []
            questions = [question.format() for question in selection]

            for questionitem in questions:
                if not questionitem["id"] in previous_questions:
                    questionids.append(questionitem["id"])

            if not questionids:
                quiz = False
            else:
                questionid = random.sample(questionids, 1)

                # selection = Question.query.order_by(Question.id).all()
                question = Question.query \
                    .filter(Question.id == questionid[0]).all()

                quiz = question[0].format()

            return jsonify({
                'success': True,
                'question': quiz,
            })
        except BaseException:
            abort(400)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "server error"
        }), 500

    return app

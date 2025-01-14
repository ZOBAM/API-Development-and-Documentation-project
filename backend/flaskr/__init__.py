from crypt import methods
from multiprocessing.dummy import current_process
import os
from sre_parse import CATEGORIES
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

#-------------------------Helper functions--------------------------------------------------------
def question_categories():
    categories = Category.query.order_by(Category.id).all()
    categories_list = {}
    for cat in categories:
        categories_list[cat.id] = cat.type

    return categories_list

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

#--------------------------------------------------------------------------------------------------

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)


    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        
        return jsonify({
            'categories': question_categories()
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    """
    """
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():

        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)
        
        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'categories': question_categories(),
            'total_questions':len(questions),
            'current_category': 1
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods = ['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter_by(id = question_id).first()
            question.delete()

            return jsonify({
                'success': True,
                'question_id': question_id
            })
        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_new_question():
        json_data = request.get_json()

        try:
            question = json_data['question']
            answer = json_data['answer']
            category = json_data['category']
            difficulty = json_data['difficulty']
            new_question = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty
            )
            new_question.insert()

            return jsonify({
                'success': True
            })
        except:
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/search', methods = ['POST'])
    def search():
        json_data = request.get_json()
        search_string = json_data['searchTerm']

        try:
            questions = Question.query.filter(Question.question.ilike('%'+search_string+'%')).all()

            if questions is None:
                abort(404)
            
            current_questions = paginate_questions(request, questions)
            return jsonify({
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': 1
            })
        except:
            abort(404)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions', methods = ['GET'])
    def get_category_questions(category_id):
        try:
            questions = Question.query.filter_by(category = category_id).all()
            current_questions = paginate_questions(request, questions)
            
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(questions),
                'current_category': category_id
            })
        except:
            abort(400)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods = ['POST'])
    def get_quiz():
        json_data = request.get_json()
        previous_questions = json_data['previous_questions']
        quiz_category = json_data['quiz_category']

        try:
            questions = Question.query.filter_by(category = quiz_category).filter(Question.id.notin_(previous_questions)).all()
            current_question = None
            if len(questions):
                current_question = questions[random.randrange(0,len(questions))]
                current_question = current_question.format()
            
            return jsonify({
                'question': current_question
            })
        except:
            abort(404)
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'not found'
        }), 404
        
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    return app


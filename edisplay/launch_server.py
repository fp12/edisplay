from bottle import route, run, response

from edisplay.generate_image import generate_binary

@route('/generated')
def generated():
    response.content_type = 'image/png'
    return generate_binary(debug=False)

run(host='localhost', port=8080)

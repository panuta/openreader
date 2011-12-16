from django.http import HttpResponse
from django.utils import simplejson

def response_json(obj=None):
	if obj != None:
		return HttpResponse(simplejson.dumps(obj))
	else:
		return HttpResponse('{}')

def response_json_success():
    return HttpResponse(simplejson.dumps({'status':'success'}))

def response_json_error(error_code):
	return HttpResponse(simplejson.dumps({'status':'error', 'error':error_code}))
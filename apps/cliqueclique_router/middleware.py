import signal

class ChangeSignalMiddleware(object):
    def process_request(self, request):
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        return None

    def process_response(self, request, response):
        if request.method == 'POST':
            with signal.global_server_signal:
                signal.global_server_signal.notifyAll()
        return response

    def process_exception(self, request, exception):
        return None

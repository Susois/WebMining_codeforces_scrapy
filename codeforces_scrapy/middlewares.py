class CustomUserAgentMiddleware:
    def process_request(self, request, spider):
        request.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        
class CustomRetryMiddleware:
    def process_response(self, request, response, spider):
        if response.status in [500, 502, 503, 504]:
            return self._retry(request, spider)
        return response

    def _retry(self, request, spider):
        retries = request.meta.get('retries', 0)
        if retries < spider.settings.get('RETRY_TIMES', 3):
            retries += 1
            request.meta['retries'] = retries
            return request
        return None

class CustomDownloaderMiddleware:
    def process_response(self, request, response, spider):
        # Add custom processing for responses here
        return response

    def process_exception(self, request, exception, spider):
        # Handle exceptions here
        spider.logger.error(f"Error processing request: {request.url} - {exception}")
class MobileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        info = request.META.get("HTTP_USER_AGENT", "Desktop")
        # print("HTTP_USER_AGENT", info)
        if "Mobile" in info:
            request.is_mobile = True
        else:
            request.is_mobile = False
            
        response = self.get_response(request)
        
        return response
        

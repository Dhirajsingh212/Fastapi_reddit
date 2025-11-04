from collections import defaultdict
import time
from typing import Dict
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Response
from starlette import status

class AdvancedMiddleware(BaseHTTPMiddleware):
    def __init__(self,app):
        super().__init__(app)
        self.rate_limit_records:Dict[str,float] = defaultdict(float)

    async def dispatch(self,request,call_next):
        client_ip = request.client.host
        current_time = time.time()
        if current_time - self.rate_limit_records[client_ip] < 1:
            return Response(content="Rate limit exceeded", status_code=status.HTTP_409_CONFLICT)

        self.rate_limit_records[client_ip] = current_time

        return await call_next(request)

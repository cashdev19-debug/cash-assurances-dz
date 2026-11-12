import logging
import re

from django.conf import settings

logger = logging.getLogger(__name__)


class OneLineHtmlMinifyMiddleware:
    EXCLUDED_PREFIXES = ('/admin/', '/django-admin/')

    # Whitespace matters inside these: restore them untouched
    PROTECTED = re.compile(
        r'<(pre|textarea|script|style)\b[^>]*>.*?</\1\s*>', re.S | re.I
    )
    # Normal comments only (keeps <!--[if IE]> conditional comments)
    COMMENT = re.compile(r'<!--(?!\[if|<!|>).*?-->', re.S)
    PLACEHOLDER = re.compile(r'@@KEEP(\d+)@@')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not (
            response.status_code == 200
            and not response.streaming
            and 'text/html' in response.get('Content-Type', '')
            and not request.path.startswith(self.EXCLUDED_PREFIXES)
        ):
            return response

        try:
            html = response.content.decode('utf-8')
            kept = []

            def keep(match):
                kept.append(match.group(0))
                return f'@@KEEP{len(kept) - 1}@@'

            html = self.PROTECTED.sub(keep, html)      # hide scripts, styles, pre, textarea
            html = self.COMMENT.sub('', html)          # remove HTML comments
            html = re.sub(r'\s+', ' ', html)           # one line
            html = re.sub(r'>\s+<', '><', html)        # remove spaces between tags
            html = self.PLACEHOLDER.sub(lambda m: kept[int(m.group(1))], html)

            result = html.strip()
            if result:
                response.content = result.encode('utf-8')
                if response.has_header('Content-Length'):
                    response['Content-Length'] = str(len(response.content))
        except Exception:
            logger.exception('OneLineHtmlMinifyMiddleware failed')

        return response
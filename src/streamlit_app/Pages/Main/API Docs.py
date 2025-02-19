import streamlit.components.v1 as components
import streamlit as st
from helpers.config import api_url

docs_url = f'{api_url}/docs'
swagger_url = f'{api_url}/openapi.json'

st.link_button('Documentación API', docs_url)

swagger_html = f"""
<html>
<head>
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css">
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js"></script>
    <style>
        #swagger-ui {{
          background-color: #f0f0f0;
          padding: 20px;
          border-radius: 8px;
          height: 100%;
          overflow: auto;
        }}
        body {{
          margin: 0;
        }}
    </style>
    <script>
        window.onload = function() {{
          const ui = SwaggerUIBundle({{
            url: '{swagger_url}',
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
              SwaggerUIBundle.presets.apis,
              SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
            layout: "BaseLayout",
          }});
        }};
    </script>
</head>
<body>
<div id="swagger-ui"></div>
</body>
</html>
"""
components.html(swagger_html, height=900, scrolling=True)

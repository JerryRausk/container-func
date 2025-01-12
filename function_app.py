import azure.functions as func
import json
import os
import base64

app = func.FunctionApp()

def get_roles(token: str):
    decoded_bytes = base64.b64decode(token)
    decoded_str = decoded_bytes.decode("utf-8")
    decoded_dict = json.loads(decoded_str)

    claims = decoded_dict.get("claims", [])
    if not claims:
        return []
    
    role_claims = [d for d in claims if d["typ"] == "roles"]
    if len(role_claims) == 0:
        return []
    
    roles = [claim["val"] for claim in role_claims]
    return roles

@app.route(route="/", auth_level=func.AuthLevel.ANONYMOUS)
def Html(req: func.HttpRequest) -> func.HttpResponse:

    static_folder = os.path.join(os.path.dirname(__file__), "static")
    html_file_path = os.path.join(static_folder, "index.html")

    try:
        with open(html_file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        return func.HttpResponse(html_content, status_code=200, mimetype="text/html")
    except FileNotFoundError:
        return func.HttpResponse("HTML file not found", status_code=404)
    except Exception as e:
        return func.HttpResponse("An internal server error occurred.", status_code=500)

@app.route(route="/api/my-headers", auth_level=func.AuthLevel.ANONYMOUS)
def MyHeaders(req: func.HttpRequest) -> func.HttpResponse:
    headers = {key: value for key, value in req.headers.items()}
    return func.HttpResponse(json.dumps(headers), status_code=200)

@app.route(route="/api/my-roles", auth_level=func.AuthLevel.ANONYMOUS)
def MyRoles(req: func.HttpRequest) -> func.HttpResponse:
    headers = {key: value for key, value in req.headers.items()}
    token = headers.get("x-ms-client-principal")
    if(token is None):
        return func.HttpResponse(json.dumps({"msg": "No token"}), status_code=200)
    
    roles = get_roles(token)

    return func.HttpResponse(json.dumps(roles), status_code=200)

AVAILABLE_ENTITIES = [
    {"label": "Entity One", "id": "one"},
    {"label": "Entity Two", "id": "two"},
]


@app.route(route="/api/available-entities", auth_level=func.AuthLevel.ANONYMOUS)
def AvailableEntities(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(json.dumps(AVAILABLE_ENTITIES), status_code=200)


ENTITY_PARAMS = {
    "one": [
        {
            "id": "11",
            "label": "(entity one) Parameter one",
            "type": "select",
            "options": [
                {"value": "111", "label": "First param First Option"},
                {"value": "112", "label": "First param Second Option"},
                {"value": "113", "label": "First param Third Option"},
            ],
        },
        {
            "id": "12",
            "label": "(entity one) Parameter two",
            "type": "select",
            "options": [
                {"value": "121", "label": "Second param First Option"},
                {"value": "122", "label": "Second param Second Option"},
                {"value": "123", "label": "Second param Third Option"},
            ],
        },
    ],
    "two": [
        {
            "id": "21",
            "label": "(entity two) Parameter one",
            "type": "select",
            "options": [
                {"value": "211", "label": "First param First Option"},
                {"value": "212", "label": "First param Second Option"},
                {"value": "213", "label": "First param Third Option"},
            ],
        },
        {
            "id": "22",
            "label": "(entity two) Parameter two",
            "type": "input",
        },
    ],
}

@app.route(route="/api/get-parameters", auth_level=func.AuthLevel.ANONYMOUS)
def GetParameters(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    print("Got ", body)
    return func.HttpResponse(json.dumps(ENTITY_PARAMS[body["entityId"]]), status_code=200)


@app.route(route="/api/send-parameters", auth_level=func.AuthLevel.ANONYMOUS)
def SendParameters(req: func.HttpRequest) -> func.HttpResponse:
    body = req.get_json()
    print("Got ", body)
    return func.HttpResponse("Backend received: " + json.dumps(body), status_code=200)

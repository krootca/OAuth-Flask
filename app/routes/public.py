from flask import Blueprint, render_template, redirect, request


# Importar para 0auth
from oauthlib.oauth2 import WebApplicationClient
import requests, json

# Importar variables de entorno
from decouple import config

# Este blueprint en Flask es esencialmente un objeto que define un conjunto de rutas
public_blueprint = Blueprint('public', __name__)


# Obtenemos las variables de entornos necesarias para OAuth
GOOGLE_CLIENT_ID=config('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET=config('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

# crea un objeto cliente de la biblioteca oauthlib llamado client para gestionar la autenticación OAuth en una aplicación web.
client = WebApplicationClient(GOOGLE_CLIENT_ID)


# realiza una solicitud HTTP GET a GOOGLE_DISCOVERY_URL y luego convierte la respuesta en un objeto JSON. 
# se utiliza para obtener la configuración del proveedor de servicios OAuth de Google
def get_google_provider_config():
	return requests.get(GOOGLE_DISCOVERY_URL).json()


# aquí por ejemplo estamos definiendo algunas rutas
@public_blueprint.route("/google_signup") # Esta línea define una nueva ruta en el blueprint public_blueprint para manejar las solicitudes GET en la URL /google_signup
def google_signup():
	
	# Esta línea llama a la función get_google_provider_config() para obtener la configuración del proveedor de servicios de Google OAuth. 
	# Esta configuración incluye la URL de punto final de autorización de Google y otros detalles importantes necesarios para interactuar con el servicio de autenticación de Google.
	google_provider_cfg = get_google_provider_config()
	
	
	# Esta línea extrae la URL del punto final de autorización del proveedor de servicios de Google OAuth de la configuración obtenida en la línea anterior.
	# Esta URL es la dirección a la que se enviarán las solicitudes de autorización de OAuth para iniciar sesión con Google.
	authorization_endpoint = google_provider_cfg["authorization_endpoint"]

	
	########
	# La siguiente línea utiliza el objeto client para construir la URL de solicitud de autorización para Google
	#
	# authorization_endpoint: La URL de punto final de autorización de Google obtenida anteriormente.
	# redirect_uri: La URL a la que Google redirigirá al usuario después de la autenticación exitosa.
	# scope: Las autorizaciones solicitadas que se le pedirán al usuario durante el proceso de autenticación.
	request_uri = client.prepare_request_uri(
		authorization_endpoint,
		redirect_uri=request.base_url + "/callback",
		scope=["openid", "email", "profile"],
	)

	return redirect(request_uri)

@public_blueprint.route("/google_signup/callback")
def callback():

	# Este "code" es un código de autorización que Google envía de vuelta a tu aplicación después
	# de que el usuario haya dado su consentimiento para acceder a su información.
	code_autorization = request.args.get("code") 


	google_provider_cfg = get_google_provider_config()
	token_endpoint = google_provider_cfg["token_endpoint"]
	token_url, headers, body = client.prepare_token_request(
		token_endpoint,
		authorization_response=request.url,
		redirect_url=request.base_url,
		code=code_autorization
	)

	token_response = requests.post(
		token_url,
		headers=headers,
		data=body,
		auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
	)
	client.parse_request_body_response(json.dumps(token_response.json()))

	userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
	uri, headers, body = client.add_token(userinfo_endpoint)
	userinfo_response = requests.get(uri, headers=headers, data=body)

	if userinfo_response.json().get("email_verified"):
		unique_id = userinfo_response.json()["sub"]
		users_email = userinfo_response.json()["email"]
		imagen = userinfo_response.json()["picture"]
		primer_nombre = userinfo_response.json()["given_name"]
		nombre_completo = userinfo_response.json()["name"]
		# Aquí puedes hacer lo que necesites con la información del usuario
		return render_template("public/logged.html", nombre=nombre_completo, picture=imagen, jsontext=userinfo_response.json())
	else:
		return "La cuenta no existe o no está verificado por google.", 400

########
@public_blueprint.route('/')
def index():
	return render_template('public/index.html')




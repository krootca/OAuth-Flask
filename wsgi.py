from app.main import app
from decouple import config


if __name__ == '__main__':
	app.run(host=config('host'), port=int(config('port')), debug=True)

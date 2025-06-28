import logging
from app.app import app
from app.extensions import csrf

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)

# Inicializar CSRF
csrf.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)

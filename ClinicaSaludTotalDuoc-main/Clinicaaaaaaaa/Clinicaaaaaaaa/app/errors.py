class LoginError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.message = message  # Cambiando el nombre del atributo a message
        self.code = code

    @classmethod
    def user_not_found(cls):
        return cls("Correo no registrado.", "user_not_found")

    @classmethod
    def invalid_password(cls):
        return cls("Contraseña incorrecta.", "invalid_password")

    @classmethod
    def not_admin(cls):
        return cls("Usuario no registrado como administrador.", "not_admin")

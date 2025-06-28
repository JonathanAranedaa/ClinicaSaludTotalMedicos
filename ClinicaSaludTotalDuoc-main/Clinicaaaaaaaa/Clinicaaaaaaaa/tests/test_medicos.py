import unittest
from app.app import app
from flask import url_for, session
from flask_wtf.csrf import generate_csrf

class TestMedicos(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Configurar el contexto de la aplicación
        self.ctx = app.app_context()
        self.ctx.push()
        
        # Obtener el CSRF token
        with self.app.session_transaction() as sess:
            sess['csrf_token'] = 'test-csrf-token'  # Usar un token de prueba fijo para los tests

    def tearDown(self):
        self.ctx.pop()

    def test_ver_medicos(self):
        """Test para verificar la visualización de médicos"""
        response = self.app.get('/get_doctors')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn('id', data[0])
        self.assertIn('nombre', data[0])

    def test_agregar_medico(self):
        """Test para agregar un nuevo médico"""
        # Primero crear una especialidad
        especialidad_data = {
            'nom_espe': 'Especialidad Test'
        }
        response = self.app.post('/api/especialidades', json=especialidad_data)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id_especialidad', data)
        especialidad_id = data['id_especialidad']

        # Crear un usuario
        user_data = {
            'rut': '12345678-9',
            'correo': 'test@test.com',
            'contrasena': 'password123',
            'nombre': 'Juan',
            'ap_paterno': 'Pérez',
            'ap_materno': 'González',
            'sexo': True,
            'direccion': 'Calle 123',
            'activo': True
        }
        response = self.app.post('/api/usuarios', json=user_data)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id_usuario', data)
        user_id = data['id_usuario']

        # Ahora crear el médico
        medico_data = {
            'certificacion': 'Certificado Test',
            'activo': True,
            'id_especialidad': especialidad_id,
            'id_usuario': user_id
        }
        response = self.app.post('/api/medicos', json=medico_data)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id_medico', data)
        self.assertEqual(data['certificacion'], 'Certificado Test')
        self.assertTrue(data['activo'])
        self.assertEqual(data['id_usuario'], user_id)

    def test_cambiar_estado_medico(self):
        """Test para cambiar el estado de un médico"""
        # Primero crear una especialidad
        especialidad_data = {
            'nom_espe': 'Especialidad Test'
        }
        response = self.app.post('/api/especialidades', json=especialidad_data)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        especialidad_id = data['id_especialidad']

        # Crear un usuario
        user_data = {
            'rut': '98765432-1',
            'correo': 'test2@test.com',
            'contrasena': 'password123',
            'nombre': 'Test',
            'ap_paterno': 'Médico',
            'ap_materno': 'Test',
            'sexo': True,
            'direccion': 'Calle 456',
            'activo': True
        }
        response = self.app.post('/api/usuarios', json=user_data)
        data = response.get_json()
        user_id = data['id_usuario']

        # Crear el médico
        medico_data = {
            'certificacion': 'Certificado Test',
            'activo': True,
            'id_especialidad': especialidad_id,
            'id_usuario': user_id
        }
        response = self.app.post('/api/medicos', json=medico_data)
        data = response.get_json()
        medico_id = data['id_medico']

        # Ahora cambiar su estado
        update_data = {
            'activo': False
        }
        response = self.app.post(f'/api/medicos/{medico_id}', 
            json=update_data,
            headers={'X-CSRFToken': 'test-csrf-token'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['activo'])

    def test_editar_medico(self):
        """Test para editar un médico"""
        # Primero crear una especialidad
        especialidad_data = {
            'nom_espe': 'Especialidad Test'
        }
        response = self.app.post('/api/especialidades', json=especialidad_data)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        especialidad_id = data['id_especialidad']

        # Crear una segunda especialidad para el test de edición
        especialidad_data_2 = {
            'nom_espe': 'Especialidad Test 2'
        }
        response = self.app.post('/api/especialidades', json=especialidad_data_2)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        especialidad_id_2 = data['id_especialidad']

        # Crear un usuario
        user_data = {
            'rut': '11111111-1',
            'correo': 'test3@test.com',
            'contrasena': 'password123',
            'nombre': 'Test',
            'ap_paterno': 'Médico',
            'ap_materno': 'Test',
            'sexo': True,
            'direccion': 'Calle 789',
            'activo': True
        }
        response = self.app.post('/api/usuarios', json=user_data)
        data = response.get_json()
        user_id = data['id_usuario']

        # Crear el médico
        medico_data = {
            'certificacion': 'Certificado Test',
            'activo': True,
            'id_especialidad': especialidad_id,
            'id_usuario': user_id
        }
        response = self.app.post('/api/medicos', json=medico_data)
        data = response.get_json()
        medico_id = data['id_medico']

        # Ahora editar
        edit_data = {
            'certificacion': 'Certificado Editado',
            'id_especialidad': especialidad_id_2
        }
        response = self.app.post(f'/api/medicos/{medico_id}', 
            json=edit_data,
            headers={'X-CSRFToken': 'test-csrf-token'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['certificacion'], 'Certificado Editado')
        self.assertEqual(data['id_especialidad'], especialidad_id_2)

    def test_ver_medico_inexistente(self):
        """Test para verificar el manejo de médicos inexistentes"""
        response = self.app.get('/api/medicos/999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Médico no encontrado')

    def test_cambiar_estado_inexistente(self):
        """Test para verificar el manejo de cambio de estado de médico inexistente"""
        update_data = {
            'activo': False
        }
        response = self.app.post('/api/medicos/999', 
            json=update_data,
            headers={'X-CSRFToken': 'test-csrf-token'})
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Médico no encontrado')

if __name__ == '__main__':
    unittest.main()

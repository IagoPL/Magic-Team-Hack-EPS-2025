"""
Gestor de clientes - Permite agregar y editar clientes
"""
from typing import Dict, List
from src.utils import load_json, save_json, get_config_path


class ClientManager:
    """Gestor para agregar, editar y eliminar clientes"""
    
    def __init__(self):
        self.config_path = get_config_path('clients.json')
        self.clients = self.load_clients()
    
    def load_clients(self) -> Dict:
        """Carga los clientes desde el archivo de configuración"""
        try:
            return load_json(self.config_path)
        except Exception as e:
            print(f"Error cargando clientes: {e}")
            return {}
    
    def save_clients(self) -> bool:
        """Guarda los clientes en el archivo de configuración"""
        try:
            save_json(self.clients, self.config_path)
            return True
        except Exception as e:
            print(f"Error guardando clientes: {e}")
            return False
    
    def get_client(self, client_id: str) -> Dict:
        """Obtiene un cliente por su ID"""
        return self.clients.get(client_id, {})
    
    def add_client(self, client_id: str, client_data: Dict) -> bool:
        """
        Agrega un nuevo cliente
        
        Args:
            client_id: ID único del cliente (ej: 'nuevo_cliente')
            client_data: Diccionario con los datos del cliente
                - name: Nombre del cliente
                - description: Descripción
                - weights: Diccionario con pesos de métricas (deben sumar 1.0)
                - preferences: Diccionario con preferencias (opcional)
        
        Returns:
            True si se agregó correctamente, False en caso contrario
        """
        # Validar que los pesos sumen 1.0
        weights = client_data.get('weights', {})
        total_weight = sum(weights.values())
        
        if abs(total_weight - 1.0) > 0.01:  # Tolerancia pequeña para errores de redondeo
            raise ValueError(f"Los pesos deben sumar 1.0, actualmente suman {total_weight:.2f}")
        
        # Validar campos requeridos
        if 'name' not in client_data:
            raise ValueError("El campo 'name' es requerido")
        if 'description' not in client_data:
            raise ValueError("El campo 'description' es requerido")
        
        # Agregar cliente
        self.clients[client_id] = client_data
        
        # Guardar
        return self.save_clients()
    
    def update_client(self, client_id: str, client_data: Dict) -> bool:
        """
        Actualiza un cliente existente
        
        Args:
            client_id: ID del cliente a actualizar
            client_data: Diccionario con los datos actualizados
        
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        if client_id not in self.clients:
            raise ValueError(f"Cliente '{client_id}' no existe")
        
        # Validar pesos si se están actualizando
        if 'weights' in client_data:
            weights = client_data['weights']
            total_weight = sum(weights.values())
            if abs(total_weight - 1.0) > 0.01:
                raise ValueError(f"Los pesos deben sumar 1.0, actualmente suman {total_weight:.2f}")
        
        # Actualizar datos
        self.clients[client_id].update(client_data)
        
        # Guardar
        return self.save_clients()
    
    def delete_client(self, client_id: str) -> bool:
        """
        Elimina un cliente (solo si no es uno de los 6 originales)
        
        Args:
            client_id: ID del cliente a eliminar
        
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        # No permitir eliminar los 6 clientes originales
        original_clients = ['daenerys', 'cersei', 'bran', 'jon_snow', 'arya', 'tyrion']
        if client_id in original_clients:
            raise ValueError(f"No se puede eliminar el cliente '{client_id}' (es uno de los 6 originales)")
        
        if client_id not in self.clients:
            raise ValueError(f"Cliente '{client_id}' no existe")
        
        # Eliminar
        del self.clients[client_id]
        
        # Guardar
        return self.save_clients()
    
    def get_all_clients(self) -> Dict:
        """Obtiene todos los clientes"""
        return self.clients.copy()
    
    def get_client_list(self) -> List[str]:
        """Obtiene la lista de IDs de clientes"""
        return list(self.clients.keys())


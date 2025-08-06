from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from database import get_collection

class User:
    """User model for authentication and authorization."""
    
    def __init__(self, email=None, role='admin', is_active=True, _id=None, **kwargs):
        self._id = _id or ObjectId()
        self.email = email
        self.password_hash = kwargs.get('password_hash', '')
        self.role = role
        self.is_active = is_active
        self.created_at = kwargs.get('created_at', datetime.utcnow())
        self.updated_at = kwargs.get('updated_at', datetime.utcnow())
    
    @classmethod
    def from_dict(cls, data):
        """Create User instance from dictionary."""
        if not data:
            return None
            
        return cls(
            _id=data.get('_id'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            role=data.get('role', 'admin'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def save(self):
        """Save user to database."""
        users_collection = get_collection('users')
        self.updated_at = datetime.utcnow()
        
        user_data = {
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if hasattr(self, '_id') and self._id:
            # Update existing user
            users_collection.update_one(
                {'_id': self._id},
                {'$set': user_data}
            )
        else:
            # Create new user
            result = users_collection.insert_one(user_data)
            self._id = result.inserted_id
        
        return self
    
    def delete(self):
        """Delete user from database."""
        users_collection = get_collection('users')
        if hasattr(self, '_id') and self._id:
            users_collection.delete_one({'_id': self._id})
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email."""
        users_collection = get_collection('users')
        user_data = users_collection.find_one({'email': email})
        return cls.from_dict(user_data) if user_data else None
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID."""
        users_collection = get_collection('users')
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user_data = users_collection.find_one({'_id': user_id})
        return cls.from_dict(user_data) if user_data else None
    
    @classmethod
    def get_all(cls):
        """Get all users."""
        users_collection = get_collection('users')
        users_data = users_collection.find()
        return [cls.from_dict(user_data) for user_data in users_data]
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': str(self._id),
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at if isinstance(self.created_at, str) else (self.created_at.isoformat() if self.created_at else None),
            'updated_at': self.updated_at if isinstance(self.updated_at, str) else (self.updated_at.isoformat() if self.updated_at else None)
        }
    
    @property
    def id(self):
        """Get string representation of ID."""
        return str(self._id)
    
    def __repr__(self):
        return f'<User {self.email}>'

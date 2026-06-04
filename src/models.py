from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()

# 1. Tabela de Usuários (RH e T.I)
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)

# 2. Tabela de Departamentos
class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    
    # Relacionamento unificado: cria o .department_owner dentro de Equipment
    # e permite usar depto.equipments para listar itens de uso comum
    equipments = db.relationship('Equipment', backref='department_owner', lazy=True)

# 3. Tabela de Funcionários/Colaboradores
class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    status = db.Column(db.String(20), default='Active') # 'Active' ou 'Terminated'
    termination_date = db.Column(db.DateTime, nullable=True)

    hiring_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Chave estrangeira ligando ao setor
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    
    # Relacionamentos
    # O backref='employees' cria depto.employees automaticamente
    department = db.relationship('Department', backref='employees', lazy=True)
    
    # O backref='owner' cria equip.owner automaticamente para rastreabilidade
    equipments = db.relationship('Equipment', backref='owner', lazy=True)
    
    # O backref='employee' cria doc.employee automaticamente para os termos
    documents = db.relationship('Document', backref='employee', lazy=True)

# 4. Tabela de Equipamentos/Ativos (Modificada para Rastreabilidade)
class Equipment(db.Model):
    __tablename__ = 'equipments'
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), nullable=True)
    inventory_status = db.Column(db.String(50), default='Available') # 'Available', 'Assigned', 'Under Review'
    item_type = db.Column(db.String(50), nullable=True)
    assignment_date = db.Column(db.DateTime, nullable=True)
    
    # Chaves Estrangeiras (Mantêm-se preenchidas em 'Under Review' para guardar o histórico)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    # Relacionamentos adicionais para Celulares (IMEI e números)
    phones = db.relationship('EquipmentPhone', backref='equipment', lazy=True, cascade="all, delete-orphan")
    imeis = db.relationship('EquipmentImei', backref='equipment', lazy=True, cascade="all, delete-orphan")

# 5. Tabela de Termos de Responsabilidade / Documentos
class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    upload_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)

# 6. Tabela de Histórico de Movimentações (Auditoria Completa)
class Movement(db.Model):
    __tablename__ = 'movements'
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, nullable=False)
    equipment_model = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), nullable=True)
    previous_user = db.Column(db.Text, nullable=True) # Ex: "Ex-colaborador: João (CPF: 123) | Obs: Devolvido riscado"
    action = db.Column(db.String(100), nullable=False) # Ex: "Retido para Revisão (Desligamento)" ou "Liberado após desligamento"
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# 7. Tabelas Auxiliares para Smartphones
class EquipmentPhone(db.Model):
    __tablename__ = 'equipment_phones'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(30), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipments.id'), nullable=False)

class EquipmentImei(db.Model):
    __tablename__ = 'equipment_imeis'
    id = db.Column(db.Integer, primary_key=True)
    imei_value = db.Column(db.String(50), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipments.id'), nullable=False)
"""
Модуль работы с базой данных SQLite через SQLAlchemy ORM.
Хранит результаты экспериментов и данные пользователей.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os

Base = declarative_base()


class Experiment(Base):
    """
    Модель для хранения результатов экспериментов по кручению.
    """
    __tablename__ = 'experiments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    user_name = Column(String(100), nullable=False)
    material = Column(String(50), nullable=False)
    diameter = Column(Float, nullable=False)  # м
    length = Column(Float, nullable=False)    # м
    
    # Входные данные в JSON
    input_params = Column(Text, nullable=False)
    
    # Результаты расчетов в JSON
    results = Column(Text, nullable=False)
    
    def __repr__(self):
        return f"<Experiment(id={self.id}, user={self.user_name}, material={self.material}, date={self.timestamp})>"


class User(Base):
    """
    Модель для хранения данных пользователей (опционально).
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    group = Column(String(50), nullable=False)
    experiments_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, group={self.group})>"


class TestResult(Base):
    """
    Модель для хранения результатов тестирования.
    """
    __tablename__ = 'test_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    user_name = Column(String(100), nullable=False)
    score = Column(Integer, nullable=False)  # Количество правильных ответов из 8
    answers = Column(Text, nullable=False)   # JSON с ответами
    
    def __repr__(self):
        return f"<TestResult(id={self.id}, user={self.user_name}, score={self.score}/8)>"


class DatabaseManager:
    """
    Менеджер для работы с базой данных.
    """
    
    def __init__(self, db_path: str = 'torsion_lab.db'):
        """
        Инициализация менеджера БД.
        
        Args:
            db_path: Путь к файлу базы данных SQLite
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_experiment(self, user_name: str, material: str, diameter: float, 
                       length: float, input_params: dict, results: dict) -> int:
        """
        Сохранение результатов эксперимента в БД.
        
        Args:
            user_name: ФИО пользователя
            material: Материал образца
            diameter: Диаметр образца, м
            length: Длина образца, м
            input_params: Словарь с входными параметрами
            results: Словарь с результатами расчетов
            
        Returns:
            ID созданной записи
        """
        session = self.Session()
        try:
            experiment = Experiment(
                user_name=user_name,
                material=material,
                diameter=diameter,
                length=length,
                input_params=json.dumps(input_params, ensure_ascii=False),
                results=json.dumps(results, ensure_ascii=False)
            )
            session.add(experiment)
            session.commit()
            exp_id = experiment.id
            
            # Обновляем счетчик экспериментов пользователя
            user = session.query(User).filter_by(name=user_name).first()
            if user:
                user.experiments_count += 1
                session.commit()
            
            return exp_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_experiment(self, experiment_id: int) -> dict:
        """
        Получение данных эксперимента по ID.
        
        Args:
            experiment_id: ID эксперимента
            
        Returns:
            Словарь с данными эксперимента
        """
        session = self.Session()
        try:
            exp = session.query(Experiment).filter_by(id=experiment_id).first()
            if exp:
                return {
                    'id': exp.id,
                    'timestamp': exp.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'user_name': exp.user_name,
                    'material': exp.material,
                    'diameter': exp.diameter,
                    'length': exp.length,
                    'input_params': json.loads(exp.input_params),
                    'results': json.loads(exp.results)
                }
            return None
        finally:
            session.close()
    
    def get_all_experiments(self, user_name: str = None) -> list:
        """
        Получение всех экспериментов (с фильтрацией по пользователю).
        
        Args:
            user_name: Фильтр по имени пользователя (опционально)
            
        Returns:
            Список словарей с данными экспериментов
        """
        session = self.Session()
        try:
            query = session.query(Experiment)
            if user_name:
                query = query.filter_by(user_name=user_name)
            
            experiments = query.order_by(Experiment.timestamp.desc()).all()
            
            result = []
            for exp in experiments:
                result.append({
                    'id': exp.id,
                    'timestamp': exp.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'user_name': exp.user_name,
                    'material': exp.material,
                    'diameter': exp.diameter,
                    'length': exp.length
                })
            return result
        finally:
            session.close()
    
    def delete_experiment(self, experiment_id: int) -> bool:
        """
        Удаление эксперимента из БД.
        
        Args:
            experiment_id: ID эксперимента
            
        Returns:
            True если удаление прошло успешно
        """
        session = self.Session()
        try:
            exp = session.query(Experiment).filter_by(id=experiment_id).first()
            if exp:
                session.delete(exp)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_user(self, name: str, group: str) -> int:
        """
        Сохранение или обновление данных пользователя.
        
        Args:
            name: ФИО пользователя
            group: Группа
            
        Returns:
            ID пользователя
        """
        session = self.Session()
        try:
            user = session.query(User).filter_by(name=name).first()
            if user:
                user.group = group
            else:
                user = User(name=name, group=group)
                session.add(user)
            session.commit()
            return user.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_test_result(self, user_name: str, score: int, answers: dict) -> int:
        """
        Сохранение результатов тестирования.
        
        Args:
            user_name: ФИО пользователя
            score: Количество правильных ответов
            answers: Словарь с ответами
            
        Returns:
            ID записи
        """
        session = self.Session()
        try:
            test_result = TestResult(
                user_name=user_name,
                score=score,
                answers=json.dumps(answers, ensure_ascii=False)
            )
            session.add(test_result)
            session.commit()
            return test_result.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_test_results(self, user_name: str = None) -> list:
        """
        Получение результатов тестирования.
        
        Args:
            user_name: Фильтр по имени (опционально)
            
        Returns:
            Список результатов тестов
        """
        session = self.Session()
        try:
            query = session.query(TestResult)
            if user_name:
                query = query.filter_by(user_name=user_name)
            
            results = query.order_by(TestResult.timestamp.desc()).all()
            
            return [{
                'id': r.id,
                'timestamp': r.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'user_name': r.user_name,
                'score': r.score,
                'answers': json.loads(r.answers)
            } for r in results]
        finally:
            session.close()


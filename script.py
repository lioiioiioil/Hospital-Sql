import random
from faker import Faker
from datetime import datetime, timedelta, date

fake = Faker('ru_RU')

class HospitalDataGenerator:
    def __init__(self):
        self.fake = fake
        self.data = {}  # Храним все сгенерированные данные
        
    def format_value_for_sql(self, value):
        """Форматирование значения для SQL"""
        if value is None:
            return 'NULL'
        elif isinstance(value, str):
            escaped_value = value.replace("'", "''")
            return f"'{escaped_value}'"
        elif isinstance(value, (datetime, date)):
            return f"'{value.strftime('%Y-%m-%d')}'"
        elif isinstance(value, bool):
            return 'TRUE' if value else 'FALSE'
        elif isinstance(value, float):
            return str(value)
        else:
            return str(value)

    def generate_and_save_data(self):
        """Генерация и сохранение всех данных в правильном порядке"""
        print("Начало генерации данных для больницы...")
        
        # Очистка файла и добавление TRUNCATE команд
        with open('hospital_data.sql', 'w', encoding='utf-8') as f:
            f.write("-- Очистка таблиц перед вставкой новых данных\n")
            f.write("TRUNCATE TABLE \n")
            f.write("  conclusions, appointments, prescriptions, patient_restrictions,\n")
            f.write("  position_history, salary_history, warehouse_history, warehouse,\n")
            f.write("  slots, cabinets, buildings, employees, patients, personal_data,\n")
            f.write("  emr, addresses, restriction_types, medications, services,\n")
            f.write("  positions, professions, suppliers\n")
            f.write("RESTART IDENTITY CASCADE;\n\n")
        
        # 1. Сначала генерируем все справочники
        self._generate_dictionaries()
        
        # 2. Затем основные таблицы в правильном порядке зависимостей
        self._generate_core_tables()
        
        # 3. Наконец, таблицы с внешними ключами
        self._generate_relation_tables()
        
        print("Генерация данных завершена! Файл: hospital_data.sql")
        print("\nДля выполнения SQL файла в PostgreSQL:")
        print("psql -d your_database_name -f hospital_data.sql")

    def _generate_dictionaries(self):
        """Генерация справочных таблиц (без внешних ключей)"""
        print("=== Генерация справочных таблиц ===")
        
        # Адреса - 15,000 записей
        addresses = []
        for i in range(15000):
            if i % 1000 == 0:
                print(f"  Генерация адресов: {i}/15000")
            addresses.append({
                'city': fake.city(),
                'street': fake.street_name(),
                'house': str(random.randint(1, 200)),
                'building': random.choice([None, str(random.randint(1, 10)), 'А', 'Б', 'В']),
                'apartment_office': str(random.randint(1, 300)) if random.random() > 0.3 else None,
                'description': fake.text(100) if random.random() > 0.7 else None
            })
        self._save_to_sql(addresses, 'addresses')
        self.data['addresses'] = list(range(1, len(addresses) + 1))
        print(f"Сгенерировано {len(addresses)} адресов")

        # Профессии - оставляем разумное количество (20)
        professions = [
            "Терапевт", "Хирург", "Кардиолог", "Невролог", "Офтальмолог",
            "Отоларинголог", "Стоматолог", "Педиатр", "Гинеколог", "Уролог",
            "Дерматолог", "Психиатр", "Онколог", "Эндокринолог", "Гастроэнтеролог",
            "Медсестра", "Фельдшер", "Лаборант", "Рентгенолог", "Физиотерапевт"
        ]
        professions_data = [{'name': name} for name in professions]
        self._save_to_sql(professions_data, 'professions')
        self.data['professions'] = list(range(1, len(professions_data) + 1))
        print(f"Сгенерировано {len(professions_data)} профессий")

        # Должности - оставляем разумное количество (15)
        positions = [
            "Врач", "Старший врач", "Заведующий отделением", "Главный врач",
            "Медсестра", "Старшая медсестра", "Фельдшер", "Лаборант",
            "Администратор", "Регистратор", "Санитар", "Младший медперсонал",
            "Интерн", "Ординатор", "Заведующий лабораторией"
        ]
        positions_data = [{'name': name} for name in positions]
        self._save_to_sql(positions_data, 'positions')
        self.data['positions'] = list(range(1, len(positions_data) + 1))
        print(f"Сгенерировано {len(positions_data)} должностей")

        # Услуги - 200 записей
        services = []
        service_types = ["Консультация", "Осмотр", "Диагностика", "Анализы", "УЗИ", "Рентген", "МРТ", "КТ", "ЭКГ", "Физиотерапия"]
        specializations = ["терапевта", "хирурга", "кардиолога", "невролога", "офтальмолога", "стоматолога", "педиатра", "гинеколога", ""]
        
        for i in range(200):
            if i % 50 == 0:
                print(f"  Генерация услуг: {i}/200")
            service_type = random.choice(service_types)
            specialization = random.choice(specializations)
            services.append({
                'name': f"{service_type} {specialization}".strip(),
                'description': fake.text(100),
                'price': round(random.uniform(500, 50000), 2),
                'actual_from': fake.date_between(start_date='-2y', end_date='-1y'),
                'actual_to': fake.date_between(start_date='+1y', end_date='+2y') if random.random() > 0.7 else None
            })
        self._save_to_sql(services, 'services')
        self.data['services'] = list(range(1, len(services) + 1))
        print(f"Сгенерировано {len(services)} услуг")

        # Лекарства - 500 записей
        medications = []
        drug_names = [
            "Парацетамол", "Ибупрофен", "Амоксициллин", "Аспирин", "Метформин",
            "Аторвастатин", "Левотрироксин", "Метопролол", "Симвастатин", "Омепразол",
            "Лозартан", "Амлодипин", "Ситаглиптин", "Глибенкламид", "Инсулин",
            "Варфарин", "Клопидогрел", "Преднизолон", "Азитромицин", "Цетрин"
        ]
        forms = ["таблетки", "капсулы", "сироп", "мазь", "инъекции", "капли", "спрей", "гель"]
        
        for i in range(500):
            if i % 100 == 0:
                print(f"  Генерация лекарств: {i}/500")
            drug_name = random.choice(drug_names)
            form = random.choice(forms)
            dosage = f"{random.randint(1, 500)} {random.choice(['мг', 'г', 'мл'])}"
            medications.append({
                'description': f"{drug_name}, {form} {dosage}",
                'expiration_date': fake.date_between(start_date='+1y', end_date='+5y')
            })
        self._save_to_sql(medications, 'medications')
        self.data['medications'] = list(range(1, len(medications) + 1))
        print(f"Сгенерировано {len(medications)} лекарств")

        # Типы ограничений - 100 записей
        restriction_types = []
        allergy_types = [
            "Пенициллин", "Аспирин", "Йод", "Новокаин", "Лидокаин", "Анальгин", 
            "Пыльца", "Пыль", "Шерсть животных", "Молоко", "Яйца", "Орехи", 
            "Морепродукты", "Цитрусовые", "Шоколад", "Глютен", "Лактоза", "Соя"
        ]
        
        for i in range(100):
            allergy = random.choice(allergy_types)
            restriction_types.append({
                'description': f"Аллергия на {allergy}",
                'prohibitions': f"Запрещены препараты содержащие {allergy}"
            })
        self._save_to_sql(restriction_types, 'restriction_types')
        self.data['restriction_types'] = list(range(1, len(restriction_types) + 1))
        print(f"Сгенерировано {len(restriction_types)} типов ограничений")

        # Поставщики - 100 записей
        suppliers = []
        for i in range(100):
            suppliers.append({
                'name': fake.company(),
                'info': fake.text(100)
            })
        self._save_to_sql(suppliers, 'suppliers')
        self.data['suppliers'] = list(range(1, len(suppliers) + 1))
        print(f"Сгенерировано {len(suppliers)} поставщиков")

    def _generate_core_tables(self):
        """Генерация основных таблиц"""
        print("\n=== Генерация основных таблиц ===")
        
        # Личные данные - 15,000 записей
        personal_data = []
        used_passports = set()
        
        for i in range(15000):
            if i % 1000 == 0:
                print(f"  Генерация личных данных: {i}/15000")
            
            while True:
                passport = f"{random.randint(1000, 9999)} {random.randint(100000, 999999)}"
                if passport not in used_passports:
                    used_passports.add(passport)
                    break
            
            # ВСЕГДА используем существующий address_id, так как поле NOT NULL
            address_id = random.choice(self.data['addresses'])
                
            gender = random.choice(['male', 'female'])
            personal_data.append({
                'last_name': fake.last_name_female() if gender == 'female' else fake.last_name_male(),
                'first_name': fake.first_name_female() if gender == 'female' else fake.first_name_male(),
                'middle_name': fake.middle_name_female() if gender == 'female' else fake.middle_name_male(),
                'birth_date': fake.date_of_birth(minimum_age=0, maximum_age=100),
                'passport': passport,
                'address_id': address_id,  # Всегда существующий ID
                'contacts': f"+7{random.randint(9000000000, 9999999999)}",
                'gender': gender
            })
        
        self._save_to_sql(personal_data, 'personal_data')
        self.data['personal_data'] = list(range(1, len(personal_data) + 1))
        print(f"Сгенерировано {len(personal_data)} личных записей")

        # ЭМК - 15,000 записей
        emr_list = []
        used_policies = set()
        
        for i in range(15000):
            if i % 1000 == 0:
                print(f"  Генерация ЭМК: {i}/15000")
            
            while True:
                policy_number = f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(100000, 999999)}"
                if policy_number not in used_policies:
                    used_policies.add(policy_number)
                    break
            emr_list.append({'policy_number': policy_number})
        
        self._save_to_sql(emr_list, 'emr')
        self.data['emr'] = list(range(1, len(emr_list) + 1))
        print(f"Сгенерировано {len(emr_list)} ЭМК")

        # Пациенты - 15,000 записей (связываем personal_data и emr 1:1)
        patients = []
        min_count = min(len(self.data['personal_data']), len(self.data['emr']))
        for i in range(min_count):
            if i % 1000 == 0:
                print(f"  Генерация пациентов: {i}/{min_count}")
            patients.append({
                'personal_data_id': i + 1,
                'emr_id': i + 1
            })
        
        self._save_to_sql(patients, 'patients')
        self.data['patients'] = list(range(1, len(patients) + 1))
        print(f"Сгенерировано {len(patients)} пациентов")

        # Сотрудники - 2,000 записей
        employees = []
        for i in range(2000):
            if i % 500 == 0:
                print(f"  Генерация сотрудников: {i}/2000")

            gender = random.choice(['male', 'female'])
            employees.append({
                'last_name': fake.last_name_female() if gender == 'female' else fake.last_name_male(),
                'first_name': fake.first_name_female() if gender == 'female' else fake.first_name_male(),
                'middle_name': fake.middle_name_female() if gender == 'female' else fake.middle_name_male(),
                'profession_id': random.choice(self.data['professions'])
            })
        
        self._save_to_sql(employees, 'employees')
        self.data['employees'] = list(range(1, len(employees) + 1))
        print(f"Сгенерировано {len(employees)} сотрудников")

        # Корпуса - 20 записей
        buildings = []
        building_names = [
            "Главный корпус", "Хирургический корпус", "Терапевтический корпус",
            "Диагностический центр", "Поликлиника", "Стационар", "Лабораторный корпус",
            "Реабилитационный центр", "Родильное отделение", "Инфекционное отделение",
            "Кардиологический корпус", "Неврологический корпус", "Онкологический центр",
            "Травматологический корпус", "Детский корпус", "Стоматологическая поликлиника"
        ]
        for i in range(20):
            buildings.append({
                'name': f"{random.choice(building_names)} {random.randint(1, 5)}",
                'address_id': random.choice(self.data['addresses'])
            })
        
        self._save_to_sql(buildings, 'buildings')
        self.data['buildings'] = list(range(1, len(buildings) + 1))
        print(f"Сгенерировано {len(buildings)} корпусов")

        # Кабинеты - 1,000 записей
        cabinets = []
        for i in range(1000):
            if i % 200 == 0:
                print(f"  Генерация кабинетов: {i}/1000")
            cabinets.append({
                'building_id': random.choice(self.data['buildings']),
                'floor': random.randint(1, 10),
                'cabinet_number': f"{random.randint(1, 10)}-{random.randint(100, 999)}",
                'description': fake.text(100) if random.random() > 0.8 else None
            })
        
        self._save_to_sql(cabinets, 'cabinets')
        self.data['cabinets'] = list(range(1, len(cabinets) + 1))
        print(f"Сгенерировано {len(cabinets)} кабинетов")

    def _generate_relation_tables(self):
        """Генерация таблиц со связями"""
        print("\n=== Генерация таблиц со связями ===")
        
        # Слоты - 100,000 записей
        slots = []
        start_date = datetime.now() - timedelta(days=730)  # 2 года назад
        
        for i in range(100000):
            if i % 10000 == 0:
                print(f"  Генерация слотов: {i}/100000")
            
            slot_date = start_date + timedelta(days=random.randint(0, 730))
            time_start = random.randint(8, 20)  # с 8 утра до 8 вечера
            
            slots.append({
                'doctor_id': random.choice(self.data['employees']),
                'cabinet_id': random.choice(self.data['cabinets']),
                'date': slot_date.date(),
                'time_from': f"{time_start:02d}:00:00",
                'time_to': f"{time_start + random.randint(1, 2):02d}:00:00",
                'is_occupied': random.random() > 0.3  # 70% занято
            })
        
        self._save_to_sql(slots, 'slots')
        self.data['slots'] = list(range(1, len(slots) + 1))
        print(f"Сгенерировано {len(slots)} слотов")

        # Обращения - 50,000 записей
        appointments = []
        statuses = ['scheduled', 'completed', 'cancelled', 'no_show']
        
        for i in range(50000):
            if i % 10000 == 0:
                print(f"  Генерация обращений: {i}/50000")
            appointments.append({
                'emr_id': random.choice(self.data['emr']),
                'service_id': random.choice(self.data['services']),
                'slot_id': random.choice(self.data['slots']),
                'status': random.choice(statuses)
            })
        
        self._save_to_sql(appointments, 'appointments')
        self.data['appointments'] = list(range(1, len(appointments) + 1))
        print(f"Сгенерировано {len(appointments)} обращений")

        # Назначения - 75,000 записей
        prescriptions = []
        for i in range(75000):
            if i % 15000 == 0:
                print(f"  Генерация назначений: {i}/75000")
            
            issue_from = fake.date_between(start_date='-1y', end_date='today')
            issue_to = issue_from + timedelta(days=random.randint(1, 90))  # до 3 месяцев
            
            prescriptions.append({
                'emr_id': random.choice(self.data['emr']),
                'medication_id': random.choice(self.data['medications']),
                'issue_from': issue_from,
                'issue_to': issue_to
            })
        
        self._save_to_sql(prescriptions, 'prescriptions')
        print(f"Сгенерировано {len(prescriptions)} назначений")

        # Ограничения пациентов - 30,000 уникальных записей
        patient_restrictions = []
        used_restriction_pairs = set()
        
        # Максимальное количество уникальных пар
        max_pairs = len(self.data['emr']) * len(self.data['restriction_types'])
        target_count = min(30000, max_pairs)
        
        print(f"  Генерация ограничений пациентов: 0/{target_count}")
        while len(patient_restrictions) < target_count:
            if len(patient_restrictions) % 5000 == 0:
                print(f"  Генерация ограничений пациентов: {len(patient_restrictions)}/{target_count}")
            
            emr_id = random.choice(self.data['emr'])
            restriction_type_id = random.choice(self.data['restriction_types'])
            pair = (emr_id, restriction_type_id)
            
            if pair not in used_restriction_pairs:
                used_restriction_pairs.add(pair)
                patient_restrictions.append({
                    'emr_id': emr_id,
                    'restriction_type_id': restriction_type_id
                })
        
        self._save_to_sql(patient_restrictions, 'patient_restrictions')
        print(f"Сгенерировано {len(patient_restrictions)} уникальных ограничений пациентов")

        # История должностей - 10,000 записей
        position_history = []
        for i in range(10000):
            if i % 2000 == 0:
                print(f"  Генерация истории должностей: {i}/10000")
            
            start_date = fake.date_between(start_date='-10y', end_date='-1y')
            end_date = fake.date_between(start_date=start_date, end_date='today') if random.random() > 0.3 else None
            
            position_history.append({
                'position_id': random.choice(self.data['positions']),
                'employee_id': random.choice(self.data['employees']),
                'start_date': start_date,
                'end_date': end_date,
                'rate': random.randint(1, 2)
            })
        
        self._save_to_sql(position_history, 'position_history')
        print(f"Сгенерировано {len(position_history)} записей истории должностей")

        # История зарплат - 15,000 записей
        salary_history = []
        for i in range(15000):
            if i % 3000 == 0:
                print(f"  Генерация истории зарплат: {i}/15000")
            
            start_date = fake.date_between(start_date='-5y', end_date='-6m')
            end_date = fake.date_between(start_date=start_date, end_date='today') if random.random() > 0.4 else None
            
            salary_history.append({
                'position_id': random.choice(self.data['positions']),
                'profession_id': random.choice(self.data['professions']),
                'employee_id': random.choice(self.data['employees']),
                'hours_per_rate': random.choice([36, 40, 48]),
                'amount': round(random.uniform(30000, 250000), 2),  # увеличен диапазон зарплат
                'actual_from': start_date,
                'actual_to': end_date
            })
        
        self._save_to_sql(salary_history, 'salary_history')
        print(f"Сгенерировано {len(salary_history)} записей истории зарплат")

        # История склада - 50,000 записей
        warehouse_history = []
        for i in range(50000):
            if i % 10000 == 0:
                print(f"  Генерация истории склада: {i}/50000")
            
            transaction_type = random.choice(['receipt', 'issue'])
            transaction_date = fake.date_between(start_date='-2y', end_date='today')
            
            warehouse_history.append({
                'medication_id': random.choice(self.data['medications']),
                'type': transaction_type,
                'emr_id': random.choice(self.data['emr']) if transaction_type == 'issue' else None,
                'supplier_id': random.choice(self.data['suppliers']) if transaction_type == 'receipt' else None,
                'quantity': random.randint(10, 5000),
                'date': transaction_date
            })
        
        self._save_to_sql(warehouse_history, 'warehouse_history')
        print(f"Сгенерировано {len(warehouse_history)} записей истории склада")

        # Заключения - 40,000 уникальных записей
        conclusions = []
        used_appointment_ids = set()
        
        print(f"  Генерация заключений: 0/40000")
        while len(conclusions) < 40000 and len(used_appointment_ids) < len(self.data['appointments']):
            if len(conclusions) % 8000 == 0:
                print(f"  Генерация заключений: {len(conclusions)}/40000")
            
            # Находим appointment_id, который еще не использовался
            available_appointments = [id for id in self.data['appointments'] if id not in used_appointment_ids]
            if not available_appointments:
                break
                
            appointment_id = random.choice(available_appointments)
            used_appointment_ids.add(appointment_id)
            
            conclusions.append({
                'appointment_id': appointment_id,
                'file_link': f"/reports/{fake.uuid4()}.pdf"
            })
        
        self._save_to_sql(conclusions, 'conclusions')
        print(f"Сгенерировано {len(conclusions)} заключений")

        # Склад - 500 записей (по количеству лекарств)
        warehouse = []
        for medication_id in self.data['medications']:
            warehouse.append({
                'medication_id': medication_id,
                'quantity': random.randint(0, 50000)
            })
        
        self._save_to_sql(warehouse, 'warehouse')
        print(f"Сгенерировано {len(warehouse)} записей склада")

    def _save_to_sql(self, data, table_name):
        """Сохранение данных в SQL файл"""
        with open('hospital_data.sql', 'a', encoding='utf-8') as f:
            for record in data:
                columns = ', '.join(record.keys())
                values = [self.format_value_for_sql(value) for value in record.values()]
                values_str = ', '.join(values)
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values_str});\n"
                f.write(sql)
            f.write('\n')

# Запуск генерации
if __name__ == "__main__":
    generator = HospitalDataGenerator()
    generator.generate_and_save_data()
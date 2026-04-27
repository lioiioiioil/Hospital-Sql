-- Создание enum для пола
CREATE TYPE gender_enum AS ENUM ('male', 'female');

-- Создание таблицы адресов
CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    street VARCHAR(100) NOT NULL,
    house VARCHAR(20) NOT NULL,
    building VARCHAR(20),
    apartment_office VARCHAR(20),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Индексы для addresses
CREATE INDEX idx_addresses_city ON addresses(city);
CREATE INDEX idx_addresses_street ON addresses(street);
CREATE INDEX idx_addresses_city_street ON addresses(city, street);

-- Создание таблицы личных данных
CREATE TABLE personal_data (
    id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    birth_date DATE NOT NULL,
    passport VARCHAR(20) UNIQUE NOT NULL,
    address_id INTEGER NOT NULL,
    contacts VARCHAR(200),
    gender gender_enum NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (address_id) REFERENCES addresses(id)
);

-- Индексы для personal_data
CREATE INDEX idx_personal_data_last_name ON personal_data(last_name);
CREATE INDEX idx_personal_data_first_name ON personal_data(first_name);
CREATE INDEX idx_personal_data_passport ON personal_data(passport);
CREATE INDEX idx_personal_data_birth_date ON personal_data(birth_date);
CREATE INDEX idx_personal_data_address ON personal_data(address_id);
CREATE INDEX idx_personal_data_full_name ON personal_data(last_name, first_name, middle_name);
CREATE INDEX idx_personal_data_active ON personal_data(deleted_at, created_at);

-- Создание таблицы ЭМК
CREATE TABLE emr (
    id SERIAL PRIMARY KEY,
    policy_number VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Индексы для emr
CREATE INDEX idx_emr_policy_number ON emr(policy_number);

-- Создание таблицы пациентов
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    personal_data_id INTEGER UNIQUE NOT NULL,
    emr_id INTEGER UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (personal_data_id) REFERENCES personal_data(id),
    FOREIGN KEY (emr_id) REFERENCES emr(id)
);

-- Индексы для patients
CREATE INDEX idx_patients_personal_data ON patients(personal_data_id);
CREATE INDEX idx_patients_emr ON patients(emr_id);
CREATE INDEX idx_patients_created ON patients(created_at);
CREATE INDEX idx_patients_active ON patients(deleted_at, created_at);

-- Создание таблицы типов ограничений
CREATE TABLE restriction_types (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    prohibitions TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Создание таблицы ограничений пациентов
CREATE TABLE patient_restrictions (
    id SERIAL PRIMARY KEY,
    emr_id INTEGER NOT NULL,
    restriction_type_id INTEGER NOT NULL,
    FOREIGN KEY (emr_id) REFERENCES emr(id),
    FOREIGN KEY (restriction_type_id) REFERENCES restriction_types(id)
);

-- Индексы для patient_restrictions
CREATE INDEX idx_patient_restrictions_emr ON patient_restrictions(emr_id);
CREATE INDEX idx_patient_restrictions_type ON patient_restrictions(restriction_type_id);
CREATE UNIQUE INDEX idx_patient_restrictions_composite ON patient_restrictions(emr_id, restriction_type_id);

-- Создание таблицы лекарств
CREATE TABLE medications (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    expiration_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Индексы для medications
CREATE INDEX idx_medications_expiration ON medications(expiration_date);
CREATE INDEX idx_medications_fresh ON medications(expiration_date, deleted_at);

-- Создание таблицы назначений
CREATE TABLE prescriptions (
    id SERIAL PRIMARY KEY,
    emr_id INTEGER NOT NULL,
    medication_id INTEGER NOT NULL,
    issue_from DATE NOT NULL,
    issue_to DATE NOT NULL,
    FOREIGN KEY (emr_id) REFERENCES emr(id),
    FOREIGN KEY (medication_id) REFERENCES medications(id)
);

-- Индексы для prescriptions
CREATE INDEX idx_prescriptions_emr ON prescriptions(emr_id);
CREATE INDEX idx_prescriptions_medication ON prescriptions(medication_id);
CREATE INDEX idx_prescriptions_issue_from ON prescriptions(issue_from);
CREATE INDEX idx_prescriptions_issue_to ON prescriptions(issue_to);
CREATE INDEX idx_prescriptions_composite ON prescriptions(emr_id, medication_id);

-- Создание таблицы услуг
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    actual_from DATE NOT NULL,
    actual_to DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Индексы для services
CREATE INDEX idx_services_name ON services(name);
CREATE INDEX idx_services_price ON services(price);
CREATE INDEX idx_services_actual_from ON services(actual_from);
CREATE INDEX idx_services_actual_to ON services(actual_to);

-- Создание таблицы профессий
CREATE TABLE professions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Индексы для professions
CREATE INDEX idx_professions_name ON professions(name);

-- Создание таблицы сотрудников
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    profession_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (profession_id) REFERENCES professions(id)
);

-- Индексы для employees
CREATE INDEX idx_employees_last_name ON employees(last_name);
CREATE INDEX idx_employees_first_name ON employees(first_name);
CREATE INDEX idx_employees_profession ON employees(profession_id);
CREATE INDEX idx_employees_full_name ON employees(last_name, first_name, middle_name);

-- Создание таблицы корпусов
CREATE TABLE buildings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (address_id) REFERENCES addresses(id)
);

-- Индексы для buildings
CREATE INDEX idx_buildings_name ON buildings(name);
CREATE INDEX idx_buildings_address ON buildings(address_id);

-- Создание таблицы кабинетов
CREATE TABLE cabinets (
    id SERIAL PRIMARY KEY,
    building_id INTEGER NOT NULL,
    floor INTEGER NOT NULL,
    cabinet_number VARCHAR(20) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (building_id) REFERENCES buildings(id)
);

-- Индексы для cabinets
CREATE INDEX idx_cabinets_building ON cabinets(building_id);
CREATE INDEX idx_cabinets_floor ON cabinets(floor);
CREATE INDEX idx_cabinets_number ON cabinets(cabinet_number);
CREATE INDEX idx_cabinets_building_floor ON cabinets(building_id, floor);

-- Создание таблицы слотов
CREATE TABLE slots (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER NOT NULL,
    cabinet_id INTEGER NOT NULL,
    date DATE NOT NULL,
    time_from TIME NOT NULL,
    time_to TIME NOT NULL,
    is_occupied BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES employees(id),
    FOREIGN KEY (cabinet_id) REFERENCES cabinets(id)
);

-- Индексы для slots
CREATE INDEX idx_slots_doctor ON slots(doctor_id);
CREATE INDEX idx_slots_cabinet ON slots(cabinet_id);
CREATE INDEX idx_slots_date ON slots(date);
CREATE INDEX idx_slots_occupied ON slots(is_occupied);
CREATE INDEX idx_slots_doctor_date ON slots(doctor_id, date);
CREATE INDEX idx_slots_date_occupied ON slots(date, is_occupied);

-- Создание таблицы обращений
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    emr_id INTEGER NOT NULL,
    service_id INTEGER NOT NULL,
    slot_id INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (emr_id) REFERENCES emr(id),
    FOREIGN KEY (service_id) REFERENCES services(id),
    FOREIGN KEY (slot_id) REFERENCES slots(id)
);

-- Индексы для appointments
CREATE INDEX idx_appointments_emr ON appointments(emr_id);
CREATE INDEX idx_appointments_service ON appointments(service_id);
CREATE INDEX idx_appointments_slot ON appointments(slot_id);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_emr_status ON appointments(emr_id, status);

-- Создание таблицы заключений
CREATE TABLE conclusions (
    id SERIAL PRIMARY KEY,
    appointment_id INTEGER UNIQUE NOT NULL,
    file_link VARCHAR(500) NOT NULL,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id)
);

-- Индексы для conclusions
CREATE INDEX idx_conclusions_appointment ON conclusions(appointment_id);

-- Создание таблицы должностей
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Индексы для positions
CREATE INDEX idx_positions_name ON positions(name);

-- Создание таблицы истории должностей
CREATE TABLE position_history (
    id SERIAL PRIMARY KEY,
    position_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    rate INTEGER NOT NULL,
    FOREIGN KEY (position_id) REFERENCES positions(id),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- Индексы для position_history
CREATE INDEX idx_position_history_position ON position_history(position_id);
CREATE INDEX idx_position_history_employee ON position_history(employee_id);
CREATE INDEX idx_position_history_start ON position_history(start_date);
CREATE INDEX idx_position_history_end ON position_history(end_date);
CREATE INDEX idx_position_history_employee_start ON position_history(employee_id, start_date);

-- Создание таблицы истории зарплат
CREATE TABLE salary_history (
    id SERIAL PRIMARY KEY,
    position_id INTEGER NOT NULL,
    profession_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    hours_per_rate INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    actual_from DATE NOT NULL,
    actual_to DATE,
    FOREIGN KEY (position_id) REFERENCES positions(id),
    FOREIGN KEY (profession_id) REFERENCES professions(id),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- Индексы для salary_history
CREATE INDEX idx_salary_history_position ON salary_history(position_id);
CREATE INDEX idx_salary_history_profession ON salary_history(profession_id);
CREATE INDEX idx_salary_history_employee ON salary_history(employee_id);
CREATE INDEX idx_salary_history_from ON salary_history(actual_from);
CREATE INDEX idx_salary_history_to ON salary_history(actual_to);
CREATE INDEX idx_salary_history_employee_from ON salary_history(employee_id, actual_from);

-- Создание таблицы поставщиков
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    info TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Индексы для suppliers
CREATE INDEX idx_suppliers_name ON suppliers(name);

-- Создание таблицы склада
CREATE TABLE warehouse (
    batch_id SERIAL PRIMARY KEY,
    medication_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    FOREIGN KEY (medication_id) REFERENCES medications(id)
);

-- Индексы для warehouse
CREATE INDEX idx_warehouse_medication ON warehouse(medication_id);
CREATE INDEX idx_warehouse_quantity ON warehouse(quantity);
CREATE INDEX idx_warehouse_medication_quantity ON warehouse(medication_id, quantity);

-- Создание таблицы истории склада
CREATE TABLE warehouse_history (
    id SERIAL PRIMARY KEY,
    medication_id INTEGER NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('receipt', 'issue')),
    emr_id INTEGER,
    supplier_id INTEGER,
    quantity INTEGER NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (medication_id) REFERENCES medications(id),
    FOREIGN KEY (emr_id) REFERENCES emr(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- Индексы для warehouse_history
CREATE INDEX idx_wh_history_medication ON warehouse_history(medication_id);
CREATE INDEX idx_wh_history_type ON warehouse_history(type);
CREATE INDEX idx_wh_history_emr ON warehouse_history(emr_id);
CREATE INDEX idx_wh_history_supplier ON warehouse_history(supplier_id);
CREATE INDEX idx_wh_history_date ON warehouse_history(date);
CREATE INDEX idx_wh_history_medication_date ON warehouse_history(medication_id, date);
CREATE INDEX idx_wh_history_type_date ON warehouse_history(type, date);

-- Триггеры для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Создание триггеров для всех таблиц с updated_at
CREATE TRIGGER update_personal_data_updated_at BEFORE UPDATE ON personal_data FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_emr_updated_at BEFORE UPDATE ON emr FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_addresses_updated_at BEFORE UPDATE ON addresses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_restriction_types_updated_at BEFORE UPDATE ON restriction_types FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_medications_updated_at BEFORE UPDATE ON medications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON employees FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_professions_updated_at BEFORE UPDATE ON professions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cabinets_updated_at BEFORE UPDATE ON cabinets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_buildings_updated_at BEFORE UPDATE ON buildings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_slots_updated_at BEFORE UPDATE ON slots FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_suppliers_updated_at BEFORE UPDATE ON suppliers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
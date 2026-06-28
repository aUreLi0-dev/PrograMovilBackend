-- migrate:up

-- ==========================================
-- SEED DATA - Aligned with Frontend JSONs
-- Fuentes:
--   users.json, carreras.json, courses.json, docentes.json,
--   curriculums.json, especialidades.json, curriculum_courses.json,
--   curriculum_course_specialties.json, course_prerequisites.json,
--   evaluaciones.json, secciones.json, enrollments.json,
--   notas_estudiantes.json, user_especialidades.json
-- ==========================================

-- 1. TABLAS BASE
INSERT INTO app_user (id, code, full_name, institutional_email, password_hash, google_id, token_version)
VALUES
  (1,  '20235218', 'Jefferson Angelo Sanchez Palacios',     '20235218@aloe.ulima.edu.pe', 'ulima123', NULL, 1),
  (2,  '20232548', 'Samantha Camila Rodríguez Melendez',    '20232548@aloe.ulima.edu.pe', 'ulima123', NULL, 1),
  (3,  '20232907', 'Martín Rodrigo Tejada Montesinos',      '20232907@aloe.ulima.edu.pe', 'ulima123', NULL, 1),
  (4,  '20232637', 'Melissa Alexandra Ruiz Delgado',        '20232637@aloe.ulima.edu.pe', 'ulima123', NULL, 1),
  (5,  '20232685', 'Julio Gabriel Salazar Torres',          '20232685@aloe.ulima.edu.pe', 'ulima123', NULL, 1),
  (6,  '20231098', 'Nehemias Luis Falcon Farfan',           '20231098@aloe.ulima.edu.pe', 'ulima123', NULL, 1),
  (7,  '20225158', 'Hans Anthony Quispe Mamani',            '20225158@aloe.ulima.edu.pe', 'ulima123', NULL, 1),
  (8,  '20231483', 'Ronald Alfredo Hurtado Lago',           '20231483@aloe.ulima.edu.pe', 'ulima123', NULL, 1),
  (9,  '20230000', 'Prueba - SetUpEspecialidad',            '20230000@aloe.ulima.edu.pe', 'ulima123', NULL, 1),
  (10, '20240000', 'Prueba2 - SetUpEspecialidad',           '20240000@aloe.ulima.edu.pe', 'ulima123', NULL, 1);

INSERT INTO career (id, code, name, faculty)
VALUES
  (1, 'ING_SISTEMAS',   'Ingeniería de Sistemas',    'Facultad de Ingeniería'),
  (2, 'ING_INDUSTRIAL', 'Ingeniería Industrial',     'Facultad de Ingeniería'),
  (3, 'ADMINISTRACION', 'Administración',            'Facultad de Ciencias Empresariales y Económicas');

INSERT INTO course (id, code, name, default_credit, origin_faculty)
VALUES
  (1,  '510003', 'Lenguaje y Comunicación I',                                4, NULL),
  (2,  '510006', 'Procesos Psicológicos',                                    3, NULL),
  (3,  '510007', 'Ética Ciudadana',                                          2, NULL),
  (4,  '510005', 'Introducción a la Ingeniería',                             3, NULL),
  (5,  '6508',   'Metodologías de Investigación',                            3, NULL),
  (6,  '510014', 'Precálculo',                                               5, NULL),
  (7,  '6511',   'Lenguaje y Comunicación II',                               3, NULL),
  (8,  '510010', 'Filosofía Aplicada',                                       3, NULL),
  (9,  '510015', 'Fundamentos de Economía',                                  3, NULL),
  (10, '510011', 'Introducción al Comercio Internacional',                   3, NULL),
  (11, '6384',   'Álgebra Lineal',                                           3, NULL),
  (12, '6503',   'Cálculo I',                                                5, NULL),
  (13, '560040', 'Inteligencia Artificial Aplicada',                         3, NULL),
  (14, '560042', 'Cálculo II',                                               5, NULL),
  (15, '560038', 'Sistemas Organizacionales',                                2, NULL),
  (16, '650053', 'Física para Sistemas',                                     4, NULL),
  (17, '650055', 'Estructuras Discretas de Computación',                     4, NULL),
  (18, '650054', 'Introducción a la Programación',                           4, NULL),
  (19, '560046', 'Estadística y Probabilidad',                               4, NULL),
  (20, '560047', 'Cálculo III',                                              3, NULL),
  (21, '650008', 'Modelación e Integración de Sistemas',                     3, NULL),
  (22, '560043', 'Costeo de Operaciones',                                    3, NULL),
  (23, '650086', 'Programación Orientada a Objetos',                         4, NULL),
  (24, '650056', 'Arquitectura de Computadoras',                             4, NULL),
  (25, '650058', 'Estadística Aplicada',                                     4, NULL),
  (26, '560048', 'Investigación de Operaciones I',                           4, NULL),
  (27, '650057', 'Sistemas Operativos',                                      4, NULL),
  (28, '650009', 'Desarrollo de Competencias Gerenciales',                   3, NULL),
  (29, '650059', 'Estructuras de Datos I',                                   4, NULL),
  (30, '650060', 'Modelamiento de Base de Datos',                            4, NULL),
  (31, '650010', 'Ingeniería de Procesos de Negocio',                        3, NULL),
  (32, '650015', 'Redes de Computadoras',                                    4, NULL),
  (33, '650018', 'Simulación',                                               3, NULL),
  (34, '650061', 'Estructuras de Datos II',                                  4, NULL),
  (35, '650022', 'Programación Web',                                         3, NULL),
  (36, '650016', 'Gestión Financiera',                                       3, NULL),
  (37, '650062', 'Sistemas de Inteligencia Empresarial',                     4, NULL),
  (38, '650019', 'Gestión de Operaciones',                                   3, NULL),
  (39, '650063', 'Ingeniería de Software I',                                 4, NULL),
  (40, '650064', 'Aprendizaje de Máquina',                                   4, NULL),
  (41, '650065', 'Ciberseguridad',                                           4, NULL),
  (42, '650066', 'Propuesta de Investigación',                               3, NULL),
  (43, '650028', 'Sistemas ERP',                                             3, NULL),
  (44, '650042', 'Auditoría y Control de Sistemas',                          3, NULL),
  (45, '1327',   'Ingeniería de Software II',                                4, NULL),
  (46, '650033', 'Planeamiento Estratégico',                                 3, NULL),
  (47, '5674',   'Gestión de Proyectos',                                     3, NULL),
  (48, '650035', 'Seminario de Investigación I',                             4, NULL),
  (49, '650067', 'Seguridad de Sistemas',                                    4, NULL),
  (50, '650040', 'Seminario de Investigación II',                            4, NULL),
  (51, '650068', 'Gestión de Servicios Digitales',                           4, NULL),
  (52, '650069', 'Proyecto Integrador de Sistemas',                          4, NULL),
  (53, '650070', 'Paradigmas de Programación',                               3, NULL),
  (54, '650012', 'Internet de las Cosas',                                    3, NULL),
  (55, '650071', 'Gestión de Base de Datos',                                 3, NULL),
  (56, '550001', 'Storytelling',                                             3, 'Comunicaciones'),
  (57, '650072', 'Análisis y Diseño de Algoritmos',                          3, NULL),
  (58, '650073', 'Redes Avanzadas',                                          3, NULL),
  (59, '650074', 'Ingeniería del Conocimiento',                              3, NULL),
  (60, '550043', 'Diseño de Videojuegos',                                    5, 'Comunicaciones'),
  (61, '550029', 'Narrativa Gráfica',                                        3, 'Comunicaciones'),
  (62, '650075', 'Deep Learning',                                            3, NULL),
  (63, '650030', 'Programación Móvil',                                       3, NULL),
  (64, '650076', 'Tópicos Avanzados en Ciberseguridad',                      3, NULL),
  (65, '650077', 'Sistemas Distribuidos',                                    3, NULL),
  (66, '650044', 'Analítica con Big Data',                                   3, NULL),
  (67, '650078', 'Analítica de Negocios',                                    3, NULL),
  (68, '650079', 'Proyecto de Desarrollo de Software',                       3, NULL),
  (69, '650025', 'Computación en la Nube',                                   3, NULL),
  (70, '650080', 'Innovación Digital',                                       3, NULL),
  (71, '650081', 'Proyecto de Videojuegos',                                  3, NULL),
  (72, '650082', 'Arquitectura Empresarial',                                 3, NULL),
  (73, '650011', 'Interacción Humano Computadora',                           3, NULL),
  (74, '650083', 'Arquitectura de Tecnologías de la Información',            3, NULL),
  (75, '650084', 'DevOps',                                                   3, NULL),
  (76, '650085', 'Arquitectura de Software',                                 3, NULL),
  (77, '520074', 'Seguridad, Salud Ocupacional y Bienestar Organizacional',  3, NULL);

INSERT INTO academic_period (id, code, start_date, end_date, is_active)
VALUES (1, '2026-I', '2026-04-01', '2026-08-30', TRUE);

INSERT INTO assessment_type (id, name, abbreviation, description)
VALUES
  (1, 'Examen',       'EX', 'Evaluación escrita teórica'),
  (2, 'Práctica',     'PR', 'Evaluación práctica calificada'),
  (3, 'Teórica',      'TE', 'Evaluación teórica'),
  (4, 'Tarea',        'TA', 'Tarea académica'),
  (5, 'Proyecto',     'PY', 'Evaluación basada en proyecto'),
  (6, 'Laboratorio',  'LB', 'Evaluación de laboratorio'),
  (7, 'Participación','PA', 'Evaluación de participación en clase'),
  (8, 'Otra',         'OT', 'Otro tipo de evaluación');

INSERT INTO teacher (id, teacher_code, full_name, institutional_email)
VALUES
  (1, 'D01', 'Hernan Alejandro Quintana Cruz',   'hquintana@ul.edu.pe'),
  (2, 'D02', 'Jose Jesús Valdivia Caballero',     'jvaldivia@ul.edu.pe');

-- 2. CURRICULUM Y ESPECIALIDADES
INSERT INTO curriculum (id, career_id, name)
VALUES (1, 1, 'Malla 2026 - Ingeniería de Sistemas');

INSERT INTO specialty (id, career_id, name, description, is_active)
VALUES
  (1, 1, 'Ingeniería de Software',              'Enfocada en el diseño, desarrollo, pruebas y mantenimiento de sistemas de software de alta calidad y rendimiento.', TRUE),
  (2, 1, 'Sistemas de Información',             'Comprensión del uso eficaz y eficiente de la información para lograr una ventaja competitiva en las empresas.', TRUE),
  (3, 1, 'Tecnologías de la Información',       'Conocimientos y competencias para desarrollar soluciones de negocio mediante plataformas de TI.', TRUE),
  (4, 1, 'Desarrollo de Videojuegos',           'Programación de juegos por computadora, diseño artístico y gráficos 2D/3D.', TRUE),
  (5, 2, 'Logística y Operaciones',             'Gestión y optimización de cadenas de suministro, inventarios y procesos.', TRUE),
  (6, 2, 'Gestión de la Calidad',               'Aseguramiento de estándares de calidad bajo marcos normativos internacionales.', TRUE),
  (7, 3, 'Finanzas',                            'Análisis financiero, mercados de capitales, valoración de empresas.', TRUE),
  (8, 3, 'Marketing y Estrategia',              'Planificación y desarrollo de estrategias de mercadotecnia e innovación comercial.', TRUE);

-- 3. OFERTA ACADÉMICA (solo cursos con sílabo en evaluaciones.json)
INSERT INTO course_offering (id, academic_period_id, course_id)
VALUES
  (1,  1, 45),  (2,  1, 40),  (3,  1, 38),  (4,  1, 63),  (5,  1, 37),
  (6,  1, 35),  (7,  1, 47),  (8,  1, 69),  (9,  1, 50),  (10, 1, 48),
  (11, 1, 51),  (12, 1, 43),  (13, 1, 54),  (14, 1, 49),  (15, 1, 55),
  (16, 1, 76),  (17, 1, 72),  (18, 1, 59),  (19, 1, 73),  (20, 1, 75),
  (21, 1, 46),  (22, 1, 66),  (23, 1, 74),  (24, 1, 57),  (25, 1, 42),
  (26, 1, 65);

INSERT INTO syllabus (id, course_offering_id, title, drive_file_id, drive_file_url)
VALUES
  (1,  1,  'Sílabo Ingeniería de Software II 2026-I',                'drive_45',  'https://drive.google.com/45'),
  (2,  2,  'Sílabo Aprendizaje de Máquina 2026-I',                   'drive_40',  'https://drive.google.com/40'),
  (3,  3,  'Sílabo Gestión de Operaciones 2026-I',                   'drive_38',  'https://drive.google.com/38'),
  (4,  4,  'Sílabo Programación Móvil 2026-I',                       'drive_63',  'https://drive.google.com/63'),
  (5,  5,  'Sílabo Sistemas de Inteligencia Empresarial 2026-I',     'drive_37',  'https://drive.google.com/37'),
  (6,  6,  'Sílabo Programación Web 2026-I',                         'drive_35',  'https://drive.google.com/35'),
  (7,  7,  'Sílabo Gestión de Proyectos 2026-I',                     'drive_47',  'https://drive.google.com/47'),
  (8,  8,  'Sílabo Computación en la Nube 2026-I',                   'drive_69',  'https://drive.google.com/69'),
  (9,  9,  'Sílabo Seminario de Investigación II 2026-I',            'drive_50',  'https://drive.google.com/50'),
  (10, 10, 'Sílabo Seminario de Investigación I 2026-I',             'drive_48',  'https://drive.google.com/48'),
  (11, 11, 'Sílabo Gestión de Servicios Digitales 2026-I',           'drive_51',  'https://drive.google.com/51'),
  (12, 12, 'Sílabo Sistemas ERP 2026-I',                             'drive_43',  'https://drive.google.com/43'),
  (13, 13, 'Sílabo Internet de las Cosas 2026-I',                    'drive_54',  'https://drive.google.com/54'),
  (14, 14, 'Sílabo Seguridad de Sistemas 2026-I',                    'drive_49',  'https://drive.google.com/49'),
  (15, 15, 'Sílabo Gestión de Base de Datos 2026-I',                 'drive_55',  'https://drive.google.com/55'),
  (16, 16, 'Sílabo Arquitectura de Software 2026-I',                 'drive_76',  'https://drive.google.com/76'),
  (17, 17, 'Sílabo Arquitectura Empresarial 2026-I',                 'drive_72',  'https://drive.google.com/72'),
  (18, 18, 'Sílabo Ingeniería del Conocimiento 2026-I',              'drive_59',  'https://drive.google.com/59'),
  (19, 19, 'Sílabo Interacción Humano Computadora 2026-I',           'drive_73',  'https://drive.google.com/73'),
  (20, 20, 'Sílabo DevOps 2026-I',                                   'drive_75',  'https://drive.google.com/75'),
  (21, 21, 'Sílabo Planeamiento Estratégico 2026-I',                 'drive_46',  'https://drive.google.com/46'),
  (22, 22, 'Sílabo Analítica con Big Data 2026-I',                   'drive_66',  'https://drive.google.com/66'),
  (23, 23, 'Sílabo Arquitectura de TI 2026-I',                       'drive_74',  'https://drive.google.com/74'),
  (24, 24, 'Sílabo Análisis y Diseño de Algoritmos 2026-I',          'drive_57',  'https://drive.google.com/57'),
  (25, 25, 'Sílabo Propuesta de Investigación 2026-I',               'drive_42',  'https://drive.google.com/42'),
  (26, 26, 'Sílabo Sistemas Distribuidos 2026-I',                    'drive_65',  'https://drive.google.com/65');

INSERT INTO section (id, course_offering_id, teacher_id, code)
VALUES
  (1, 1,  1, 'IS-856'),  (2, 2,  2, 'ML-753'),  (3, 3,  1, 'GDO-754'),
  (4, 3,  2, 'GDO-755'), (5, 4,  2, 'PM-854'),  (6, 5,  2, 'SIE-755'),
  (7, 6,  1, 'PW-855'),  (8, 7,  2, 'GP-802'),  (9, 7,  1, 'GP-804');

-- 4. ESTUDIANTES
INSERT INTO student (id, user_id, career_id, curriculum_id, current_level, specialty_setup_completed)
VALUES
  (1, 1,  1, 1, 7, TRUE),  (2, 2,  1, 1, 6, TRUE),  (3, 3,  1, 1, 5, TRUE),
  (4, 4,  1, 1, 7, TRUE),  (5, 5,  1, 1, 7, TRUE),  (6, 6,  1, 1, 3, TRUE),
  (7, 7,  1, 1, 3, TRUE),  (8, 8,  1, 1, 9, TRUE),  (9, 9,  1, 1, 9, FALSE),
  (10, 10, 1, 1, 9, FALSE);

-- 5. CURSOS DEL PLAN DE ESTUDIOS
INSERT INTO curriculum_course (id, curriculum_id, course_id, cycle, display_order, credit, category)
VALUES
  (1,  1, 1,  1, 1,  4, 'general_studies'), (2,  1, 2,  1, 2,  3, 'general_studies'),
  (3,  1, 3,  1, 3,  2, 'general_studies'), (4,  1, 4,  1, 4,  3, 'general_studies'),
  (5,  1, 5,  1, 5,  3, 'general_studies'), (6,  1, 6,  1, 6,  5, 'general_studies'),
  (7,  1, 7,  2, 1,  3, 'general_studies'), (8,  1, 8,  2, 2,  3, 'general_studies'),
  (9,  1, 9,  2, 3,  3, 'general_studies'), (10, 1, 10, 2, 4,  3, 'general_studies'),
  (11, 1, 11, 2, 5,  3, 'general_studies'), (12, 1, 12, 2, 6,  5, 'general_studies'),
  (13, 1, 13, 3, 1,  3, 'common'),          (14, 1, 14, 3, 2,  5, 'common'),
  (15, 1, 15, 3, 3,  2, 'common'),          (16, 1, 16, 3, 4,  4, 'faculty'),
  (17, 1, 17, 3, 5,  4, 'faculty'),         (18, 1, 18, 3, 6,  4, 'faculty'),
  (19, 1, 19, 4, 1,  4, 'common'),          (20, 1, 20, 4, 2,  3, 'common'),
  (21, 1, 21, 4, 3,  3, 'faculty'),         (22, 1, 22, 4, 4,  3, 'common'),
  (23, 1, 23, 4, 5,  4, 'faculty'),         (24, 1, 24, 4, 6,  4, 'faculty'),
  (25, 1, 25, 5, 1,  4, 'faculty'),         (26, 1, 26, 5, 2,  4, 'common'),
  (27, 1, 27, 5, 3,  4, 'faculty'),         (28, 1, 28, 5, 4,  3, 'faculty'),
  (29, 1, 29, 5, 5,  4, 'faculty'),         (30, 1, 30, 5, 6,  4, 'faculty'),
  (31, 1, 31, 6, 1,  3, 'faculty'),         (32, 1, 32, 6, 2,  4, 'faculty'),
  (33, 1, 33, 6, 3,  3, 'faculty'),         (34, 1, 34, 6, 4,  4, 'faculty'),
  (35, 1, 35, 6, 5,  3, 'faculty'),         (36, 1, 36, 6, 6,  3, 'faculty'),
  (37, 1, 37, 7, 1,  4, 'faculty'),         (38, 1, 38, 7, 2,  3, 'faculty'),
  (39, 1, 39, 7, 3,  4, 'faculty'),         (40, 1, 40, 7, 4,  4, 'faculty'),
  (41, 1, 41, 7, 5,  4, 'faculty'),         (42, 1, 42, 8, 1,  3, 'faculty'),
  (43, 1, 43, 8, 2,  3, 'faculty'),         (44, 1, 44, 8, 3,  3, 'faculty'),
  (45, 1, 45, 8, 4,  4, 'faculty'),         (46, 1, 46, 9, 1,  3, 'faculty'),
  (47, 1, 47, 9, 2,  3, 'common'),          (48, 1, 48, 9, 3,  4, 'faculty'),
  (49, 1, 49, 9, 4,  4, 'faculty'),         (50, 1, 50, 10, 1, 4, 'faculty'),
  (51, 1, 51, 10, 2, 4, 'faculty'),         (52, 1, 52, 10, 3, 4, 'faculty'),
  (53, 1, 53, 6,  7, 3, 'elective'),        (54, 1, 54, 6,  8, 3, 'elective'),
  (55, 1, 55, 6,  9, 3, 'elective'),        (56, 1, 56, 6,  10, 3, 'elective'),
  (57, 1, 57, 7,  6, 3, 'elective'),        (58, 1, 58, 7,  7, 3, 'elective'),
  (59, 1, 59, 7,  8, 3, 'elective'),        (60, 1, 60, 7,  10, 5, 'elective'),
  (61, 1, 61, 7,  11, 3, 'elective'),       (62, 1, 62, 8,  5, 3, 'elective'),
  (63, 1, 63, 8,  6, 3, 'elective'),        (64, 1, 64, 8,  7, 3, 'elective'),
  (65, 1, 65, 9,  5, 3, 'elective'),        (66, 1, 66, 9,  6, 3, 'elective'),
  (67, 1, 67, 9,  7, 3, 'elective'),        (68, 1, 68, 9,  8, 3, 'elective'),
  (69, 1, 69, 10, 4, 3, 'elective'),        (70, 1, 70, 10, 5, 3, 'elective'),
  (71, 1, 71, 10, 6, 3, 'elective'),        (72, 1, 72, 10, 7, 3, 'elective'),
  (73, 1, 73, 10, 8, 3, 'elective'),        (74, 1, 74, 10, 9, 3, 'elective'),
  (75, 1, 75, 10, 10, 3, 'elective'),       (76, 1, 76, 10, 11, 3, 'elective'),
  (77, 1, 77, 7,  9, 3, 'elective');

-- 6. ESPECIALIDADES POR ESTUDIANTE
INSERT INTO student_specialty (student_id, specialty_id, selection_type, is_active)
VALUES
  (1, 1, 'interest', TRUE), (2, 1, 'interest', TRUE), (3, 1, 'interest', TRUE),
  (4, 1, 'interest', TRUE), (5, 1, 'interest', TRUE), (6, 1, 'interest', TRUE),
  (8, 1, 'interest', TRUE);

-- 7. MATRÍCULAS
INSERT INTO enrollment (id, student_id, section_id, status, attended_hours, absent_hours, total_hours)
VALUES
  (1, 1, 1, 'active', 48, 4,  64),  (2, 1, 5, 'active', 50, 2,  64),
  (3, 2, 1, 'active', 52, 0,  64),  (4, 2, 5, 'active', 47, 5,  64),
  (5, 2, 2, 'active', 44, 8,  64),  (6, 3, 1, 'active', 46, 6,  64),
  (7, 3, 5, 'active', 49, 3,  64),  (8, 3, 2, 'active', 45, 7,  64),
  (9, 3, 3, 'active', 42, 10, 64),  (10, 4, 1, 'active', 51, 1, 64),
  (11, 4, 5, 'active', 48, 4, 64),  (12, 5, 1, 'active', 50, 2, 64),
  (13, 5, 5, 'active', 47, 5, 64),  (14, 6, 1, 'active', 44, 8, 64),
  (15, 6, 5, 'active', 46, 6, 64),  (16, 6, 3, 'active', 43, 9, 64),
  (17, 6, 2, 'active', 41, 11, 64), (18, 6, 6, 'active', 45, 7, 64),
  (19, 7, 5, 'active', 48, 4, 64),  (20, 8, 1, 'active', 49, 3, 64);

-- 8. EVALUACIONES POR SÍLABO
INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (1, 1, 1, 'EE1',   'Examen Escrito 1',                    4,  20.0),
  (2, 1, 2, 'Proy1', 'Proyecto',                            8,  25.0),
  (3, 1, 1, 'EE2',   'Examen Escrito 2',                    12, 25.0),
  (4, 1, 2, 'Proy2', 'Proyecto',                            16, 30.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (5,  2, 3, 'EE1',  'Examen Escrito 1',                    5,  10.0),
  (6,  2, 3, 'EE2',  'Examen Escrito 2',                    9,  25.0),
  (7,  2, 5, 'PROY', 'Proyecto (20% programa, 80% reporte)',13, 30.0),
  (8,  2, 3, 'EE3',  'Examen Escrito 3',                    16, 35.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (9,  3, 1, 'EE1',  'Examen Escrito 1',                    4,  25.0),
  (10, 3, 1, 'EE2',  'Examen Escrito 2',                    12, 25.0),
  (11, 3, 1, 'EP',   'Examen Parcial',                      8,  20.0),
  (12, 3, 1, 'EF',   'Examen Final',                        16, 30.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (13, 4, 2, 'TP1',  'Trabajo de Producción 1',             4,  25.0),
  (14, 4, 2, 'TP2',  'Trabajo de Producción 2',             8,  25.0),
  (15, 4, 2, 'TP3',  'Trabajo de Producción 3',             12, 25.0),
  (16, 4, 5, 'PF',   'Proyecto Final',                      15, 25.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (17, 5, 3, 'EE',   'Examen escrito',                      5,  20.0),
  (18, 5, 6, 'LB1',  'Laboratorio 1',                       9,  25.0),
  (19, 5, 6, 'LB2',  'Laboratorio 2',                       13, 25.0),
  (20, 5, 2, 'TI',   'Exposición de Trabajos finales',      16, 30.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (21, 6, 4, 'EI1',  'Ejercicio Individual 1',              2,  10.0),
  (22, 6, 2, 'EC',   'Ejercicio Colaborativo',              6,  20.0),
  (23, 6, 4, 'EI2',  'Ejercicio Individual 2',              10, 20.0),
  (24, 6, 1, 'EE',   'Examen Escrito',                      14, 20.0),
  (25, 6, 5, 'PROY', 'Proyecto',                            16, 30.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (26, 7, 5, 'PROY1','Proyecto 1',                          6,  20.0),
  (27, 7, 5, 'PROY2','Proyecto 2',                          12, 20.0),
  (28, 7, 7, 'PART', 'Participación',                       9,  30.0),
  (29, 7, 8, 'EXP',  'Exposición',                          16, 30.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (30, 8, 1, 'EE',   'Examen Escrito',                      6,  10.0),
  (31, 8, 6, 'LB1',  'Laboratorio 1',                       4,  15.0),
  (32, 8, 6, 'LB2',  'Laboratorio 2',                       8,  20.0),
  (33, 8, 6, 'LB3',  'Laboratorio 3',                       12, 20.0),
  (34, 8, 5, 'PR',   'Proyecto',                            16, 35.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (35, 9,  5, 'TI1', 'Trabajo de Investigación 1',          6,  20.0),
  (36, 9,  5, 'TI2', 'Trabajo de Investigación 2',          11, 30.0),
  (37, 9,  5, 'TI3', 'Trabajo de Investigación 3',          16, 50.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (38, 10, 5, 'TI1', 'Trabajo de Investigación 1',          6,  20.0),
  (39, 10, 5, 'TI2', 'Trabajo de Investigación 2',          11, 30.0),
  (40, 10, 5, 'TI3', 'Trabajo de Investigación 3',          16, 50.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (41, 11, 1, 'EE1',  'Examen Escrito 1',                   5,  20.0),
  (42, 11, 5, 'PROY1','Proyecto 1',                         9,  30.0),
  (43, 11, 1, 'EE2',  'Examen Escrito 2',                   12, 20.0),
  (44, 11, 5, 'PROY2','Proyecto 2',                         16, 30.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (45, 12, 1, 'EE1',  'Examen Escrito 1',                   5,  20.0),
  (46, 12, 1, 'EE2',  'Examen Escrito 2',                   9,  25.0),
  (47, 12, 1, 'EE3',  'Examen Escrito 3',                   13, 20.0),
  (48, 12, 8, 'EC',   'Estudio de Caso',                    16, 35.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (49, 13, 6, 'PL1',  'Práctica en Laboratorio 1',          5,  20.0),
  (50, 13, 6, 'PL2',  'Práctica en Laboratorio 2',          9,  20.0),
  (51, 13, 6, 'PL3',  'Práctica en Laboratorio 3',          13, 25.0),
  (52, 13, 5, 'PROY', 'Proyecto',                           16, 35.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (53, 14, 1, 'EE1',  'Examen Escrito 1',                   5,  20.0),
  (54, 14, 1, 'EE2',  'Examen Escrito 2',                   11, 25.0),
  (55, 14, 6, 'PL',   'Práctica en Laboratorio',            8,  25.0),
  (56, 14, 5, 'PROY', 'Proyecto',                           16, 30.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (57, 15, 1, 'EE',   'Examen Escrito',                     6,  20.0),
  (58, 15, 6, 'LB1',  'Laboratorio 1',                      4,  15.0),
  (59, 15, 6, 'LB2',  'Laboratorio 2',                      8,  15.0),
  (60, 15, 6, 'LB3',  'Laboratorio 3',                      12, 20.0),
  (61, 15, 5, 'PR',   'Proyecto',                           16, 30.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (62, 16, 1, 'EE1',  'Examen Escrito 1',                   5,  25.0),
  (63, 16, 5, 'PROY1','Proyecto 1',                         9,  20.0),
  (64, 16, 1, 'EE2',  'Examen Escrito 2',                   12, 25.0),
  (65, 16, 5, 'PF',   'Proyecto Final',                     16, 30.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (66, 17, 1, 'EE1',  'Examen Escrito 1',                   4,  15.0),
  (67, 17, 1, 'EE2',  'Examen Escrito 2',                   8,  15.0),
  (68, 17, 2, 'TP1',  'Trabajo de Producción 1',            6,  20.0),
  (69, 17, 1, 'EE3',  'Examen Escrito 3',                   12, 15.0),
  (70, 17, 2, 'TP2',  'Trabajo de Producción 2',            16, 35.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (71, 18, 1, 'EE',   'Examen Escrito',                     7,  30.0),
  (72, 18, 8, 'EC',   'Estudio de Caso',                    11, 35.0),
  (73, 18, 5, 'PROY', 'Proyecto',                           14, 15.0),
  (74, 18, 8, 'EXP',  'Exposición',                         16, 20.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (75, 19, 5, 'TI1',  'Trabajo de Investigación 1',         6,  30.0),
  (76, 19, 1, 'EE1',  'Examen Escrito 1',                   9,  20.0),
  (77, 19, 5, 'TI2',  'Trabajo de Investigación 2',         13, 30.0),
  (78, 19, 1, 'EE2',  'Examen Escrito 2',                   16, 20.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (79, 20, 1, 'EE1',  'Examen Escrito 1',                   5,  20.0),
  (80, 20, 8, 'EXP',  'Exposición',                         9,  30.0),
  (81, 20, 1, 'EE2',  'Examen Escrito 2',                   13, 20.0),
  (82, 20, 5, 'PR',   'Proyecto',                           16, 30.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (83, 21, 1, 'EE1',  'Examen Escrito 1',                   4,  15.0),
  (84, 21, 1, 'EE2',  'Examen Escrito 2',                   8,  15.0),
  (85, 21, 2, 'TP1',  'Trabajo de Producción 1',            6,  20.0),
  (86, 21, 1, 'EE3',  'Examen Escrito 3',                   12, 15.0),
  (87, 21, 2, 'TP2',  'Trabajo de Producción 2',            16, 35.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (88, 22, 1, 'EE1',  'Examen Escrito 1',                   5,  25.0),
  (89, 22, 1, 'EE2',  'Examen Escrito 2',                   10, 25.0),
  (90, 22, 1, 'EE3',  'Examen Escrito 3',                   14, 25.0),
  (91, 22, 2, 'TP',   'Trabajo de Producción',              16, 25.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (92, 23, 8, 'EXP',  'Exposición',                         7,  15.0),
  (93, 23, 5, 'PROY1','Proyecto 1',                         9,  30.0),
  (94, 23, 5, 'PROY2','Proyecto 2',                         14, 35.0),
  (95, 23, 1, 'EE',   'Examen Escrito',                     16, 20.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (96, 24, 1, 'EE1',  'Examen Escrito 1',                   5,  20.0),
  (97, 24, 1, 'EE2',  'Examen Escrito 2',                   10, 20.0),
  (98, 24, 5, 'TI',   'Trabajo de Investigación',           8,  30.0),
  (99, 24, 1, 'EE3',  'Examen Escrito 3',                   14, 30.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (100, 25, 5, 'TI1', 'Trabajo de Investigación 1',         6,  20.0),
  (101, 25, 8, 'EXP', 'Exposición',                         10, 30.0),
  (102, 25, 5, 'TI2', 'Trabajo de Investigación 2',         15, 50.0);

INSERT INTO assessment (id, syllabus_id, assessment_type_id, code, name, week_number, weight) VALUES
  (103, 26, 1, 'EE1', 'Examen Escrito 1',                   6,  35.0),
  (104, 26, 6, 'PL',  'Práctica en Laboratorio',            10, 15.0),
  (105, 26, 1, 'EE2', 'Examen Escrito 2',                   14, 35.0),
  (106, 26, 5, 'PROY','Proyecto',                           16, 15.0);

-- 9. NOTAS DE ESTUDIANTES
INSERT INTO student_score (id, enrollment_id, assessment_id, value) VALUES
  (1, 1, 1, 16.5),  -- 20235218 IS-856 EE1
  (2, 1, 2, 18.0),  -- 20235218 IS-856 Proy1
  (3, 3, 1, 14.0),  -- 20232548 IS-856 EE1
  (4, 3, 2, 15.5);  -- 20232548 IS-856 Proy1

INSERT INTO curriculum_course_specialty (curriculum_course_id, specialty_id) VALUES
  (53, 1), (54, 3), (55, 2), (56, 4),
  (57, 1), (58, 3), (59, 2), (60, 4), (61, 4),
  (62, 1), (63, 1), (63, 4), (64, 3),
  (65, 3), (66, 2), (67, 2), (68, 1), (68, 4),
  (69, 3), (70, 2), (71, 4), (72, 2),
  (73, 1), (73, 4), (74, 3), (74, 2),
  (75, 3), (76, 1);

INSERT INTO course_prerequisite (id, curriculum_id, curriculum_course_id, prerequisite_type, prerequisite_curriculum_course_id, required_cycle)
VALUES
  (1,  1, 7,  'course',         1,  NULL),  (2,  1, 11, 'course',         6,  NULL),
  (3,  1, 12, 'course',         6,  NULL),  (4,  1, 14, 'course',         12, NULL),
  (5,  1, 15, 'course',         9,  NULL),  (6,  1, 19, 'course',         12, NULL),
  (7,  1, 20, 'course',         14, NULL),  (8,  1, 21, 'course',         13, NULL),
  (9,  1, 22, 'course',         15, NULL),  (10, 1, 23, 'course',         17, NULL),
  (11, 1, 23, 'course',         18, NULL),  (12, 1, 24, 'course',         16, NULL),
  (13, 1, 25, 'course',         19, NULL),  (14, 1, 26, 'course',         20, NULL),
  (15, 1, 27, 'course',         24, NULL),  (16, 1, 28, 'course',         15, NULL),
  (17, 1, 29, 'course',         23, NULL),  (18, 1, 30, 'course',         23, NULL),
  (19, 1, 31, 'course',         26, NULL),  (20, 1, 32, 'course',         27, NULL),
  (21, 1, 33, 'course',         21, NULL),  (22, 1, 34, 'course',         29, NULL),
  (23, 1, 35, 'course',         29, NULL),  (24, 1, 36, 'course',         22, NULL),
  (25, 1, 37, 'course',         30, NULL),  (26, 1, 38, 'course',         31, NULL),
  (27, 1, 39, 'course',         30, NULL),  (28, 1, 40, 'course',         25, NULL),
  (29, 1, 41, 'course',         32, NULL),  (30, 1, 42, 'course',         33, NULL),
  (31, 1, 43, 'course',         38, NULL),  (32, 1, 44, 'course',         36, NULL),
  (33, 1, 45, 'course',         39, NULL),  (34, 1, 47, 'course',         44, NULL),
  (35, 1, 48, 'course',         42, NULL),  (36, 1, 49, 'course',         41, NULL),
  (37, 1, 50, 'course',         48, NULL),  (38, 1, 52, 'course',         47, NULL),
  (39, 1, 53, 'completed_cycle', NULL, 5),  (40, 1, 54, 'completed_cycle', NULL, 5),
  (41, 1, 55, 'completed_cycle', NULL, 5),  (42, 1, 57, 'completed_cycle', NULL, 5),
  (43, 1, 57, 'course',         34, NULL),  (44, 1, 58, 'completed_cycle', NULL, 5),
  (45, 1, 58, 'course',         32, NULL),  (46, 1, 59, 'completed_cycle', NULL, 5),
  (47, 1, 60, 'course',         56, NULL),  (48, 1, 61, 'course',         56, NULL),
  (49, 1, 62, 'completed_cycle', NULL, 5),  (50, 1, 62, 'course',         40, NULL),
  (51, 1, 63, 'completed_cycle', NULL, 5),  (52, 1, 63, 'course',         35, NULL),
  (53, 1, 64, 'completed_cycle', NULL, 5),  (54, 1, 64, 'course',         41, NULL),
  (55, 1, 65, 'completed_cycle', NULL, 5),  (56, 1, 66, 'completed_cycle', NULL, 5),
  (57, 1, 66, 'course',         37, NULL),  (58, 1, 67, 'completed_cycle', NULL, 5),
  (59, 1, 68, 'completed_cycle', NULL, 5),  (60, 1, 68, 'course',         45, NULL),
  (61, 1, 69, 'completed_cycle', NULL, 5),  (62, 1, 70, 'completed_cycle', NULL, 5),
  (63, 1, 71, 'completed_cycle', NULL, 5),  (64, 1, 72, 'completed_cycle', NULL, 5),
  (65, 1, 72, 'course',         46, NULL),  (66, 1, 73, 'completed_cycle', NULL, 5),
  (67, 1, 74, 'completed_cycle', NULL, 5),  (68, 1, 75, 'completed_cycle', NULL, 5),
  (69, 1, 76, 'completed_cycle', NULL, 5),  (70, 1, 77, 'completed_cycle', NULL, 6);

-- migrate:down

DELETE FROM course_prerequisite;
DELETE FROM curriculum_course_specialty;
DELETE FROM student_score;
DELETE FROM assessment;
DELETE FROM enrollment;
DELETE FROM student_specialty;
DELETE FROM curriculum_course;
DELETE FROM student;
DELETE FROM section;
DELETE FROM syllabus;
DELETE FROM course_offering;
DELETE FROM teacher;
DELETE FROM assessment_type;
DELETE FROM academic_period;
DELETE FROM course;
DELETE FROM curriculum;
DELETE FROM specialty;
DELETE FROM career;
DELETE FROM app_user;

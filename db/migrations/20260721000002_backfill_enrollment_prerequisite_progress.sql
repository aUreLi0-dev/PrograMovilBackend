-- Marca como aprobados los prerequisitos directos de los cursos con matricula activa.
-- Esto mantiene consistente la malla oficial: si el alumno esta cursando una seccion,
-- sus prerequisitos de curso ya deben figurar como completados.

-- migrate:up
INSERT OR IGNORE INTO student_course_progress (student_id, curriculum_id, curriculum_course_id, status)
SELECT DISTINCT
    st.id,
    st.curriculum_id,
    cp.prerequisite_curriculum_course_id,
    'approved'
FROM enrollment e
JOIN student st ON st.id = e.student_id
JOIN section s ON s.id = e.section_id
JOIN course_offering co ON co.id = s.course_offering_id
JOIN curriculum_course cc
  ON cc.curriculum_id = st.curriculum_id
 AND cc.course_id = co.course_id
JOIN course_prerequisite cp
  ON cp.curriculum_course_id = cc.id
 AND cp.prerequisite_type = 'course'
WHERE e.status = 'active'
  AND cp.prerequisite_curriculum_course_id IS NOT NULL;

UPDATE student_course_progress
SET status = 'approved'
WHERE EXISTS (
    SELECT 1
    FROM enrollment e
    JOIN student st ON st.id = e.student_id
    JOIN section s ON s.id = e.section_id
    JOIN course_offering co ON co.id = s.course_offering_id
    JOIN curriculum_course cc
      ON cc.curriculum_id = st.curriculum_id
     AND cc.course_id = co.course_id
    JOIN course_prerequisite cp
      ON cp.curriculum_course_id = cc.id
     AND cp.prerequisite_type = 'course'
    WHERE e.status = 'active'
      AND cp.prerequisite_curriculum_course_id IS NOT NULL
      AND st.id = student_course_progress.student_id
      AND st.curriculum_id = student_course_progress.curriculum_id
      AND cp.prerequisite_curriculum_course_id = student_course_progress.curriculum_course_id
);

-- migrate:down
-- No se revierte: este backfill normaliza historial academico oficial.

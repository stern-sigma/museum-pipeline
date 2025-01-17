DROP VIEW IF EXISTS avg_exh_rating;
DROP VIEW IF EXISTS num_requests;
DROP VIEW IF EXISTS request_over_time;
DROP TABLE IF EXISTS request_interaction;
DROP TABLE IF EXISTS rating_interaction;
DROP TABLE IF EXISTS request;
DROP TABLE IF EXISTS rating;
DROP TABLE IF EXISTS exhibition;
DROP TABLE IF EXISTS department;
DROP TABLE IF EXISTS floor;
DROP TABLE IF EXISTS museum;
-- DROP DATABASE museum;
-- CREATE DATABASE museum;
-- \c museum;


CREATE TABLE department(
  department_id SMALLINT GENERATED ALWAYS AS IDENTITY,
  department_name VARCHAR(100) NOT NULL,
  PRIMARY KEY(department_id)
);

CREATE TABLE floor( floor_id SMALLINT GENERATED ALWAYS AS IDENTITY,
  floor_name VARCHAR(100) NOT NULL,
  PRIMARY KEY(floor_id)
);

CREATE TABLE request(
  request_id  SMALLINT GENERATED ALWAYS AS IDENTITY,
  request_value SMALLINT,
  request_description VARCHAR(100) NOT NULL,
  PRIMARY KEY(request_id)
);

CREATE TABLE rating(
  rating_id SMALLINT GENERATED ALWAYS AS IDENTITY,
  rating_value SMALLINT NOT NULL,
  rating_description VARCHAR(100) NOT NULL,
  PRIMARY KEY(rating_id)
);

CREATE TABLE museum(
  museum_id SMALLINT GENERATED ALWAYS AS IDENTITY,
  museum_name VARCHAR(30) NOT NULL,
  PRIMARY KEY(museum_id)
)
;

CREATE TABLE exhibition(
  exhibition_id SMALLINT GENERATED ALWAYS AS IDENTITY,
  exhibition_name VARCHAR(100) NOT NULL,
  exhibition_description TEXT NOT NULL,
  department_id SMALLINT NOT NULL,
  floor_id SMALLINT NOT NULL,
  exhibition_start_date DATE NOT NULL,
  public_id TEXT NOT NULL,
  museum_id SMALLINT NOT NULL,
  PRIMARY KEY (exhibition_id),
  FOREIGN KEY (department_id) REFERENCES department(department_id),
  FOREIGN KEY (floor_id) REFERENCES floor(floor_id),
  FOREIGN KEY (museum_id) REFERENCES museum(museum_id)
);

CREATE TABLE request_interaction(
  request_interaction_id BIGINT GENERATED ALWAYS AS IDENTITY,
  request_id INT NOT NULL,
  exhibition_id SMALLINT NOT NULL,
  event_at TIMESTAMPTZ NOT NULL NOT NULL,
  PRIMARY KEY(request_interaction_id),
  FOREIGN KEY (exhibition_id) REFERENCES exhibition(exhibition_id),
  FOREIGN KEY(request_id) REFERENCES request(request_id)
);

CREATE TABLE rating_interaction(
  rating_interaction_id BIGINT GENERATED ALWAYS AS IDENTITY,
  exhibition_id SMALLINT NOT NULL,
  rating_id SMALLINT NOT NULL,
  event_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY(rating_interaction_id),
  FOREIGN KEY(exhibition_id) REFERENCES exhibition(exhibition_id)
);

CREATE VIEW avg_exh_rating AS (
  SELECT 
    AVG(rating_value::REAL),
    exhibition_name,
    public_id
  FROM  
    rating_interaction
  JOIN
    exhibition
  USING
    (exhibition_id)
  JOIN 
    rating 
  USING
    (rating_id)
  GROUP BY 
    public_id, exhibition_name
)
;

CREATE VIEW num_requests AS (
  SELECT 
    exhibition_name,
    public_id,
    COUNT(*) as number
  FROM  
    request_interaction
  JOIN 
    exhibition
  USING 
    (exhibition_id)
  GROUP BY 
    public_id, exhibition_name
)
;

CREATE VIEW request_over_time AS (
  SELECT
    DATE_TRUNC('day', event_at) as day,
    exhibition_name,
    public_id,
    COUNT(*) as number
  FROM  
    request_interaction
  JOIN  
    exhibition
  USING 
    (exhibition_id)
  GROUP BY 
    day, exhibition_name, public_id
  ORDER BY 
    day DESC, public_id ASC
)
;

INSERT INTO department (department_name) VALUES
  ('entomology'),
  ('geology'),
  ('paleontology'),
  ('zoology'),
  ('ecology'),
  ('technology'),
  ('astronomy'),
  ('biology')
;

INSERT INTO floor(floor_name) VALUES
  ('1'),
  ('2'),
  ('3'),
  ('vault'),
  ('1.'),
  ('planetarium')

;

INSERT INTO rating (rating_value, rating_description) VALUES
(0, 'terrible'),
(1, 'bad'),
(2, 'neutral'),
(3, 'good'),
(4, 'amazing')
;

INSERT INTO request (request_value, request_description) VALUES
(0, 'assistance'),
(1, 'emergency')
;

INSERT INTO museum (museum_name) VALUES
  ('lmnh'),
  ('lms')
;

INSERT INTO exhibition (exhibition_name, public_id, floor_id, department_id, exhibition_start_date, exhibition_description, museum_id)
VALUES
('adaptation', 'EXH_01',
    (SELECT floor_id FROM floor WHERE floor_name = 'vault'),
    (SELECT department_id FROM department WHERE department_name = 'entomology'),
    DATE '2019-07-01',
    'how insect evolution has kept pace with an industrialised world',
    (SELECT museum_id FROM museum WHERE museum_name = 'lmnh')
),
    

('measureless to man', 'EXH_00',
    (SELECT floor_id FROM floor WHERE floor_name = '1'),
    (SELECT department_id FROM department WHERE department_name = 'geology'),
    DATE '2021-08-23',
    'an immersive 3d experience: delve deep into a previously-inaccessible cave system.',
    (SELECT museum_id FROM museum WHERE museum_name = 'lmnh')
  ),

('thunder lizards', 'EXH_05',
    (SELECT floor_id FROM floor WHERE floor_name = '1'),
    (SELECT department_id FROM department WHERE department_name = 'paleontology'),
    DATE '2023-02-01',
    'how new research is making scientists rethink what dinosaurs really looked like.',
    (SELECT museum_id FROM museum WHERE museum_name = 'lmnh')
  ),

('the crenshaw collection', 'EXH_02',
    (SELECT floor_id FROM floor WHERE floor_name = '2'),
    (SELECT department_id FROM department WHERE department_name = 'zoology'),
    DATE '2021-03-03',
    'an exhibition of 18th century watercolours, mostly focused on south american wildlife.',
    (SELECT museum_id FROM museum WHERE museum_name = 'lmnh')
  ),

('our polluted world', 'EXH_04',
    (SELECT floor_id FROM floor WHERE floor_name = '3'),
    (SELECT department_id FROM department WHERE department_name = 'ecology'),
    DATE '2021-05-12',
    'a hard-hitting exploration of humanity''s impact on the environment.',
    (SELECT museum_id FROM museum WHERE museum_name = 'lmnh')
  ),

('cetacean sensations', 'EXH_03',
    (SELECT floor_id FROM floor WHERE floor_name = '1'),
    (SELECT department_id FROM department WHERE department_name = 'zoology'),
    DATE '2019-07-01',
    'whales: from ancient myth to critically endangered.',
    (SELECT museum_id FROM museum WHERE museum_name = 'lmnh')
  ),

(
  'ai',
  'EXH_00',
  (SELECT floor_id FROM floor WHERE floor_name = '1.'),
  (SELECT department_id FROM department WHERE department_name = 'technology'),
  DATE '2023-02-15',
  'building a new future with thinking machines.',
  (SELECT museum_id FROM museum WHERE museum_name = 'lms')
  ),

(
  'exploring the solar system',
  'EXH_01',
  (SELECT floor_id FROM floor WHERE floor_name = 'planetarium'),
  (SELECT department_id FROM department WHERE department_name = 'astronomy'),
  DATE '2018-03-01',
  'our place in the universe.',
  (SELECT museum_id FROM museum WHERE museum_name = 'lms')
  ),

(
  'vicious garden',
  'EXH_02',
  (SELECT  floor_id FROM floor WHERE floor_name = 'vault'),
  (SELECT department_id FROM department WHERE department_name = 'biology'),
  DATE '2022-08-21',
  'plants: animal food or deadly killers?',
  (SELECT museum_id FROM museum WHERE museum_name = 'lms')
  )

;


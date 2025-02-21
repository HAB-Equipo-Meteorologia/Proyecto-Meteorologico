CREATE DATABASE datos_AEMET;

CREATE TABLE comunidades_autonomas (
  id INT NOT NULL,
  nombre VARCHAR(100),
  codigo VARCHAR(100)
  PRIMARY KEY (id)
);

CREATE TABLE provincias (
  id INT NOT NULL,
  nombre VARCHAR(100),
  com_auto_id INT,
  PRIMARY KEY (id),
  FOREIGN KEY (com_auto_id) REFERENCES comunidades_autonomas (id)
);

CREATE TABLE estaciones (
  idema VARCHAR(100) NOT NULL,
  nombre VARCHAR(100),
  provincia_id INT,
  latitud FLOAT,
  longitud FLOAT,
  altitud INT ,
  PRIMARY KEY (idema),
  FOREIGN KEY (provincia_id) REFERENCES provincias (id)
);

CREATE TABLE municipios (
  id INT NOT NULL,
  provincia_id INT,
  cod_mun INT,
  nombre VARCHAR(100),
  altitud INT,
  latitud FLOAT,
  longitud FLOAT,
  num_hab INT,
  zona_comarcal INT,
  destacada BOOLEAN,
  url VARCHAR(100),
  PRIMARY KEY (id),
  FOREIGN KEY (provincia_id) REFERENCES provincias (id)
);

CREATE TABLE temperatura_historico (
  uuid UUID NOT NULL DEFAULT gen_random_uuid(),
  fecha DATE,
  idema VARCHAR(100),
  tmed REAL,
  tmin REAL,
  hotatmin TIME,
  tmax REAL,
  horatmax TIME,
  extracted TIMESTAMP,
  PRIMARY KEY (uuid),
  FOREIGN KEY (idema) REFERENCES estaciones(idema) ON DELETE CASCADE
);


CREATE TABLE lluvia_historico (
  uuid UUID NOT NULL DEFAULT gen_random_uuid(),
  fecha DATE NOT NULL,
  idema VARCHAR(100),
  prec REAL,
  extracted TIMESTAMP,
  PRIMARY KEY (uuid),
  FOREIGN KEY (idema) REFERENCES estaciones(idema) ON DELETE CASCADE   
);


CREATE TABLE humedad_historico (
  uuid UUID NOT NULL DEFAULT gen_random_uuid(),
  fecha DATE NOT NULL,
  idema VARCHAR(100),
  hrMax INT,
  horaHrMax VARCHAR(10),
  hrMin INT,
  horaHrMin TIME,
  hrMedia INT,
  extracted TIMESTAMP,
  PRIMARY KEY (uuid),
  FOREIGN KEY (idema) REFERENCES estaciones(idema) ON DELETE CASCADE
);


CREATE TABLE viento_historico (
  uuid UUID NOT NULL DEFAULT gen_random_uuid(),
  fecha DATE NOT NULL,
  idema VARCHAR(100),
  dir VARCHAR(10),
  velmedia REAL,
  racha REAL,
  horaracha TIME,
  PRIMARY KEY (cod_estacion, fecha),
  extracted TIMESTAMP,
  FOREIGN KEY (cod_estacion) REFERENCES estaciones(idema) ON DELETE CASCADE
);

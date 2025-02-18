CREATE DATABASE datos_AEMET;

CREATE TABLE comunidades_autonomas (
  id INT NOT NULL,
  nombre VARCHAR(100),
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

CREATE TABLE temperatura (
  cod_estacion VARCHAR(10) NOT NULL,
  fecha DATE NOT NULL,
  temp_media REAL,
  temp_min REAL,
  hora_temp_min TIME,
  temp_max REAL,
  hora_temp_max TIME,
  PRIMARY KEY (cod_estacion, fecha),
  FOREIGN KEY (cod_estacion) REFERENCES estaciones(idema) ON DELETE CASCADE
);


CREATE TABLE precipitaciones (
  cod_estacion VARCHAR(10) NOT NULL,
  fecha DATE NOT NULL,
  precipitacion REAL,
  PRIMARY KEY (cod_estacion, fecha),
  FOREIGN KEY (cod_estacion) REFERENCES estaciones(idema) ON DELETE CASCADE   
);


CREATE TABLE humedad (
  cod_estacion VARCHAR(10) NOT NULL,
  fecha DATE NOT NULL,
  humedad_max INT,
  hora_hum_max VARCHAR(10),
  humedad_min INT,
  hora_hum_min TIME,
  humedad_media INT,
  PRIMARY KEY (cod_estacion, fecha),
  FOREIGN KEY (cod_estacion) REFERENCES estaciones(idema) ON DELETE CASCADE
);


CREATE TABLE sol (
  cod_estacion VARCHAR(10) NOT NULL,
  fecha DATE NOT NULL,
  horas_sol REAL,
  PRIMARY KEY (cod_estacion, fecha),
  FOREIGN KEY (cod_estacion) REFERENCES estaciones(idema) ON DELETE CASCADE   
);


CREATE TABLE presion (
  cod_estacion VARCHAR(10) NOT NULL,
  fecha DATE NOT NULL,
  presion_max REAL,
  hora_pres_max TIME,
  presion_min REAL,
  hora_pres_min TIME,
  PRIMARY KEY (cod_estacion, fecha),
  FOREIGN KEY (cod_estacion) REFERENCES estaciones(idema) ON DELETE CASCADE
);


CREATE TABLE viento (
  cod_estacion VARCHAR(10) NOT NULL,
  fecha DATE NOT NULL,
  direccion VARCHAR(10),
  velocidad_media REAL,
  racha REAL,
  hora_racha TIME,
  PRIMARY KEY (cod_estacion, fecha),
  FOREIGN KEY (cod_estacion) REFERENCES estaciones(idema) ON DELETE CASCADE
);

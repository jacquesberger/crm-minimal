create table entreprise (
  id integer primary key,
  nom varchar
);

create table rappel (
  id integer primary key,
  done integer,
  activation date,
  note varchar,
  entreprise_id integer,
  foreign key(entreprise_id) references entreprise(id)
);

create table role (
    id        integer primary key autoincrement,
    role_name text not null unique
);

insert into role (role_name) values ('admin');
insert into role (role_name) values ('regulier');

create table etat
(
    id        integer primary key autoincrement,
    etat_name text not null unique
);

insert into etat (etat_name)
values ('actif');
insert into etat (etat_name)
values ('suspendu');

create table utilisateur (
  id              INTEGER PRIMARY KEY,
  username        VARCHAR(25),
  email           VARCHAR(100),
  salt            VARCHAR(32),
  hashed_password VARCHAR(128),
  role_id         INTEGER,
  etat_id         INTEGER,
  FOREIGN KEY (role_id) REFERENCES role (id),
  FOREIGN KEY (etat_id) REFERENCES etat (id)
);

create table interaction (
  id integer primary key,
  description varchar,
  moment date,
  entreprise_id integer,
  cree_par varchar,
  foreign key(entreprise_id) references entreprise(id),
  foreign key (cree_par) references  utilisateur(username)
);


create table session (
  id integer primary key,
  id_session varchar(32),
  username varchar(25)
);

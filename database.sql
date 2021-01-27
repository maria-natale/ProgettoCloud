DROP DATABASE IF EXISTS BotTipBooksDatabase;
create database BotTipBooksDatabase;
use BotTipBooksDatabase;

create table Utenti(
	id varchar (50) not null,
	PRIMARY KEY (id));

create table Categorie(
	nomeCategoria varchar(50) not null,
    primary key (nomeCategoria)
);

create table UtentiCategorie(
	utente varchar(50) not null,
    categoria varchar(50) not null,
    primary key(utente, categoria),
    foreign key (categoria)
		references Categorie (nomeCategoria)
		on update cascade on delete cascade,
	foreign key (utente)
		references Utenti(id)
		on update cascade on delete cascade
);

create table Libri(
	titolo VARCHAR(50) NOT NULL,
    autore VARCHAR (50) not null,
    categoria varchar (50),
    FOREIGN KEY (categoria)
        REFERENCES Categorie (nomeCategoria)
        ON UPDATE CASCADE ON DELETE CASCADE,
    PRIMARY KEY (titolo, autore)
);


create table Wishlist(
	utente varchar (50) not null,
    titoloLibro varchar(50) not null,
    autoreLibro varchar(50) not null,
    primary key(utente, titoloLibro, autoreLibro),
    FOREIGN KEY (utente)
        REFERENCES Utenti (id)
        ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY (titoloLibro, autoreLibro)
        REFERENCES Libri (titolo, autore)
        on update cascade on delete cascade
);
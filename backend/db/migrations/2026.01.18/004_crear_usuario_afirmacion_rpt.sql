CREATE TABLE ALEJO.USUARIO_AFIRMACION_RPTA (
    id int primary key,
    afirmacion_id int not null,
    riasec_id int not null,
    usuario_id int not null,
    CONSTRAINT fk_afirmacion foreign key (afirmacion_id) references alejo.afirmaciones(id),
    CONSTRAINT fk_riasec foreign key (riasec_id) references alejo.riasec(id),
    CONSTRAINT fk_usuario foreign key (usuario_id) references alejo.usuario(id)
)

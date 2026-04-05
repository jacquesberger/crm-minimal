# Copyright (C) 2026  CODE3 Cooperative de solidarite
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import hashlib
import sqlite3
import datetime
import uuid


def _build_entreprise(result_set_item):
    entreprise = {}
    entreprise["id"] = result_set_item[0]
    entreprise["nom"] = result_set_item[1]
    return entreprise


def _build_interaction(result_set_item):
    interaction = {}
    interaction["id"] = result_set_item[0]
    interaction["moment"] = result_set_item[1]
    interaction["description"] = result_set_item[2]
    interaction["cree_par"] = result_set_item[3]
    return interaction


def _build_rappel(result_set_item):
    rappel = {}
    rappel["id"] = result_set_item[0]
    rappel["activation"] = result_set_item[1]
    rappel["note"] = result_set_item[2]
    return rappel


def _build_rappel_todo(result_set_item):
    rappel = {}
    rappel["id"] = result_set_item[0]
    rappel["activation"] = result_set_item[1]
    rappel["note"] = result_set_item[2]
    rappel["entreprise_id"] = result_set_item[3]
    rappel["entreprise_nom"] = result_set_item[4]
    return rappel


def _build_resume_quotidien(result_set_item):
    interaction = {}
    interaction["description"] = result_set_item[0]
    interaction["entreprise_nom"] = result_set_item[1]
    return interaction


def _build_resume_depuis(result_set_item):
    interaction = {}
    interaction["description"] = result_set_item[0]
    interaction["moment"] = result_set_item[1]
    interaction["entreprise_nom"] = result_set_item[2]
    return interaction


def _build_utilisateur(result_set_item):
    utilisateur = {}
    utilisateur["id"] = result_set_item[0]
    utilisateur["username"] = result_set_item[1]
    utilisateur["email"] = result_set_item[2]
    utilisateur["role_id"] = result_set_item[3]
    utilisateur["etat_id"] = result_set_item[4]
    return utilisateur


def _build_role(result_set_item):
    role = {}
    role["id"] = result_set_item[0]
    role["role_name"] = result_set_item[1]
    return role


def _build_etat(result_set_item):
    etat = {}
    etat["id"] = result_set_item[0]
    etat["etat_name"] = result_set_item[1]
    return etat


class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect("db/minimal.db")
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def get_entreprises(self):
        cursor = self.get_connection().cursor()
        query = "select id, nom from entreprise"
        cursor.execute(query)
        all_data = cursor.fetchall()
        return [_build_entreprise(item) for item in all_data]

    def get_entreprise(self, entreprise_id):
        cursor = self.get_connection().cursor()
        query = "select id, nom from entreprise where id = ?"
        cursor.execute(query, (entreprise_id,))
        item = cursor.fetchone()
        if item is None:
            return item
        else:
            return _build_entreprise(item)

    def add_entreprise(self, nom):
        connection = self.get_connection()
        query = "insert into entreprise(nom) values(?)"
        connection.execute(query, (nom,))
        cursor = connection.cursor()
        cursor.execute("select last_insert_rowid()")
        lastId = cursor.fetchone()[0]
        connection.commit()
        return lastId

    def get_interactions(self, entreprise_id):
        cursor = self.get_connection().cursor()
        query = "select id, moment, description, cree_par from interaction where entreprise_id = ? order by moment"
        cursor.execute(query, (entreprise_id,))
        all_data = cursor.fetchall()
        return [_build_interaction(item) for item in all_data]

    def add_interaction(self, moment, description, entreprise_id, cree_par):
        connection = self.get_connection()
        query = (
            "insert into interaction(moment, description, entreprise_id, "
            "cree_par) values(?,?,?,?)"
        )
        connection.execute(query, (moment, description, entreprise_id, cree_par))
        cursor = connection.cursor()
        cursor.execute("select last_insert_rowid()")
        lastId = cursor.fetchone()[0]
        connection.commit()
        return lastId

    def add_rappel(self, activation, note, entreprise_id):
        connection = self.get_connection()
        query = (
            "insert into rappel(done, activation, note, entreprise_id) values(0,?,?,?)"
        )
        connection.execute(
            query,
            (
                activation,
                note,
                entreprise_id,
            ),
        )
        cursor = connection.cursor()
        cursor.execute("select last_insert_rowid()")
        lastId = cursor.fetchone()[0]
        connection.commit()
        return lastId

    def delete_rappel(self, rappel_id):
        connection = self.get_connection()
        query = "delete from rappel where id = ?"
        connection.execute(query, (rappel_id,))
        connection.commit()

    def get_rappels_non_termines(self, entreprise_id):
        cursor = self.get_connection().cursor()
        query = "select id, activation, note from rappel where entreprise_id = ? and done = 0"
        cursor.execute(query, (entreprise_id,))
        all_data = cursor.fetchall()
        return [_build_rappel(item) for item in all_data]

    def get_rappels_todo(self):
        cursor = self.get_connection().cursor()
        query = "select rappel.id, rappel.activation, rappel.note, entreprise.id, entreprise.nom from rappel inner join entreprise on (entreprise.id = rappel.entreprise_id) where rappel.done = 0 and rappel.activation <= ? order by rappel.activation, entreprise.nom"
        cursor.execute(query, (datetime.date.today(),))
        all_data = cursor.fetchall()
        return [_build_rappel_todo(item) for item in all_data]

    def get_resume_quotidien(self, date):
        cursor = self.get_connection().cursor()
        query = "select interaction.description, entreprise.nom from interaction inner join entreprise on (interaction.entreprise_id = entreprise.id) where interaction.moment = ?"
        cursor.execute(query, (date,))
        all_data = cursor.fetchall()
        return [_build_resume_quotidien(item) for item in all_data]

    def get_resume_depuis(self, date):
        cursor = self.get_connection().cursor()
        query = "select interaction.description, interaction.moment, entreprise.nom from interaction inner join entreprise on (interaction.entreprise_id = entreprise.id) where interaction.moment >= ?"
        cursor.execute(query, (date,))
        all_data = cursor.fetchall()
        return [_build_resume_depuis(item) for item in all_data]

    def get_utilisateur_login_info(self, username):
        cursor = self.get_connection().cursor()
        cursor.execute(
            "select salt, hashed_password from utilisateur where username=?",
            (username,),
        )
        user_login_info = cursor.fetchone()
        if user_login_info is None:
            return None
        else:
            return user_login_info[0], user_login_info[1]

    def get_utilisateur_info_by_session(self, id_session):
        cursor = self.get_connection().cursor()
        query = (
            " select utilisateur.id, utilisateur.username, utilisateur.email, "
            "utilisateur.role_id, utilisateur.etat_id from utilisateur  "
            " join session  on utilisateur.username = session.username "
            "where session.id_session = ? "
        )
        cursor.execute(query, (id_session,))
        item = cursor.fetchone()

        if item is None:
            return item
        return _build_utilisateur(item)

    def get_utilisateur_by_id(self, user_id):
        cursor = self.get_connection().cursor()
        query = (
            "select id, username, email, role_id, etat_id from utilisateur where id = ?"
        )
        cursor.execute(query, (user_id,))
        item = cursor.fetchone()
        if item is None:
            return item
        else:
            return _build_utilisateur(item)

    def get_utilisateur_by_username(self, username):
        cursor = self.get_connection().cursor()
        query = "select id, username, email, role_id, etat_id from utilisateur where username = ?"
        cursor.execute(query, (username,))
        item = cursor.fetchone()
        if item is None:
            return item
        else:
            return _build_utilisateur(item)

    def get_utilisateurs(self):
        cursor = self.get_connection().cursor()
        query = "select id, username, email, role_id, etat_id from utilisateur"
        cursor.execute(query)
        all_data = cursor.fetchall()
        return [_build_utilisateur(item) for item in all_data]

    def get_role(self, role_id):
        cursor = self.get_connection().cursor()
        query = "select id, role_name  from role where id = ?"
        cursor.execute(query, (role_id,))
        item = cursor.fetchone()
        if item is None:
            return item
        else:
            return _build_role(item)

    def get_roles(self):
        cursor = self.get_connection().cursor()
        query = "select id, role_name  from role"
        cursor.execute(query)
        all_data = cursor.fetchall()
        return [_build_role(item) for item in all_data]

    def get_role_id(self, username):
        cursor = self.get_connection().cursor()
        query = "select role_id from utilisateur where username = ?"
        cursor.execute(query, (username,))
        item = cursor.fetchone()
        return item[0]

    def role_exists(self, role_id):
        cursor = self.get_connection().cursor()
        query = "select id from role where id = ?"
        cursor.execute(query, (role_id,))
        exists = cursor.fetchone() is not None
        return exists

    def etat_exists(self, etat_id):
        cursor = self.get_connection().cursor()
        query = "select id from etat where id = ?"
        cursor.execute(query, (etat_id,))
        exists = cursor.fetchone() is not None
        return exists

    def get_etats(self):
        cursor = self.get_connection().cursor()
        query = "select id, etat_name  from etat"
        cursor.execute(query)
        all_data = cursor.fetchall()
        return [_build_etat(item) for item in all_data]

    def add_utilisateur_actif(self, username, password, salt, hashed_password, role_id):
        connection = self.get_connection()
        cursor = connection.cursor()

        etat_id = 1
        query = "insert into utilisateur(username, salt, hashed_password, role_id, etat_id) values(?,?,?,?,?)"
        cursor.execute(query, (username, salt, hashed_password, role_id, etat_id))
        user_id = cursor.lastrowid
        connection.commit()
        query = (
            "SELECT id, username, email, role_id, etat_id FROM utilisateur WHERE id = ?"
        )
        cursor.execute(query, (user_id,))
        item = cursor.fetchone()

        if item is None:
            return None

        return _build_utilisateur(item)

    def modify_utilisateur(self, user_id, role_id, etat_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        query = "update utilisateur set role_id=?, etat_id=? " "where id=? "
        cursor.execute(query, (role_id, etat_id, user_id))
        connection.commit()

        query = (
            "select id, username, email, role_id, etat_id from utilisateur where id = ?"
        )
        cursor.execute(query, (user_id,))
        item = cursor.fetchone()
        if item is None:
            return item
        else:
            return _build_utilisateur(item)

    def save_session(self, id_session, username):
        connection = self.get_connection()
        connection.execute(
            ("insert into session(id_session, username) " "values(?, ?)"),
            (id_session, username),
        )
        connection.commit()

    def delete_session(self, id_session):
        connection = self.get_connection()
        connection.execute(("delete from session where id_session=?"), (id_session,))
        connection.commit()

    def get_session_username(self, id_session):
        cursor = self.get_connection().cursor()
        cursor.execute(
            ("select username from session where id_session=?"), (id_session,)
        )
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]

    def modify_mot_de_passe(self, username, salt, mot_de_passe_hash):
        connection = self.get_connection()
        cursor = connection.cursor()
        query = "update utilisateur set salt=?, hashed_password=? " "where username=? "
        cursor.execute(query, (salt, mot_de_passe_hash, username))
        connection.commit()
        if cursor.rowcount == 1:
            return True
        else:
            print(
                f"Erreur : Aucun utilisateur trouvé avec le username "
                f"'{username}' lors de la mise à jour du mot de passe."
            )
            return False

    def modify_mot_de_passe_by_id(self, user_id, salt, mot_de_passe_hash):
        connection = self.get_connection()
        cursor = connection.cursor()
        query = "update utilisateur set salt=?, hashed_password=? " "where id=? "
        cursor.execute(query, (salt, mot_de_passe_hash, user_id))
        connection.commit()
        if cursor.rowcount == 1:
            return True
        else:
            print(
                f"Erreur : Aucun utilisateur trouvé avec le ID "
                f"'{user_id}' lors de la mise à jour du mot de passe."
            )
            return False

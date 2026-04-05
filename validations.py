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

"""
Module de validation des utilisateurs et des mots de passe.

Ce module centralise les règles de validation applicatives liées :
- à la création d’utilisateurs
- à la modification des informations d’un utilisateur
- à la validation des mots de passe (hors validation par schéma)

"""

import datetime
from db import get_db
from password_hashing import derive_mot_de_passe_hash


def validate_entreprise(entreprise):
    result = {}
    result["is_valid"] = True
    result["global_errors"] = []

    if "nom" not in entreprise or len(entreprise["nom"]) == 0:
        result["is_valid"] = False
        result["global_errors"].append("Le nom d'entreprise est obligatoire.")

    return result


def validate_interaction(interaction, entreprise_id):
    result = {}
    result["is_valid"] = True
    result["global_errors"] = []

    print(interaction["moment"])
    if "moment" not in interaction or len(interaction["moment"]) == 0:
        result["is_valid"] = False
        result["global_errors"].append("La date de l'interaction est obligatoire.")
    elif not validate_isodate_format(interaction["moment"]):
        result["is_valid"] = False
        result["global_errors"].append(
            "Le format de la date de l'interaction est incorrect."
        )

    if "description" not in interaction or len(interaction["description"]) == 0:
        result["is_valid"] = False
        result["global_errors"].append(
            "La description de l'interaction est obligatoire."
        )

    if "entreprise_id" not in interaction or interaction["entreprise_id"] != str(
        entreprise_id
    ):
        result["is_valid"] = False
        result["global_errors"].append(
            "Le lien avec l'entreprise a été compromis. Veuillez recharger la page et recommencer."
        )

    return result


def validate_rappel(rappel, entreprise_id):
    result = {}
    result["is_valid"] = True
    result["global_errors"] = []

    print(rappel["activation"])
    if "activation" not in rappel or len(rappel["activation"]) == 0:
        result["is_valid"] = False
        result["global_errors"].append(
            "La date de l'activation du rappel est obligatoire."
        )
    elif not validate_isodate_format(rappel["activation"]):
        result["is_valid"] = False
        result["global_errors"].append(
            "Le format de la date de l'activation du rappel est incorrect."
        )

    if "note" not in rappel or len(rappel["note"]) == 0:
        result["is_valid"] = False
        result["global_errors"].append("La note du rappel est obligatoire.")

    if "entreprise_id" not in rappel or rappel["entreprise_id"] != str(entreprise_id):
        result["is_valid"] = False
        result["global_errors"].append(
            "Le lien avec l'entreprise a été compromis. Veuillez recharger la page et recommencer."
        )

    return result


def validate_isodate_format(string):
    try:
        datetime.date.fromisoformat(string)
        return True
    except:
        return False


def is_valid_user_login_info(user_info, mot_de_passe):
    salt, hashed_stored = user_info
    mot_de_pass_hash = derive_mot_de_passe_hash(salt, mot_de_passe)
    return mot_de_pass_hash == hashed_stored


def validation_nouvel_utilisateur(data):
    result = {"is_valid": True, "global_errors": []}

    username = data.get("nom-utilisateur", "")

    if get_db().get_utilisateur_by_username(username) is not None:
        result["is_valid"] = False
        result["global_errors"].append("Nom d'utilisateur déjà utilisé.")

    return result

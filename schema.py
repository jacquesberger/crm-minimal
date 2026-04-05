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

edit_utilisateur_schema = {
    "type": "object",
    "required": ["etat", "role"],
    "properties": {"etat": {"enum": ["1", "2"]}, "role": {"enum": ["1", "2"]}},
    "additionalProperties": False,
}

new_utilisateur_schema = {
    "type": "object",
    "required": ["nom-utilisateur", "role", "mot-de-passe"],
    "properties": {
        "nom-utilisateur": {
            "type": "string",
            "minLength": 1,
        },
        "role": {"enum": ["1", "2"]},
        "mot-de-passe": {
            "type": "string",
            "minLength": 15,
        },
    },
    "additionalProperties": False,
}

self_mot_de_passe_schema = {
    "type": "object",
    "required": [
        "ancien-mot-de-passe",
        "nouveau-mot-de-passe",
        "confirme-mot-de-passe",
    ],
    "properties": {
        "ancien-mot-de-passe": {
            "type": "string",
        },
        "nouveau-mot-de-passe": {
            "type": "string",
            "minLength": 15,
        },
        "confirme-mot-de-passe": {
            "type": "string",
            "minLength": 15,
        },
    },
    "additionalProperties": False,
}

admin_set_mot_de_passe_schema = {
    "type": "object",
    "required": ["nouveau-mot-de-passe"],
    "properties": {
        "nouveau-mot-de-passe": {
            "type": "string",
            "minLength": 15,
        }
    },
    "additionalProperties": False,
}
